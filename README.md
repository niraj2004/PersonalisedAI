# 📚 Personal Learning Assistant

A powerful, AI-driven application that helps you master new topics by curating, processing, and delivering personalized learning materials directly to your inbox.

## 🚀 Features

*   **Curriculum Management**: Upload PDF or Text files to define your learning path. The system extracts topics and generates embeddings for semantic matching.
*   **Resource Ingestion**: Add YouTube videos or Web Articles. The app automatically fetches transcripts/text, chunks them, and stores them for retrieval.
*   **Smart Matching (RAG)**: Uses Retrieval-Augmented Generation to match your uploaded resources against your curriculum topics.
*   **Daily Digest Emails**: Generates a personalized email summary of a matched resource using Llama-3 via Groq, delivered via Resend.
*   **Dashboard**: A Streamlit-based UI to manage resources, view metrics, trigger manual emails, and preview uploaded files.
*   **Automated Scheduler**: Runs a daily job to process unread resources and send emails.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following:

1.  **Python 3.8+** installed.
2.  **Supabase Account**: For the PostgreSQL database with `pgvector` support.
3.  **Groq API Key**: For the LLM (Llama-3).
4.  **Resend API Key**: For sending emails.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd PersonalisedAI
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory and add your credentials:

```ini
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key

# LLM (Groq)
GROQ_API_KEY=your_groq_api_key

# Email (Resend)
RESEND_API_KEY=your_resend_api_key
TARGET_EMAIL=your_email@example.com

# App Config
API_URL=http://localhost:8000
```

### 5. Database Setup
1.  Go to your Supabase project's **SQL Editor**.
2.  Copy the contents of `schema.sql` from this repository.
3.  Run the SQL script to create the necessary tables (`curriculum_topics`, `resources`, `resource_chunks`, `curriculum_files`) and enable the `vector` extension.

---

## 🏃‍♂️ Running the Application

You need to run both the Backend (FastAPI) and the Frontend (Streamlit).

### Terminal 1: Backend
```bash
uvicorn backend.main:app --reload
```
*The API will start at `http://localhost:8000`.*

### Terminal 2: Frontend
```bash
streamlit run frontend/app.py
```
*The UI will open in your browser at `http://localhost:8501`.*

---

## 📖 Usage Guide

### 1. Upload Curriculum
*   Navigate to **"Upload Curriculum"** in the sidebar.
*   Upload a PDF or Text file containing the topics you want to learn.
*   The system will chunk and embed these topics for future matching.
*   You can preview uploaded files in the "Uploaded Curriculum" section.

### 2. Add Resources
*   Go to **"Add Resource"**.
*   Paste a URL (YouTube Video or Article).
*   Click **"Process Resource"**.
*   The app will fetch the content (transcript or text), chunk it, and save it to the database.

### 3. Dashboard & Emails
*   The **Dashboard** shows your "Unread" and "Shared" resources.
*   **Unread Resources**: Items you've added but haven't received an email for yet.
*   **Trigger Email**: You can manually trigger an email for any unread resource. The system will:
    1.  Find the most relevant topic from your curriculum.
    2.  Generate a summary and "Why this matters" explanation.
    3.  Send it to your `TARGET_EMAIL`.
*   **Delete**: You can remove resources directly from the dashboard.

### 4. Automated Scheduler
*   The backend includes a scheduler that runs daily (default: 8:00 AM) to automatically process one unread resource and email it to you.

---

## 🧩 Tech Stack

*   **Backend**: FastAPI, Supabase (Postgres + pgvector), APScheduler
*   **Frontend**: Streamlit
*   **AI/LLM**: Groq (Llama-3.1-8b), SentenceTransformers (Embeddings)
*   **Ingestion**: `yt-dlp` (YouTube), `trafilatura` (Web), `pypdf` (PDF)
*   **Email**: Resend API

---

## 🤝 Contributing
Feel free to open issues or submit pull requests to improve the Personal Learning Assistant!
