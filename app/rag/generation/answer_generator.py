"""
Multi-provider answer generator.
Supports OpenAI, Google Gemini (FREE), and Groq (FREE).
Provider is selected via LLM_PROVIDER env var: "openai" | "gemini" | "groq"
"""
from typing import List, Dict, Any
import logging
from app.api.core.config import settings
from app.rag.generation.prompt_builder import build_prompt

logger = logging.getLogger(__name__)

NO_ANSWER_PHRASE = "This information was not found in the indexed documents."


def _call_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )
    logger.info(f"OpenAI tokens used: {response.usage.total_tokens}")
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
        ),
    )
    logger.info("Gemini response received.")
    return response.text.strip()


def _call_groq(prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )
    logger.info(f"Groq tokens used: {response.usage.total_tokens}")
    return response.choices[0].message.content.strip()


def generate_answer(
    question: str,
    retrieved_chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate an answer using the configured LLM provider.

    Args:
        question: The user's question.
        retrieved_chunks: List of {\"text\", \"metadata\", \"score\"} from ChromaDB.

    Returns:
        {\"answer\": str, \"raw_chunks\": list, \"has_answer\": bool}
    """
    if not retrieved_chunks:
        return {"answer": NO_ANSWER_PHRASE, "raw_chunks": [], "has_answer": False}

    prompt = build_prompt(question, retrieved_chunks)
    provider = settings.LLM_PROVIDER.lower().strip()

    try:
        if provider == "gemini":
            answer = _call_gemini(prompt)
        elif provider == "groq":
            answer = _call_groq(prompt)
        elif provider == "openai":
            answer = _call_openai(prompt)
        else:
            logger.error(f"Unknown LLM_PROVIDER: '{provider}'. Falling back to Gemini.")
            answer = _call_gemini(prompt)

        logger.info(f"[{provider.upper()}] Answer generated successfully.")

    except Exception as e:
        logger.error(f"[{provider.upper()}] LLM API error: {e}")
        answer = f"I encountered an error while generating an answer ({provider}). Please try again."

    has_answer = NO_ANSWER_PHRASE.lower() not in answer.lower()

    return {
        "answer": answer,
        "raw_chunks": retrieved_chunks,
        "has_answer": has_answer,
    }
