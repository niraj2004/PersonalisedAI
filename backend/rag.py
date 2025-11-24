from sentence_transformers import SentenceTransformer

# Initialize the model once
# all-MiniLM-L6-v2 is fast and good for this use case (384 dimensions)
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list[float]:
    """
    Generates a 384-dimensional embedding for the input text.
    """
    if not text or not text.strip():
        return []
    
    # encode returns a numpy array, convert to list for JSON serialization/DB storage
    embedding = model.encode(text)
    return embedding.tolist()

def search_similar_topics(resource_embedding: list[float], match_threshold: float = 0.3, match_count: int = 1):
    """
    Searches for curriculum topics similar to the resource embedding.
    """
    from backend.db import supabase
    
    try:
        response = supabase.rpc(
            "match_curriculum_topics",
            {
                "query_embedding": resource_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
            }
        ).execute()
        return response.data
    except Exception as e:
        print(f"Error searching topics: {e}")
        return []
