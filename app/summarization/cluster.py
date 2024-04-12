import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List
from app.models import Transcription


class VideoTopicSummarizer:
    def __init__(self, transcription: Transcription):
        self.transcription = transcription
        # self.summarize = TFIDFSummarizer(language=transcription.language)

    def identify_topic(self):
        # Vetorização do texto usando TF-IDF
        tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=20000,
                                           min_df=0.2, stop_words=self.transcription.language,
                                           use_idf=True, ngram_range=(1, 3))

        segments_text = [segment.text for segment in self.transcription.segments]
        tfidf_matrix = tfidf_vectorizer.fit_transform(segments_text)

        num_clusters = max(1, int(len(segments_text) * 0.3))

        # Aplicação do algoritmo K-means para agrupamento
        # num_clusters = 3  # Definir o número de clusters
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(tfidf_matrix)

        # Recuperar os termos mais representativos de cada cluster
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
        terms = tfidf_vectorizer.get_feature_names_out()

        # Retorna os tópicos baseados nos termos mais representativos de cada cluster
        topics = []
        for i in range(num_clusters):
            topic = ' '.join([terms[ind] for ind in order_centroids[i, :5]])
            topics.append(topic)

        return topics
