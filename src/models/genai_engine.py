from groq import Groq
import os
import json
import re

# 🔐 Initialize Groq client safely
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


def analyze_with_llm(data):
    """
    Uses Groq LLM to analyze fraud risk and return structured JSON.
    """

    prompt = f"""
You are a fraud detection expert.

Analyze this transaction:
{data}

Return ONLY valid JSON (no explanation, no markdown):

{{
  "risk_score": number between 0 and 1,
  "decision": "SAFE" or "MEDIUM RISK" or "HIGH RISK",
  "reasons": ["short reason 1", "short reason 2"]
}}
"""

    try:
        # 🔥 Call Groq API
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # 🔥 Extract output
        output = response.choices[0].message.content
        print("RAW LLM OUTPUT:", output)

        # 🔥 Clean unwanted markdown (```json blocks)
        cleaned = re.sub(r"```json|```", "", output).strip()

        # 🔥 Parse JSON safely
        parsed = json.loads(cleaned)

        print("PARSED SUCCESS:", parsed)

        return {
            "success": True,
            "parsed": parsed
        }

    except json.JSONDecodeError as e:
        print("❌ JSON PARSE FAILED:", str(e))
        print("CLEANED OUTPUT:", cleaned)

        return {
            "success": False,
            "error": "Invalid JSON from LLM"
        }

    except Exception as e:
        print("❌ GENAI ERROR:", str(e))

        return {
            "success": False,
            "error": str(e)
        }