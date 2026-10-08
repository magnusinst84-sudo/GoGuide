# GoGuide

## 1. Project Overview
GoGuide is a privacy-first, AI-assisted career and education decision-support platform. It helps students and their families make informed career choices by considering student skills, academic streams, financial constraints, and market evidence.

**The Problem:** Students often choose careers based on incomplete information or peer pressure, ignoring critical factors like skill gaps, financial realities, and educational pathways.
**The Solution:** GoGuide's recommendation engine acts as a comprehensive advisor, taking inputs through a detailed questionnaire, processing them through customized scoring engines, and providing actionable learning pathways and AI guidance.

## 2. Key Features
- **Student Questionnaire:** A comprehensive intake form for student profile data.
- **Career Recommendations:** AI-driven matching of students to suitable careers.
- **PRISM-Style Scoring & Fit Analysis:** Evaluates students against occupational requirements.
- **Financial Feasibility Solver:** Calculates total costs, funding needs, monthly EMIs, and affordability ratios. Explains "blocked" careers.
- **Skill-Gap Analysis:** Highlights missing skills needed for target occupations.
- **Education/Pathway Generation:** Provides structured steps for achieving career goals.
- **Quick Doubts Chatbot:** Immediate, conversational AI assistance for specific student queries.
- **RAG-Backed Intelligence:** Uses FAISS vector search to retrieve accurate occupational and educational data.
- **Local LLM (Ollama) Support:** Fully supports running offline local LLMs for inference to protect privacy.

## 3. Architecture
- **Frontend:** Next.js (React 18), Tailwind CSS, handling the user interface and routing.
- **FastAPI Backend:** A robust Python backend providing REST APIs.
- **Recommendation/Analysis Engines:** Custom Python engines (`skill_gap_engine.py`, `financial_solver.py`, `conflict_engine.py`) for deterministic scoring and analysis.
- **RAG/FAISS:** Employs `sentence-transformers` (`all-MiniLM-L6-v2`) and CPU FAISS for document indexing and retrieval.
- **LLM Integrations:**
  - **Local/Ollama:** For private, local inference via `LLM_PROVIDER=local` and `OLLAMA_BASE_URL`.
  - **Gemini:** Used for the Quick Doubts feature.
- **Data Flow:** Frontend sends structured user profile JSON to the FastAPI backend. The backend orchestrates scoring, fetches contextual data via FAISS, queries the LLM provider, and returns actionable recommendations to the client.

## 4. Repository Structure
```text
DataQuest/
├── frontend/                  # Next.js Application
│   ├── app/                   # Next.js App Router
│   ├── components/            # React UI Components
│   ├── package.json           # Frontend dependencies
│   └── .env.example           # Frontend environment variables
├── backend/                   # FastAPI Application
│   ├── app/                   # Application source
│   │   ├── api/               # API Routers (guide, quick_doubts, health)
│   │   ├── engines/           # Scoring and Logic Engines
│   │   ├── llm/               # LLM Provider Integrations (Local, Groq, etc.)
│   │   ├── rag/               # FAISS Index Retrieval
│   │   ├── schemas/           # Pydantic Data Models
│   │   └── services/          # Business Logic and Orchestration
│   ├── data/                  # Source datasets and RAG data
│   │   └── rag/               # RAG documents and built index.faiss
│   ├── scripts/               # Maintenance scripts (e.g., build_rag_index.py)
│   ├── tests/                 # Pytest test suite
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Backend environment variables
└── README.md                  # This file
```

## 5. Local Setup
Follow these exact PowerShell commands to get the project running on Windows:

**1. Clone the repository:**
```powershell
git clone <your-repo-url>
cd DataQuest
```

**2. Setup Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

**3. Setup RAG Files:**
Ensure `documents.jsonl` exists in `backend/data/rag/`, then build the FAISS index:
```powershell
python -m scripts.build_rag_index
```
*(This creates `index.faiss` in `backend/data/rag/`)*

**4. Start Backend (Port 8001):**
```powershell
uvicorn app.main:app --port 8001 --reload
```

**5. Setup Frontend:**
Open a new PowerShell terminal:
```powershell
cd DataQuest\frontend
npm install
Copy-Item .env.example .env.local
```

**6. Start Frontend:**
```powershell
npm run dev
```

## 6. Environment Variables

### Backend (`backend/.env`)
| Variable | Required | Default / Example | Purpose |
|----------|----------|-------------------|---------|
| `BACKEND_CORS_ORIGINS` | No | `http://localhost:3000` | Allowed CORS origins for frontend requests. |
| `LLM_PROVIDER` | Yes | `local` | Provider selection (`local`, `groq`, `huggingface`, `openrouter`). |
| `LLM_MODEL` | Yes* | `qwen3:4b-instruct` | Required if provider is `local`. Model name in Ollama. |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | URL where the Ollama server is running. |
| `GEMINI_API_KEY` | No* | `<your_gemini_key>` | Required if using the Gemini-powered Quick Doubts or Provider. |
| `GEMINI_MODEL` | No | `gemini-3.5-flash-lite` | The specific Gemini model to use. |

### Frontend (`frontend/.env.local`)
| Variable | Required | Default / Example | Purpose |
|----------|----------|-------------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8001` | URL of the FastAPI backend. Update to 8001 if testing locally. |

*(Ensure you never commit real API keys to version control!)*

## 7. API Documentation
Key endpoints currently implemented:

- **GET `/api/health`**
  - **Purpose:** Checks backend health.
  - **Response:** `{"status": "ok", "service": "goguide-backend", "version": "0.1.0"}`

- **POST `/api/guide`**
  - **Purpose:** Core recommendation endpoint. Processes the student profile and returns comprehensive career and pathway advice.
  - **Request:** JSON matching the `GuideRequest` schema (includes profile data).
  - **Response:** JSON matching the `GuideResponse` schema.

- **POST `/api/quick-doubts`**
  - **Purpose:** Chatbot API for answering immediate student queries.
  - **Request:** `{"message": "What is the difference between computer science and IT?"}`
  - **Response:** `{"status": "AVAILABLE", "answer": "..."}`

## 8. Testing
To run the automated backend test suite, use `pytest`:
```powershell
cd backend
.\venv\Scripts\activate
pytest
```
*Note: Test execution requires a valid python environment with `pytest-anyio` and the app dependencies installed.*

## 9. Privacy & Data Handling
GoGuide is designed with a strict privacy-first architecture:
- **No User Accounts:** The platform requires zero registration or persistent user accounts.
- **No Server-Side Storage:** User profile data is processed entirely in-memory for inference. No data is stored, retained, or logged in a persistent database.
- **Local AI:** By using local LLM providers (e.g., Ollama), sensitive questionnaire data can remain entirely on the host machine without ever reaching external cloud providers.
- Open source transparency allows users to verify our data handling practices.

## 10. Development Notes
- **Ports:** The backend is configured to run on port `8001` (to avoid conflicts with default `8000`), and the frontend on port `3000`. Ensure `NEXT_PUBLIC_API_URL=http://localhost:8001` in the frontend environment.
- **Ollama:** If using `LLM_PROVIDER=local`, ensure the Ollama server is running and the specified `LLM_MODEL` (e.g., `qwen3:4b-instruct`) is pulled locally (`ollama run qwen3:4b-instruct`).
- **RAG Dependency:** The `/api/guide` endpoint relies on FAISS. You MUST run the index build script (`build_rag_index.py`) before attempting to get recommendations, otherwise, the backend will fail to retrieve context.

## 11. Troubleshooting

- **`uvicorn` not recognized:** Ensure your Python virtual environment is activated (`.\venv\Scripts\activate`) before running the command.
- **Port 8001 in use:** If port 8001 is already bound, specify a different port: `uvicorn app.main:app --port 8002` and update the frontend `.env.local`.
- **Backend returns `503 Service Unavailable`:** This commonly happens if the LLM provider fails. Check your `LLM_PROVIDER` setting. If `local`, verify Ollama is running and accessible at `OLLAMA_BASE_URL`.
- **RAG index not found errors:** Ensure `python -m scripts.build_rag_index` completed successfully and `backend/data/rag/index.faiss` exists.
- **Frontend cannot reach backend:** Ensure `NEXT_PUBLIC_API_URL` points precisely to your running FastAPI instance (e.g., `http://localhost:8001`).

## 12. Project Status
- **Core Recommendation Engines:** Implemented (Skill Gap, Financial Solver, Pathway Engine).
- **Backend API:** Functioning REST API with FastAPI, integrating FAISS RAG and local/remote LLMs.
- **Frontend UI:** Next.js application structure established.
- **Account & Persistence:** Intentionally excluded for maximum privacy.
- **Production Deployment:** Not yet deployed; designed for Render (backend) and Vercel (frontend).
