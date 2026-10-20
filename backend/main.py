
import json

from scrapper import scrape_job_url
from extractor import extract_job_details
from agent import run_agent


def process_job_url(url: str):
    """Scrape a job page, extract details, and ask the agent to track it."""

    print("\nScraping the webpage...")

    raw_text = scrape_job_url(url)

    if not raw_text or not raw_text.strip():
        print("No readable text was found on this webpage.")
        return

    print(f"Scraped {len(raw_text)} characters.")

    print("\nExtracting job details with the LLM...")
    details = extract_job_details(raw_text)

    # Validate the essential fields before asking the agent to save.
    if not isinstance(details, dict):
        print("Extraction failed: the result is not a dictionary.")
        return

    if not details.get("company") or not details.get("role"):
        print("Could not identify the company and role.")
        print("Please try another job posting URL.")
        print("Extracted result:", details)
        return

    print("\n=== Extracted Job Details ===")
    print(json.dumps(details, indent=2, ensure_ascii=False))

    confirmation = input(
        "\nDo you want to add this job to your tracker? (y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("Job not submitted to the agent.")
        return

    print("\nChecking and saving the job through the agent...")

    user_message = (
        "Please track this job. Check for duplicates first, "
        "and save it only if it is not already present.\n\n"
        "Extracted job details:\n"
        f"{json.dumps(details, ensure_ascii=False)}"
    )

    result = run_agent(user_message)

    print("\n=== Agent Response ===")
    print(result)


def main():
    """Application entry point."""

    while True:
        print("\n===== AI JOB TRACKER =====")
        print("1. Scrape and track a job from a URL")
        print("2. Ask about tracked jobs")
        print("3. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            url = input("Paste the public job posting URL: ").strip()

            if not url.startswith(("https://", "http://")):
                print("Please enter a valid HTTP or HTTPS URL.")
                continue

            try:
                process_job_url(url)
            except Exception as error:
                print(f"\nCould not process this job: {error}")

        elif choice == "2":
            question = input(
                "What would you like to know about your jobs? "
            ).strip()

            if question:
                try:
                    print("\nAgent:", run_agent(question))
                except Exception as error:
                    print(f"Agent error: {error}")

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()



# import os
# from groq import Groq
# from fastapi import FastAPI
# from dotenv import load_dotenv
# import httpx 
# import json

# app = FastAPI(title="Tavily Chatbot API")
# # ── Load environment ────
# load_dotenv()
# api_key = os.environ.get("GROQ_API_KEY","gorq_test_1e2f3g4h5i6j7k8l9m0n")
# # print(f"Using GROQ_API_KEY: {api_key}")

# client = Groq(api_key=api_key)

# # models = client.models.list()
# # for m in models.data:
# #     print(m.id)

# def get_application_count(status):
#      fake_db = {"applied": 12, "interviewing": 3, "rejected": 5}
#      return fake_db.get(status, 0)
 
# def add_application(company, role, status="applied"):
#     # pretend this writes to your DB
#     return f"Added {role} at {company} with status '{status}'" 

# available_funcs = {
#      "get_app_count" : get_application_count,
#       "add_app"  : add_application
     
# }
 

# tools = [
#     {
#       "type":"function",
#         "function":{
#         "name":"get_app_count",
#         "description":"Get number of job applications with a given status",   
#         "parameters":{
#                 "type":"object",
#                     "properties":{
#                     "status":{"type":"string","enum":["applied","interviewing","rejected"]}  
#                     },
#                 "required":["status"]
#             }
#         }
#     } ,
#     {   
#      "type" :"function",
#         "function":{
#             "name":"add_app",
#             "description":"Add a new job application record with a company, role, and optional status",   
#             "parameters":{
#                 "type":"object",
#                     "properties":{
#                     "company":{"type":"string"},
#                     "role":{ "type":"string" },
#                     "status":{ "type":"string","enum":["applied","interviewing","rejected"]}
#                     },         
#                 "required":["company","role"]
#             }
#         }     
#      }
#     ] 
 

# #system prompt
# system_prompt = """
# You are a helpful IT support chatbot for 'Tech Solutions'.
# rules:
#  retrun json format wgen user asked to summarize  something
#  Reply normally for general questions, but if the user asks about application status or count, make a tool call instead of answering directly.
# """

# #message array
# messages =[
#     {"role":"system", "content":system_prompt},
    
# ]
# def cli():
#     MAX_TOOL_ROUNDS = 5
    
#     while True:
#         user_input = input("You:")
#         if user_input == 'x':
#             print("existing the agent")
#             break
#         messages.append({"role":"user","content":user_input})
#         for _ in range(MAX_TOOL_ROUNDS):
#             resp = client.chat.completions.create(
#                 model="qwen/qwen3.8-27b",
#                 messages=messages,
#                 tools=tools,
#                 tool_choice="auto",
#                 max_tokens=500,
#                 # response_format={"type": "json_object"}
#             )
            
#             msg = resp.choices[0].message
#             print("DEBUG tool_calls:", msg.tool_calls) 
#             if not msg.tool_calls:
#                 print("Assistant:", msg.content) 
#                 messages.append({"role":"assistant","content":msg.content,})
#                 break
                
#             messages.append({
#                 "role":"assistant",
#                 "content":msg.content,
#                 "tool_calls":[tc.model_dump() for tc in msg.tool_calls]
#             })
#             for call in msg.tool_calls:
#                 func = available_funcs.get(call.function.name)
#                 if func is None:
#                     result = f"Error:no such tool exist '{call.function.name}'"
#                 try:    
#                    args = json.loads(call.function.arguments)
#                 except:
#                     result = "Error: could not parse tool arguments"
#                 try:       
#                     result = func(**args)
#                 except Exception as e:
#                     result = f"Error: tool failed — {e}"
                       
                
#                 messages.append({
#                     "role": "tool",
#                     "tool_call_id": call.id,
#                     "content": str(result)
#                 })
#     else:  
#        print("closing the application safely!!!!!!!!!!!!!")        

# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1 and sys.argv[1] == "server":
#         import uvicorn
#         uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
#     else:
#         try:
#           cli()
#         except Exception as e:
#             print("closing the application safely!!!!!!!!!!!!!",e) 
   

