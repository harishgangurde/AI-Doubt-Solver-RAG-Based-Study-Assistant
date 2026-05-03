# 🎓 AI Doubt Solver

> An intelligent, RAG-powered study assistant that answers doubts, generates quizzes, creates flashcards, and summarizes topics — all from your own uploaded PDF documents.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-0.2.6-1C3C3C?style=for-the-badge)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [RAG Pipeline](#-rag-pipeline-explained)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Supabase Setup](#-supabase-setup)
- [Running the App](#-running-the-app)
- [Screenshots](#-screenshots)
- [API / Pages](#-pages)
- [How It Works](#-how-it-works)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

---

## 🧠 Overview

**AI Doubt Solver** is a full-stack AI-powered education tool built for students. Instead of searching generic answers on the internet, students upload their own study material (PDF textbooks, notes, question papers) and interact with an AI that answers **strictly from their document content**.

The project uses **Retrieval Augmented Generation (RAG)** — a cutting-edge AI architecture that combines semantic vector search with large language model generation to produce accurate, context-aware answers.

### Problem it solves
- Students can't get instant doubt resolution outside college hours
- Generic search engines don't know the student's specific syllabus
- AI chatbots hallucinate answers not grounded in actual study material

### Solution
Upload your PDF → Ask doubts → Get answers from your document → Practice with AI quizzes → Track your progress

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **PDF Upload** | Upload any PDF — textbook, notes, question paper. Drag and drop supported. |
| 💬 **Doubt Solver** | RAG-powered chat that answers questions from your document with conversation memory |
| 📝 **Quiz Generator** | Auto-generates MCQs with 4 options, correct answer, and explanation |
| 🃏 **Flashcards** | AI-generated flip cards with term on front and definition on back |
| 📋 **Topic Summarizer** | Bullet-point summaries of any topic from your document |
| 📊 **Dashboard** | Track quiz scores, average performance, and learning progress |
| 🔐 **Multi-user Auth** | Each student has their own account with completely isolated data |
| 🎓 **Learning Modes** | Beginner / Intermediate / Expert modes adjust AI answer complexity |
| 🔒 **Data Security** | Row Level Security ensures users never see each other's data |

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| Streamlit | 1.35.0 | Frontend UI framework |
| LangChain | 0.2.6 | RAG pipeline orchestration |
| LangChain-Groq | 0.1.6 | Groq API integration |
| Groq API | — | LLM inference (LLaMA 3.3 70B) |
| Sentence Transformers | 2.7.0 | Local text embedding model |
| PyMuPDF | 1.24.5 | PDF text extraction |
| Supabase-py | 2.5.0 | Database client |
| python-dotenv | 1.0.1 | Environment variable management |

### AI Models
| Model | Type | Purpose |
|---|---|---|
| `llama-3.3-70b-versatile` | LLM (via Groq) | Answering doubts, generating MCQs, flashcards, summaries |
| `all-MiniLM-L6-v2` | Embedding model (local) | Converting text chunks and queries into 384-dim vectors |

### Database & Infrastructure
| Technology | Purpose |
|---|---|
| Supabase | Managed PostgreSQL + Auth + RLS |
| PostgreSQL | Relational database |
| pgvector | Vector similarity search extension |
| Supabase Auth | User authentication with JWT |
| Row Level Security | Per-user data isolation at DB level |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Student Browser                       │
│              (Streamlit Multi-page App)                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Python Backend                          │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │PDF Processor│  │  RAG Chain   │  │Quiz Generator │  │
│  │  (PyMuPDF)  │  │ (LangChain)  │  │  (LangChain)  │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                │                   │          │
└─────────┼────────────────┼───────────────────┼──────────┘
          │                │                   │
          ▼                ▼                   ▼
┌─────────────────┐  ┌──────────┐    ┌─────────────────┐
│  Supabase DB    │  │ Groq API │    │ HuggingFace      │
│  (PostgreSQL    │  │ LLaMA    │    │ Sentence         │
│  + pgvector)    │  │ 3.3 70B  │    │ Transformers     │
└─────────────────┘  └──────────┘    └─────────────────┘
```

---

## 🔄 RAG Pipeline Explained

RAG (Retrieval Augmented Generation) is the core AI architecture. Here's the complete flow:

### Phase 1 — Ingestion (PDF Upload)

```
PDF File
   │
   ▼
PyMuPDF extracts raw text from all pages
   │
   ▼
LangChain RecursiveCharacterTextSplitter
   └── chunk_size = 500 characters
   └── chunk_overlap = 50 characters
   │
   ▼
all-MiniLM-L6-v2 encodes each chunk
   └── Output: 384-dimensional float vector per chunk
   │
   ▼
Supabase document_chunks table
   └── Stores: content (text) + embedding (vector 384)
```

### Phase 2 — Retrieval + Generation (Asking a Question)

```
User Question (string)
   │
   ▼
all-MiniLM-L6-v2 encodes question → 384-dim query vector
   │
   ▼
pgvector cosine similarity search (match_chunks SQL function)
   └── Compares query vector against all stored chunk vectors
   └── Returns Top-5 most semantically similar chunks
   │
   ▼
Context = Top-5 chunks concatenated
   │
   ▼
LangChain builds prompt:
   └── System: "Answer only from this context: {context}"
   └── History: Last 6 chat messages (memory)
   └── User: {question}
   │
   ▼
Groq API → LLaMA 3.3 70B generates answer
   │
   ▼
Answer displayed in chat UI + saved to Supabase
```

### Why RAG instead of sending the whole PDF?
- LLMs have context window limits — a 200-page textbook won't fit
- RAG sends only the 5 most relevant chunks (~2500 chars) instead of the entire document
- Answers are grounded in actual document content — no hallucination
- Fast and cost-efficient

---

## 🗄️ Database Schema

```sql
-- User profiles (linked to Supabase Auth)
profiles
├── id          UUID (FK → auth.users)
├── email       TEXT
├── full_name   TEXT
└── created_at  TIMESTAMPTZ

-- Uploaded PDF documents
documents
├── id           UUID PK
├── user_id      UUID (FK → profiles)
├── file_name    TEXT
├── subject      TEXT
├── total_chunks INT
└── created_at   TIMESTAMPTZ

-- Text chunks with vector embeddings
document_chunks
├── id           UUID PK
├── document_id  UUID (FK → documents)
├── user_id      UUID (FK → profiles)
├── content      TEXT
├── embedding    VECTOR(384)    ← pgvector
├── chunk_index  INT
└── created_at   TIMESTAMPTZ

-- Chat sessions
chat_sessions
├── id           UUID PK
├── user_id      UUID (FK → profiles)
├── document_id  UUID (FK → documents)
├── title        TEXT
└── created_at   TIMESTAMPTZ

-- Individual chat messages
chat_messages
├── id           UUID PK
├── session_id   UUID (FK → chat_sessions)
├── role         TEXT ('user' | 'assistant')
├── content      TEXT
└── created_at   TIMESTAMPTZ

-- Quiz attempt records
quiz_attempts
├── id              UUID PK
├── user_id         UUID (FK → profiles)
├── document_id     UUID (FK → documents)
├── topic           TEXT
├── score           INT
├── total_questions INT
└── created_at      TIMESTAMPTZ
```

**Security:** Row Level Security (RLS) is enabled on all tables. Every user can only read and write their own rows.

---

## 📁 Project Structure

```
ai-doubt-solver/
│
├── app/
│   ├── main.py                    # Streamlit home page — PDF upload & management
│   │
│   ├── pages/
│   │   ├── 01_doubt_solver.py     # RAG chat interface
│   │   ├── 02_quiz.py             # MCQ quiz generator
│   │   ├── 03_flashcards.py       # Flip card review
│   │   └── 04_dashboard.py        # Score tracking dashboard
│   │
│   ├── components/
│   │   ├── auth.py                # Login / Signup UI
│   │   └── sidebar.py             # Shared sidebar navigation
│   │
│   ├── core/
│   │   ├── pdf_processor.py       # PDF parse → chunk → embed → store
│   │   ├── rag_chain.py           # RAG pipeline + Groq LLM
│   │   ├── quiz_generator.py      # MCQ + flashcard + summarizer
│   │   └── summarizer.py          # Topic summarizer
│   │
│   └── utils/
│       └── helpers.py             # Session state, auth guards, utilities
│
├── database/
│   ├── supabase_client.py         # Supabase connection (anon + admin)
│   ├── vector_store.py            # pgvector similarity search
│   └── schema.sql                 # Complete SQL schema
│
├── .env                           # API keys (never commit!)
├── .env.example                   # Template for setup
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- Git
- A Supabase account (free) — [supabase.com](https://supabase.com)
- A Groq account (free) — [console.groq.com](https://console.groq.com)

### Step 1 — Clone the repository
```bash
git clone https://github.com/yourusername/ai-doubt-solver.git
cd ai-doubt-solver
```

### Step 2 — Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ First install may take 3-5 minutes as it downloads PyTorch and Sentence Transformers.

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# Groq API (get from console.groq.com → API Keys)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Supabase (get from supabase.com → Project Settings → API)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🗃️ Supabase Setup

### Step 1 — Create a new Supabase project
1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **New Project**
3. Name it `ai-doubt-solver`
4. Wait ~2 minutes for it to spin up

### Step 2 — Enable pgvector
Go to **SQL Editor** and run:
```sql
create extension if not exists vector;
```

### Step 3 — Run the full schema
Copy and run the entire contents of `database/schema.sql` in the SQL Editor.

### Step 4 — Disable email confirmation (for development)
Go to **Authentication → Sign In / Providers → Email** → Toggle OFF **Confirm email** → Save

### Step 5 — Get your API keys
Go to **Settings → API** and copy:
- `Project URL` → `SUPABASE_URL`
- `anon public` key → `SUPABASE_ANON_KEY`
- `service_role` key → `SUPABASE_SERVICE_KEY`

---

## 🚀 Running the App

```bash
streamlit run app/main.py
```

Open your browser at:
```
http://localhost:8501
```

> 💡 First launch takes 20-30 seconds as the AI embedding model (`all-MiniLM-L6-v2`) loads for the first time. Subsequent launches are much faster due to caching.

---

## 📱 Pages

| Page | URL | Description |
|---|---|---|
| Home | `/` | Upload PDFs, manage documents, select active document |
| Doubt Solver | `/doubt_solver` | Ask questions, get AI answers from your document |
| Quiz | `/quiz` | Generate MCQs, submit answers, see score and explanations |
| Flashcards | `/flashcards` | Flip card review with progress tracking |
| Dashboard | `/dashboard` | Quiz history, average score, performance charts |

---

## 🔍 How It Works

### 1. Sign Up / Login
Create an account with email and password. Supabase Auth handles authentication and returns a session token. Your data is completely isolated from other users via Row Level Security.

### 2. Upload a PDF
Select a PDF and enter the subject name. The system:
- Extracts all text using PyMuPDF
- Splits into 500-character chunks with 50-character overlap
- Embeds each chunk using `all-MiniLM-L6-v2` (384-dim vectors)
- Stores chunks + embeddings in Supabase's pgvector table
- Typical PDF (50 pages) = ~200-400 chunks, takes ~30 seconds

### 3. Ask Doubts
Type any question. The system:
- Embeds your question into a vector
- Finds the 5 most semantically similar chunks using cosine similarity
- Sends those chunks as context to LLaMA 3.3 70B on Groq
- Returns an answer grounded in your document
- Remembers last 6 messages for conversation context

### 4. Generate Quiz
Enter a topic. The system retrieves relevant chunks and prompts the LLM to generate MCQs in strict JSON format with question, 4 options, correct answer, and explanation.

### 5. Flashcards
Enter a topic. The LLM generates key term-definition pairs from the document content, displayed as interactive flip cards with a progress bar.

---

## 🔮 Future Improvements

- [ ] Support for multiple document types (DOCX, PPT, images with OCR)
- [ ] Spaced repetition algorithm for flashcard scheduling
- [ ] Collaborative study rooms (multiple students, shared documents)
- [ ] Voice input for asking doubts
- [ ] Export quiz results as PDF report
- [ ] Mobile app using React Native
- [ ] Admin dashboard for teachers to upload material for students
- [ ] Integration with Google Classroom / LMS platforms
- [ ] Multi-language support
- [ ] Real-time collaborative notes

---

## 📦 Requirements

```
streamlit==1.35.0
streamlit-chat==0.1.1
streamlit-extras==0.4.2
langchain==0.2.6
langchain-community==0.2.6
langchain-groq==0.1.6
groq==0.9.0
sentence-transformers==2.7.0
pymupdf==1.24.5
supabase==2.5.0
python-dotenv==1.0.1
pydantic==2.7.4
```

---

## 🧪 Key Concepts Used

| Concept | Where Used |
|---|---|
| RAG (Retrieval Augmented Generation) | Core doubt-solving pipeline |
| Vector Embeddings | Converting text to 384-dim numerical vectors |
| Cosine Similarity | Finding relevant chunks via pgvector |
| LLM Prompt Engineering | System prompts for quiz, flashcard, summary generation |
| JWT Authentication | Supabase Auth session management |
| Row Level Security | Per-user database access control |
| Text Chunking | Splitting PDFs into overlapping segments |
| Semantic Search | Finding meaning-based matches, not keyword matches |
| Multi-page Streamlit | Routing across pages with shared session state |
| Caching (`@st.cache_resource`) | Keeping embedding model in memory across reruns |

---

## 🙋 Author

**Harish Gangurde**
- 📧 harishgangurde1539@gmail.com
- 🐙 GitHub: [@harishgangurde](https://github.com/harishgangurde)


---

## ⭐ Show Your Support

If this project helped you, please consider giving it a ⭐ on GitHub!

---

> Built with ❤️ using Python, Streamlit, LangChain, Groq, and Supabase
