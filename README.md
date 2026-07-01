# 🏢 Enterprise RAG Chatbot

> **A production-ready Multi-Document RAG (Retrieval-Augmented Generation) Platform** featuring granular Role-Based Access Control (RBAC), multi-provider LLM integration (OpenAI, Google Gemini, Groq), hybrid vector search, PII masking, and source-attributed answers.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 🌟 Key Features

* **⚡ Ultra-Low Latency:** Answers complex questions in **1.5 - 3 seconds** using local semantic indexing coupled with cloud-based LLM generation.
* **🛡️ Security First (RBAC & PII Masking):** Integrated Role-Based Access Control allows documents to be partitioned by department (e.g., HR, Engineering, Sales). Access filters are applied at the database querying stage before the LLM, ensuring strict data boundaries. PII masking prevents sensitive information from leaking.
* **🤖 Multi-Provider LLM Engine:** Seamlessly toggle between:
  * **OpenAI** (gpt-4.1-mini)
  * **Google Gemini** (gemini-1.5-flash / gemini-2.0-flash via new google-genai SDK) - **[FREE Tier]**
  * **Groq** (llama-3.1-8b-instant) - **[FREE Tier / Ultra-Fast]**
* **🔍 Clean Source Attribution:** Every response includes direct document citations showing the filename, page number, section, and text excerpt.
* **💻 Dev-Friendly Footprint:** Optimized to run perfectly on 8GB RAM machines without a GPU (under 4.5GB peak local RAM utilization).

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

## 🚀 Quick Start Guide

### 1. Clone & Initialize Environment

```bash
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
```bash
cp .env.example .env
```

Open `.env` and set your preferred provider. For **free usage**, we recommend using **Groq** or **Gemini**:
```ini
LLM_PROVIDER=groq

# ── OpenAI ──
OPENAI_API_KEY=your-openai-key-here

# ── Google Gemini ──
GEMINI_API_KEY=your-gemini-key-here

# ── Groq ──
GROQ_API_KEY=your-groq-key-here
```

### 3. Initialize & Seed Users
Run the seeding script to create default user accounts with pre-defined security roles:
```bash
python scripts/seed_users.py
```

The script initializes the following credentials:
| Username | Password | Role | Access Scope |
|---|---|---|---|
| `admin` | `admin123` | `admin` | All Documents |
| `hr_user` | `hr123` | `hr` | HR + Public Documents |
| `eng_user` | `eng123` | `engineering` | Engineering + Public Documents |
| `sales_user` | `sales123` | `sales` | Sales + Public Documents |
| `employee` | `emp123` | `employee` | Public Documents Only |

### 4. Run the Application

Start the **FastAPI Backend**:
```bash
# Windows / Bash
uvicorn app.api.main:app --port 8000
```

Start the **Streamlit Frontend** (in a separate terminal):
```bash
streamlit run app/ui/streamlit_app.py --server.port 8501
```

Open **`http://localhost:8501`** in your browser to log in and chat!

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

---

## 🧪 Testing & Evaluation

### Automated Tests
Run the pytest suite to verify authentication, database operations, and document ingestion:
```bash
pytest
```

### RAG Performance Evaluation
Run the RAG evaluation script to generate latency, hallucination check, and relevance metrics:
```bash
python scripts/eval_rag.py
```
Outputs a detailed JSON report scoring retrieval precision and answer validity.
