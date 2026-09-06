import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Load existing ChromaDB
vectorstore = Chroma(
    persist_directory="./data/chroma_db",
    embedding_function=embeddings,
    collection_name="second_brain"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that answers questions 
based on the user's personal Notion notes.
Use the context below to answer. If the answer isn't in the notes, 
say 'I couldn't find anything about that in your notes.'

Context from notes:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

def ask_streaming(question, chat_history = None):
    if chat_history is None:
        chat_history = []

    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    chain = prompt | llm
    
    response = chain.stream({
        "context": context,
        "chat_history": chat_history,
        "question": question
    })

    for chunk in response:
        if isinstance(chunk.content, str):
            text = chunk.content
        elif chunk.content and isinstance(chunk.content, list):
            text = chunk.content[0].get("text", "")
        else:
            text = ""
    
        if text:
            yield text

def ask(question, chat_history = None):
    if chat_history is None:
        chat_history = []
    
    # Retrieve relevant chunks
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Build chain
    chain = prompt | llm

    # Invoke with history
    response = chain.invoke({
        "context": context,
        "chat_history": chat_history,
        "question": question
    })

    # Update history
    answer = response.content if isinstance(response.content, str) else response.content[0]["text"]
    updated_history = chat_history + [
        HumanMessage(content=question),
        AIMessage(content=answer),
    ]

    # Deduplicate sources
    seen = set()
    unique_sources = []
    for doc in docs:
        title = doc.metadata.get("title", "Untitled")
        url = doc.metadata.get("url", "")
        if title not in seen:
            seen.add(title)
            unique_sources.append({
                "title": title,
                "section": doc.metadata.get("section", ""),
                "url": url
            })

    return answer, unique_sources, updated_history


if __name__ == "__main__":
    print("🧠 Second Brain is ready! Type 'exit' to quit.\n")

    while True:
        question = input("You: ")
        if question.lower() == "exit":
            break

        answer, sources = ask(question)
        print(f"\nAI: {answer}")
        print("\n📌 Sources:")
        for s in sources:
            print(f"  - {s['title']} → {s['url']}")
        print()