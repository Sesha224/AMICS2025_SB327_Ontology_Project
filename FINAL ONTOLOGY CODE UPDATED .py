import spacy
import json
import PyPDF2
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS
import re
from spacy.lang.en.stop_words import STOP_WORDS
import string

nlp = spacy.load("en_core_web_lg") #using larger model

main_entity_keywords = {
    "Stakeholder": r"\b(stakeholder|person|organization|individual|company|firm|vendor|provider)\b",
    "Connected Device": r"\b(device|product|appliance|sensor|gadget|thing|equipment|hardware|software|system|platform|technology|iot device|connected product|smart device|wearable|implantable|mobile device|home device|router|camera|speaker|appliance|toy|vehicle|thermostat|watch|fitness tracker|security camera|smart tv|smart speaker|smart lock|medical device|health device|fitness tracker|smart home device|wearable device|automotive device|industrial device)\b",
    "Security Feature": r"\b(security|protection|safeguard|defense|encryption|authorization|firewall|access control|data masking|pseudonymization|logging|monitoring|vulnerability management|patch management|software update|security update|biometric authentication|multi-factor authentication|two-factor authentication|data encryption|end-to-end encryption|firmware security|secure boot|secure storage|data integrity|privacy protection)\b",
    "Security Risk": r"\b(risk|threat|vulnerability|attack|breach|data breach|security breach|cyberattack|malware|ransomware|phishing|denial-of-service|unauthorized access|data leak|data exposure|privacy violation|identity theft|spoofing|tampering|eavesdropping|hacking|data exfiltration)\b",
    "Law Enforcement Agency": r"\b(law enforcement agency|police|sheriff|fbi|department of justice|local police|state police|federal police)\b",
    "Federal Regulation": r"\b(federal regulation|federal law|hipaa|public law 104-191|ftc act|coppa|glba|fisma|nist standards)\b",
    "State Law": r"\b(state law|california law|sb-327|ab-1906)\b",
    "HIPAA Entity": r"\b(covered entity|health care provider|health plan|health care clearinghouse|business associate|hipaa covered entity|health care organization|medical provider|hospital|clinic|pharmacy)\b",
    "Attorney General": r"\b(attorney general|state attorney general)\b",
    "Unauthorized access": r"\b(unauthorized access|unauthorized use|unauthorized disclosure|unauthorized modification|unauthorized viewing|unauthorized copying|unlawfulaccess|illegalaccess|impropeaccess|intrusion|hacking)\b",
    "Consumer": r"\b(consumer)\b",
    "Manufacturer": r"\b(manufacturer)\b"
}

sub_entity_keywords = {
    "Third-Party Software Provider": {"parent": "Manufacturer", "keywords": r"\b(third-party software provider|third-party software providers|software vendor|software provider|software developer|software company)\b"},
    "Device Manufacturer": {"parent": "Manufacturer", "keywords": r"\b(device manufacturer|device manufacturers|device manufacturing|device manufactured|device made by|device produced by|device maker|device creator|device builder)\b"},
    "Smart Watch": {"parent": "Connected Device", "keywords": r"\b(smart watch|smart watches|smartwatch)\b"},
    "Smart Thermostat": {"parent": "Connected Device", "keywords": r"\b(smart thermostat|smart thermostats)\b"},
    "Medical Device": {"parent": "Connected Device", "keywords": r"\b(medical device|medical devices|health device|health devices|wearable medical device|implantable medical device)\b"},
    "Encryption": {"parent": "Security Feature", "keywords": r"\b(encryption|data encryption|end-to-end encryption|strong encryption|military-grade encryption)\b"},
    "Authentication": {"parent": "Security Feature", "keywords": r"\b(authentication|verification|identification|login|sign-in|sign-on|credentials|password|biometrics|multi-factor authentication|two-factor authentication|user authentication|device authentication)\b"},
    "Firewall": {"parent": "Security Feature", "keywords": r"\b(firewall|firewalls|network firewall|device firewall)\b"},
    "Data Breach": {"parent": "Security Risk", "keywords": r"\b(data breach|data breaches|security breach|security breaches|privacy breach|privacy breaches|data leak|data leaks|data exposure)\b"},
    "Unauthorized access": {"parent": "Security Risk", "keywords": r"\b(unauthorized access|unauthorized use|unauthorized disclosure|unauthorized modification|unauthorized viewing|unauthorized copying|unlawfulaccess|illegalaccess|impropeaccess|intrusion|hacking)\b"},
    "Malware": {"parent": "Security Risk", "keywords": r"\b(malware|ransomware|spyware|adware|virus|worms|trojans|keyloggers)\b"},
    "Attorney General": {"parent": "Law Enforcement Agency", "keywords": r"\b(attorney general|state attorney general|AG)\b"},
    "Local Police": {"parent": "Law Enforcement Agency", "keywords": r"\b(local police|city police|county police|police department)\b"},
    "HIPAA": {"parent": "Federal Regulation", "keywords": r"\b(HIPAA|Health Insurance Portability and Accountability Act)\b"},
    "CCPA": {"parent": "State Law", "keywords": r"\b(CCPA|California Consumer Privacy Act)\b"},
}

def extract_entities(doc):
    entities = {}

    # Main entities extraction
    for entity_type, regex in main_entity_keywords.items():
        matches = re.finditer(r"\b" + regex + r"\b", doc.text, re.IGNORECASE)
        for match in matches:
            entity_text = match.group(0).strip().lower()
            cleaned_entity_text = " ".join([word for word in entity_text.split() if word not in STOP_WORDS and word not in string.punctuation]).strip()
            if cleaned_entity_text and cleaned_entity_text not in entities:
                entities[cleaned_entity_text] = {"type": entity_type}

    # Sub entities extraction
    for sub_entity_name, data in sub_entity_keywords.items():
        parent_entity = data["parent"]
        regex = data["keywords"]
        matches = re.finditer(r"\b" + regex + r"\b", doc.text, re.IGNORECASE)
        for match in matches:
            sub_entity_text = match.group(0).strip().lower()
            cleaned_sub_entity_text = " ".join([word for word in sub_entity_text.split() if word not in STOP_WORDS and word not in string.punctuation]).strip()
            if cleaned_sub_entity_text and cleaned_sub_entity_text not in entities:
                for entity_name, entity_data in entities.items():
                    if entity_data["type"] == parent_entity:
                        if "sub_entities" not in entity_data:
                            entity_data["sub_entities"] = []
                        if cleaned_sub_entity_text not in entity_data["sub_entities"]:
                            entity_data["sub_entities"].append(cleaned_sub_entity_text)
                        break

    # Instance extraction using spaCy's NER
    for ent in doc.ents:
        if ent.label_ == "ORG":  # Organizations as instances of Stakeholder
            entity_text = ent.text.strip().lower()
            if entity_text and entity_text not in entities:
                entities[entity_text] = {"type": "Stakeholder", "instance": True}

    print(f"Extracted Entities: {entities}")
    return entities

def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    return text

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def load_deontic_phrases(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    obligations = data.get("obligations", [])
    permissions = data.get("permissions", [])
    prohibitions = data.get("prohibitions", [])
    return obligations, permissions, prohibitions

def find_subject_action_object(token):
    subject = None
    action = None
    obj = None
    action_token = None

    if token.pos_ == "VERB":
        action_token = token
    else:
        for child in token.children:
            if child.pos_ == "VERB":
                action_token = child
                break

    if action_token:
        print(f"Action token: {action_token.text}")
        for child in action_token.children:
            print(f"Child: {child.text}, Dep: {child.dep_}")
            if child.dep_ in ["nsubj", "nsubjpass"]:
                subject = child.text
                action = action_token.lemma_
                break
        for child in action_token.children:
            print(f"Child: {child.text}, Dep: {child.dep_}")
            if child.dep_ in ["dobj", "pobj"]:
                obj = " ".join([tok.text for tok in child.subtree])
                break

    return subject, action, obj

def find_phrase_in_text(phrase, text):
    phrase_tokens = phrase.lower().split()
    doc = nlp(text)
    text_tokens = [token.text.lower() for token in doc]
    indices = []
    for i in range(len(text_tokens) - len(phrase_tokens) + 1):
        if text_tokens[i:i+len(phrase_tokens)] == phrase_tokens:
            indices.append(i)
    return indices

def extract_deontic_relations_phrase_centric(doc, obligations, permissions, prohibitions):
    relations = []

    for phrase in obligations:
        indices = find_phrase_in_text(phrase, doc.text)
        print(f"Checking phrase: {phrase}, found at indices: {indices}")
        for index in indices:
            token = doc[index]
            subject, action, obj = find_subject_action_object(token.head)
            if subject and action and obj:
                print(f"Found obligation: Subject={subject}, Action={action}, Object={obj}")
                relations.append({"type": "obligation", "subject": subject, "action": action, "object": obj})

    for phrase in permissions:
        indices = find_phrase_in_text(phrase, doc.text)
        print(f"Checking phrase: {phrase}, found at indices: {indices}")
        for index in indices:
            token = doc[index]
            subject, action, obj = find_subject_action_object(token.head)
            if subject and action and obj:
                print(f"Found permissions: Subject={subject}, Action={action}, Object={obj}")
                relations.append({"type": "permission", "subject": subject, "action": action, "object": obj})

    for phrase in prohibitions:
        indices = find_phrase_in_text(phrase, doc.text)
        print(f"Checking phrase: {phrase}, found at indices: {indices}")
        for index in indices:
            token = doc[index]
            subject, action, obj = find_subject_action_object(token.head)
            if subject and action and obj:
                print(f"Found prohibitions: Subject={subject}, Action={action}, Object={obj}")
                relations.append({"type": "prohibition", "subject": subject, "action": action, "object": obj})

    return relations

def generate_ontology(entities, extracted_relations, hardcoded_relations):
    g = Graph()
    SB = Namespace("http://example.org/sb327/")
    g.bind("sb", SB)
    OWL = Namespace("http://www.w3.org/2002/07/owl#")

    # Define Object Properties and declare them as owl:ObjectProperty
    equipsWith = SB.equipsWith
    g.add((equipsWith, RDF.type, OWL.ObjectProperty))
    manufacturer_uri = SB["manufacturer"]
    security_feature_uri = SB["security_feature"]
    g.add((equipsWith, RDFS.domain, manufacturer_uri))
    g.add((equipsWith, RDFS.range, security_feature_uri))

    hasAuthority = SB.hasAuthority
    g.add((hasAuthority, RDF.type, OWL.ObjectProperty))
    stakeholder_uri = SB["stakeholder"]
    g.add((hasAuthority, RDFS.domain, stakeholder_uri))
    g.add((hasAuthority, RDFS.range, security_feature_uri))

    requires = SB.requires
    g.add((requires, RDF.type, OWL.ObjectProperty))
    g.add((requires, RDFS.domain, stakeholder_uri))
    g.add((requires, RDFS.range, security_feature_uri))

    hasAuthenticationRequirement = SB.hasAuthenticationRequirement
    g.add((hasAuthenticationRequirement, RDF.type, OWL.ObjectProperty))
    connected_device_uri = SB["connected_device"]
    authentication_uri = SB["authentication"]
    g.add((hasAuthenticationRequirement, RDFS.domain, connected_device_uri))
    g.add((hasAuthenticationRequirement, RDFS.range, authentication_uri))

    isProhibitedFrom = SB.isProhibitedFrom
    g.add((isProhibitedFrom, RDF.type, OWL.ObjectProperty))
    g.add((isProhibitedFrom, RDFS.domain, manufacturer_uri))
    g.add((isProhibitedFrom, RDFS.range, connected_device_uri))

    mayInstitute = SB.mayInstitute
    g.add((mayInstitute, RDF.type, OWL.ObjectProperty))
    consumer_uri = SB["consumer"]
    g.add((mayInstitute, RDFS.domain, consumer_uri))
    g.add((mayInstitute, RDFS.range, stakeholder_uri))

    for entity, label_dict in entities.items():
        entity_uri = SB[entity.replace(" ", "_")]
        if "instance" in label_dict:
            class_type = label_dict["type"]
            class_uri = SB[class_type.replace(" ", "_")]
            g.add((entity_uri, RDF.type, class_uri))
        else:
            g.add((entity_uri, RDF.type, RDFS.Class))

        # Add Subclass Relationships
        if entity == "manufacturer" or entity == "consumer":
            stakeholder_uri = SB["stakeholder"]
            print(f"Creating subclass for: {entity}, parent: stakeholder")
            g.add((entity_uri, RDFS.subClassOf, stakeholder_uri))
        elif entity == "city_attorney" or entity == "district_attorney" or entity == "county_counsel":
            law_enforcement_uri = SB["law_enforcement_agency"]
            print(f"Creating subclass for: {entity}, parent: law_enforcement_agency")
            g.add((entity_uri, RDFS.subClassOf, law_enforcement_uri))
        elif entity == "security" or entity == "authentication":
            security_feature_uri = SB["security_feature"]
            print(f"Creating subclass for: {entity}, parent: security_feature")
            g.add((entity_uri, RDFS.subClassOf, security_feature_uri))

    for relation in extracted_relations:
        subject = relation['subject']
        action = relation['action']
        obj = relation['object']

        subject_uri = SB[subject.replace(" ", "_")]
        object_uri = SB[obj.replace(" ", "_")]

        if action == 'equip':
            g.add((subject_uri, equipsWith, object_uri))
        elif action == 'have':
            g.add((subject_uri, hasAuthority, object_uri))
        elif action == 'require':
            g.add((subject_uri, requires, object_uri))

    for relation in hardcoded_relations:
        subject = relation['subject']
        action = relation['action']
        obj = relation['object']

        subject_uri = SB[subject.replace(" ", "_")]
        object_uri = SB[obj.replace(" ", "_")]

        if action == 'equipsWith':
            g.add((subject_uri, equipsWith, object_uri))
        elif action == 'hasAuthenticationRequirement':
            g.add((subject_uri, hasAuthenticationRequirement, object_uri))
        elif action == 'isProhibitedFrom':
            g.add((subject_uri, isProhibitedFrom, object_uri))
        elif action == 'mayInstitute':
            g.add((subject_uri, mayInstitute, object_uri))

    return g.serialize(format='xml')

if __name__ == "__main__":
    pdf_path = "/content/Califorina_law_SB-327.pdf"
    deontic_phrases_path = "/content/deontic_phrases.json"

    text = extract_text_from_pdf(pdf_path)
    doc = nlp(text)

    entities = extract_entities(doc)
    obligations, permissions, prohibitions = load_deontic_phrases(deontic_phrases_path)
    extracted_relations = extract_deontic_relations_phrase_centric(doc, obligations, permissions, prohibitions)

    hardcoded_relations = [
        {"subject": "manufacturer", "action": "equipsWith", "object": "security"},
        {"subject": "device", "action": "hasAuthenticationRequirement", "object": "authentication"},
        {"subject": "manufacturer", "action": "isProhibitedFrom", "object": "device"},
        {"subject": "consumer", "action": "mayInstitute", "object": "stakeholder"}
    ]

    ontology_data = generate_ontology(entities, extracted_relations, hardcoded_relations)

    with open("sb327_full_ontology.owl", "w", encoding="utf-8") as f:
        f.write(ontology_data)
