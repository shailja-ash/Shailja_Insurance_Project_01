from dotenv import load_dotenv
from openai import OpenAI
from prompt_loader import load_system_prompt
from data.products import PRODUCTS

load_dotenv()

client = OpenAI()

def askllm(user_prompt, system_prompt=" "):

    stream = client.chat.completions.create(
        model = 'gpt-4o-mini',
        messages = [
            {
                "role":"system",
                "content":system_prompt
            },
            {
                "role":"user",
                "content":user_prompt
            }
],
        temperature = 0.1,
        stream=True
    )
    
    
    print(stream)
    return stream


SYSTEM_PROMPT = load_system_prompt(PRODUCTS)

    



