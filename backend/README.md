# Backend — Document Copilot API

FastAPI service handling identity verification, hybrid retrieval (pgvector + FTS), LLM orchestration, and response streaming.

## Setup & Running Locally

### 1. Install Dependencies
Make sure you have [`uv`](https://github.com/astral-sh/uv) installed, then run:

```bash
uv sync
```

### 2. Environment Variables
Copy `.env.example` to `.env` if not already present and configure your credentials:

```bash
cp .env.example .env
```

Ensure `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`, and your API keys (`OPENAI_API_KEY` or `GEMINI_API_KEY`) are set in `.env`.

### 3. Run the Development Server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Verify the server is running by opening:
- Health check: `http://localhost:8000/health`
- OpenAPI docs: `http://localhost:8000/docs`

### 4. Run Tests

```bash
uv run pytest
```
