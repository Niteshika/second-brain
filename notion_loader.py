import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))

SYNC_FILE = "./data/last_sync.json"

def load_sync_record():
    """ Load record of previously synced pages"""
    if os.path.exists(SYNC_FILE):
        with open(SYNC_FILE, "r") as f:
            return json.load(f)
    return {}

def save_sync_record(record):
    """Save sync record to disc"""
    os.makedirs("./data", exist_ok=True)
    with open(SYNC_FILE, "w") as f:
        json.dump(record, f, indent=2)

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
    """Extract text chunked by headings from a Notion page"""
    blocks = notion.blocks.children.list(block_id=page_id)
    
    chunks = []
    current_heading = "Introduction"
    current_lines = []

    for block in blocks["results"]:
        block_type = block["type"]

        # When we hit a heading, save the previous section and start a new one
        if block_type in ["heading_1", "heading_2", "heading_3"]:
            if current_lines:
                chunks.append({
                    "heading": current_heading,
                    "content": "\n".join(current_lines)
                })
            rich_text = block[block_type].get("rich_text", [])
            current_heading = "".join([t["plain_text"] for t in rich_text])
            current_lines = []

        #Standard text blocks  
        elif block_type in ["paragraph", "bulleted_list_item",
                             "numbered_list_item", "quote", "callout"]:
            rich_text = block[block_type].get("rich_text", [])
            line = "".join([t["plain_text"] for t in rich_text])
            if line.strip():
                current_lines.append(line)

        #Code Blocks
        elif block_type == "code":
            rich_text = block["code"].get("rich_text", [])
            language = block["code"].get("language", "")
            code = "".join([t["plain_text"] for t in rich_text])
            if code.strip():
                current_lines.append(f"[{language} code]: {code}")

        # Toggle blocks
        elif block_type == "toggle":
            rich_text = block["toggle"].get("rich_text", [])
            line = "".join([t["plain_text"] for t in rich_text])
            if line.strip():
                current_lines.append(f"[Toggle]: {line}")

        # To-do blocks
        elif block_type == "to_do":
            rich_text = block["to_do"].get("rich_text", [])
            checked = block["to_do"].get("checked", False)
            line = "".join([t["plain_text"] for t in rich_text])
            status = "✅" if checked else "⬜"
            if line.strip():
                current_lines.append(f"{status} {line}")

        # Divider — treat as section break
        elif block_type == "divider":
            if current_lines:
                chunks.append({
                    "heading": current_heading,
                    "content": "\n".join(current_lines)
                })
                current_lines = []

        # Tables
        elif block_type == "table":
            # Handle table rows
            try:
                table_rows = notion.blocks.children.list(block_id=block["id"])
                for row in table_rows["results"]:
                    if row["type"] == "table_row":
                        cells = row["table_row"]["cells"]
                        row_text = " | ".join(
                            "".join([t["plain_text"] for t in cell])
                            for cell in cells
                        )
                        if row_text.strip():
                            current_lines.append(row_text)
            except:
                pass

    # Don't forget the last section
    if current_lines:
        chunks.append({
            "heading": current_heading,
            "content": "\n".join(current_lines)
        })

    return chunks

def load_notion_documents(force_resync=False):
    """Load only new or edited Notion pages (incremental sync)"""
    pages = get_all_pages()
    sync_record = load_sync_record()
    documents = []
    skipped = 0

    for page in pages:
        try:
            page_id = page["id"]
            last_edited = page.get("last_edited_time", "")

            # Skip if not changed since last sync
            if not force_resync and sync_record.get(page_id) == last_edited:
                skipped += 1
                continue

            # Get page title
            props = page.get("properties", {})
            title = ""
            for prop in props.values():
                if prop["type"] == "title":
                    title_parts = prop["title"]
                    title = "".join([t["plain_text"] for t in title_parts])
                    break

            # Get heading-based chunks
            chunks = extract_text_from_blocks(page["id"])

            if not chunks:
                continue

            page_url = page.get("url", "")

            # Each heading section becomes its own document
            for chunk in chunks:
                content = f"{chunk['heading']}\n{chunk['content']}"
                documents.append({
                    "title": title or "Untitled",
                    "section": chunk["heading"],
                    "content": content,
                    "url": page_url,
                    "last_edited": last_edited,
                    "page_id": f"{page['id']}_{chunk['heading']}"
                })

            # Update sync record
            sync_record[page_id] = last_edited
            print(f"✅ Loaded: {title or 'Untitled'} ({len(chunks)} sections)")

        except Exception as e:
            print(f"⚠️ Skipped a page: {e}")
            continue
    
    save_sync_record(sync_record)
    print(f"\n📄 New/updated sections: {len(documents)}")
    print(f"⏭️  Skipped unchanged pages: {skipped}")
    return documents

if __name__ == "__main__":
    docs = load_notion_documents()
    for doc in docs :
        print(f"\n--- {doc['title']} / {doc['section']} ---")
        print(doc['content'][:200])