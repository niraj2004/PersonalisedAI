from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.db import supabase
from backend.rag import generate_embedding
from backend.ingestion import fetch_content, chunk_text
from backend.llm import generate_email
from backend.rag import search_similar_topics
from backend.scheduler import start_scheduler
from backend.email_service import send_email
from contextlib import asynccontextmanager
from pydantic import BaseModel
import pypdf
import io
import os
import markdown

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    pass

app = FastAPI(title="Personal Learning Assistant API", lifespan=lifespan)

@app.get("/health")
def health_check():
    try:
        # Simple query to check connection
        supabase.table("resources").select("id").limit(1).execute()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}

@app.post("/upload/curriculum")
async def upload_curriculum(file: UploadFile = File(...)):
    try:
        content = ""
        filename = file.filename.lower()
        
        # Extract text based on file type
        if filename.endswith(".pdf"):
            pdf_bytes = await file.read()
            pdf_file = io.BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                content += page.extract_text() + "\n"
        elif filename.endswith(".txt") or filename.endswith(".md"):
            content_bytes = await file.read()
            content = content_bytes.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or TXT.")

        if not content.strip():
            raise HTTPException(status_code=400, detail="File is empty or could not be read.")

        # Simple splitting by newlines to get topics
        # In a real app, we might want smarter chunking
        topics = [line.strip() for line in content.split('\n') if line.strip()]
        
        inserted_count = 0
        for topic in topics:
            # Generate embedding
            embedding = generate_embedding(topic)
            
            # Store in DB
            data = {
                "topic_text": topic,
                "embedding": embedding,
                "source_file": filename
            }
            supabase.table("curriculum_topics").insert(data).execute()
            inserted_count += 1
            
        # Store the full file content for later retrieval
        file_data = {
            "filename": filename,
            "content": content
        }
        supabase.table("curriculum_files").insert(file_data).execute()
            
        return {"status": "success", "message": f"Processed {inserted_count} topics from {file.filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ResourceRequest(BaseModel):
    url: str

@app.post("/upload/resource")
async def upload_resource(request: ResourceRequest):
    try:
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")

        # 1. Check if already exists
        existing = supabase.table("resources").select("id").eq("url", url).execute()
        if existing.data:
            return {"status": "info", "message": "Resource already exists."}

        # 2. Fetch Content
        content_data = fetch_content(url)
        
        # 3. Insert Resource Record
        resource_record = {
            "url": url,
            "title": content_data["title"],
            "type": content_data["type"],
            "is_processed": True # We are processing it immediately
        }
        res = supabase.table("resources").insert(resource_record).execute()
        resource_id = res.data[0]['id']

        # 4. Chunk and Embed
        chunks = chunk_text(content_data["text"])
        
        inserted_chunks = 0
        for chunk in chunks:
            embedding = generate_embedding(chunk)
            chunk_data = {
                "resource_id": resource_id,
                "chunk_text": chunk,
                "embedding": embedding
            }
            supabase.table("resource_chunks").insert(chunk_data).execute()
            inserted_chunks += 1

        return {
            "status": "success", 
            "message": f"Processed {content_data['type']}: {inserted_chunks} chunks created."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/resources/{resource_id}")
def delete_resource(resource_id: int):
    """
    Delete a resource and its chunks.
    """
    try:
        # Delete chunks first (cascade should handle this, but good to be explicit or rely on DB)
        # Our schema has ON DELETE CASCADE for chunks, so deleting resource is enough.
        res = supabase.table("resources").delete().eq("id", resource_id).execute()
        if not res.data:
             raise HTTPException(status_code=404, detail="Resource not found")
        return {"status": "success", "message": "Resource deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curriculum/files")
def list_curriculum_files():
    """
    List uploaded curriculum files.
    """
    try:
        res = supabase.table("curriculum_files").select("id, filename, created_at").order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curriculum/files/{file_id}/content")
def get_curriculum_file_content(file_id: int):
    """
    Get content of a curriculum file.
    """
    try:
        res = supabase.table("curriculum_files").select("content, filename").eq("id", file_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="File not found")
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resources")
def list_resources():
    """
    List all processed resources.
    """
    try:
        res = supabase.table("resources").select("*").order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-email")
async def trigger_email_manual(resource_id: int = None):
    """
    Manually triggers the email generation for a specific resource or the next unprocessed one.
    """
    from backend.processor import process_and_email_resource
    try:
        return await process_and_email_resource(resource_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
