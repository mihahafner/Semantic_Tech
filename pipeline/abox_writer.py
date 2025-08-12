# pipeline/abox_writer.py
import os
from rdflib import Graph, Namespace, RDF, Literal, XSD
from owlready2 import get_ontology, ThingClass, ObjectPropertyClass, DataPropertyClass

EX_IRI = "http://example.org/aec#"

# pipeline/abox_writer.py
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD
import re
from typing import Any, Dict, Iterable, List, Tuple, Optional





EX = Namespace("http://example.org/aec#")

def _get(d: Dict[str, Any], *names):
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return None

def _norm_label(x: Any) -> str:
    # Keep qnames like ex:Hydrant if already present; else sanitize to Camel-ish id
    if isinstance(x, str):
        return x.strip()
    return str(x)

def _looks_qname(s: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][\w\-]*:[A-Za-z_][\w\-]*$", s))

def _looks_iri(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")

def _as_literal_or_uri(o: str):
    # number?
    try:
        if re.fullmatch(r"-?\d+", o):
            return Literal(int(o), datatype=XSD.integer)
        if re.fullmatch(r"-?\d+\.\d+", o):
            return Literal(float(o), datatype=XSD.float)
    except Exception:
        pass
    # qname or iri?
    if _looks_qname(o):
        # allow other prefixes later; for now only ex:
        pref, local = o.split(":", 1)
        if pref == "ex":
            return EX[local]
    if _looks_iri(o):
        return URIRef(o)
    # default: EX IRI (object-as-resource)
    return EX[_safe_id(o)]

def _safe_id(s: str) -> str:
    s = s.strip().replace(" ", "_")
    s = re.sub(r"[^A-Za-z0-9_:-]", "", s)
    if re.match(r"^\d", s):
        s = "n_" + s
    return s

def _normalize_triple(t: Any) -> Optional[Dict[str, Any]]:
    """
    Returns dict {subject, predicate, object, ptype?, confidence?} or None if unusable.
    Supports:
      - dicts with various key aliases
      - tuples/lists (s,p,o[,ptype])
    """
    if isinstance(t, (tuple, list)):
        if len(t) < 3:
            return None
        s, p, o = t[0], t[1], t[2]
        ptype = t[3] if len(t) > 3 else None
        return {
            "subject": _norm_label(s),
            "predicate": _norm_label(p),
            "object": _norm_label(o),
            "ptype": ptype,
        }

    if isinstance(t, dict):
        s = _get(t, "subject", "subj", "s", "source")
        p = _get(t, "predicate", "pred", "p", "relation", "property")
        o = _get(t, "object", "obj", "o", "target")
        if not (s and p and o):
            return None
        out = {
            "subject": _norm_label(s),
            "predicate": _norm_label(p),
            "object": _norm_label(o),
        }
        pt = _get(t, "ptype", "type")
        if pt: out["ptype"] = pt
        cf = _get(t, "confidence", "score")
        if cf: out["confidence"] = cf
        return out

    # unknown shape
    return None

def write_abox(triples: Iterable[Any], out_ttl: str = "Tests/auto_abox.ttl") -> Graph:
    g = Graph()
    g.bind("ex", EX)

    total = 0
    ok = 0
    skipped: List[Any] = []

    for raw in triples:
        total += 1
        t = _normalize_triple(raw)
        if not t:
            skipped.append({"reason": "unusable triple shape", "raw": raw})
            continue

        s = _safe_id(t["subject"])
        p = _safe_id(t["predicate"])
        o = t["object"]

        # subjects/predicates are resources
        s_term = EX[s] if not _looks_iri(s) else URIRef(s)
        p_term = EX[p] if not _looks_iri(p) else URIRef(p)

        # object may be literal or resource
        if isinstance(o, (int, float)):
            o_term = Literal(o, datatype=XSD.float if isinstance(o, float) else XSD.integer)
        elif isinstance(o, str):
            o_term = _as_literal_or_uri(o)
        else:
            o_term = Literal(str(o))

        try:
            g.add((s_term, p_term, o_term))
            ok += 1
        except Exception as e:
            skipped.append({"reason": f"rdflib add failed: {e}", "triple": t})

    g.serialize(out_ttl, format="turtle")
    print(f"✅ ABox written: {out_ttl}  (ok={ok}, total={total}, skipped={len(skipped)})")

    if skipped:
        print("⚠️ Skipped triples (showing up to 10):")
        for row in skipped[:10]:
            print("  -", row)

    return g
