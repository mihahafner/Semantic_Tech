# Text_data_retreival/Text_data_retreival.py
import os


# --- bootstrap imports so "pipeline" resolves ---
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]  # .../Semantic_Tech
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docx import Document
from rdflib import Graph
from pipeline.ontology_vocab import load_ontology, extract_vocab
from pipeline.llm_ie import extract_triples_llm
from pipeline.emb_linker import OntologyLinker
from pipeline.abox_writer import write_abox
# from pipeline.wikidata import wikidata_search    # optional
# from pipeline.viz import visualize_tbox_abox, visualize_abox_rdf  # if you already have these


ROOT = os.path.dirname(os.path.dirname(__file__))
ONTO_PATH = os.path.join(ROOT, "ontology", "general_aec.owl")
DOCX = os.path.join(ROOT, "input", "Building_X_Risk_Analysis.docx")
OUT_TTL = os.path.join(ROOT, "input", "llm_linked_abox.ttl")

def read_docx_text(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()

def main(docx_path: str, subject_id="Asset_X"):
    # 1) Load ontology + vocab
    if not os.path.exists(ONTO_PATH):
        raise FileNotFoundError(f"Ontology not found at {ONTO_PATH}")
    onto = load_ontology(ONTO_PATH)
    classes, obj_props, data_props = extract_vocab(onto)
    linker = OntologyLinker(classes, obj_props, data_props)

    # 2) Read text
    print(f"📄 Using DOCX: {docx_path}")
    text = read_docx_text(docx_path)

    # 3) LLM → triples (mention-level; unlinked)
    triples = extract_triples_llm(text)
    if not triples:
        print("⚠️ LLM returned no triples.")
        return

    # 4) Link mentions to ontology (embeddings)
    linked = []
    for t in triples:
        subj_m = t["subject"].strip()
        pred_m = t["predicate"].strip()
        obj_is_lit = t.get("object_is_literal", False)

        # subject class via embeddings
        subj_link = linker.link_entity(subj_m, top_k=1)
        subj_class = subj_link[0]["name"] if subj_link else None

        # predicate → object or data property
        pred_link = linker.link_property(pred_m, top_k=1)
        if not pred_link:
            # skip if we cannot decide predicate
            continue
        pred_best = pred_link[0]

        triple_out = {
            "subject": {"name": subject_id if subj_m.lower() in ("building","tunnel","asset") else subj_m.replace(" ","_"),
                        "class": subj_class},
            "predicate": {"name": pred_best["name"], "kind": pred_best["kind"]}
        }

        if pred_best["kind"] == "object" and not obj_is_lit:
            obj_m = str(t["object"]).strip()
            obj_link = linker.link_entity(obj_m, top_k=1)
            obj_class = obj_link[0]["name"] if obj_link else None
            triple_out["object"] = {"name": obj_m.replace(" ","_"), "class": obj_class}
        else:
            # data value
            val = t.get("object")
            triple_out["object_literal"] = {"value": val}

        linked.append(triple_out)

    # 5) Write ABox TTL
    g = write_abox(linked, out_ttl=OUT_TTL)

    # 6) (Optional) visualize like before
    # visualize_abox_rdf(OUT_TTL, os.path.join(ROOT, "input", "llm_abox.html"))
    # visualize_tbox_abox(onto, OUT_TTL, os.path.join(ROOT, "input", "llm_tbox_abox.html"))

if __name__ == "__main__":
    if not os.path.exists(DOCX):
        print(f"⚠️ DOCX missing at {DOCX}")
    else:
        main(DOCX, subject_id="Building_X")
        print(f"Done. ABox at: {OUT_TTL}")
