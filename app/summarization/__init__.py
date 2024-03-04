# app/summarization/__init__.py
from flask import Blueprint

# Cria um Blueprint chamado 'summarization' e associa-o ao pacote 'app.summarization'
summarization_bp = Blueprint('summarization', __name__)

# Importa as funcionalidades de sumarização
from .nltk import summarize_nltk
from .bert import summarize_bert
from .spacy import summarize_spacy
from .tfidf import summarize_tfidf
