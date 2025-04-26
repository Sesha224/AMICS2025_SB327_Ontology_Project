This project accompanies our research paper:
"Bridging AI and Legal Compliance: Knowledge Graphs for IoT Cybersecurity Regulations,"
accepted at the Thirty-First Americas Conference on Information Systems (AMCIS 2025).

We propose a structured methodology to extract legal knowledge from the California Senate Bill 327 (SB-327) cybersecurity regulation using:

Natural Language Processing (NLP)
Ontology engineering
Deontic logic principles

The extracted legal entities, obligations, permissions, and prohibitions are structured into an OWL/RDF Ontology and visualized as a Knowledge Graph, enabling manufacturers and stakeholders to easily query and verify compliance requirements for IoT devices.


Files Included are:
EntitiesFINAL_PAPER.py – Code for extracting legal entities and relationships using pattern matching and NLP (spaCy).

FINAL_ONTOLOGY_CODE_UPDATED.py – Code for constructing the ontology and knowledge graph structure from the extracted data.

Requirements:
Python 3.8+
spaCy
rdflib
owlready2

Install all the dependencies using : pip install spacy rdflib owlready2

How to Run
Run EntitiesFINAL_PAPER.py to extract legal entities and relationships.
Run FINAL_ONTOLOGY_CODE_UPDATED.py to build the ontology and generate the knowledge graph.

CITATION:
If you use this code or dataset, please cite our AMCIS 2025 paper:
"Bridging AI and Legal Compliance: Knowledge Graphs for IoT Cybersecurity Regulations," AMCIS 2025.
(Full citation details will be updated once published.)



