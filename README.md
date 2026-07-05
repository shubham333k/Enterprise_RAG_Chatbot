# 🏢 Enterprise RAG Chatbot

> **A production-ready Multi-Document RAG (Retrieval-Augmented Generation) Platform** featuring granular Role-Based Access Control (RBAC), multi-provider LLM integration (OpenAI, Google Gemini, Groq), hybrid vector search, PII masking, and source-attributed answers.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://github.com/shubham333k/Enterprise_RAG_Chatbot/blob/main/LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture Overview](#️-architecture-overview)
- [Tech Stack](#️-tech-stack)
- [Quick Start Guide](#-quick-start-guide)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Security & Access Control](#-security--access-control)
- [Deployment (Render.com)](#-deployment-rendercom)
- [Testing & Evaluation](#-testing--evaluation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Enterprise RAG Chatbot** (internally configured as the *Enterprise Knowledge Assistant*) is a self-hostable Retrieval-Augmented Generation platform built for organizations that need employees to query internal documents — policies, engineering docs, HR handbooks, sales collateral — without leaking data across departments or paying for a dedicated on-prem GPU.

It solves three problems that generic "chat with your PDF" demos usually ignore:

- ✅ **Department-level data isolation** — an HR employee's query never surfaces Engineering-only documents, because access filters are applied at the vector database query stage, before the LLM ever sees the retrieved chunks.
- ✅ **No vendor lock-in on the LLM** — the generation layer is provider-agnostic (OpenAI / Gemini / Groq), so you can run entirely on free-tier APIs (Gemini, Groq) or swap to OpenAI for production quality without touching the retrieval pipeline.
- ✅ **Runs on modest hardware** — embeddings are generated locally with a lightweight sentence-transformer model, so the only network calls are to the LLM API; no GPU, no 16GB+ RAM requirement.

---

## 🌟 Key Features

- **⚡ Ultra-Low Latency:** Answers complex questions in **1.5 - 3 seconds** using local semantic indexing coupled with cloud-based LLM generation.
- **🛡️ Security First (RBAC & PII Masking):** Integrated Role-Based Access Control allows documents to be partitioned by department (e.g., HR, Engineering, Sales). Access filters are applied at the database querying stage before the LLM, ensuring strict data boundaries. PII masking prevents sensitive information from leaking.
- **🤖 Multi-Provider LLM Engine:** Seamlessly toggle between:
  - **OpenAI** (gpt-4.1-mini)
  - **Google Gemini** (gemini-1.5-flash / gemini-2.0-flash via new google-genai SDK) - **[FREE Tier]**
  - **Groq** (llama-3.1-8b-instant) - **[FREE Tier / Ultra-Fast]**
- **🔍 Clean Source Attribution:** Every response includes direct document citations showing the filename, page number, section, and text excerpt.
- **💻 Dev-Friendly Footprint:** Optimized to run perfectly on 8GB RAM machines without a GPU (under 4.5GB peak local RAM utilization).

---

## 🛠️ Architecture Overview

```
             ┌────────────────────────┐
             │  Streamlit Frontend   │ (Port 8501)
             └───────────┬────────────┘
                         │ REST API
                         ▼
             ┌────────────────────────┐
             │    FastAPI Backend     │ (Port 8000)
             └───────────┬────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌───────────────┐
│   SQLite     │ │   ChromaDB   │ │  Cloud LLM    │
│  DB Store    │ │ Vector Store │ │   API Layer   │
│ (Auth & RBAC)│ │(all-MiniLM-L6)│ (OpenAI/Gemini/ │
└──────────────┘ └──────────────┘ │     Groq)     │
                                  └───────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Streamlit 1.36 | Chat UI, login screen |
| **Backend** | FastAPI 0.111, Python 3.11 | REST API server, JWT-secured routes |
| **Orchestration** | LangChain 0.2.x | Document loaders, text splitting, prompt building |
| **Embeddings** | `sentence-transformers` (all-MiniLM-L6-v2) | Local, free, no API key required |
| **Vector Database** | ChromaDB | Storing & retrieving document embeddings, with metadata-based RBAC filters |
| **LLM Providers** | OpenAI (`gpt-4.1-mini`), Google Gemini (`gemini-2.0-flash` via `google-genai`), Groq (`llama-3.1-8b-instant`) | Swappable answer-generation backend |
| **Relational DB** | SQLite (dev) / PostgreSQL-ready (`DATABASE_URL`) | User accounts, roles |
| **Authentication** | `python-jose` (JWT) + `bcrypt` | Login sessions, password hashing |
| **Document Parsing** | PyMuPDF, `python-docx`, `pandas`, `openpyxl` | PDF, DOCX, CSV/XLSX ingestion |
| **Testing** | Pytest, `pytest-asyncio` | 30+ automated integration tests |
| **Deployment** | Render.com Blueprint (`render.yaml`), Windows batch scripts (`setup.bat`, `start.bat`) | One-click cloud deploy + local Windows setup |
| **CI** | GitHub Actions (`.github/workflows`) | Automated checks on push/PR |

> Full, pinned versions are listed in [`requirements.txt`](https://github.com/shubham333k/Enterprise_RAG_Chatbot/blob/main/requirements.txt).

---

## 🚀 Quick Start Guide

### 1. Clone & Initialize Environment

```
git clone https://github.com/shubham333k/Enterprise_RAG_Chatbot.git
cd Enterprise_RAG_Chatbot
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure your API keys:

```
cp .env.example .env
```

Open `.env` and set your preferred provider. For **free usage**, we recommend using **Groq** or **Gemini**:

```
LLM_PROVIDER=groq

# ── OpenAI ──
OPENAI_API_KEY=your-openai-key-here

# ── Google Gemini ──
GEMINI_API_KEY=your-gemini-key-here

# ── Groq ──
GROQ_API_KEY=your-groq-key-here
```

Other useful variables you can tune in `.env` (see `.env.example` for the full list):

| Variable | Default | Purpose |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model, no API key needed |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | Where the vector store is persisted on disk |
| `DATABASE_URL` | `sqlite:///./data/enterprise_rag.db` | Swap for a `postgresql://...` URL in production |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `700` / `125` | Document chunking strategy for retrieval |
| `TOP_K_DEFAULT` | `5` | Number of chunks retrieved per query |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT session length |
| `RATE_LIMIT_PER_MINUTE` | `30` | Basic API rate limiting |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max file size accepted for ingestion |

### 3. Initialize & Seed Users

Run the seeding script to create default user accounts with pre-defined security roles:

```
python scripts/seed_users.py
```

The script initializes the following credentials:

| Username     | Password   | Role          | Access Scope                   |
| ------------ | ---------- | ------------- | ------------------------------- |
| `admin`      | `admin123` | `admin`       | All Documents                   |
| `hr_user`    | `hr123`    | `hr`          | HR + Public Documents           |
| `eng_user`   | `eng123`   | `engineering` | Engineering + Public Documents  |
| `sales_user` | `sales123` | `sales`       | Sales + Public Documents        |
| `employee`   | `emp123`   | `employee`    | Public Documents Only           |

> ⚠️ These are demo credentials meant for local evaluation only. Rotate every password (and `SECRET_KEY`) before exposing this app on a public network.

### 4. Run the Application

Start the **FastAPI Backend**:

```
# Windows / Bash
uvicorn app.api.main:app --port 8000
```

Start the **Streamlit Frontend** (in a separate terminal):

```
streamlit run app/ui/streamlit_app.py --server.port 8501
```

Open **`http://localhost:8501`** in your browser to log in and chat!

> Windows users can skip steps 1–4 individually and just run `setup.bat` once, then `start.bat` on every subsequent run.

---

## 📂 Project Structure

```
Enterprise_RAG_Chatbot/
├── app/
│   ├── api/          # FastAPI server routes, JWT security, database sessions
│   ├── db/           # SQL database schema and models (SQLite/PostgreSQL)
│   ├── rag/          # Text loaders, document chunker, local embedder, prompt builder
│   │   ├── embeddings/     # Local all-MiniLM-L6-v2 vector generation
│   │   ├── generation/     # Multi-provider chat client (OpenAI, Gemini, Groq)
│   │   ├── guardrails/     # Access filters, hallucination checks, PII masks
│   │   └── vectorstores/   # ChromaDB database setup
│   ├── ui/           # Streamlit Web Interface
│   └── tests/        # PyTest integration suite (30+ automated tests)
├── data/
│   ├── raw/          # Ingested documents (PDFs, docx, txt, xlsx)
│   └── sample_docs/  # Default test documents
├── scripts/          # Database seeding, RAG CLI evaluation, batch ingestion
├── deployment/       # Production Dockerfiles, docker-compose & Nginx configs
└── render.yaml       # Blueprint file for Render.com automated deployment
```

---

## 📡 API Reference

The FastAPI backend exposes a REST API. Once the server is running, the full interactive contract is available at:

| Resource | URL |
|---|---|
| 🌐 Backend base URL | `http://localhost:8000` |
| 📖 Interactive Swagger docs | `http://localhost:8000/docs` |
| ❤️ Health check | `http://localhost:8000/health` |

> **Honest note:** exact route names for login, document upload, and query endpoints live inside `app/api/` and weren't fully readable from this pass — rather than guess and give you wrong paths, open `/docs` after starting the server for the authoritative, always-current list of endpoints, request bodies, and response schemas. If you'd like, paste the contents of `app/api/main.py` (and the files under `app/api/`) and I'll write out the exact endpoint table accurately.

---

## 🔒 Security & Access Control

- **🔑 JWT Authentication** — stateless access tokens (`python-jose`, `HS256` by default), configurable expiry via `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **🔐 Password Hashing** — user passwords are hashed with `bcrypt`, never stored in plain text.
- **👮 Role-Based Access Control (RBAC)** — five seeded roles (`admin`, `hr`, `engineering`, `sales`, `employee`); document retrieval is filtered by role **before** chunks reach the LLM, not after.
- **🧹 PII Masking** — sensitive information (e.g. emails, phone numbers) is masked as part of the `guardrails` pipeline prior to indexing/response generation.
- **🛑 Hallucination Guardrails** — the `app/rag/guardrails/` module includes checks intended to catch answers that aren't actually grounded in retrieved context.
- **⏱️ Rate Limiting** — basic per-minute request throttling via `RATE_LIMIT_PER_MINUTE`.
- **🔒 Secrets Management** — all credentials/API keys are loaded from environment variables (`.env`), never hardcoded; `SECRET_KEY` should be replaced with a long random value in production (Render auto-generates one for you — see below).

---

## ⚡ Deployment (Render.com)

This repository includes a `render.yaml` Blueprint file for automatic configuration on **Render.com**:

1. Fork/Push this repository to your GitHub account.
2. Log into the **Render Dashboard**.
3. Click **New** → **Blueprint**.
4. Connect this GitHub repository.
5. In the environmental config, fill in:
  - `LLM_PROVIDER` (e.g. `groq` or `gemini`)
  - `GROQ_API_KEY` (or `GEMINI_API_KEY`/`OPENAI_API_KEY`)
6. Deploy! Render will deploy the API and UI automatically with a persistent storage mount for database files.

The blueprint provisions **two web services** and **one persistent disk**:

| Service | Plan | Notes |
|---|---|---|
| `enterprise-rag-api` | Starter ($7/mo) | FastAPI backend; health-checked at `/health`; mounts a 5 GB disk at `/data` so ChromaDB + uploaded files survive redeploys |
| `enterprise-rag-ui` | Starter ($7/mo) | Streamlit frontend; auto-wires `API_URL` to the backend service host |

`SECRET_KEY` is set with `generateValue: true`, so Render generates a secure random value automatically — you don't need to create one yourself for this deployment path.

---

## 🧪 Testing & Evaluation

### Automated Tests

Run the pytest suite to verify authentication, database operations, and document ingestion:

```
pytest
```

### RAG Performance Evaluation

Run the RAG evaluation script to generate latency, hallucination check, and relevance metrics:

```
python scripts/eval_rag.py
```

Outputs a detailed JSON report scoring retrieval precision and answer validity.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please make sure your changes pass the existing test suite before opening a PR:

```
pytest
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [`LICENSE`](https://github.com/shubham333k/Enterprise_RAG_Chatbot/blob/main/LICENSE) file for details.

> **Disclaimer:** This is a demonstration/portfolio project. Review and harden the default credentials, secrets, and rate limits before using it with real internal company data.

---

Built with ❤️ by [Shubham](https://github.com/shubham333k)

⭐ If you found this project useful, please give it a star!
