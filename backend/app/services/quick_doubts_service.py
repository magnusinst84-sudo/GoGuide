import os
import httpx
from typing import Dict, Any

# Instruction provided in prompt
SYSTEM_INSTRUCTION = """You are GoGuide Quick Doubts, a concise and friendly assistant for students exploring education, careers, skills, and learning.

Answer questions clearly at an appropriate student-friendly level.

You can explain concepts, compare career fields, explain terminology, suggest learning approaches, and provide general educational guidance.

You are NOT the authoritative GoGuide personalized recommendation engine.

Do not claim to know a student's personalized career recommendation, exact eligibility, tuition fees, scholarships, salaries, market statistics, or financial feasibility unless that information is explicitly provided in the conversation.

If the user asks for personalized career recommendations, financial calculations, scholarship eligibility, skill-gap analysis, or education pathway decisions, explain that the main GoGuide guidance system handles those decisions.

Do not invent factual numbers or statistics.

Be concise by default. Use bullets or short sections when useful.

If a question is ambiguous, ask one short clarification question."""

async def generate_quick_doubt_answer(message: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing Gemini API key")

    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },
        "contents": [
            {
                "parts": [
                    {
                        "text": message
                    }
                ]
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract the text from the Gemini response structure
            try:
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                return answer
            except (KeyError, IndexError):
                raise ValueError("Unexpected response format from Gemini")
                
    except httpx.TimeoutException:
        raise ValueError("Timeout connecting to Gemini")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise ValueError("Rate limit exceeded")
        else:
            raise ValueError(f"Gemini API failure")
    except Exception:
        raise ValueError("Unexpected error communicating with Gemini")
