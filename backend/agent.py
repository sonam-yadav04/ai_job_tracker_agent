import os
from groq import Groq
import json
from dotenv import load_dotenv
load_dotenv()
from job_tools import(get_application_count,save_job,check_duplicate)
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

MODEL = "qwen/qwen3.8-27b"

available_funcs = {
    "get_app_count" : get_application_count,
    "save_job"  : save_job,
    "check_duplicate" : check_duplicate
}

tools = [
          {
           "type":"function",
            "function":{
              "name" : "check_duplicate",
              "description":"check whether the job from this company  and role already exists.",
              "parameters": {
                "type":"object",
                 "properties":{
                   "company":{"type":"string"},
                    "role"  :{"type":"string"} 
                  } ,
                 "required":["company","role"]
              },
             },
           },
        {
        "type":"function",
          "function":{
           "name" : "save_job",
              "description":"Save a new job. Use only after checking for duplicates. Do not mark a job as applied unless the user says they applied.",
              "parameters": {
                "type":"object",
                 "properties":{
                   "company":{"type":"string"},
                    "role"  :{"type":"string"},
                    "salary": {
                        "type": ["string", "null"],
                        "description": "Salary if available, otherwise null.",
                    },
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "status": {
                        "type": "string",
                        "description": "Use saved for a job that has only been saved.",
                    },
                  } ,
                 "required":["company","role"]
              },
             },
           },
        {
        "type":"function",
         "function":{
           "name":"get_application_count",
           "description":"Count tracked jobs. Use status all to count every job, or a specific status to count matching jobs.",
           "parameters":{
             "type":"object",
             "properties":{
               "status":
               {
                "type":"string",
                "description":"Optional. 'all' for total, or 'saved'/'applied'/'rejected'. Defaults to 'all'.",
               }
             },
             "required":["status"]
           },
         } , 
        }, 
      ]

SYSTEM_PROMPT = """
You are an AI job-tracking assistant.

When the user provides extracted job details and wants to track the job:
1. Call check_duplicate first with the company and role.
2. If the result is true, do not save the job.
3. If the result is false, call save_job with the available details.
4. Report success only if save_job confirms that the job was saved.
When the user asks for application counts, use get_application_count.
Never invent job details or claim an operation succeeded without tool results.
"""

def run_agent(user_message:str)->str:
    """send a message to llm and  excute it's requested tool."""
    messages = [
        {"role":"system", "content":SYSTEM_PROMPT},
        {"role":"user", "content" : user_message }

    ]
    for _ in range(5):   
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=500,
            )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""

        messages .append({
            "role":"assistant",
            "content":msg.content,
            "tool_calls":[{
              "id":call.id,
              "type":"function",
              "function":{
                "name":call.function.name,
                "arguments":call.function.arguments
              },
            }
            for call in messages.tool_calls
            ],
        })
        for call in messages.tool_calls:
            function_name = call.function_name
            function = available_funcs.get(function_name)
            try:
                arguments = json.loads(call.function.arguments)

                if function is None:
                    result = {"error": f"Unknown tool: {function_name}"}
                else:
                    result = function(**arguments)

            except (json.JSONDecodeError, TypeError, ValueError) as error:
                result = {"error": str(error)}
            except Exception as error:
                result = {"error": f"Tool execution failed: {error}"}
            
            messages.append({
              "role":"tool",
              "tool_call_id":call.id,
              "contnet":json.dumps(result,ensure_ascii=False),
            })
        
    return "I couldn't complete the request within the allowed tool-call rounds."

 
        
     