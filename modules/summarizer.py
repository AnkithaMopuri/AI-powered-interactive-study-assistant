"""
Robust Text Summarization Module
Handles empty vocabulary safely
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Summarizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            min_df=1
        )

    def summarize_improved(self, text, sentences, ratio=0.3):
        if not sentences or len(sentences) < 3:
            return text

        try:
            num_sentences = max(3, int(len(sentences) * ratio))

            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            scores = np.array(tfidf_matrix.sum(axis=1)).flatten()

            if scores.sum() == 0:
                return " ".join(sentences[:num_sentences])

            top_indices = scores.argsort()[-num_sentences:]
            top_indices = sorted(top_indices)

            return " ".join([sentences[i] for i in top_indices])

        except Exception as e:
            print("Summary fallback used:", e)
            return " ".join(sentences[:3])

    def generate_bullet_points(self, text, sentences, num_points=5):
        try:
            if not sentences:
                return []

            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            scores = np.array(tfidf_matrix.sum(axis=1)).flatten()

            top_indices = scores.argsort()[-num_points:]
            top_indices = sorted(top_indices)

            return [sentences[i] for i in top_indices]

        except Exception as e:
            print("Bullet fallback used:", e)
            return sentences[:num_points]
