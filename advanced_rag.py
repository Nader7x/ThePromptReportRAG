"""
Advanced RAG Features - Phase 3
===============================

This module implements advanced features for the RAG application:
1. Advanced Chunking for larger documents
2. Hybrid Search (vector + keyword search)
3. Enhanced retrieval strategies
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import faiss
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


@dataclass
class DocumentChunk:
    """Represents a document chunk with metadata"""

    content: str
    chunk_id: str
    source: str
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


@dataclass
class SearchResult:
    """Enhanced search result with multiple scores"""

    content: str
    source: str
    vector_score: float
    keyword_score: float
    hybrid_score: float
    rank: int
    metadata: Dict[str, Any]


class AdvancedChunker:
    """Advanced document chunking with multiple strategies"""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50, strategy: str = "semantic"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self.logger = logging.getLogger(__name__)

    def chunk_document(self, text: str, source: str = "unknown") -> List[DocumentChunk]:
        """Chunk document using the specified strategy"""
        if self.strategy == "semantic":
            return self._semantic_chunking(text, source)
        elif self.strategy == "sentence":
            return self._sentence_chunking(text, source)
        elif self.strategy == "sliding_window":
            return self._sliding_window_chunking(text, source)
        else:
            return self._simple_chunking(text, source)

    def _semantic_chunking(self, text: str, source: str) -> List[DocumentChunk]:
        """Semantic chunking based on sentence boundaries and meaning"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        current_start = 0

        for i, sentence in enumerate(sentences):
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunk = DocumentChunk(
                    content=current_chunk.strip(),
                    chunk_id=f"{source}_chunk_{len(chunks)}",
                    source=source,
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    metadata={"sentence_count": len(sent_tokenize(current_chunk))},
                )
                chunks.append(chunk)

                # Start new chunk with overlap
                overlap_sentences = sentences[max(0, i - 2) : i]
                current_chunk = " ".join(overlap_sentences) + " " + sentence
                current_start = text.find(overlap_sentences[0]) if overlap_sentences else text.find(sentence)
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Add the last chunk
        if current_chunk:
            chunk = DocumentChunk(
                content=current_chunk.strip(),
                chunk_id=f"{source}_chunk_{len(chunks)}",
                source=source,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                metadata={"sentence_count": len(sent_tokenize(current_chunk))},
            )
            chunks.append(chunk)

        return chunks

    def _sentence_chunking(self, text: str, source: str) -> List[DocumentChunk]:
        """Chunk by sentences with smart grouping"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk = DocumentChunk(
                    content=chunk_text,
                    chunk_id=f"{source}_sent_chunk_{len(chunks)}",
                    source=source,
                    start_pos=text.find(current_chunk[0]),
                    end_pos=text.find(current_chunk[-1]) + len(current_chunk[-1]),
                    metadata={"sentence_count": len(current_chunk)},
                )
                chunks.append(chunk)
                current_chunk = []
                current_length = 0

            current_chunk.append(sentence)
            current_length += len(sentence)

        # Add remaining sentences as last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = DocumentChunk(
                content=chunk_text,
                chunk_id=f"{source}_sent_chunk_{len(chunks)}",
                source=source,
                start_pos=text.find(current_chunk[0]),
                end_pos=text.find(current_chunk[-1]) + len(current_chunk[-1]),
                metadata={"sentence_count": len(current_chunk)},
            )
            chunks.append(chunk)

        return chunks

    def _sliding_window_chunking(self, text: str, source: str) -> List[DocumentChunk]:
        """Sliding window chunking with overlap"""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Adjust end to word boundary
            if end < len(text):
                while end > start and text[end] not in " \n\t":
                    end -= 1

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = DocumentChunk(
                    content=chunk_text,
                    chunk_id=f"{source}_window_{len(chunks)}",
                    source=source,
                    start_pos=start,
                    end_pos=end,
                    metadata={"window_size": len(chunk_text)},
                )
                chunks.append(chunk)

            start = max(start + self.chunk_size - self.chunk_overlap, end)

        return chunks

    def _simple_chunking(self, text: str, source: str) -> List[DocumentChunk]:
        """Simple character-based chunking"""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk_text = text[i : i + self.chunk_size]
            chunk = DocumentChunk(
                content=chunk_text,
                chunk_id=f"{source}_simple_{len(chunks)}",
                source=source,
                start_pos=i,
                end_pos=min(i + self.chunk_size, len(text)),
                metadata={"simple_chunk": True},
            )
            chunks.append(chunk)

        return chunks


class HybridRetriever:
    """Advanced retriever combining vector and keyword search"""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        self.logger = logging.getLogger(__name__)

        # Initialize search components
        self.vector_index = None
        self.bm25 = None
        self.tfidf_vectorizer = None
        self.documents = []
        self.chunks = []

    def build_indices(self, chunks: List[DocumentChunk]):
        """Build both vector and keyword indices"""
        self.chunks = chunks
        self.documents = [chunk.content for chunk in chunks]

        # Build vector index
        self._build_vector_index()

        # Build keyword indices
        self._build_keyword_indices()

        self.logger.info(f"Built hybrid indices for {len(chunks)} chunks")

    def _build_vector_index(self):
        """Build FAISS vector index"""
        embeddings = self.embedding_model.encode(self.documents)
        embeddings = np.array(embeddings).astype("float32")

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.vector_index = faiss.IndexFlatIP(dimension)
        self.vector_index.add(embeddings)

        # Store embeddings in chunks
        for i, chunk in enumerate(self.chunks):
            chunk.embedding = embeddings[i]

    def _build_keyword_indices(self):
        """Build BM25 and TF-IDF indices"""
        # Tokenize documents for BM25
        tokenized_docs = [word_tokenize(doc.lower()) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)

        # Build TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(max_features=10000, stop_words="english", ngram_range=(1, 2))
        self.tfidf_vectorizer.fit(self.documents)

    def hybrid_search(
        self, query: str, top_k: int = 5, vector_weight: Optional[float] = None, keyword_weight: Optional[float] = None
    ) -> List[SearchResult]:
        """Perform hybrid search combining vector and keyword search"""

        if vector_weight is None:
            vector_weight = self.vector_weight
        if keyword_weight is None:
            keyword_weight = self.keyword_weight

        # Ensure weights sum to 1
        total_weight = vector_weight + keyword_weight
        vector_weight /= total_weight
        keyword_weight /= total_weight

        # Vector search
        vector_scores = self._vector_search(query, len(self.documents))

        # Keyword search
        keyword_scores = self._keyword_search(query, len(self.documents))

        # Combine scores
        hybrid_scores = []
        for i in range(len(self.documents)):
            hybrid_score = vector_weight * vector_scores[i] + keyword_weight * keyword_scores[i]
            hybrid_scores.append(hybrid_score)

        # Get top results
        top_indices = np.argsort(hybrid_scores)[-top_k:][::-1]

        results = []
        for rank, idx in enumerate(top_indices):
            result = SearchResult(
                content=self.chunks[idx].content,
                source=self.chunks[idx].source,
                vector_score=vector_scores[idx],
                keyword_score=keyword_scores[idx],
                hybrid_score=hybrid_scores[idx],
                rank=rank + 1,
                metadata=self.chunks[idx].metadata,
            )
            results.append(result)

        return results

    def _vector_search(self, query: str, k: int) -> List[float]:
        """Perform vector similarity search"""
        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = self.vector_index.search(query_embedding, k)

        # Convert to list with proper ordering
        score_list = [0.0] * len(self.documents)
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                score_list[idx] = float(score)

        return score_list

    def _keyword_search(self, query: str, k: int) -> List[float]:
        """Perform keyword search using BM25"""
        query_tokens = word_tokenize(query.lower())
        bm25_scores = self.bm25.get_scores(query_tokens)

        # Normalize scores to 0-1 range
        if max(bm25_scores) > 0:
            bm25_scores = bm25_scores / max(bm25_scores)

        return bm25_scores.tolist()


class AdvancedRAGProcessor:
    """Enhanced RAG processor with advanced features"""

    def __init__(self, chunker: AdvancedChunker, retriever: HybridRetriever):
        self.chunker = chunker
        self.retriever = retriever
        self.logger = logging.getLogger(__name__)

    def process_documents(self, documents: Dict[str, str]):
        """Process multiple documents with advanced chunking"""
        all_chunks = []

        for doc_name, content in documents.items():
            chunks = self.chunker.chunk_document(content, doc_name)
            all_chunks.extend(chunks)
            self.logger.info(f"Processed {doc_name}: {len(chunks)} chunks")

        # Build search indices
        self.retriever.build_indices(all_chunks)

        return all_chunks

    def enhanced_search(self, query: str, search_strategy: str = "hybrid", top_k: int = 5) -> List[SearchResult]:
        """Enhanced search with multiple strategies"""

        if search_strategy == "hybrid":
            return self.retriever.hybrid_search(query, top_k)
        elif search_strategy == "vector_only":
            return self.retriever.hybrid_search(query, top_k, vector_weight=1.0, keyword_weight=0.0)
        elif search_strategy == "keyword_only":
            return self.retriever.hybrid_search(query, top_k, vector_weight=0.0, keyword_weight=1.0)
        else:
            return self.retriever.hybrid_search(query, top_k)


# Factory function for easy setup
def create_advanced_rag(
    chunk_size: int = 512,
    chunk_strategy: str = "semantic",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> AdvancedRAGProcessor:
    """Create an advanced RAG processor with default settings"""

    chunker = AdvancedChunker(chunk_size=chunk_size, chunk_overlap=50, strategy=chunk_strategy)

    retriever = HybridRetriever(embedding_model=embedding_model, vector_weight=0.7, keyword_weight=0.3)

    return AdvancedRAGProcessor(chunker, retriever)
