# summarization/tfidf.py
from sklearn.feature_extraction.text import TfidfVectorizer


def summarize_tfidf(text):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = X[0].toarray()

    top_words_index = tfidf_scores.argsort()[0][-5:][::-1]

    return ' '.join([feature_names[i] for i in top_words_index])