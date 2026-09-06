# Second Brain Frontend — Setup

## 1. Where to put this folder

Unzip `second-brain-frontend.zip`. Put the `second-brain-frontend/` folder
as a SIBLING of your `app/` backend folder, inside `SECOND-BRAIN`:

```
SECOND-BRAIN/
  app/                      ← your FastAPI backend
  second-brain-frontend/    ← this new folder
  ...
```

## 2. Install and run

You need Node.js installed. Check with `node --version` — if that fails,
install Node from nodejs.org first.

```bash
cd SECOND-BRAIN/second-brain-frontend
npm install
npm run dev
```

It'll print a local URL, usually `http://localhost:5173`. Open that in
your browser.

## 3. Run the backend too

The frontend expects your FastAPI backend running at
`http://127.0.0.1:8000` (see `src/api.js` — change `API_BASE` there if
your backend runs elsewhere). In a separate terminal:

```bash
cd SECOND-BRAIN
uvicorn app.main:app --reload
```

Both need to be running at the same time — backend on :8000, frontend
on :5173.

## 4. What you get

- `/signup` — create an account
- `/login` — log in, stores your JWT in localStorage
- `/chat` — chat with your notes, protected (redirects to /login if not
  authenticated)
- `/knowledge-gap` — dashboard UI, currently showing **placeholder data**
  since there's no backend endpoint for this yet (see TODO below)

## 5. What's NOT done yet

**Knowledge Gap backend endpoint.** Your `knowledge_gap.py` logic exists
in `app/core/` on the backend but was never wired into a FastAPI route.
The dashboard page (`src/pages/KnowledgeGap.jsx`) is hardcoded with
placeholder data so the UI has something to show. To wire it up for
real:

1. Build a `GET /knowledge-gap` (or similar) endpoint in
   `app/routers/` on the backend, calling into your existing
   `knowledge_gap.py` functions.
2. Uncomment the `knowledgeGap` line in `src/api.js`.
3. In `src/pages/KnowledgeGap.jsx`, replace the `placeholderData` object
   and its usages with a `useEffect` that calls
   `api.knowledgeGap()` and stores the result in state — the comment
   block at the top of that file has the exact pattern to follow.

**Streaming responses.** Chat currently waits for the full answer before
showing it (a "thinking…" bubble in the meantime), not a token-by-token
stream. That's step 5 in the original roadmap if you want to add it
later — would need Server-Sent Events or WebSockets on the backend, and
an updated fetch in `src/api.js` to consume the stream.

## 6. File map (for reference — you don't need to touch most of these)

```
src/
  api.js                   — all backend calls live here
  App.jsx                  — routes
  context/AuthContext.jsx  — login state, token storage
  components/
    Layout.jsx              — topbar + nav, wraps every logged-in page
    ProtectedRoute.jsx       — redirects to /login if not authenticated
  pages/
    Login.jsx
    Signup.jsx
    Chat.jsx
    KnowledgeGap.jsx         — placeholder data, see TODO above
  index.css                 — theme variables (colors, fonts)
  App.css                   — all component styles
```
