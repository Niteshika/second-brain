# Second Brain

A full-stack, retrieval-augmented personal knowledge assistant. Syncs notes from Notion, embeds them into a vector store, and exposes a chat interface (with streaming, persistent history, and authentication) plus a "knowledge gap" dashboard that surfaces topic clusters, blind spots, contradictions, and stale notes across your notes.

Originally prototyped in Streamlit, then rebuilt as a proper full-stack application (FastAPI + React + Postgres) to practice production-grade patterns: authentication, background jobs, streaming responses, and a custom RAG evaluation harness.

## Features

- **Chat with your notes** — RAG pipeline over Notion content, with streaming responses and persistent per-user conversation history
- **Authentication** — JWT-based signup/login, protected routes
- **Knowledge Gap Dashboard** — background-job-powered analysis that surfaces:
  - Topic clusters (KMeans over note embeddings)
  - Blind spots (LLM-suggested topics missing from your notes)
  - Contradictions between notes (embedding similarity + LLM verification)
  - Stale notes (not updated in 90+ days)
- **RAG evaluation harness** — custom-built evaluation dataset and metrics (Retrieval Recall@k, MRR; Faithfulness/Relevance/Context Precision in progress) run against an isolated synthetic dataset, ingested through the real production pipeline

## Tech stack

| Layer | Tools |
|---|---|
| Backend | FastAPI, SQLAlchemy |
| Frontend | React (Vite), React Router |
| Database | Postgres (Neon) — users, chat history |
| Vector store | ChromaDB — note embeddings |
| LLMs | Gemini (chat + embeddings), Groq (knowledge gap reasoning) |
| Auth | JWT, bcrypt |
| Notes source | Notion API |

## Project structure

```
SECOND-BRAIN/
  app/
    main.py                  # FastAPI entrypoint, router registration
    core/
      rag_chain.py            # RAG pipeline (retrieval + generation, streaming variant)
      embedder.py              # Embeds Notion chunks into ChromaDB
      notion_loader.py         # Notion sync — pages, blocks, incremental sync
      parser.py                 # Chunk cleaning/validation
      knowledge_gap.py          # Clustering, blind spots, contradictions, staleness
      security.py                # Password hashing, JWT creation/verification
      database.py                 # SQLAlchemy engine/session setup
      models_db.py                 # User, ChatMessage tables
      jobs.py                       # In-memory background job tracking
    models/                          # Pydantic request/response schemas
    routers/                          # chat, chat_stream, auth, knowledge_gap, health
  second-brain-frontend/               # React app (auth, chat, dashboard)
  streamlit_app.py                      # Original prototype UI (kept for reference)
  eval_sync.py, eval_questions.py,       # RAG evaluation harness
    eval_metrics.py
  
```

## Setup

### Backend

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
NOTION_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
JWT_SECRET_KEY=any_long_random_string
```

Sync your Notion notes into the vector store (populates the local `data/chroma_db` folder, which is gitignored):

```bash
python -c "from app.core.notion_loader import load_notion_documents; from app.core.embedder import embed_documents; embed_documents(load_notion_documents())"
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Interactive API docs at `http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd second-brain-frontend
npm install
npm run dev
```

## Evaluation

Retrieval quality is measured against a synthetic evaluation dataset (fictional topics with unambiguous ground truth), ingested through the real Notion → parser → embedder pipeline into an isolated ChromaDB collection, kept separate from production data.

| Dataset | Avg Recall@4 | MRR |
|---|---|---|
| Easy set (8 distinct topics) | 1.000 | 0.881 |
| Hard set (12 topics, incl. similar-domain pairs) | 0.932 | 0.792 |

