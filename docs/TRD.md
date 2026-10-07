# Technical Requirements Document (TRD)

## 1. Frontend
- **Framework**: Next.js (App Router)
- **Language**: TypeScript
- **Deployment**: Vercel
- **Communication**: REST communication with backend via `NEXT_PUBLIC_API_URL`
- **Constraint**: The frontend must not contain business logic for recommendations, financial calculations, conflict calculations, or skill matching. It is strictly a presentation and interaction layer.

## 2. Backend
- **Framework**: FastAPI
- **Language**: Python
- **Validation**: Pydantic
- **Deployment**: Render
- **Communication**: REST APIs
- **Configuration**: Environment-based configuration (e.g., CORS restrictions via `BACKEND_CORS_ORIGINS`).

## 3. Backend Layers
The FastAPI backend is structured as follows:
- `api/`: Route definitions and endpoint handlers.
- `core/`: Application configuration, constants, and logging.
- `schemas/`: Pydantic models for request/response validation.
- `models/`: Domain models (if distinct from schemas).
- `services/`: Business logic orchestration.
- `engines/`: Deterministic calculation modules (Recommendation, Financial, Conflict, Skill Gap, Pathway).
- `llm/`: Provider abstractions and prompt templates.
- `data/`: Interfaces to load and index local static datasets.
- `utils/`: Shared utilities (normalization, validation).
- `integrations/`: Abstractions for live web/API retrieval.

## 4. Data Layer
- **Source of Truth**: The backend consumes existing outputs from `data/processed/`, `data/crosswalks/`, and `data/dictionaries/`.
- **Constraint**: Do not duplicate raw datasets into the backend structure.

## 5. Recommendation Engine
- **Source**: Treats Phase 7.2.1 outputs and logic as validated and frozen.
- **Constraint**: Do not silently change scoring behavior. The engine provides deterministic, evidence-gated rankings.

## 6. Financial Engine
- **Logic**: Uses purely deterministic calculations (Total Cost, EMI, Funding Need). 
- **Source**: Relies on user inputs and optionally live web retrieval for current tuition parameters.

## 7. Conflict Engine
- **Logic**: Uses deterministic preference vectors to calculate alignment between student and parent inputs.

## 8. LLM Architecture
- **Design**: Strict provider abstraction. No hard-coded models. No model weights downloaded or stored in the repository.
- **Placeholders**:
  - `LLMProvider` (Base Interface)
  - `LocalProvider`
  - `HuggingFaceProvider`
  - `GroqProvider`
  - `OpenRouterProvider`

## 9. Live Web/API Layer
- **Abstraction**: Creates a pluggable interface for external retrieval.
- **Capabilities**: The backend can request current college data, scholarships, admissions, loans, jobs, and market signals without coupling core business logic to a single provider.
- **Provenance**: External results must carry provenance/source metadata.

## 10. Grounding
The LLM operates exclusively on structured backend context.
**Conceptual Flow:**
1. User request
2. Backend retrieval/calculation
3. Structured context generated
4. LLM synthesis
5. Response returned

## 11. Deployment
- **Frontend**: Vercel
- **Backend**: Render
- **LLM**: External/swappable model-serving service (Never assume Render free tier hosts the model).
- **Training**: Local/appropriate GPU environment.
- **Adapter**: External model-serving environment when deployed.

## 12. Security
- Secrets injected only through environment variables.
- No API keys committed to Git.
- No raw PII in the LLM corpus.
- No model weights in Git.
- External data must be strictly validated.
- Source/provenance tracking enforced for all retrieved data.
- CORS restrictions explicitly configured in production.
