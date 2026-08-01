from AI.database import database as db
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = OPENROUTER_API_KEY


)

def get_response(message):
    original_message = message

    if db.get_setting("memory_enabled") == "true":
        update_memory()
    


    memories = db.get_all_memories()

    memory_text = ""
    
    for key, value in memories:
        memory_text += f"{key}: {value}\n"

    messages = [{
        "role" : "system",
        "content": f"""
You are Abuukar AI, a senior software engineer assistant.

You specialise in:
- Python
- Flask
- HTML/CSS
- JavaScript
- Databases
- APIs
- Cyber Security basics

Your goal is to help the user build projects and become a better developer.

User information:
{memory_text}

Rules:
1. Give accurate technical answers.
2. Explain code clearly.
3. Prefer practical solutions.
4. If code has mistakes, explain what is wrong.
5. Do not pretend to know something you don't know.
"""
}]


    history = db.get_chat_history()

    messages.extend(history)

    messages.append({
        "role" : "user",
        "content" : message
    })

    response = client.chat.completions.create(
        model = "meta-llama/llama-3.2-3b-instruct",
        messages=messages
    )

    content = response.choices[0].message.content

    db.save_chat("user", message)
    db.save_chat("assistant", content)
    



    return content

def update_memory():

    history = db.get_chat_history()


    #ask the AI what should be remembered
    response = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct",
        messages = [{
            "role" : "system",
            "content" : """
You are a memory extraction AI.

Your job is to extract useful long-term information about the user from the conversation.

Only save:
- Name
- Interests
- Skills
- Goals
- Preferences
- Important facts that help personalize future conversations.

Do NOT save:
- Greetings
- Random questions
- Temporary emotions
- Short-term situations

IMPORTANT OUTPUT RULES:

Return ONLY valid JSON.
Do not use markdown.
Do not use ```.

Your output MUST always be a JSON array.

Each item MUST have exactly two fields:
- "key"
- "value"

The key must describe the memory category.
The value must be a normal string.

Never use:
"name": "..."
"skill": "..."
"interest": "..."

Always use:

{
 "key": "category",
 "value": "information"
}

Example output:

[
 {
   "key": "name",
   "value": "Josh"
 },
 {
   "key": "interest",
   "value": "Python programming"
 },
 {
   "key": "skill",
   "value": "Python and Flask"
 }
]

If there is nothing important to remember, return:

[]"""
        },
        {
            "role" : "user",
            "content" : str(history)
        }])

    content = response.choices[0].message.content
    if not content:
        print("AI returned nothing")
        return
    
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    # just incase
    if not content:
        print("AI returned nothing")
        return

    try:
        memories = json.loads(content)

    except json.JSONDecodeError:
        print("BROKEN JSON")
        return

    for memory in memories:
        if not isinstance(memory, dict):
            continue

        value = memory.get("value")
        key = memory.get("key")

        if not key or not value:
            continue

        if isinstance(value, list):
            value = ", ".join(value)

        if value.strip():
            db.save_memory(
            key,
            value
        )












        

     





    



    
    
    
