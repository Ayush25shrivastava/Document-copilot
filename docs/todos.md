# Document Copilot — Implementation Checklist

This checklist breaks down the technical execution of Document Copilot for **Driftwood Capital**, adhering to the [Architecture Specification](file:///c:/Users/Ayush/OneDrive/Desktop/document-copilot/docs/architecture.md) and [Client Brief](file:///c:/Users/Ayush/OneDrive/Desktop/document-copilot/docs/client-brief.md).

---

## Phase 1: Environment & Foundation Setup
- [x] **Backend Baseline Setup**
  - [x] Initialize Python virtual environment / `uv` project in `backend/`.
  - [x] Configure `backend/app/config.py` using `pydantic-settings` for all environment variables (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`, `ALLOWED_ORIGINS`).
  - [x] Set up basic FastAPI application entrypoint in `backend/app/main.py` with CORS middleware.
- [x] **Frontend Baseline Setup**
  - [x] Initialize Vite + React + TypeScript app in `frontend/`.
  - [x] Configure `frontend/lib/env.ts` (`VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`).
  - [x] Set up Supabase browser client (`frontend/lib/supabase.ts`) and HTTP client with Bearer token header (`frontend/lib/http.ts`).

---

## Phase 2: Database Schema & Migrations
- [x] **SQLAlchemy Models (`backend/app/database/models.py`)**
  - [x] `profiles`: Maps to Supabase `auth.users`.
  - [x] `chat_threads`: Thread metadata (user_id, title, timestamps).
  - [x] `chat_messages`: Message history (thread_id, role, content, raw JSON).
  - [x] `message_citations`: Grounded citation links attached to assistant messages.
  - [x] `source_documents`: Source SEC filings metadata, raw/markdown content, SEC URLs.
  - [x] `document_chunks`: Text chunk, page/section metadata, vector embedding, `tsvector` column.
- [x] **Alembic Setup & Migrations**
  - [x] Configure `backend/alembic.ini` and `backend/alembic/env.py` pointing to Supabase database URL.
  - [x] Generate & refine initial migration (`18f4dc2b1571_initial_schema.py`):
    - [x] Enable `pgvector` extension.
    - [x] Add vector embedding column on `document_chunks`.
    - [x] Add HNSW index on embeddings and GIN index on full-text `tsvector`.
    - [x] Apply migration to database (`uv run alembic upgrade head`).

---

## Phase 3: Data Ingestion & Indexing Pipeline
- [x] **SEC Filing Parser & Chunker (`backend/app/ingestion/`)**
  - [x] Build script to ingest SEC 10-K filings (2021–2025 filings for Apple, Amazon, Alphabet, Microsoft, NVIDIA in `data/downloads`).
  - [x] Parse filings into structured Markdown keeping section/page headers intact.
  - [x] Implement semantic chunking strategy (e.g. 500-1000 tokens with overlap) preserving company, filing type, fiscal year, section, and page metadata.
- [x] **Embeddings & Persistence**
  - [ ] Generate Gemini embeddings (`text-embedding-004`) for each chunk (pending valid Gemini API key).
  - [x] Store raw source documents into `source_documents` and chunks into `document_chunks`.
  - [x] Populate `tsvector` search column for keyword matching.

---

## Phase 4: Retrieval Engine & Grounding
- [ ] **Hybrid Search Engine (`backend/app/retrieval/`)**
  - [ ] Implement `pgvector` cosine similarity query (`queries.py`).
  - [ ] Implement Postgres Full-Text Search query (`queries.py`).
  - [ ] Implement Reciprocal Rank Fusion (RRF) (`fusion.py`) to combine vector and keyword search results.
  - [ ] Add surrounding context retriever (fetching adjacent chunks when requested).
- [ ] **Grounding & Citation Verification (`backend/app/grounding/`)**
  - [ ] Implement validator ensuring every generated claim maps directly to a retrieved chunk.
  - [ ] Enforce strict fallback: return controlled failure / "insufficient evidence" response if citation verification fails or context lacks proof.

---

## Phase 5: Backend LLM Orchestration & Streaming API
- [ ] **Supabase Auth Middleware (`backend/app/auth/`)**
  - [ ] Create FastAPI dependency (`dependencies.py`) to verify incoming JWT access tokens with Supabase Auth and derive `user_id`.
- [ ] **PydanticAI Agent Boundary (`backend/app/assistant/`)**
  - [ ] Define agent dependencies (`deps.py`), grounded output schema (`outputs.py`), and system prompt (`instructions.md`).
  - [ ] Register retrieval tools (`search_filings`, `read_chunk`, `read_surrounding_chunks`).
- [ ] **Streaming API Endpoint (`backend/app/api/chat.py`)**
  - [ ] Implement `POST /chat/stream` supporting AI SDK UI protocol format.
  - [ ] Stream text deltas and structured citation metadata.
  - [ ] Persist final user message, assistant message, and citations into `chat_messages` and `message_citations`.

---

## Phase 6: Frontend Chat Application & UI
- [x] **Authentication Flow**
  - [x] Build email login/sign-up screen with Supabase Auth.
- [ ] **Chat Navigation & Thread Management**
  - [ ] Sidebar displaying past chat threads owned by the user.
  - [ ] Ability to create a new thread or load an existing thread history.
- [ ] **Interactive Chat Experience**
  - [ ] Integrate Vercel AI SDK React primitives (`useChat`).
  - [ ] Render Markdown assistant responses with inline citation markers.
  - [ ] Interactive source passage side-drawer / modal for analysts to click a citation and read the exact filing excerpt & page number.
  - [ ] Display streaming state, error toasts, and empty state prompt suggestions.

---

## Phase 7: Verification & Client Acceptance
- [ ] **Sample Questions Verification**
  - [ ] Test the 10 representative client queries from `client-brief.md` (revenue mix shifts, AWS margins, NVIDIA data center drivers, risk factor changes, etc.).
  - [ ] Verify zero hallucinations, 100% cited claims, and exact page/document references.
- [ ] **End-to-End Build & Test**
  - [ ] Run backend unit tests and API checks.
  - [ ] Verify production build of Vite frontend (`npm run build`).
