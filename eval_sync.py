"""
One-off script to sync the eval Notion database into a separate,
isolated ChromaDB collection ("eval_second_brain"). Does not touch
notion_loader.py or your real "second_brain" collection.
"""

import os
import chromadb
from dotenv import load_dotenv
from notion_client import Client

from app.core.notion_loader import extract_text_from_blocks
from app.core.parser import parse_documents
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

EVAL_DATABASE_ID = "3d0bf28522b9801aa9bef169b398a733"

notion = Client(auth=os.getenv("NOTION_API_KEY"))

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
eval_collection = chroma_client.get_or_create_collection(name="eval_second_brain")


def get_eval_pages():
    """Fetch all pages inside the eval database."""
    # Databases now contain "data sources" — we need the data source ID,
    # not the database ID, to actually query rows.
    database = notion.databases.retrieve(database_id=EVAL_DATABASE_ID)
    data_source_id = database["data_sources"][0]["id"]

    pages = []
    response = notion.data_sources.query(data_source_id=data_source_id)
    pages.extend(response["results"])

    while response.get("has_more"):
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            start_cursor=response["next_cursor"],
        )
        pages.extend(response["results"])

    return pages


def get_page_title(page):
    props = page.get("properties", {})
    for prop in props.values():
        if prop["type"] == "title":
            return "".join([t["plain_text"] for t in prop["title"]])
    return "Untitled"


def sync_eval_notes():
    print("🔍 Fetching eval pages from Notion...")
    pages = get_eval_pages()
    print(f"Found {len(pages)} pages.\n")

    documents = []

    for page in pages:
        title = get_page_title(page)
        print(f"📄 Processing: {title}")

        chunks = extract_text_from_blocks(page["id"], title)

        for chunk in chunks:
            content = f"{chunk['heading']}\n{chunk['content']}"
            documents.append({
                "title": title,
                "section": chunk["heading"],
                "content": content,
                "url": page.get("url", ""),
                "last_edited": page.get("last_edited_time", ""),
                "page_id": f"{page['id']}_{chunk['heading']}",
            })

    print(f"\n🧹 Cleaning and validating {len(documents)} raw chunks...")
    documents = parse_documents(documents)

    print(f"\n🔄 Embedding {len(documents)} chunks into 'eval_second_brain'...\n")

    for doc in documents:
        chunk_id = doc["page_id"]

        existing = eval_collection.get(ids=[chunk_id])
        if existing["ids"]:
            print(f"⏭️  Already embedded: {doc['title']} — {doc['section']}")
            continue

        vector = embeddings.embed_query(doc["content"])

        eval_collection.add(
            ids=[chunk_id],
            embeddings=[vector],
            documents=[doc["content"]],
            metadatas=[{
                "title": doc["title"],
                "section": doc["section"],
                "url": doc["url"],
                "last_edited": doc["last_edited"],
            }],
        )
        print(f"✅ Embedded: {doc['title']} — {doc['section']}")

    print(f"\n🧠 Total chunks in eval collection: {eval_collection.count()}")


if __name__ == "__main__":
    sync_eval_notes()