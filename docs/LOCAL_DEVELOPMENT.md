# Local Development Guide

## 1. Prerequisites
- Python 3.11+
- Node.js (v18+)
- npm or pnpm

## 2. Environment Variables
Create `.env` files from their respective `.env.example` templates:

### Backend
Copy `backend/.env.example` to `backend/.env`:
```
BACKEND_CORS_ORIGINS=http://localhost:3000
LLM_PROVIDER=local
LLM_MODEL=
LLM_BASE_URL=
LLM_API_KEY=
```

### Frontend
Copy `frontend/.env.example` to `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 3. Backend Setup & Running
```bash
cd backend
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```
The backend API will be available at `http://localhost:8000`.

### API Health Check
```bash
curl http://localhost:8000/api/health
```

## 4. Frontend Setup & Running
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:3000`.

## 5. Deployment

### Vercel Deployment (Frontend)
Deploy the `frontend/` directory to Vercel. Ensure you set the environment variable:
`NEXT_PUBLIC_API_URL=https://<render-backend-url>`

### Render Deployment (Backend)
Deploy the `backend/` directory to Render as a Web Service. The configuration is stored in `backend/render.yaml`.
Ensure you set the environment variable:
`BACKEND_CORS_ORIGINS=https://<vercel-frontend-url>`

## 6. LLM Provider Architecture
The LLM integration is abstracted. You can switch providers (e.g., local, huggingface, groq, openrouter) by setting `LLM_PROVIDER` in `backend/.env` without changing business logic.
