# summarization/bert.py
from transformers import pipeline


def summarize_bert(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=50, min_length=5, length_penalty=2.0, num_beams=4)
    return summary[0]['summary_text']