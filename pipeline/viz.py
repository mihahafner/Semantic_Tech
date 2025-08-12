# pipeline/viz.py
from pyvis.network import Network
from rdflib import Graph, URIRef, RDF
from owlready2 import get_ontology, ThingClass

def _enable_controls(net: Network):
    if isinstance(net.options, dict):
        net.options["configure"] = {"enabled": True}
    else:
        net.show_buttons()

def visualize_abox(abox_path: str, html_out: str):
    g = Graph(); g.parse(abox_path, format="turtle")
    net = Network(height="800px", width="100%", directed=True, bgcolor="white", font_color="black")
    net.set_options("""{
      "physics": {"solver": "forceAtlas2Based", "stabilization": {"iterations": 300}},
      "nodes": {"shape": "dot", "font": {"size": 17}},
      "edges": {"font": {"size": 14, "align": "middle"}, "arrows": {"to": {"enabled": true}}}
    }""")
    _enable_controls(net)

    added = set()
    def add_node(nid, label, color):
        if nid not in added:
            net.add_node(nid, label=label, color=color); added.add(nid)

    for s, p, o in g:
        s_lbl = s.split("#")[-1]
        pred  = p.split("#")[-1]
        if isinstance(o, URIRef):
            o_lbl = o.split("#")[-1]
            add_node(s_lbl, s_lbl, "mediumseagreen")
            add_node(o_lbl, o_lbl, "mediumseagreen")
            net.add_edge(s_lbl, o_lbl, label=pred)
        else:
            lit_id = f"lit::{s_lbl}::{pred}::{o}"
            add_node(s_lbl, s_lbl, "mediumseagreen")
            add_node(lit_id, str(o), "lightgray")
            net.add_edge(s_lbl, lit_id, label=pred)

    net.add_node("Legend", label="Legend:\nGreen=Instance\nGray=Literal", shape="box", color="#f0f0f0")
    net.write_html(html_out)
    print(f"✅ ABox graph saved to {html_out}")

def visualize_tbox_abox(onto_path: str, abox_path: str, html_out: str):
    onto = get_ontology(onto_path).load()
    g = Graph(); g.parse(abox_path, format="turtle")

    net = Network(height="800px", width="100%", directed=True)
    net.set_options("""{
      "physics": {"solver": "forceAtlas2Based", "stabilization": {"iterations": 300}},
      "nodes": {"shape": "dot", "font": {"size": 17}},
      "edges": {"font": {"size": 14, "align": "middle"}, "arrows": {"to": {"enabled": true}}}
    }""")
    _enable_controls(net)

    added = set()
    def add_node(nid, label, color):
        if nid not in added:
            net.add_node(nid, label=label, color=color); added.add(nid)

    # TBox (classes)
    for cls in onto.classes():
        add_node(cls.name, cls.name, "lightblue")
        for parent in [p for p in cls.is_a if isinstance(p, ThingClass)]:
            add_node(parent.name, parent.name, "lightblue")
            net.add_edge(parent.name, cls.name, label="is_a", color="#8ec7ff")

    # ABox overlay
    for s, p, o in g:
        s_lbl = s.split("#")[-1]
        pred  = p.split("#")[-1]
        if isinstance(o, URIRef):
            o_lbl = o.split("#")[-1]
            add_node(s_lbl, s_lbl, "mediumseagreen")
            if pred == "type" or pred == "rdf:type":
                add_node(o_lbl, o_lbl, "lightblue")
                net.add_edge(s_lbl, o_lbl, label="rdf:type", color="#8ec7ff")
            else:
                add_node(o_lbl, o_lbl, "mediumseagreen")
                net.add_edge(s_lbl, o_lbl, label=pred, color="#999999")
        else:
            lit_id = f"lit::{s_lbl}::{pred}::{o}"
            add_node(s_lbl, s_lbl, "mediumseagreen")
            add_node(lit_id, str(o), "lightgray")
            net.add_edge(s_lbl, lit_id, label=pred, color="#999999")

    net.add_node("Legend",
                 label="Legend:\nBlue=Class (TBox)\nGreen=Instance (ABox)\nGray=Literal\nis_a (blue), others (gray/orange)",
                 shape="box", color="#f0f0f0")
    net.write_html(html_out)
    print(f"✅ TBox+ABox graph saved to {html_out}")
