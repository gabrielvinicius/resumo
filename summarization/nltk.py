# summarization/nltk.py
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
import string


def summarize_nltk(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)

    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]

    fdist = FreqDist(filtered_words)
    common_words = fdist.most_common(5)

    return ' '.join([word[0] for word in common_words])
