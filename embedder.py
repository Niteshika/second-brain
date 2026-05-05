import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key = os.getenv("GEMINI_API_KEY")
)

chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = chroma_client.get_or_create_collection(name="second_brain")


def embed_documents(documents):
    """Embed heading-based chunks into ChromaDB"""
    print("🔄 Starting embedding process...\n")

    for doc in documents:
        chunk_id = doc["page_id"]

        # Skip if already embedded
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue

        vector = embeddings.embed_query(doc["content"])

        collection.add(
            ids=[chunk_id],
            embeddings=[vector],
            documents=[doc["content"]],
            metadatas=[{
                "title": doc["title"],
                "section": doc.get("section", ""),
                "url": doc["url"],
                "last_edited": doc["last_edited"],
            }]
        )

        print(f"✅ Embedded: {doc['title']} — {doc.get('section', '')}")

    print(f"\n🧠 Total chunks in vector store: {collection.count()}")

def query_vector_store(query, n_results=4):
    """Search ChromaDB for most relevant chunks"""
    query_vector = embeddings.embed_query(query)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return results


if __name__ == "__main__":
    from notion_loader import load_notion_documents

    docs = load_notion_documents()
    embed_documents(docs)

    # Quick test query
    print("\n🔍 Testing retrieval...")
    test_results = query_vector_store("What are my notes about?")
    for i, (doc, meta) in enumerate(zip(
        test_results["documents"][0],
        test_results["metadatas"][0]
    )):
        print(f"\nResult {i+1} — from: {meta['title']}")
        print(doc[:150])