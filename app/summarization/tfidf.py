import nltk
import time
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from heapq import nlargest
from typing import Tuple


class TFIDFSummarizer:
    def __init__(self, language: str = 'portuguese'):
        """
        Inicializa o sumarizador TF-IDF.

        Args:
            language (str): Idioma para processamento (padrão: 'portuguese')
        """
        self._download_nltk_resources()
        self.stopwords = self._load_stopwords(language)
        self.vectorizer = TfidfVectorizer()
        self.feature_names = None

    def _download_nltk_resources(self):
        """Baixa os recursos necessários do NLTK se não estiverem instalados"""
        try:
            nltk.data.find('corpora/stopwords')
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('stopwords')
            nltk.download('punkt')
            nltk.download('punkt_tab')

    def _load_stopwords(self, language: str) -> set:
        """
        Carrega as stopwords para o idioma especificado.

        Raises:
            ValueError: Se o idioma não for suportado
        """
        if language.lower() in stopwords.fileids():
            return set(stopwords.words(language))
        raise ValueError(f"Idioma '{language}' não suportado")

    def _preprocess_text(self, text: str) -> str:
        """
        Pré-processa o texto removendo stopwords e pontuação.

        Returns:
            str: Texto limpo e tokenizado
        """
        tokens = word_tokenize(text.lower(), language='portuguese')
        return ' '.join(
            token for token in tokens
            if token.isalnum() and token not in self.stopwords
        )

    def summarize(self, text: str, ratio: float = 0.3) -> Tuple[str, float]:
        """
        Gera um resumo do texto usando o algoritmo TF-IDF.

        Args:
            text (str): Texto para sumarizar
            ratio (float): Porcentagem de frases para incluir (0-1)

        Returns:
            Tuple[str, float]: (resumo, tempo_de_processamento)

        Raises:
            ValueError: Se ratio for inválido ou texto vazio
        """
        start_time = time.time()

        # Validações
        if not text.strip():
            return "", 0.0

        if not 0 < ratio <= 1:
            raise ValueError("Ratio deve estar entre 0 e 1")

        # Processamento
        processed_text = self._preprocess_text(text)
        sentences = sent_tokenize(text, language='portuguese')

        if len(sentences) <= 1:
            return text, time.time() - start_time

        # Cálculo TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform([processed_text])
        self.feature_names = self.vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray().flatten()

        # Pontuação das frases
        word_to_index = {word: idx for idx, word in enumerate(self.feature_names)}
        sentence_scores = {}

        for i, sentence in enumerate(sentences):
            words = [
                w for w in word_tokenize(sentence.lower(), language='portuguese')
                if w in word_to_index
            ]
            sentence_scores[i] = sum(
                scores[word_to_index[word]]
                for word in words
            ) / (len(words) or 1)  # Evita divisão por zero

        # Seleciona as melhores frases
        n_sentences = max(1, int(len(sentences) * ratio))
        best_sentences = nlargest(
            n_sentences,
            sentence_scores,
            key=sentence_scores.get
        )

        # Ordena na sequência original
        summary = ' '.join(sentences[i] for i in sorted(best_sentences))

        return summary, time.time() - start_time