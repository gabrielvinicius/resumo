from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim import corpora, models
import re


class TopicModeling:
    def __init__(self, text):
        self.text = text
        self.stop_words = set(stopwords.words('portuguese'))

    def preprocess_text(self):
        words = word_tokenize(self.text.lower())
        words = [word for word in words if word.isalnum() and word not in self.stop_words]
        return words

    def identify_topics_lda(self):
        words = self.preprocess_text()

        # Criando um dicionário de palavras
        dictionary = corpora.Dictionary([words])

        # Criando o corpus
        corpus = [dictionary.doc2bow(words)]

        # Criando o modelo LDA
        lda_model = models.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15)

        # Extraindo os tópicos
        topics = lda_model.show_topics(num_words=5, formatted=False)

        return topics
