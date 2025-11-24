# prd.md (final version with tech stack)

# CONTENTS
- Abstract
- Business Objectives
- KPI
- Success Criteria
- User Journeys
- Scenarios
- User Flow
- Functional Requirements
- Tech Stack
- Model Requirements
- Data Requirements
- Prompt Requirements
- Testing & Measurement
- Risks & Mitigations
- Costs
- Assumptions & Dependencies
- Compliance/Privacy/Legal
- GTM/Rollout Plan

---

## 📝 Abstract

A personal learning assistant app that converts a backlog of saved resources (YouTube videos, blog posts, web articles) into structured, curriculum-aligned daily learning. The user uploads their curriculum and resources anytime. Every morning at 8am, the system picks the first resource that matches any curriculum topic via RAG (embedding-based similarity), extracts its content, generates a first-principles explanation email, and sends it via Resend. This eliminates overwhelm and ensures steady daily progress.

---

## 🎯 Business Objectives
- Turn scattered saved resources into structured daily learning.
- Automate the process of resource classification and curriculum mapping.
- Reduce cognitive overload and increase curriculum completion rates.

---

## 📊 KPI

| GOAL                | METRIC                               | QUESTION                                                   |
|---------------------|---------------------------------------|------------------------------------------------------------|
| Backlog Reduction   | 80% reduction in unread resources     | Are we clearing the saved-resources backlog effectively?  |
| Learning Consistency| Daily emails successfully sent        | Are we maintaining consistent daily learning?              |
| Relevance Quality   | % emails marked “useful”              | Is the curated output actually helpful for the curriculum? |

---

## 🏆 Success Criteria
- Daily 8am emails delivered reliably.
- Resource-to-curriculum mapping is consistently relevant.
- User experiences reduced overwhelm within 4 weeks.
- Majority of backlog processed within the goal timeline.

---

## 🚶‍♀️ User Journeys
- User uploads curriculum (PDF, text).
- User uploads resources—links, YouTube videos, articles—at any time.
- At 8am daily, the system scans all unprocessed resources, finds the first one that matches a curriculum topic using embeddings + similarity search.
- System extracts the content, generates a first-principles explanation email, and sends it via Resend.
- Resource is marked as processed; backlog decreases automatically.

---

## 📖 Scenarios
- System finds a matching topic → generates and sends email → marks done.
- Resource fails parsing → logs error → moves to next resource the same morning.
- YouTube transcript missing → skip and continue scanning.
- Curriculum updated → embeddings recalculated and stored.
- Email quality is too low → model retries with expanded context.

---

## 🕹️ User Flow

**Upload Curriculum**  
→ Store in Supabase Storage  
→ Extract topics  
→ Create embeddings  
→ Store in pgvector  

**Upload Resource**  
→ URL saved  
→ Fetch content (YouTube or HTML)  
→ Store raw + extracted text  

**Daily Cron (8am)**  
1. Fetch unprocessed resources  
2. Extract text if not done  
3. Embed resource text  
4. Query curriculum embeddings in pgvector  
5. Select highest-confidence topic  
6. Generate email (Groq + prompt + RAG context)  
7. Send via Resend  
8. Mark resource as processed  

**User Receives Email**  
→ First-principles explanation + mapping + next steps

---

## 🧰 Functional Requirements

### Core Features
- Upload curriculum file & extract topics
- Upload resource links anytime
- Daily automated processing & email generation
- RAG-based topic matching using embeddings
- First-principles email generation via Groq LLM
- Delivery via Resend API
- Logging for errors, parsing failures, and quality

### Requirements Table

| SECTION     | SUB-SECTION | USER STORY & EXPECTED BEHAVIORS          | SCREENS    |
|-------------|-------------|-------------------------------------------|------------|
| Upload      | Curriculum  | User uploads → stored → topics extracted | Streamlit  |
| Upload      | Resource    | User adds link → stored with timestamp   | Streamlit  |
| Daily Job   | Cron        | At 8am, auto-process next matching resource | None     |
| Output      | Email       | High-quality structured email delivered  | Inbox      |
| Management  | Backlog     | System tracks processed/unprocessed      | Streamlit  |

---

# 🏗️ Tech Stack (Finalized)

### Frontend
- Streamlit  
  - Curriculum upload  
  - Resource upload  
  - Backlog & log viewer  

### Backend
- FastAPI  
  - Endpoints for upload, indexing, processing, debugging  
  - API layer for Streamlit  

### Database & Vector Store
- Supabase Postgres with pgvector  
  - `curriculum_topics` → text + embedding  
  - `resource_chunks` → extracted text + embedding  
  - `resources` → URL + timestamps  
  - Cosine similarity queries for RAG retrieval  

### File Storage
- Supabase Storage  
  - PDFs  
  - HTML dumps  
  - YouTube transcripts  
  - Chunked text  

### RAG Components
- HuggingFace Sentence-Transformers  
  - Recommended: `all-MiniLM-L6-v2` (384-dim)  
- LlamaIndex  
  - Chunking  
  - Retrieval orchestration  
  - Prompt assembly  

### Content Extraction
- `trafilatura` — main article extraction  
- `beautifulsoup4` — fallback HTML parsing  
- `youtube-transcript-api` — YouTube transcripts  

### LLM (Email Generation)
- Groq API  
  - For structured email generation  
  - Fast & high quality  

### Email Delivery
- Resend API  
  - Simple, reliable sending  

### Background Processing
- APScheduler or OS Cron  
  - Daily 8am job  
  - Manual “Send Now” trigger  

### Other Libraries
- `supabase-py`  
- `python-dotenv`  
- `loguru` or built-in `logging`  
- `requests` / `httpx`  

---

## 📐 Model Requirements

| SPECIFICATION   | REQUIREMENT          | RATIONALE                        |
|-----------------|----------------------|----------------------------------|
| LLM Engine      | Groq API             | Reliable & fast inference        |
| Embeddings      | HF MiniLM            | CPU-friendly semantic matching   |
| RAG             | Yes (matching only)  | Accurate topic mapping           |
| Context Window  | ~16k recommended     | Handle transcripts & chunks      |
| Latency         | <5s acceptable       | Offline job, not user-facing     |
| Fine-tuning     | None                 | RAG is enough                    |

---

## 🧮 Data Requirements
- Curriculum text stored & chunked  
- Embeddings for curriculum topics  
- Embeddings for resource chunks  
- pgvector for similarity search  
- Store parsing failures & logs  
- Store generated emails (optional audit)  

### RAG Workflow
1. Embed curriculum topics  
2. Embed resource  
3. Query top-k curriculum topics  
4. Select via confidence threshold  
5. Feed curriculum + resource text to Groq for email creation  

---

## 💬 Prompt Requirements

### Prompts in v1

**System Prompt**
- First-principles teacher  
- Concise, structured  
- Email-style formatting  
- Grounded in RAG context  

**Mapping Prompt**
- Interprets cosine similarity  
- Applies confidence threshold  

**Email Generation Prompt**
Inputs:  
- Resource text  
- Curriculum topic text  

Output sections:  
- Subject  
- TL;DR  
- First-principles explanation  
- Why it matters  
- Next steps  

**Fallback Prompt**
- Used when extraction partially fails  

---

## 🧪 Testing & Measurement

### Offline Tests
- 10–12 test resources  
- Mapping accuracy  
- Extraction quality  
- Email clarity score (≥ 8/10)

### Online Tests
- Cron reliability  
- Email delivery  
- Parsing failure rate  

### Live Monitoring
- Daily logs  
- Threshold tuning  
- User satisfaction  

---

## ⚠️ Risks & Mitigations

| RISK                       | MITIGATION                                       |
|----------------------------|---------------------------------------------------|
| Resource mis-matched       | Tune thresholds; fallback prompts                |
| Email quality inconsistent | Add quality rubric + retry                       |
| Parsing failures           | Use trafilatura fallback; skip & log             |
| Missing transcripts        | Skip resource automatically                      |
| Resend/LLM quotas          | Retry + backoff                                  |

---

## 💰 Costs
- Groq API usage  
- Resend API usage  
- Supabase free tier (DB + storage)  
- No paid LLM or vector DB needed  

---

## 🔗 Assumptions & Dependencies
- Single-user system  
- Runs on Antigravity environment  
- Groq + Resend API keys available  
- Supabase pgvector enabled  
- All content owned by user  
- No special compliance constraints  

---

## 🔒 Compliance/Privacy/Legal
- Only user-provided content processed  
- Emails sent only to the user  
- Logs do not store sensitive data  
- API keys stored securely in environment variables  

---

## 📣 GTM/Rollout Plan
- **Day 1–3:** FastAPI + Streamlit setup, Supabase schema  
- **Day 3–5:** Curriculum ingest + embeddings  
- **Day 5–8:** Resource extraction pipeline  
- **Day 8–12:** RAG + topic matching  
- **Day 12–15:** Email generation + Resend integration  
- **Day 15–18:** Testing & cron job setup  
- **Day 18–20:** Polishing + QA + logs  
- **Launch:** Internal use with real resources  
