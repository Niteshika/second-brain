import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))

def get_all_pages():
    """Fetch all pages this integration has access to"""
    results=[]

    response = notion.search(filter={"property": "object", "value": "page"})
    results.extend(response["results"])

    while response.get("has_more"):
        response = notion.search(
            filter={"property": "object", "value": "page"},
            start_cursor = response["next_cursor"]
        )
        results.extend(response["results"])

    return results

def extract_text_from_blocks(page_id):
    """Etract plain text from a Notion page's blocks"""
    blocks = notion.blocks.children.list(block_id=page_id)
    text_content=[]

    for block in blocks["results"]:
        block_type = block["type"]

        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "quote", "callout"]:
            rich_text = block[block_type].get("rich_text", [])
            line = "".join([t["plain_text"] for t in rich_text])
            if line.strip():
                text_content.append(line)

    return "\n".join(text_content)

def load_notion_documents():
    """Loads all notion pages as documents"""
    pages = get_all_pages()
    documents=[]

    for page in pages:
        try:
            props = page.get("properties", {})
            title = ""
            for prop in props.values():
                if prop["type"] == "title":
                    title_parts = prop["title"]
                    title = "".join([t["plain_text"] for t in title_parts])
                    break
            
            content = extract_text_from_blocks(page["id"])

            if not content.strip():
                continue
            page_url = page.get("url", "")
            last_edited = page.get("last_edited_time", "")

            documents.append({
                "title": title or "Untitled",
                "content": content,
                "url": page_url,
                "last_edited": last_edited,
                "page_id": page["id"]
            })

            print(f"✅Loaded: {title or 'Untitled'} ;)")
        
        except Exception as e:
            print(f"⚠️ Skipped a page due to error: {e}")
            continue
    
    print(f"\n📄 Total pages loaded: {len(documents)}")
    return documents

if __name__ == "__main__":
    docs = load_notion_documents()
    for doc in docs :
        print(f"\n--- {doc['title']} ---")
        print(doc['content'][:200])