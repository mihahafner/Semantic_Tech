# pipeline/llm_ie.py
import os, json
from typing import List, Dict, Any
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY missing in env")

SYSTEM = """Extract factual triples from the text as JSON.
- Use keys: subject, predicate, object, object_is_literal (bool), datatype (optional), confidence (0..1)
- Subjects/objects should be short noun phrases.
- Predicates should be verbs or ontology-like properties (e.g., hasHeight, hasRiskLevel).
- Prefer canonical spellings (singular)."""

def extract_triples_llm(text: str, model: str = "gpt-4o-mini") -> List[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: raise RuntimeError("OPENAI_API_KEY missing in env")
    client = OpenAI(api_key=api_key)

    prompt = f"Text:\n{text}\n\nReturn a JSON array of triples."
    r = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role":"system", "content": SYSTEM},
            {"role":"user", "content": prompt}
        ]
    )
    content = r.choices[0].message.content.strip()
    # be tolerant: find first JSON array
    start = content.find("[")
    end   = content.rfind("]")
    if start == -1 or end == -1:
        return []
    payload = content[start:end+1]
    try:
        triples = json.loads(payload)
        return [t for t in triples if isinstance(t, dict)]
    except Exception:
        return []
