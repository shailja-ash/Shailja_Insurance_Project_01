from pathlib import Path
from typing import List, Literal, Optional

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError


# Load OPENAI_API_KEY from .env file if available
load_dotenv()

# OpenAI client reads OPENAI_API_KEY automatically from environment
client = OpenAI()

# Read the system prompt from markdown file
SYSTEM_PROMPT = Path("prompts/insurance_system_prompt.md").read_text(encoding="utf-8")


# This Pydantic model is the expected JSON structure from OpenAI.
# Python 3.9 compatible: use Optional[str], not str | None.
class InsuranceBotResponse(BaseModel):
    answer_type: Literal[
        "recommendation",
        "comparison",
        "information",
        "clarifying_question",
        "out_of_scope",
    ]
    product_category: Literal["health", "term", "car", "home", "none"]
    greeting: str = Field(default="")
    final_response: str
    recommended_plan: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    coverage: Optional[str] = None
    premium: Optional[str] = None


def model_to_dict(model_obj):
    """Works with both Pydantic v1 and v2."""
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump()
    return model_obj.dict()


def ask_llm(messages: List[dict]) -> InsuranceBotResponse:
    """Call OpenAI and return a validated Pydantic object."""

    completion = client.chat.completions.parse(
        model=st.session_state["openai_model"],
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        response_format=InsuranceBotResponse,
    )

    # OpenAI parse returns a Pydantic object in message.parsed
    parsed_answer = completion.choices[0].message.parsed

    if parsed_answer is None:
        raise ValueError("OpenAI did not return valid structured JSON.")

    # Explicit validation kept for teaching clarity.
    return InsuranceBotResponse(**model_to_dict(parsed_answer))


st.title("Coverwise Insurance Chat Bot")

# Set a default model that supports structured outputs
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about health, term, car, or home insurance"):
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        try:
            validated_answer = ask_llm(st.session_state.messages)
            response_text = validated_answer.final_response

            # Show only the final human-friendly answer to the user
            st.markdown(response_text)

            # Show structured JSON for learning/debugging
            #with st.expander("Validated JSON"):
              #  st.json(model_to_dict(validated_answer))

        except ValidationError as e:
            response_text = "Sorry, I could not validate the answer structure."
            st.error(response_text)
            st.code(str(e))

        except Exception as e:
            response_text = "Sorry, something went wrong while generating the answer."
            st.error(response_text)
            st.code(str(e))

    # Save assistant response in chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
