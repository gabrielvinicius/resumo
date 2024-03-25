# app/summarization/__init__.py
from flask import Blueprint

# Cria um Blueprint chamado 'summarization' e associa-o ao pacote 'app.summarization'
summarization_bp = Blueprint('summarization', __name__)

# Importa as funcionalidades de sumarização
from .nltk import TextSummarizer
# from .bert import TextSummarizer
# from .spacy import summarize_spacy
from .tfidf import TFIDFSummarizer
# from .bart import BartTextSummarizer
# from .T5 import T5TextSummarizer
# from .gpt2 import GPT2TextSummarizer
# from .xlnet import XLNetTextSummarizer
