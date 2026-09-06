import os
import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.rag_chain import llm, prompt

from eval_questions import EVAL_QUESTIONS  

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
eval_collection = chroma_client.get_or_create_collection(name="eval_second_brain")


def query_eval_store(query, n_results=4):
    """Search the eval collection for the most relevant chunks."""
    query_vector = embeddings.embed_query(query) # embeded the query

    results = eval_collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return results

def get_retrieved_pairs(results):
    """
    Convert Chroma query results into a list of (title, section) tuples,
    in the order they were retrieved (rank order matters for MRR).
    """
    pairs=[]
    metadatas = results["metadatas"][0]

    for meta in metadatas:
        pair = (meta["title"], meta["section"])
        pairs.append(pair)

    return pairs

def recall_at_k(retrieved_pairs, relevant_pairs):
    """
    What fraction of the truly relevant chunks appear in the retrieved list?
    Returns None if relevant_pairs is empty (distractor question — recall doesn't apply).
    """
    if not relevant_pairs:
        return None

    count = 0
    
    #count how many items in relevant_pairs also appear in retrieved_pairs
    for relevant in relevant_pairs:
            if relevant in retrieved_pairs:
                count += 1
    return count/len(relevant_pairs)
    
def reciprocal_rank(retrieved_pairs, relevant_pairs):
    if not relevant_pairs:
        return None

    for i, retrieved in enumerate(retrieved_pairs):
            if retrieved in relevant_pairs:
                return 1/(i+1)

    return 0

def run_retrieval_eval(k=4):
    """Run Recall@k and MRR across all eval questions with ground truth."""
    recalls = []
    reciprocal_ranks = []

    for item in EVAL_QUESTIONS:
        question = item["question"]
        relevant_pairs = item["relevant"]

        results = query_eval_store(question, n_results=k)
        retrieved_pairs = get_retrieved_pairs(results)

        recall = recall_at_k(retrieved_pairs, relevant_pairs)
        rr = reciprocal_rank(retrieved_pairs, relevant_pairs)

        if recall is not None:
            recalls.append(recall)
        if rr is not None:
            reciprocal_ranks.append(rr)

        print(f"Q: {question}")
        print(f"  Retrieved: {retrieved_pairs}")
        print(f"  Relevant:  {relevant_pairs}")
        print(f"  Recall@{k}: {recall}, RR: {rr}\n")

    avg_recall = sum(recalls) / len(recalls) if recalls else 0
    avg_mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0

    print(f"\n📊 Retrieval Eval Summary (k={k})")
    print(f"Average Recall@{k}: {avg_recall:.3f}")
    print(f"MRR: {avg_mrr:.3f}")

def eval_generate(question, k=4):
    """Retrieve from eval collection, generate an answer, no chat history."""
    results = query_eval_store(question, n_results=k)
    retrieved_pairs = get_retrieved_pairs(results) 
    context = "\n\n".join(results["documents"][0])  
    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "chat_history": [],
        "question": question
    })
    
    answer = response.content if isinstance(response.content, str) else response.content[0]["text"]
    return answer, context, retrieved_pairs  

# if __name__ == "__main__":
#     run_retrieval_eval()

if __name__ == "__main__":
    sample_questions = EVAL_QUESTIONS[-8:]  # just try the first 3 for now

    for item in sample_questions:
        question = item["question"]
        answer, context, retrieved_pairs = eval_generate(question)

        print(f"Q: {question}")
        print(f"\nRetrieved sections: {retrieved_pairs}")
        print(f"\nContext:\n{context}")
        print(f"\nAnswer:\n{answer}")
        print("\n" + "="*80 + "\n")