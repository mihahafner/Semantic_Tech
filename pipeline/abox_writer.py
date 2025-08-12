# pipeline/abox_writer.py
import os
from rdflib import Graph, Namespace, RDF, Literal, XSD
from owlready2 import get_ontology, ThingClass, ObjectPropertyClass, DataPropertyClass

EX_IRI = "http://example.org/aec#"



# pipeline/abox_writer.py
from rdflib import Graph, Namespace, RDF, Literal, XSD, URIRef

EX = Namespace("http://example.org/aec#")

def write_abox(linked_triples, out_ttl="Tests/extracted_abox.ttl"):
    """
    linked_triples: list of dicts
      {
        "subject":{"name":"Building_X","class":"BuildingInfrastructure"},
        "predicate":{"name":"hasRiskLevel","kind":"object"|"data"},
        "object":{"name":"RiskLevel_BX","class":"RiskLevel"}  # if object prop
        # or
        "object_literal":{"value": 25.0, "datatype":"xsd:float"}  # if data prop
      }
    """
    g = Graph(); g.bind("ex", EX)

    # First, type every subject/object that has a class
    for t in linked_triples:
        s = t["subject"]
        if s.get("class"):
            g.add((EX[s["name"]], RDF.type, EX[s["class"]]))
        if t["predicate"]["kind"] == "object":
            o = t["object"]
            if o.get("class"):
                g.add((EX[o["name"]], RDF.type, EX[o["class"]]))

    # Then add properties
    for t in linked_triples:
        s_iri = EX[t["subject"]["name"]]
        p_iri = EX[t["predicate"]["name"]]
        if t["predicate"]["kind"] == "object":
            o_iri = EX[t["object"]["name"]]
            g.add((s_iri, p_iri, o_iri))
        else:
            lit = t["object_literal"]
            val = lit["value"]
            if isinstance(val, float):
                dt = XSD.float
            elif isinstance(val, int):
                dt = XSD.integer
            else:
                # allow passing explicit "datatype" string if you want
                dt = XSD.string
            g.add((s_iri, p_iri, Literal(val, datatype=dt)))

    g.serialize(out_ttl, format="turtle")
    print(f"✅ ABox written to {out_ttl}")
    return g

"""
def write_abox(onto_path: str, out_path: str, facts, datas, tunnel_id: str):
    onto = get_ontology(onto_path).load()
    EX = Namespace(EX_IRI)

    g = Graph()
    g.bind("ex", EX)

    # Minimal typing based on predicates used
    used_nodes = set()
    for s, p, o in facts:
        used_nodes.add(s)
        used_nodes.add(o)
    for s, p, v in datas:
        used_nodes.add(s)

    # naive typing (adjust as needed)
    # e.g., ensure the main subject is a Tunnel, sub-nodes typed by name pattern
    g.add((EX[tunnel_id], RDF.type, EX["Tunnel"]))

    for n in used_nodes:
        if n.endswith("_Spec"):
            g.add((EX[n], RDF.type, EX["TunnelStructureSpec"]))
        if n.endswith("_Hydrant"):
            g.add((EX[n], RDF.type, EX["Hydrant"]))
        if n.endswith("_Extinguisher"):
            g.add((EX[n], RDF.type, EX["FireExtinguisher"]))

    # emit object triples
    for s, p, o in facts:
        g.add((EX[s], EX[p], EX[o]))

    # emit data triples
    for s, p, v in datas:
        if isinstance(v, float):
            lit = Literal(v, datatype=XSD.float)
        elif isinstance(v, int):
            lit = Literal(v, datatype=XSD.integer)
        else:
            lit = Literal(str(v))
        g.add((EX[s], EX[p], lit))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    g.serialize(out_path, format="turtle")
    print(f"✅ ABox saved to {out_path}")
    return out_path
"""
