# ontology/ontology_builder.py
import os
from owlready2 import *

BASE_IRI = "http://example.org/aec.owl"
OUT_PATH = os.path.join(os.path.dirname(__file__), "general_aec.owl")

def build_and_save():
    onto = get_ontology(BASE_IRI)

    with onto:
        # ----- Upper -----
        class AEC(Thing): pass
        class State(AEC): pass
        class Phase(AEC): pass
        class Discipline(AEC): pass
        class Infrastructure(AEC): pass
        class Specification(AEC): pass
        class Risk(AEC): pass
        class SafetyMeasure(AEC): pass
        class SafetyInfrastructure(SafetyMeasure): pass

        # States & phases
        class Normal(State): pass
        class Emergency(State): pass
        class Design(Phase): pass
        class Construction(Phase): pass
        class Operation(Phase): pass
        class Refurbishment(Phase): pass
        class Removal(Phase): pass

        # Disciplines
        class Architecture(Discipline): pass
        class Engineering(Discipline): pass
        class ConstructionDiscipline(Discipline): pass

        # Infrastructure
        class BuildingInfrastructure(Infrastructure): pass
        class HighriseBuilding(BuildingInfrastructure): pass
        class House(BuildingInfrastructure): pass
        class TechnicalBuilding(BuildingInfrastructure): pass
        class Factory(BuildingInfrastructure): pass

        class TrafficInfrastructure(Infrastructure): pass
        class Tunnel(TrafficInfrastructure): pass
        class Viaduct(TrafficInfrastructure): pass
        class OpenRoad(TrafficInfrastructure): pass

        # Specifications / docs
        class BuildingSpecification(Specification): pass
        class TunnelSpecification(Specification): pass
        class TunnelStructureSpec(TunnelSpecification): pass
        class TunnelSafetyDoc(TunnelSpecification): pass
        class TunnelGeologyDoc(TunnelSpecification): pass

        # Risks
        class FireRisk(Risk): pass
        class AccidentRisk(Risk): pass
        class RiskLevel(Risk): pass

        # Fire safety measures
        class FireSafetyMeasure(SafetyMeasure): pass
        class FireDetectionSystem(FireSafetyMeasure): pass
        class FireExtinguisher(FireSafetyMeasure): pass
        class Hydrant(FireSafetyMeasure): pass
        class Sprinkler(FireSafetyMeasure): pass
        class EvacuationPath(SafetyInfrastructure): pass
        class InterventionPath(SafetyInfrastructure): pass

        # Object properties
        class hasSpecification(Infrastructure >> Specification): pass
        class inPhase(Infrastructure >> Phase): pass
        class hasSafetyMeasure(Infrastructure >> SafetyMeasure): pass
        class hasSafetyInfrastructure(Infrastructure >> SafetyInfrastructure): pass
        class hasRisk(Infrastructure >> Risk): pass
        class hasRiskLevel(FireRisk >> RiskLevel): pass
        class mitigates(SafetyMeasure >> FireRisk): pass
        class consistsOf(SafetyInfrastructure >> SafetyMeasure): pass

        # Data properties
        class tunnelLength(TunnelStructureSpec >> float): pass
        class numberOfCrossPassages(TunnelStructureSpec >> int): pass
        class pressure(Hydrant >> float): pass
        class hasWeight(FireExtinguisher >> float): pass
        class riskScore(RiskLevel >> float): pass
        class evacPathWidth(EvacuationPath >> float): pass
        class intervPathWidth(InterventionPath >> float): pass

        # SKOS labels (minimal demo)
        skos = onto.get_namespace("http://www.w3.org/2004/02/skos/core#")
        class prefLabel(AnnotationProperty): namespace = skos
        class altLabel(AnnotationProperty):  namespace = skos
        from owlready2 import locstr
        Tunnel.prefLabel.append(locstr("Tunnel", "en"))
        HighriseBuilding.prefLabel.append(locstr("High-rise building", "en"))
        Hydrant.altLabel.append(locstr("fire plug", "en"))
        FireExtinguisher.altLabel.append(locstr("portable extinguisher", "en"))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    onto.save(file=OUT_PATH, format="rdfxml")
    print(f"✅ Ontology saved to {OUT_PATH}")

if __name__ == "__main__":
    build_and_save()
