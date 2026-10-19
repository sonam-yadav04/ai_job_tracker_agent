import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()


def extract_job_details(raw_text: str) -> dict:
     resp = client.chat.completions.create(
        model = "qwen/qwen3.8-27b",
        messages=[
                    {
                    "role": "system",
                    "content": """
                        Extract job details from the provided job description.
                        Return a JSON object with these fields:
                        - company
                        - role
                        - salary
                        - requirements

                        Use null if company, role, or salary is missing.
                        Use an empty list if requirements are missing.
                        Do not invent information.
                        """
                    },
                    {
                        "role":"user",
                        "content":raw_text
                    }
                ],


        response_format={"type": "json_object"},
        max_tokens=500,
        temperature=0,
     )
     result =  json.loads(resp.choices[0].message.content)
     return result
