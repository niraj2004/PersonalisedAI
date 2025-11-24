from backend.db import supabase
from backend.rag import search_similar_topics
from backend.llm import generate_email
from backend.email_service import send_email
from backend.logger import setup_logger
import markdown
import os

logger = setup_logger(__name__)

async def process_and_email_resource(resource_id: int = None):
    """
    Core logic to process a resource, generate an email, and send it.
    """
    logger.info(f"Starting process_and_email_resource for resource_id={resource_id}")
    
    # 1. Get a resource (either specific or next unprocessed)
    if resource_id:
        res = supabase.table("resources").select("*").eq("id", resource_id).execute()
    else:
        # In a real app, we'd filter by is_processed=False
        # For testing, let's just pick the latest one
        res = supabase.table("resources").select("*").order("created_at", desc=True).limit(1).execute()
        
    if not res.data:
        logger.info("No resources found.")
        return {"status": "info", "message": "No resources found."}
        
    resource = res.data[0]
    logger.info(f"Processing resource: {resource['title']}")
    
    # 2. Get chunks for this resource to form context
    chunks_res = supabase.table("resource_chunks").select("*").eq("resource_id", resource['id']).limit(5).execute()
    if not chunks_res.data:
            logger.error(f"Resource {resource['id']} has no chunks.")
            return {"status": "error", "message": "Resource has no chunks."}
            
    # Combine chunks for context (naive approach)
    resource_content = "\n".join([c['chunk_text'] for c in chunks_res.data])
    
    # 3. Find matching topic using the first chunk's embedding (simplified)
    query_embedding = chunks_res.data[0]['embedding']
    
    matched_topics = search_similar_topics(query_embedding)
    
    if not matched_topics:
        logger.info("No matching curriculum topic found.")
        return {"status": "info", "message": "No matching curriculum topic found for this resource."}
        
    topic = matched_topics[0]
    logger.info(f"Matched topic: {topic['topic_text']}")
    
    # 4. Generate Email
    email_data = generate_email(
        topic=topic['topic_text'],
        resource_title=resource['title'],
        resource_content=resource_content
    )
    
    if not email_data:
            logger.error("Failed to generate email.")
            return {"status": "error", "message": "Failed to generate email."}

    # 5. Send Email
    logger.info("Sending email...")
    # Convert markdown body to HTML (simple conversion)
    html_body = markdown.markdown(email_data['body'])
    
    target_email = os.environ.get("TARGET_EMAIL", "delivered@resend.dev") # Default to sink
    
    send_email(target_email, email_data['subject'], html_body)
    logger.info(f"Email sent to {target_email}")

    # 6. Update Resource Record
    try:
        supabase.table("resources").update({
            "is_processed": True,
            "email_sent": True,
            "matched_topic": topic['topic_text']
        }).eq("id", resource['id']).execute()
        logger.info(f"Updated resource {resource['id']} status.")
    except Exception as e:
        logger.error(f"Failed to update resource status: {e}")

    return {
        "status": "success",
        "match": {
            "topic": topic['topic_text'],
            "similarity": topic['similarity']
        },
        "email": email_data,
        "delivery": "sent"
    }
