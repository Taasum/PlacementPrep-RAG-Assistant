import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Find project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)


def generate_answer(question, context):

    prompt = f"""
You are a placement preparation assistant.

Answer the user's question using the provided context.

Rules:
1. Use the provided context as the primary source.
2. If the answer is not present in the context, say:
   "I could not find this information in the uploaded study material."
3. Do not invent information.
4. Keep the answer clear and suitable for a technical interview.

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Groq API Error:", e)
        return "An error occurred while generating the answer."