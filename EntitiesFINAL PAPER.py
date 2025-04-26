import spacy
import re
from spacy.lang.en.stop_words import STOP_WORDS
import string



nlp = spacy.load("en_core_web_sm")

main_entity_keywords = {
    "Stakeholder": r"\b(manufacturer|manufacturers|stakeholder|person|organization|individual|company|firm|vendor|provider|manufacturer|consumer|customer|user)\b",  # More specific
    "Connected Device": r"\b(device|product|appliance|sensor|gadget|thing|equipment|hardware|software|system|platform|technology|iot device|connected product|smart device|wearable|implantable|mobile device|home device|router|camera|speaker|appliance|toy|vehicle|thermostat|watch|fitness tracker|security camera|smart tv|smart speaker|smart lock|medical device|health device|fitness tracker|smart home device|wearable device|automotive device|industrial device)\b",  # More specific, lowercase
    "Security Feature": r"\b(security|protection|safeguard|defense|encryption|authentication|authorization|firewall|access control|data masking|pseudonymization|logging|monitoring|vulnerability management|patch management|software update|security update|password|biometric authentication|multi-factor authentication|two-factor authentication|data encryption|end-to-end encryption|firmware security|secure boot|secure storage|data integrity|privacy protection)\b", #no changes
    "Security Risk": r"\b(risk|threat|vulnerability|attack|breach|data breach|security breach|cyberattack|malware|ransomware|phishing|denial-of-service|unauthorized access|data leak|data exposure|privacy violation|identity theft|spoofing|tampering|eavesdropping|hacking|data exfiltration)\b", #no changes
    "Law Enforcement Agency": r"\b(law enforcement agency|police|sheriff|district attorney|city attorney|county counsel|attorney general|state attorney general|fbi|department of justice|local police|state police|federal police)\b",  # More specific, lowercase
    "Federal Regulation": r"\b(federal regulation|federal law|hipaa|public law 104-191|ftc act|coppa|glba|fisma|nist standards)\b",  # More specific, lowercase
    "State Law": r"\b(state law|california law|sb-327|ab-1906)\b",  # More specific, lowercase
    "HIPAA Entity": r"\b(covered entity|health care provider|health plan|health care clearinghouse|business associate|hipaa covered entity|health care organization|medical provider|hospital|clinic|pharmacy)\b",  # More specific, lowercase
    "Attorney General": r"\b(attorney general|state attorney general)\b",  # More specific, lowercase
    "Authentication": r"\b(authentication|verification|identification|login|sign-in|sign-on|credentials|password|biometrics|multi-factor authentication|two-factor authentication|user authentication|device authentication)\b", #no changes
}

sub_entity_keywords = {
    "Third-Party Software Provider": {
        "parent": "Manufacturer",
        "keywords": r"\b(third-party software provider|third-party software providers|software vendor|software provider|software developer|software company)\b"
    },
    "Device Manufacturer": {
        "parent": "Manufacturer",
        "keywords": r"\b(device manufacturer|device manufacturers|device manufacturing|device manufactured|device made by|device produced by|device maker|device creator|device builder)\b"
    },


    "Smart Watch": {
        "parent": "Connected Device",
        "keywords": r"\b(smart watch|smart watches|smartwatch)\b"
    },
    "Smart Thermostat": {
        "parent": "Connected Device",
        "keywords": r"\b(smart thermostat|smart thermostats)\b"
    },
    "Medical Device": {
        "parent": "Connected Device",
        "keywords": r"\b(medical device|medical devices|health device|health devices|wearable medical device|implantable medical device)\b"
    },
    "Encryption": {
        "parent": "Security Feature",
        "keywords": r"\b(encryption|data encryption|end-to-end encryption|strong encryption|military-grade encryption)\b"
    },
    "Authentication": {
         "parent": "Security Feature",
         "keywords": r"\b(authentication|verification|identification|login|sign-in|sign-on|credentials|password|biometrics|multi-factor authentication|two-factor authentication|user authentication|device authentication)\b"

    },
    "Firewall": {
        "parent": "Security Feature",
        "keywords": r"\b(firewall|firewalls|network firewall|device firewall)\b"
    },
    "Data Breach": {
        "parent": "Security Risk",
        "keywords": r"\b(data breach|data breaches|security breach|security breaches|privacy breach|privacy breaches|data leak|data leaks|data exposure)\b"
    },
    "Unauthorized access": {
        "parent": "Security Risk",
        "keywords": r"\b(unauthorized access|unauthorized use|unauthorized disclosure|unauthorized modification|unauthorized viewing|unauthorized copying|unlawfulaccess|illegalaccess|impropeaccess|intrusion|hacking)\b"
    },
    "Malware": {
        "parent": "Security Risk",
        "keywords": r"\b(malware|ransomware|spyware|adware|virus|worms|trojans|keyloggers)\b"
    },
    "Attorney General": {
        "parent": "Law Enforcement Agency",
        "keywords": r"\b(attorney general|state attorney general|AG)\b"
    },
    "Local Police": {
        "parent": "Law Enforcement Agency",
        "keywords": r"\b(local police|city police|county police|police department)\b"
    },

    "HIPAA": {
        "parent": "Federal Regulation",
        "keywords": r"\b(HIPAA|Health Insurance Portability and Accountability Act)\b"
    },
    "CCPA": {
        "parent": "State Law",
        "keywords": r"\b(CCPA|California Consumer Privacy Act)\b"
    },

}

nlp = spacy.load("en_core_web_sm")


import spacy
import re
from spacy.lang.en.stop_words import STOP_WORDS
import string



def extract_entities(doc):
    entities = {}

    # 1. Extract Main Entities (Improved - Whole Word Matching, Case Consistency)
    for entity_type, regex in main_entity_keywords.items():
        matches = re.finditer(r"\b" + regex + r"\b", doc.text, re.IGNORECASE)  # Whole word matching!
        for match in matches:
            entity_text = match.group(0).strip().lower()  # Lowercase conversion
            cleaned_entity_text = " ".join(
                [word for word in entity_text.split() if word not in STOP_WORDS and word not in string.punctuation]
            ).strip()

            if cleaned_entity_text and cleaned_entity_text not in entities:
                entities[cleaned_entity_text] = {"type": entity_type}

    # 2. Extract Sub-entities and Link to Parents (Improved - Whole Word Matching, Case Consistency)
    for sub_entity_name, data in sub_entity_keywords.items():
        parent_entity = data["parent"]
        regex = data["keywords"]
        matches = re.finditer(r"\b" + regex + r"\b", doc.text, re.IGNORECASE)  # Whole word matching!
        for match in matches:
            sub_entity_text = match.group(0).strip().lower()  # Lowercase conversion
            cleaned_sub_entity_text = " ".join(
                [word for word in sub_entity_text.split() if word not in STOP_WORDS and word not in string.punctuation]
            ).strip()
            if cleaned_sub_entity_text and cleaned_sub_entity_text not in entities:
                for entity_name, entity_data in entities.items():
                    if entity_data["type"] == parent_entity:
                        if "sub_entities" not in entity_data:
                            entity_data["sub_entities"] = []
                        if cleaned_sub_entity_text not in entity_data["sub_entities"]:
                            entity_data["sub_entities"].append(cleaned_sub_entity_text)
                        break

    # 3. Remove General Entities if More Specific Sub-entities Exist (Optional - Adjust if needed)
    # entities_to_remove = [] #comment it out if you do not want to remove it
    # for entity_text, entity_data in entities.items():
    #     if "sub_entities" in entity_data and entity_data["sub_entities"]:
    #         general_type = entity_data["type"]
    #         if entity_text not in entity_data["sub_entities"]:
    #             entities_to_remove.append(entity_text)

    # for entity in entities_to_remove:
    #     if entity in entities:
    #       del entities[entity]

    return entities

def clean_text(text):
    """Clean the extracted text from the PDF."""

    # 1. Remove headers, footers, and page numbers (using regex)
    text = re.sub(r"https://leginfo\.legislature\.ca\.gov/faces/.*?$", "", text, flags=re.MULTILINE)  # Remove URLs and related lines
    text = re.sub(r"SHARE THIS:\s*X", "", text)  # remove share this
    text = re.sub(r"CHAPTER \d+", "", text)  # remove chapter info
    text = re.sub(r"Date Published:.*?\n", "", text)  # remove date published
    text = re.sub(r"Senate Bill No. \d+", "", text)  # remove senate bill no
    text = re.sub(r"\[ Approved by Governor.*?\]", "", text)  # remove approval info
    text = re.sub(r"LEGISLATIVE COUNSEL'S DIGEST", "", text)  # remove legislative counsel's digest
    text = re.sub(r"SEC\. \d+\.", "", text)  # remove section numbers
    text = re.sub(r"ASSEMBLY BILL \d+", "", text)  # remove assembly bill no
    text = re.sub(r"Regular Session is also\s*enacted and becomes effective\.", "", text)  # remove regular session info
    text = re.sub(r"California\s*LEGISLATIVE INFORMATION\s*Home\s*Bill Information\s*California Law Publications\s*Other Resources\s*My Subscriptions\s*My Favorites", "", text)  # remove header

    # 2. Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()  # Replace multiple spaces with single space

    # 3. Handle special characters (if needed) - be careful not to remove important legal symbols
    # Example: text = text.replace("’", "'")  # Replace curly apostrophe with straight apostrophe

    return text  # The indentation was missing here as well

nlp = spacy.load("en_core_web_sm")
def extract_relationships(doc, entities):
    relationships = []

    for sent in doc.sents:
        subject = None
        object = None

        for token in sent:
            if token.dep_ == "nsubjpass" and token.head.text == "equip":
                subject_candidate = token.text
                of_token = None
                for child in token.children:
                    if child.dep_ == "prep" and child.text == "of":
                        of_token = child
                        break
                if of_token:
                    for child in of_token.children:
                        if child.dep_ == "det" and child.text == "a":
                            for child2 in of_token.children:
                                if child2.dep_ == "compound":
                                    subject = subject_candidate + " " + child2.text + " " + of_token.text + " " + child.text
                                    break
                            if subject is None:
                                subject = subject_candidate + " " + of_token.text + " " + child.text
                else:
                    subject = subject_candidate

                break

        for token in sent:
            if token.dep_ == "dobj" and token.head.text == "equip":
                object_candidate = token.text
                for child in token.children:
                    if child.dep_ == "amod":
                        object = child.text + " " + object_candidate
                        break
                if object is None:
                    object = object_candidate
                break

        if subject and object:  # Only proceed if both subject and object are found
            cleaned_subject = clean_text(subject)  # Clean *after* full subject is identified
            cleaned_object = clean_text(object)  # Clean *after* full object is identified

            found_subject = False
            for entity_text, entity_data in entities.items():
                cleaned_entity_text = clean_text(entity_text)  # Clean the entity text from the dictionary
                if cleaned_subject in cleaned_entity_text:  # Compare cleaned text with cleaned text
                    found_subject = True
                    subject = entity_text  # Use the original entity text
                    break

            found_object = False
            for entity_text, entity_data in entities.items():
                cleaned_entity_text = clean_text(entity_text)  # Clean the entity text from the dictionary
                if cleaned_object in cleaned_entity_text:  # Compare cleaned text with cleaned text
                    found_object = True
                    object = entity_text  # Use the original entity text
                    break

            if found_subject and found_object:
                relationships.append({"subject": subject, "relation": "hasSecurityFeatures", "object": object})

    return relationships
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

pdf_path = "/content/Califorina_law_SB-327.pdf"
text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_text(text)
doc = nlp(cleaned_text)
entities = extract_entities(doc)
relationships = extract_relationships(doc, entities)

print("Entities:", entities)
print("Relationships:", relationships)
