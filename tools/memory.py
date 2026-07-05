import chromadb
from pydantic import BaseModel, Field
from pathlib import Path

# Initialize local persistent database database
DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "vector_store")
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="jarvis_memory")


#class MemorizeArgs(BaseModel):
#    fact: str = Field(description="The semantic fact, preference, or piece of data the user wants Jarvis to remember.")


#class RecallArgs(BaseModel):
#    query: str = Field(description="The search query topic to retrieve relevant past facts or data for.")

# 1. Define your schemas (keep them exactly as they are)
class MemorizeArgs(BaseModel):
    fact: str = Field(description="The actual fact or preference the user wants to save.")

class RecallArgs(BaseModel):
    query: str = Field(description="The search query topic to retrieve relevant past facts.")


def memorize_fact(fact: str) -> str:
    """Stores a piece of historical fact or user preference into long-term vector memory."""
    # Chroma handles basic string tokenization automatically
    collection.add(
        documents=[fact],
        ids=[f"fact_{collection.count() + 1}"]
    )
    return f"I have committed that to memory logs, sir."


def recall_facts(query: str) -> str:
    """Queries long-term vector memory to extract semantically matching historical notes."""
    results = collection.query(query_texts=[query], n_results=3)
    documents = results.get('documents', [[]])[0]
    if not documents:
        return "My memory stores contain no records matching that inquiry, sir."

    formatted_memory = "\n- ".join(documents)
    return f"Historical records indicate:\n- {formatted_memory}"