# pipeline/rules_ie.py
import re

# Quick & dirty, extend freely
TUNNEL_RULES = [
    # Length
    {
        "pattern": r"(tunnel|structure)\s+length\s*[:\-]?\s*(\d{2,6})\s*m\b",
        "subject": "{tunnel_id}",
        "predicate": "hasSpecification",
        "object": "{tunnel_id}_Spec",
        "emit_data": ("{tunnel_id}_Spec", "tunnelLength", float, "{2}")
    },
    # Cross-passages
    {
        "pattern": r"(cross passages?|cross-passages?)\s*[:\-]?\s*(\d{1,3})\b",
        "subject": "{tunnel_id}_Spec",
        "predicate": "numberOfCrossPassages",
        "object": "{2}",  # data
        "emit_data": ("{tunnel_id}_Spec", "numberOfCrossPassages", int, "{2}")
    },
    # Hydrant pressure
    {
        "pattern": r"(hydrant).*?(pressure)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*bar",
        "subject": "{tunnel_id}",
        "predicate": "hasSafetyMeasure",
        "object": "{tunnel_id}_Hydrant",
        "emit_data": ("{tunnel_id}_Hydrant", "pressure", float, "{3}")
    },
    # Extinguisher weight
    {
        "pattern": r"(fire extinguisher).*?(weight)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*kg",
        "subject": "{tunnel_id}",
        "predicate": "hasSafetyMeasure",
        "object": "{tunnel_id}_Extinguisher",
        "emit_data": ("{tunnel_id}_Extinguisher", "hasWeight", float, "{3}")
    },
]

def extract_with_rules(text: str, tunnel_id: str):
    facts = []
    datas = []
    for rule in TUNNEL_RULES:
        for m in re.finditer(rule["pattern"], text, flags=re.I | re.M | re.S):
            subj = rule["subject"].format(tunnel_id=tunnel_id, **{str(i): m.group(i) for i in range(0, len(m.groups())+1)})
            pred = rule["predicate"]
            obj  = rule["object"].format(tunnel_id=tunnel_id, **{str(i): m.group(i) for i in range(0, len(m.groups())+1)})

            # If object looks numeric but predicate is an object property, we'll still emit triple (subj pred obj)
            facts.append((subj, pred, obj))

            if "emit_data" in rule:
                target, dp, cast, val = rule["emit_data"]
                v = cast(val.format(tunnel_id=tunnel_id, **{str(i): m.group(i) for i in range(0, len(m.groups())+1)}))
                datas.append((target, dp, v))
    return facts, datas
