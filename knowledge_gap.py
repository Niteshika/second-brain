import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Load ChromaDB
vectorstore = Chroma(
    persist_directory="./data/chroma_db",
    embedding_function=embeddings,
    collection_name="second_brain"
)


def get_all_chunks():
    """Fetch all chunks and embeddings from ChromaDB"""
    collection = vectorstore._collection
    results = collection.get(include=["documents", "metadatas", "embeddings"])
    return results


def cluster_chunks(embeddings_matrix, n_clusters=None):
    """Cluster chunks using KMeans"""
    n = len(embeddings_matrix)
    if n < 2:
        return None, None

    # Auto-decide cluster count if not given
    if n_clusters is None:
        n_clusters = min(max(2, n // 3), 8)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings_matrix)
    return labels, kmeans


def name_cluster(chunks_in_cluster):
    """Ask Gemini to name a cluster based on its content"""
    sample = "\n\n".join(chunks_in_cluster[:3])
    prompt = f"""Based on these notes, give a short 2-4 word topic name that best describes them.
Reply with ONLY the topic name, nothing else.

Notes:
{sample}"""
    response = llm.invoke(prompt)
    answer = response.content if isinstance(response.content, str) else response.content[0]["text"]
    return answer.strip()


def detect_blind_spots(cluster_names, user_context=""):
    """Ask Gemini to identify missing topics based on existing ones"""
    topics_list = "\n".join([f"- {name}" for name in cluster_names])
    context_line = f"About the person: {user_context}\n" if user_context.strip() else ""
    prompt = f"""You are a strict knowledge advisor who always finds gaps. 
A person's notes cover these topics:
{topics_list}

Based on these topics, what are 4-5 important related topics they have NOT covered that would significantly 
strengthen their knowledge?
Be specific — not generic. For example don't say "Machine Learning", say "Supervised vs Unsupervised Learning tradeoffs".
For each topic, give a short 1-2 sentence description of what they should learn about it.
Reply ONLY as a JSON array of objects in this exact format:
[
  {{"topic": "Topic Name", "description": "What to learn about this topic"}},
  {{"topic": "Topic Name", "description": "What to learn about this topic"}}
]
No explanation, no markdown, just the JSON array."""

    response = llm.invoke(prompt)
    import json
    try:
        answer = response.content if isinstance(response.content, str) else response.content[0]["text"]
        clean = response.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return [{"topic": "Could not detect gaps", "description": "Try adding more notes and rerunning"}]


def run_knowledge_gap_analysis(user_context=""):
    """Main function — runs full analysis and returns results"""
    print("🔍 Fetching all chunks...")
    data = get_all_chunks()

    if not data["ids"]:
        return None, "No notes found. Please sync your Notion notes first."

    documents = data["documents"]
    metadatas = data["metadatas"]
    embeddings_matrix = np.array(data["embeddings"])

    print(f"📊 Clustering {len(documents)} chunks...")
    labels, kmeans = cluster_chunks(embeddings_matrix)

    if labels is None:
        return None, "Not enough notes to analyze. Add more notes and sync again."

    # Group chunks by cluster
    clusters = {}
    for i, label in enumerate(labels):
        if label not in clusters:
            clusters[label] = {"chunks": [], "metadatas": []}
        clusters[label]["chunks"].append(documents[i])
        clusters[label]["metadatas"].append(metadatas[i])

    # Name each cluster
    print("🏷️  Naming clusters...")
    cluster_names = {}
    for label, data in clusters.items():
        name = name_cluster(data["chunks"])
        cluster_names[label] = name
        print(f"  Cluster {label}: {name}")

    # Detect blind spots
    print("🔦 Detecting knowledge gaps...")
    blind_spots = detect_blind_spots(list(cluster_names.values()), user_context)

    results = {
        "clusters": [
            {
                "name": cluster_names[label],
                "chunk_count": len(data["chunks"]),
                "sources": list(set([m.get("title", "Untitled")
                                for m in data["metadatas"]]))
            }
            for label, data in clusters.items()
        ],
        "blind_spots": blind_spots,
    }

    return results, None