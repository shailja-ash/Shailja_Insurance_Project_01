# Coverwise Insurance Advisor

A GenAI-powered insurance advisor chatbot built using OpenAI GPT-4o-mini, Streamlit, and Pydantic Structured Outputs.

The chatbot helps users understand, compare, and select insurance plans based on their needs while enforcing domain-specific guardrails and returning validated structured responses.

---

# Features

* Health Insurance recommendations
* Term Insurance information
* Car Insurance guidance
* Home Insurance guidance
* Guardrails to restrict responses to insurance-related questions only
* Prompt engineering using external Markdown prompt templates
* Product catalog maintained separately from application code
* Streamlit-based conversational interface
* OpenAI GPT-4o-mini integration
* Structured JSON outputs using Pydantic
* Response schema validation

---

# Project Structure


STREAMLIT_DEMO/
│
├── data/
│   └── products.py
│
├── prompts/
│   └── insurance_system_prompt.md
│
├── app.py
├── prompt_loader.py
├── streamlit_demo.py
├── requirements.txt
├── .env
└── ReadMe.md


---

# Folder Description

| File / Folder                      | Purpose                                   |
| ---------------------------------- | ----------------------------------------- |
| data/products.py                   | Stores insurance product catalog          |
| prompts/insurance_system_prompt.md | Externalized system prompt                |
| prompt_loader.py                   | Loads prompt templates from markdown      |
| app.py                             | OpenAI integration and chatbot logic      |
| streamlit_demo.py                  | Streamlit chat interface                  |
| .env                               | Stores API keys and environment variables |
| ReadMe.md                          | Project documentation                     |

---

# Supported Insurance Products

## Health Insurance

* Bronze Health Plan
* Silver Health Plan
* Gold Health Plan

## Term Insurance

* Life Secure Term Plan

## Car Insurance

* Car Protect Plan

## Home Insurance

* Home Secure Plus

---

# Structured Output Validation

The application uses OpenAI Structured Outputs and Pydantic models to ensure responses follow a predictable schema.

## Response Schema

```python
class InsuranceBotResponse(BaseModel):
    answer_type: Literal[
        "recommendation",
        "comparison",
        "information",
        "clarifying_question",
        "out_of_scope",
    ]

    product_category: Literal[
        "health",
        "term",
        "car",
        "home",
        "none",
    ]

    greeting: str
    final_response: str
    recommended_plan: Optional[str]
    reasons: List[str]
    coverage: Optional[str]
    premium: Optional[str]
```

## Benefits

* Strong schema validation
* Consistent response structure
* Type-safe AI outputs
* Easier frontend integration
* Better error handling
* Reduced risk of malformed responses

---

# Technical Highlights

* OpenAI GPT-4o-mini integration
* Streamlit chat interface
* Pydantic structured outputs
* OpenAI response parsing
* Prompt externalization using Markdown
* Product catalog externalization
* Session-based conversation memory
* Environment variable management using python-dotenv


---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd STREAMLIT_DEMO
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Virtual Environment

### Linux / Mac

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Setup

Create a `.env` file in the project root.

```text
OPENAI_API_KEY=your_openai_api_key
```

---

# Run the Application

```bash
streamlit run streamlit_demo.py
```

The application will launch locally in your browser.

---

# Example Questions

## Health Insurance

* I am 25 years old and single. Which health insurance should I buy?
* I am married and have two children. Which health plan is suitable?
* Compare Bronze and Gold Health Plans.
* What are the available health insurance plans?

## Car Insurance

* I recently purchased a new car. Which insurance should I take?
* Tell me about the Car Protect Plan.

## Home Insurance

* What does Home Secure Plus cover?
* Do you provide home insurance?

## Term Insurance

* What term insurance plans do you offer?
* Tell me about Life Secure Term Plan.

---

# Guardrails

The chatbot only answers questions related to:

* Health Insurance
* Term Insurance
* Car Insurance
* Home Insurance

For unrelated questions, the chatbot responds appropriately and prevents out-of-scope discussions.

Examples:

* Who is the Prime Minister of India?
* Write a Python program.
* Give me stock market advice.

These queries are intentionally rejected.

---

# Evaluation Approach

The chatbot can be evaluated on:

* Recommendation accuracy
* Product selection correctness
* Guardrail effectiveness
* Response formatting
* Structured output compliance
* Hallucination prevention

Evaluation

The chatbot was evaluated using an automated rubric-based evaluation framework.

Evaluation Coverage

The evaluation suite tests:

Insurance recommendations
Product comparisons
Information requests
Clarifying questions
Out-of-scope queries
Guardrail compliance
Structured JSON response validation
Scoring Criteria

Each test case is scored against:

Valid structured JSON output
Correct answer type classification
Correct product category identification
Correct plan recommendation
Coverage accuracy
Premium accuracy
Required content presence
Forbidden content absence
Greeting compliance
Out-of-scope handling
Evaluation Files
evaluate_coverwise_rubric.py
coverwise_eval_cases.json
evaluation_report.json
Running Evaluation
python evaluate_coverwise_rubric.py
Generated Report

Running the evaluation generates:

evaluation_report.json

The report includes:

Total test cases
Passed and failed cases
Overall accuracy percentage
Detailed scoring breakdown
Guardrail effectiveness checks
Structured output validation results

---



# Tech Stack

* Python
* Streamlit
* OpenAI API
* GPT-4o-mini
* Pydantic
* Markdown Prompt Templates
* Git & GitHub

---

----------------------------------------------------------------------------
Week2  Project:

Project Brief

## Topics
# Project Insurance and policy advisor co pilot
# Insurance
# Insurance suggestion, risk analysis

**Build a Banking/Insurance FAQ Chatbot that demonstrates all Week 1-2 skills:**

## prompt engineering- done, 
## few-shot learning- done,  
## chain-of-thought reasoning- done,  
## structured JSON outputs- done
## guardrails done
## and a  simple UI- done.

# Requirements
Accept natural language banking questions (account types, loan eligibility, interest rates, KYC process)
Use engineered system prompts with role-setting, output formatting, and safety guardrails
Implement few-shot examples for at least 3 banking intent categories
Use chain-of-thought for complex queries (e.g., loan eligibility calculation)
Return structured JSON responses validated with Pydantic
Include input guardrails: PII detection, off-topic filtering, prompt injection defense.
Build a simple UI using Streamlit or Gradio or any framework of your choice
Deliverables
GitHub repository with README, requirements.txt, and clear setup instructions
Working Streamlit/Gradio app
Prompt template library (YAML/JSON)
Evaluation report: test 20 queries and document accuracy, formatting, and guardrail effectiveness
