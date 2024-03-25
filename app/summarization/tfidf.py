import nltk
import time
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from heapq import nlargest

# Baixe as stopwords e o punkt
nltk.download('stopwords')
nltk.download('punkt')

class TFIDFSummarizer:
    def __init__(self, language='english'):
        if language.lower() in stopwords.fileids():
            self.stopwords = set(stopwords.words(language))
        else:
            raise ValueError(f"Idioma '{language}' não é suportado para stopwords.")
        self.vectorizer = TfidfVectorizer()
        self.feature_names = None

    def _preprocess_text(self, text):
        tokens = word_tokenize(text.lower())
        return ' '.join(token for token in tokens if token.isalnum() and token not in self.stopwords)

    def summarize(self, text, ratio=0.3):
        start_time = time.time()
        preprocessed_text = self._preprocess_text(text)
        tfidf_matrix = self.vectorizer.fit_transform([preprocessed_text])
        self.feature_names = self.vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray().flatten()

        sentence_scores = {}
        for i, sentence in enumerate(sent_tokenize(text)):
            # Aqui convertemos feature_names para uma lista para usar o método index
            feature_names_list = list(self.feature_names)
            sentence_score = sum(scores[feature_names_list.index(word)]
                                 for word in word_tokenize(sentence.lower())
                                 if word in feature_names_list)
            sentence_scores[i] = sentence_score

        summary_indices = nlargest(int(len(sentence_scores) * ratio), sentence_scores, key=sentence_scores.get)
        summary = ' '.join(sent_tokenize(text)[i] for i in sorted(summary_indices))

        processing_time = time.time() - start_time
        return summary, processing_time
