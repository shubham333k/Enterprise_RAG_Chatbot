# Enterprise Knowledge Assistant

> **AI-Powered Multi-Document RAG Platform** with Role-Based Access, Hybrid Search & Source Attribution

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What it does

Answers enterprise knowledge questions in **2–3 seconds** with **exact document citations** — no hallucinations, no guessing. Upload HR policies, engineering wikis, sales proposals, contracts, or support tickets and ask questions like:

> *"What is our maternity leave policy?"*  
> ↳ **Answer:** "Eligible permanent employees are entitled to 6 months of maternity leave."  
> ↳ **Source:** HR_Policy_2024.pdf · Page 12 · Section 4.2

---

## Architecture

```
Browser → Streamlit UI → FastAPI Backend → ChromaDB (vector search)
                                        → SQLite (users, sessions)
                                        → OpenAI API (GPT-4.1-mini) [cloud LLM]
```

**Key design decision:** The LLM runs entirely in the cloud (OpenAI). Only the embedding model (`all-MiniLM-L6-v2`, ~90MB) and ChromaDB run locally. This keeps RAM usage ≈ 3.5–4.5 GB on an 8 GB machine.

---

## Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd enterprise-rag-chatbot
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Initialize Database & Seed Users

```bash
python scripts/seed_users.py
```

Default users created:
| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | admin |
| `hr_user` | `hr123` | hr |
| `eng_user` | `eng123` | engineering |
| `sales_user` | `sales123` | sales |
| `employee` | `emp123` | employee |

### 4. Run the Application

**Terminal 1 — Backend:**
```bash
uvicorn app.api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
streamlit run app/ui/streamlit_app.py
```

Open **http://localhost:8501** in your browser.

### 5. Upload Sample Documents

The `data/sample_docs/` folder contains demo documents. Upload them from the sidebar in the Streamlit UI.

---

## API Documentation

With the backend running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Get JWT token |
| POST | `/auth/register` | Register new user |
| POST | `/documents/upload` | Upload a document |
| POST | `/documents/index` | Chunk, embed, and index a document |
| GET | `/documents` | List all documents |
| POST | `/chat/query` | Ask a question |
| GET | `/chat/history/{session_id}` | Get chat history |
| GET | `/analytics/overview` | Usage statistics (admin only) |
| GET | `/health` | Health check |

---

## Role-Based Access Control

| Role | Accessible Documents |
|---|---|
| `admin` | All documents |
| `hr` | HR + Public |
| `engineering` | Engineering + Public |
| `sales` | Sales + Public |
| `employee` | Public only |

Access filters are applied **at the vector-search level** — restricted chunks never reach the LLM context.

---

## Batch Ingestion

To index an entire folder of documents:

```bash
python scripts/batch_ingest.py --dir ./data/raw --department hr --access_level hr
```

---

## RAG Evaluation

```bash
python scripts/eval_rag.py
```

Measures: retrieval precision@k, citation correctness, no-answer rate, latency.

---

## Docker

```bash
# Build and run both API + UI
docker-compose -f deployment/docker-compose.yml up --build
```

- API: http://localhost:8000
- UI: http://localhost:8501

---

## Deployment (Render.com)

1. Push to GitHub
2. Connect repo to [Render.com](https://render.com)
3. Set environment variables in Render dashboard (copy from `.env`)
4. Render auto-deploys on push

See `render.yaml` for configuration.

---

## Project Structure

```
enterprise-rag-chatbot/
├── app/
│   ├── api/          # FastAPI routes, schemas, core config
│   ├── rag/          # Loaders, chunker, embeddings, vector store, LLM generation
│   ├── db/           # SQLAlchemy models + session
│   ├── ui/           # Streamlit frontend
│   └── tests/        # pytest test suite
├── data/
│   ├── raw/          # Uploaded documents
│   ├── chroma_db/    # ChromaDB persistent store
│   └── sample_docs/  # Demo documents
├── scripts/          # CLI tools: seed, batch ingest, eval
├── deployment/       # Docker, Nginx configs
└── .github/          # CI workflow
```

---

## Resume Bullets

- Built an enterprise-grade Retrieval-Augmented Generation (RAG) platform with multi-format document ingestion, hybrid semantic retrieval, role-based access control, and citation-backed answers using FastAPI, ChromaDB, LangChain, and OpenAI GPT-4.1-mini.
- Designed a laptop-optimized architecture (8 GB RAM, no GPU) using local embeddings + ChromaDB + SQLite for dev, with a separate production-deployment blueprint using Docker, Nginx, and Render.com.
- Implemented access-filtered retrieval pipelines, prompt-injection guardrails, PII masking, and an evaluation framework for retrieval precision and answer groundedness.
