from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

import numpy as np

from .config import EMBEDDER_MODE


@dataclass
class Embedder:
    name: str

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        raise NotImplementedError


def _load_stub() -> Embedder:
    class Stub(Embedder):
        dim = 384

        def __init__(self) -> None:
            super().__init__('stub')

        def encode(self, texts: Iterable[str]) -> np.ndarray:
            vectors: List[np.ndarray] = []
            for text in texts:
                tokens = re.findall(r'[a-z0-9]+', text.lower())
                bucket = np.zeros(self.dim, dtype=np.float32)
                for token in tokens:
                    bucket[hash(token) % self.dim] += 1.0
                norm = np.linalg.norm(bucket)
                if norm > 0:
                    bucket /= norm
                vectors.append(bucket.astype(np.float32))
            if not vectors:
                return np.zeros((0, self.dim), dtype=np.float32)
            return np.stack(vectors, axis=0)

    return Stub()


def _load_transformer() -> Embedder:
    from sentence_transformers import SentenceTransformer

    class Transformer(Embedder):
        def __init__(self) -> None:
            super().__init__('sentence-transformers/all-MiniLM-L6-v2')
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')

        def encode(self, texts: Iterable[str]) -> np.ndarray:
            output = self.model.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True)
            return output.astype(np.float32)

    return Transformer()


def load_embedder() -> Embedder:
    mode = EMBEDDER_MODE.lower()
    if mode == 'stub':
        return _load_stub()
    return _load_transformer()


EMBEDDER = load_embedder()


def embed_text(text: str) -> np.ndarray:
    vec = EMBEDDER.encode([text])
    if vec.ndim == 1:
        return vec.astype(np.float32)
    return vec[0].astype(np.float32)
