"""
Semantic Search Module
Improved accuracy and stability
"""

from sentence_transformers import SentenceTransformer, util
import torch

class SemanticSearch:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.document_embeddings = None
        self.document_sentences = None

    def encode_documents(self, sentences):
        self.document_sentences = sentences
        self.document_embeddings = self.model.encode(
            sentences,
            convert_to_tensor=True,
            show_progress_bar=False
        )

    def search(self, query, top_k=5, similarity_threshold=0.2):
        if self.document_embeddings is None:
            return []

        query_embedding = self.model.encode(query, convert_to_tensor=True)
        similarities = util.cos_sim(query_embedding, self.document_embeddings)[0]

        top_results = torch.topk(similarities, k=min(top_k, len(similarities)))

        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            score_val = score.item()
            if score_val >= similarity_threshold:
                results.append({
                    'sentence': self.document_sentences[idx],
                    'score': round(score_val, 3),
                    'index': idx.item()
                })

        return results

    def find_answer(self, query, context_window=2):
        results = self.search(query)

        if not results:
            return None

        best = results[0]
        idx = best['index']

        start = max(0, idx - context_window)
        end = min(len(self.document_sentences), idx + context_window + 1)

        context = self.document_sentences[start:end]

        return {
            'answer': ' '.join(context),
            'confidence': best['score'],
            'relevant_sentences': [r['sentence'] for r in results]
        }
