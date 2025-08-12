# pipeline/ontology_vocab.py
from owlready2 import get_ontology, ThingClass, AnnotationProperty
from rdflib import Namespace

def load_ontology(owl_path: str):
    return get_ontology(f"file://{owl_path}").load()

def extract_vocab(onto):
    """
    Returns:
      classes:   list of {"iri","name","labels":[...]}
      obj_props: list of {"iri","name","labels":[...]}
      data_props:list of {"iri","name","labels":[...]}
    """
    # Try to access SKOS annotation properties if present
    skos = onto.get_namespace("http://www.w3.org/2004/02/skos/core#")
    prefLabel = getattr(skos, "prefLabel", None)
    altLabel  = getattr(skos, "altLabel",  None)

    def labels_for(ent):
        labs = set()
        # owlready2 rdfs:label:
        for v in getattr(ent, "label", []):
            labs.add(str(v))
        # SKOS preferred / alt labels if bound
        if isinstance(prefLabel, AnnotationProperty):
            for v in ent.get_property_value(prefLabel) or []:
                labs.add(str(v))
        if isinstance(altLabel, AnnotationProperty):
            for v in ent.get_property_value(altLabel) or []:
                labs.add(str(v))
        # Always include the Python name
        labs.add(ent.name)
        return sorted(labs)

    classes, obj_props, data_props = [], [], []

    for c in onto.classes():
        classes.append({
            "iri": c.iri, "name": c.name,
            "labels": labels_for(c)
        })

    for p in onto.object_properties():
        obj_props.append({
            "iri": p.iri, "name": p.name,
            "labels": labels_for(p)
        })

    for p in onto.data_properties():
        data_props.append({
            "iri": p.iri, "name": p.name,
            "labels": labels_for(p)
        })

    return classes, obj_props, data_props
