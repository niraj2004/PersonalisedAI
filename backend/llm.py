import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

SYSTEM_PROMPT = """
You are a First-Principles Teacher. Your goal is to explain complex concepts by breaking them down into their fundamental truths.
You are writing a daily learning email to a student.
The email should be structured, concise, and actionable.
"""

EMAIL_TEMPLATE = """
Context:
You have a curriculum topic: "{topic}"
And a resource (video/article) titled: "{resource_title}"
Content of the resource:
{resource_content}

Task:
Write a short, engaging email that explains how this resource relates to the curriculum topic.
Use a first-principles approach.

Structure:
1. Subject Line: Catchy and relevant.
2. TL;DR: 1-2 sentences summary.
3. The Core Concept: Explain the topic using the resource content (First Principles).
4. Why it Matters: Practical application.
5. Actionable Takeaway: One thing to do or think about today.

Keep it under 400 words.
"""

def generate_email(topic: str, resource_title: str, resource_content: str) -> dict:
    """
    Generates an email using Groq.
    Returns a dict with 'subject' and 'body'.
    """
    prompt = EMAIL_TEMPLATE.format(
        topic=topic,
        resource_title=resource_title,
        resource_content=resource_content[:8000] # Truncate to avoid context limit if needed
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.1-8b-instant", # Fast and good enough
            temperature=0.7,
        )
        
        full_response = chat_completion.choices[0].message.content
        
        # Simple parsing (assuming the model follows structure, or we just send the whole thing)
        # For now, let's just return the whole text as body, and try to extract subject if possible.
        # A better way is to ask for JSON output, but text is fine for v1.
        
        subject = "Daily Learning: " + topic
        body = full_response
        
        # Try to extract subject if the model explicitly wrote "Subject:"
        lines = full_response.split('\n')
        for line in lines[:5]:
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                break
        
        return {
            "subject": subject,
            "body": body
        }
    except Exception as e:
        print(f"Error generating email: {e}")
        return None
