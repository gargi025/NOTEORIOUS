from sentence_transformers import SentenceTransformer
import numpy as np


MODEL_NAME = "all-MiniLM-L6-v2"


class SemanticConsistency:

    def __init__(self):
        print("Loading semantic consistency model...")
        self.model = SentenceTransformer(MODEL_NAME)
        print("Semantic consistency model loaded.")

    def score(self, candidate, context):

        if not context.strip():
            return 0.5

        embeddings = self.model.encode(
            [candidate, context],
            normalize_embeddings=True
        )

        similarity = np.dot(
            embeddings[0],
            embeddings[1]
        )

        # Convert cosine similarity [-1, 1] → [0, 1]
        score = (similarity + 1) / 2

        return float(score)


semantic_checker = None


def calculate_semantic_consistency(candidate, context):

    global semantic_checker

    if semantic_checker is None:
        semantic_checker = SemanticConsistency()

    return semantic_checker.score(candidate, context)