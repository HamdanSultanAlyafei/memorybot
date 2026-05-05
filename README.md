<div align="center">

# 🧠 MemoryBot

### A conversational AI that actually remembers you — across every session.

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://memorybot-zbwpuplgtvemmsgvfafy9l.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://python.langchain.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-1D6AFF?style=for-the-badge)](https://www.pinecone.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

> **"Most chatbots forget you the moment you close the tab. MemoryBot doesn't."**

<br/>

</div>

---

## ✨ What Makes This Different

Every time you open a new chat session, traditional bots start from zero. MemoryBot maintains a **persistent, searchable memory** of who you are, what you care about, and what you've discussed — then uses that context to give you smarter, more personalised responses.

This is a full demonstration of **long-term memory architecture** — one of the core unsolved challenges in production AI agents.

---

## 🎯 Live Demo

**👉 [Try it now — no sign-up required](https://memorybot-zbwpuplgtvemmsgvfafy9l.streamlit.app/)**

Just enter your name and start chatting. Come back later — it will remember you.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MEMORYBOT                            │
│                                                             │
│  ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │   Streamlit  │───▶│         Memory Manager          │   │
│  │      UI      │    │                                 │   │
│  └──────────────┘    │  ┌───────────┐  ┌───────────┐  │   │
│                       │  │Short-Term │  │ Long-Term │  │   │
│  ┌──────────────┐    │  │  Buffer   │  │  Pinecone │  │   │
│  │  ChatGroq    │◀───│  │(deque k=6)│  │  Vectors  │  │   │
│  │ Llama 3.3 70B│    │  └───────────┘  └───────────┘  │   │
│  └──────────────┘    └─────────────────────────────────┘   │
│                                      │                      │
│  ┌──────────────────────────────────▼──────────────────┐   │
│  │               SQLite (WAL mode)                     │   │
│  │          Raw message history · user store           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### How Memory Works

| Layer | Technology | Purpose |
|---|---|---|
| **Short-Term Buffer** | Python `deque` (k=6) | Last 6 exchanges injected into every prompt |
| **Long-Term Memory** | Pinecone (384-dim, cosine) | Semantic search across all past conversations |
| **Raw Persistence** | SQLite (WAL mode) | Durable message store survives restarts |
| **Summarisation** | Groq LLaMA 3.3 70B | Every 10 messages → ≤80-word summary → embedded → Pinecone |
| **Embeddings** | `all-MiniLM-L6-v2` | Local, free, no API cost |

---

## 🚀 Tech Stack

| Component | Technology | Cost |
|---|---|---|
| LLM | Groq — LLaMA 3.3 70B Versatile | **Free** |
| Vector DB | Pinecone Serverless | **Free tier** |
| Embeddings | sentence-transformers (local) | **Free** |
| Orchestration | LangChain 0.3+ | Open source |
| Database | SQLite | Open source |
| UI | Streamlit | **Free** |
| **Total** | | **$0** |

---

## ⚙️ Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/hamdansultanalyafei/memorybot.git
cd memorybot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API keys

Copy the example env file and fill in your own keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=memorybot
BUFFER_WINDOW_K=6
PINECONE_TOP_K=3
SUMMARIZE_EVERY=10
SQLITE_DB_PATH=memorybot.db
```

**Getting free API keys:**
- **Groq** (LLM): [console.groq.com](https://console.groq.com) — free tier, no credit card needed
- **Pinecone** (Vector DB): [pinecone.io](https://www.pinecone.io) — free serverless tier

### 4. Launch

```bash
python -m streamlit run app.py
```

Or on Windows, just double-click `run.bat`.

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your fork
3. In **Settings → Secrets**, add your keys in TOML format:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
PINECONE_API_KEY = "your_pinecone_api_key_here"
PINECONE_INDEX_NAME = "memorybot"
BUFFER_WINDOW_K = "6"
PINECONE_TOP_K = "3"
SUMMARIZE_EVERY = "10"
SQLITE_DB_PATH = "memorybot.db"
```

4. Click **Deploy** — done.

---

## 📁 Project Structure

```
memorybot/
├── app.py                  # Streamlit UI
├── requirements.txt        # Dependencies (no version pins for cloud compat)
├── run.bat                 # One-click Windows launcher
├── .env.example            # Safe key template
├── .gitignore              # Protects .env and .db files
├── architecture.svg        # System diagram
├── memorybot/
│   ├── __init__.py
│   ├── chain.py            # LangChain + Groq LLM setup
│   ├── database.py         # SQLite persistence layer
│   ├── memory_manager.py   # Short + long-term memory logic
│   └── vector_store.py     # Pinecone embeddings + retrieval
└── README.md
```

---

## 💡 Why I Built This

Long-term memory is the missing piece in most AI agent demos. Tools like RAG get attention, but persistent, per-user conversational memory — where the bot genuinely learns who you are over time — is much harder to do well.

This project shows:

- **Hybrid memory** (vector semantic search + structured SQL)
- **Automatic summarisation** to compress history without losing meaning
- **Zero-cost deployment** using free-tier services only
- **Production-grade architecture** patterns: WAL mode SQLite, serverless vector DB, local embeddings

It's designed to be the kind of memory system a real product would build, not a toy demo.

---

## 🔒 Security Note

Your `.env` file is listed in `.gitignore` and will never be committed. The `.env.example` file contains only placeholder values — never real keys. If you fork this project, your secrets stay local.

---

## 📜 License

MIT — do whatever you want with it.

---

<div align="center">

Built with ❤️ by **Hamdan Alyafei**

[![GitHub](https://img.shields.io/badge/GitHub-hamdansultanalyafei-181717?style=flat-square&logo=github)](https://github.com/hamdansultanalyafei)

</div>
