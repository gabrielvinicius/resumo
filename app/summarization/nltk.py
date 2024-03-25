import time
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from heapq import nlargest


class TextSummarizer:
    def __init__(self, language='english'):
        nltk.download('stopwords')
        nltk.download('punkt')
        self.stopwords = set(stopwords.words(language))

    def _calculate_word_frequencies(self, text):
        word_frequencies = {}
        for sentence in sent_tokenize(text):
            for word in word_tokenize(sentence.lower()):
                if word not in self.stopwords:
                    word_frequencies[word] = word_frequencies.get(word, 0) + 1
        return word_frequencies

    def _score_sentences(self, text, word_frequencies):
        sentence_scores = {}
        for i, sentence in enumerate(sent_tokenize(text)):
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies:
                    if len(sentence.split()) < 30:
                        sentence_scores[i] = sentence_scores.get(i, 0) + word_frequencies[word]
        return sentence_scores

    def summarize(self, text, ratio=0.3):
        start_time = time.time()
        word_frequencies = self._calculate_word_frequencies(text)
        sentence_scores = self._score_sentences(text, word_frequencies)

        summary_sentences = nlargest(int(len(sentence_scores) * ratio), sentence_scores, key=sentence_scores.get)
        summary = ' '.join(sent_tokenize(text)[i] for i in sorted(summary_sentences))

        processing_time = time.time() - start_time
        return summary, processing_time
