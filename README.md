# Semantic_Tech
"""
├── ontology/
│   ├── ontology_builder.py        # builds/updates the GENERAL ontology (TBox)
│   └── general_aec.owl            # saved here after you run ontology_builder.py
├── abox/
│   ├── instances.ttl              # ABox output (auto-built from docs)
│   └── fire_safety_shapes.ttl     # SHACL shapes (optional)
├── pipeline/
│   ├── __init__.py
│   ├── gazetteer.py               # labels/synonyms → canonical ontology terms
│   ├── rules_ie.py                # fast regex/heuristic extraction (no API needed)
│   ├── llm_ie.py                  # optional LLM extraction (uses OPENAI_API_KEY if present)
│   ├── linker.py                  # normalizes text → ontology IRIs (classes/properties)
│   ├── abox_writer.py             # writes rdflib graph → abox/instances.ttl
│   └── viz.py                     # pyvis visualizations (ABox-only & TBox+ABox)
└── Text_data_retreival/
    └── Text_data_retreival.py     # main entry point (reads .docx, runs pipeline, validates, visualizes)


.docx
  │
  ├─ 1) Ingest & structure
  │     • extract plain text + section headers + tables + captions
  │     • sentence split (spaCy), keep offsets to original text
  │
  ├─ 2) Document/domain detection
  │     • classify the asset/domain (Tunnel, Building, …) using gazetteer cues + heuristics
  │     • create/choose the root instance ID (e.g., Tunnel_X) for the ABox
  │
  ├─ 3) Coreference & normalization (LLM-assisted where helpful)
  │     • resolve pronouns/abbreviations (“it”, “this”, “CP”) across sections
  │     • normalize numbers/units (m, kg, bar) + expand acronyms
  │
  ├─ 4) Ontology gazetteer match (SKOS + synonyms + fuzzy)
  │     • generate candidates for classes/properties from labels, altLabels, synonyms
  │     • detect known data fields (length, cross passages, hydrant pressure, …)
  │
  ├─ 5) Dual extraction (run in parallel)
  │     A) Rule/regex extractor (high precision, also reads tables)
  │     B) LLM triple extractor (high recall; prompt constrained by your schema)
  │
  ├─ 6) Fusion & disambiguation  ← NEW (glue step)
  │     • merge A & B results; deduplicate; assign confidence + provenance (rule vs LLM)
  │     • map surface predicates to TBox properties; map entities to classes/instances
  │     • choose best candidate when conflicts; keep alternates with lower confidence
  │
  ├─ 7) Validation
  │     • TBox check: is every predicate a known object/data property?
  │     • SHACL validate (ranges, minCount, numeric bounds)
  │     • unit & value sanity checks (e.g., pressure > 0)
  │
  ├─ 8) ABox writer (.ttl)
  │     • materialize instances, object/data triples (with prefixes)
  │     • optionally add provenance (named graphs or reification)
  │
  ├─ 9) Post-process & enrich
  │     • link out (Wikidata IDs) where unambiguous
  │     • compute derived facts (rules/SWRL/py rules), optional reasoning
  │
  └─ 10) Visualize & report
        • pyvis: ABox; TBox+overlay
        • extraction report: what matched, conflicts, drops, and why
"""