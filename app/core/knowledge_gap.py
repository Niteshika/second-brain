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
    model="openai/gpt-oss-120b",
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
    """Ask llama to name a cluster based on its content"""
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

def detect_contradictions(chunks, metadatas):
    """Find contradicting notes within the same cluster"""
    if len(chunks) < 2:
        return []

    contradictions = []
    emb_matrix = np.array([
        embeddings.embed_query(chunk) for chunk in chunks
    ])

    similarity_matrix = cosine_similarity(emb_matrix)
    checked_pairs = set()

    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            if (i, j) in checked_pairs:
                continue
            checked_pairs.add((i, j))

            if similarity_matrix[i][j] < 0.75:
                continue

            prompt = f"""Do these two notes contradict each other?
Note 1: {chunks[i]}

Note 2: {chunks[j]}

Reply ONLY with a JSON object in this exact format:
{{"contradicts": true/false, "reason": "one sentence explanation or empty string"}}
No markdown, no extra text."""

            try:
                response = llm.invoke(prompt)
                answer = response.content if isinstance(response.content, str) else response.content[0]["text"]
                clean = answer.strip().replace("```json", "").replace("```", "").strip()
                result = json.loads(clean)

                if result.get("contradicts"):
                    contradictions.append({
                        "note_1": chunks[i][:200],
                        "note_2": chunks[j][:200],
                        "reason": result.get("reason", ""),
                        "source_1": metadatas[i].get("title", "Untitled"),
                        "source_2": metadatas[j].get("title", "Untitled"),
                    })
            except:
                continue

    return contradictions


def detect_stale_notes(metadatas, documents, days_threshold=90):
    """Find notes that haven't been updated in over 30 days"""
    from datetime import datetime, timezone

    stale = []
    seen_pages = set()

    for i, meta in enumerate(metadatas):
        page_id = meta.get("title", "Untitled")
        if page_id in seen_pages:
            continue
        seen_pages.add(page_id)

        last_edited = meta.get("last_edited", "")
        if not last_edited:
            continue

        try:
            edited_date = datetime.fromisoformat(
                last_edited.replace("Z", "+00:00")
            )
            age_days = (datetime.now(timezone.utc) - edited_date).days

            if age_days >= days_threshold:
                stale.append({
                    "title": meta.get("title", "Untitled"),
                    "url": meta.get("url", ""),
                    "last_edited": edited_date.strftime("%B %d, %Y"),
                    "age_days": age_days,
                    "preview": documents[i][:150]
                })
        except:
            continue

    # Sort by oldest first
    stale.sort(key=lambda x: x["age_days"], reverse=True)
    return stale


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

    # Detect contradictions
    print("⚡ Detecting contradictions...")
    all_contradictions = []
    for label, data in clusters.items():
        contradictions = detect_contradictions(
            data["chunks"],
            data["metadatas"]
        )
        all_contradictions.extend(contradictions)

    # Detect stale notes
    print("🕰️  Detecting stale notes...")
    stale_notes = detect_stale_notes(metadatas, documents, days_threshold=90)

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
        "contradictions": all_contradictions,
        "stale_notes": stale_notes
    }

    return results, None