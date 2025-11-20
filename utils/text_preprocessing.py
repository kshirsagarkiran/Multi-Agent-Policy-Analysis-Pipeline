import spacy
import re

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spacy model...")
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def tokenize(text):
    doc = nlp(text)
    return [token.text for token in doc]

def lemmatize(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc]

def pos_tag(text):
    doc = nlp(text)
    return [(token.text, token.pos_) for token in doc]

def ner(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def redact_pii(text):
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[REDACTED_PHONE]', text)
    return text

def preprocess_text(text):
    tokens = tokenize(text)
    lemmas = lemmatize(text)
    pos_tags = pos_tag(text)
    entities = ner(text)
    redacted_text = redact_pii(text)
    return {
        'tokens': tokens,
        'lemmas': lemmas,
        'pos_tags': pos_tags,
        'entities': entities,
        'redacted_text': redacted_text
    }
