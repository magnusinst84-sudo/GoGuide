# GoGuide

GoGuide is an AI-assisted career and education decision-support platform designed to help students and families make career decisions using student preferences, parent preferences, education pathways, skills, financial constraints, market evidence, and future-oriented career signals.

## Current Status

Data/recommendation pipeline:
COMPLETE THROUGH PHASE 7.2.1

Backend:
SKELETON

Frontend:
SKELETON

LLM:
NOT YET SELECTED/TRAINED

Deployment:
NOT YET DEPLOYED

## Architecture

Frontend → Render Backend → GoGuide Engines → LLM Provider/Data

## Repository Structure

- `frontend/`: Next.js app, intended for Vercel
- `backend/`: FastAPI app, intended for Render
- `data/`: validated data pipeline/data assets
- `scripts/`: validated data pipeline
- `training/`: future local LLM training
- `models/`: model/adapters documentation only
- `docs/`: architecture/deployment/API/LLM documentation

## Data Integrity

The raw data layer is immutable and the validated recommendation engine should not be modified casually.

## Planned Features

- student assessment
- parent input
- education matching
- skill-gap analysis
- career recommendations
- financial constraint solver
- EMI/affordability
- parent–student preference alignment
- what-if simulation
- learning pathways
- alternative career paths
- future/market signals
- final action plan
- conversational LLM guidance
