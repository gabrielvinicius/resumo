# summarization/spacy.py
import spacy


def summarize_spacy(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = list(doc.sents)
    summary = ' '.join([str(sentence) for sentence in sentences[:5]])
    return summary
