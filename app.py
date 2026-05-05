import streamlit as st
from notion_loader import load_notion_documents
from embedder import embed_documents
from rag_chain import ask

# ---- Page Config ----
st.set_page_config(
    page_title="Second Brain",
    page_icon="🧠",
    layout="centered"
)

# ---- Header ----
st.title("🧠 Second Brain")
st.caption("Chat with your Notion notes using AI")

# ---- Sidebar ----
with st.sidebar:
    st.header("⚙️ Settings")

    if st.button("🔄 Sync New/Updated Notion Notes", use_container_width=True):
        with st.spinner("Checking for updated notes..."):
            docs = load_notion_documents(force_resync=False)
        if docs:
            with st.spinner("Embedding changes..."):
                embed_documents(docs)
            st.success(f"✅ Synced {len(docs)} new/updated sections!")
        else:
            st.info("✅ Everything is already up to date!")

    if st.button("🔄 Force Full Resync", use_container_width=True):
        with st.spinner("Resyncing all notes from Notion..."):
            docs = load_notion_documents()
        with st.spinner("Embedding into vector store..."):
            embed_documents(docs)
        st.success(f"✅ Resynced {len(docs)} sections!")

    st.divider()
    st.markdown("### How to use")
    st.markdown("""
    1. Click **Sync Notion Notes** to load your latest notes
    2. Ask anything in the chat
    3. Sources show which Notion page was used
    """)
    st.divider()
    st.markdown("### Example questions")
    st.markdown("""
    - *What are my notes about?*
    - *Summarize my project ideas*
    - *What did I write about [topic]?*
    """)

# ---- Chat Interface ----

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📌 Sources"):
                for source in message["sources"]:
                    title = source['title'] if source['title'] else "Untitled"
                    section = source.get('section', '')
                    url = source['url']
                    label = f"{title} — *{section}*" if section else title
                    if url:
                        st.markdown(f"- [{label}]({url})")
                    else:
                        st.markdown(f"- {label}")

# Chat input
if question := st.chat_input("Ask anything about your notes..."):

    # Show user message
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, sources = ask(question)
        st.markdown(answer)
        if sources:
            with st.expander("📌 Sources"):
                for source in sources:
                    title = source['title'] if source['title'] else "Untitled"
                    section = source.get('section', '')
                    url = source['url']
                    label = f"{title} — *{section}*" if section else title
                    if url:
                        st.markdown(f"- [{label}]({url})")
                    else:
                        st.markdown(f"- {label}")

    # Save to session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })