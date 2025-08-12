# pipeline/gazetteer.py
import unicodedata
from owlready2 import get_ontology, ThingClass




def _norm(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKC", s)
    return " ".join(s.split())

def build_gazetteer(onto_path: str):
    """
    Build simple maps for label→class-name and label→property-name using
    ontology names, rdfs:label and SKOS (prefLabel/altLabel).
    """
    onto = get_ontology(onto_path).load()
    skos = onto.get_namespace("http://www.w3.org/2004/02/skos/core#")

    label_to_class = {}
    label_to_prop  = {}

    # classes
    for cls in onto.classes():
        names = set([cls.name])
        # rdfs:label (Owlready2 attribute 'label')
        for lab in getattr(cls, "label", []):
            names.add(str(lab))
        # SKOS
        for lab in getattr(cls, "prefLabel", []):
            names.add(str(lab))
        for lab in getattr(cls, "altLabel", []):
            names.add(str(lab))

        for n in names:
            label_to_class[_norm(n)] = cls.name

    # properties
    for prop in list(onto.object_properties()) + list(onto.data_properties()):
        names = set([prop.name])
        for lab in getattr(prop, "label", []):
            names.add(str(lab))
        for n in names:
            label_to_prop[_norm(n)] = prop.name

    return label_to_class, label_to_prop
