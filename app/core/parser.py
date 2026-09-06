import re

def clean_text(text):
    """Clean raw text extracted from Notion"""

    #Remove excessive white space
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    #remove zero-width and invisible characters
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)

    # Remove lines that are just symbols or punctuation
    lines = text.split('\n')
    cleaned_lines = [
        line for line in lines
        if len(line.strip()) > 2 and not re.match(r'^[\W_]+$', line.strip())
    ]

    return '\n'.join(cleaned_lines).strip()

def is_valid_chunk(text, min_words=5):
    """Check if a chunk has enough meaningful content"""
    words = text.strip().split()
    return len(words) >= min_words

def parse_documents(documents):
    """Clean and validate all documents before embedding"""
    parsed = []
    skipped = 0

    for doc in documents:
        cleaned_content = clean_text(doc["content"])

        # Skip chunks that are too short or empty
        if not is_valid_chunk(cleaned_content):
            skipped += 1
            continue

        parsed.append({
            **doc,
            "content": cleaned_content
        })

    print(f"✅ Parsed: {len(parsed)} valid chunks")
    print(f"🗑️  Skipped: {skipped} low quality chunks")
    return parsed