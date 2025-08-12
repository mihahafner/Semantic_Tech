# pipeline/linker.py
from typing import Tuple, List
from .gazetteer import build_gazetteer

def normalize_entities(facts: List[tuple], datas: List[tuple], onto_path: str) -> Tuple[List[tuple], List[tuple]]:
    """
    Map surface labels (predicates & class-like objects) to canonical ontology names.
    Only predicate mapping is applied here; subjects/objects (IDs) we keep as-is.
    """
    _, label_to_prop = build_gazetteer(onto_path)

    def norm_pred(p):
        key = p.strip().lower()
        return label_to_prop.get(key, p)

    facts_n = [(s, norm_pred(p), o) for (s, p, o) in facts]
    datas_n = [(s, norm_pred(p), v) for (s, p, v) in datas]
    return facts_n, datas_n

