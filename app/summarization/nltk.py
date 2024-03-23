# app/summarizer.py
import time
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from heapq import nlargest


class TextSummarizer:
    def __init__(self, language='english'):
        # nltk.download('stopwords')
        # nltk.download('punkt')
        self.stopwords = set(stopwords.words(language))

    def summarize(self, text, ratio=0.3):
        start_time = time.time()
        sentences = sent_tokenize(text)
        word_frequencies = {}

        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            for word in words:
                if word not in self.stopwords:
                    if word not in word_frequencies:
                        word_frequencies[word] = 1
                    else:
                        word_frequencies[word] += 1

        maximum_frequency = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word] / maximum_frequency)

        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies.keys():
                    if len(sentence.split(' ')) < 30:
                        if i not in sentence_scores.keys():
                            sentence_scores[i] = word_frequencies[word]
                        else:
                            sentence_scores[i] += word_frequencies[word]

        summary_sentences = nlargest(int(len(sentence_scores) * ratio), sentence_scores, key=sentence_scores.get)
        summary_sentences = sorted(summary_sentences)
        summary = ' '.join(sentences[i] for i in summary_sentences)
        end_time = time.time()
        processing_time = end_time - start_time
        return summary, processing_time
