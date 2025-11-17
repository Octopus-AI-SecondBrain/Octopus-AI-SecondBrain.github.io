"""
Hybrid Retriever - Combines vector and keyword search with Reciprocal Rank Fusion (RRF).

This retriever provides state-of-the-art search by combining:
1. Semantic search (vector similarity) - finds conceptually similar content
2. Keyword search (BM25/full-text) - finds lexically matching content
3. RRF fusion - intelligently merges results from both methods
"""
from typing import Any, Optional
from collections import defaultdict

from ..interfaces import Retriever, Embedder, VectorStore, QueryResult, EmbeddedDocument
from ..stores.pgvector_store import PgVectorStore
from ...core.logging import get_logger

logger = get_logger(__name__)


def reciprocal_rank_fusion(
    results_list: list[list[tuple[str, float]]],
    k: int = 60,
) -> list[tuple[str, float]]:
    """
    Combine multiple ranked lists using Reciprocal Rank Fusion (RRF).

    RRF is a robust algorithm that merges results from different retrieval methods
    without requiring score normalization. It's particularly effective for hybrid search.

    Formula: RRF_score(d) = Σ(1 / (k + rank(d)))
    where k is a constant (typically 60) and rank(d) is the rank of document d in each list.

    Args:
        results_list: List of ranked result lists, each containing (doc_id, score) tuples
        k: RRF constant parameter (default: 60, as per research)

    Returns:
        Fused ranked list of (doc_id, rrf_score) tuples, sorted by score descending

    References:
        - Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009).
          "Reciprocal rank fusion outperforms condorcet and individual rank learning methods."
    """
    # Calculate RRF scores
    rrf_scores: dict[str, float] = defaultdict(float)

    for result_list in results_list:
        for rank, (doc_id, _score) in enumerate(result_list, start=1):
            # RRF formula: 1 / (k + rank)
            rrf_scores[doc_id] += 1.0 / (k + rank)

    # Sort by RRF score descending
    sorted_results = sorted(
        rrf_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    logger.debug(f"RRF fused {len(results_list)} result lists into {len(sorted_results)} unique documents")

    return sorted_results


class HybridRetriever(Retriever):
    """
    Hybrid retriever that combines semantic (vector) and keyword (BM25) search.

    Uses Reciprocal Rank Fusion (RRF) to merge results from both retrieval methods,
    providing superior search quality compared to using either method alone.

    Key benefits:
    - Semantic search: Finds conceptually similar content (e.g., "ML" matches "machine learning")
    - Keyword search: Finds exact matches and rare terms (e.g., specific product names)
    - RRF fusion: Balances both methods without manual tuning

    Usage:
        retriever = HybridRetriever(embedder, vector_store, alpha=0.5)
        results = await retriever.retrieve_async("what is deep learning?", k=10)
    """

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        alpha: float = 0.5,
        rrf_k: int = 60,
    ) -> None:
        """
        Initialize the hybrid retriever.

        Args:
            embedder: Embedder for query encoding
            vector_store: Vector store (must support keyword search)
            alpha: Weight for semantic vs keyword search (0.0-1.0)
                   - 0.0 = pure keyword search
                   - 0.5 = balanced (recommended)
                   - 1.0 = pure semantic search
            rrf_k: RRF constant parameter (default: 60)
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.alpha = max(0.0, min(1.0, alpha))  # Clamp to [0, 1]
        self.rrf_k = rrf_k

        # Validate vector store supports keyword search
        if not isinstance(vector_store, PgVectorStore):
            logger.warning(
                f"Vector store {type(vector_store).__name__} may not support keyword search. "
                "Hybrid search requires PgVectorStore with search_keywords_async method."
            )

        logger.info(
            f"Initialized HybridRetriever (alpha={alpha}, rrf_k={rrf_k}, "
            f"semantic_weight={alpha:.1%}, keyword_weight={1-alpha:.1%})"
        )

    async def retrieve_async(
        self,
        query: str,
        k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> QueryResult:
        """
        Retrieve relevant documents using hybrid search (vector + keyword + RRF).

        Workflow:
        1. Perform semantic search (vector similarity)
        2. Perform keyword search (BM25/full-text)
        3. Merge results using Reciprocal Rank Fusion
        4. Return top-k fused results

        Args:
            query: Query string
            k: Number of results to return
            filters: Optional metadata filters (applied to both searches)

        Returns:
            QueryResult with fused documents and RRF scores
        """
        # Retrieve more results from each method to ensure good coverage after fusion
        # This is a common best practice in hybrid search
        retrieval_k = k * 2

        # 1. Semantic search (vector similarity)
        semantic_results = None
        if self.alpha > 0:
            try:
                query_embedding = self.embedder.embed_query(query)
                semantic_results = await self.vector_store.search_async(
                    query_embedding=query_embedding,
                    k=retrieval_k,
                    filters=filters,
                )
                logger.debug(f"Semantic search returned {len(semantic_results.documents)} results")
            except Exception as e:
                logger.error(f"Semantic search failed: {e}", exc_info=True)

        # 2. Keyword search (BM25)
        keyword_results = None
        if self.alpha < 1 and hasattr(self.vector_store, 'search_keywords_async'):
            try:
                keyword_results = await self.vector_store.search_keywords_async(  # type: ignore
                    query=query,
                    k=retrieval_k,
                    filters=filters,
                )
                logger.debug(f"Keyword search returned {len(keyword_results.documents)} results")
            except Exception as e:
                logger.error(f"Keyword search failed: {e}", exc_info=True)

        # Handle fallback cases
        if semantic_results is None and keyword_results is None:
            logger.error("Both semantic and keyword search failed")
            return QueryResult(
                documents=[],
                scores=[],
                query=query,
                metadata={"error": "All search methods failed"},
            )

        if semantic_results is None:
            logger.warning("Semantic search failed, using keyword results only")
            keyword_results.query = query
            keyword_results.metadata["search_type"] = "keyword_only"
            return keyword_results

        if keyword_results is None:
            logger.warning("Keyword search failed, using semantic results only")
            semantic_results.query = query
            semantic_results.metadata["search_type"] = "semantic_only"
            return semantic_results

        # 3. Merge results using RRF
        # Prepare result lists for RRF: [(doc_id, score), ...]
        semantic_list = [
            (doc.doc_id, score)
            for doc, score in zip(semantic_results.documents, semantic_results.scores)
        ]

        keyword_list = [
            (doc.doc_id, score)
            for doc, score in zip(keyword_results.documents, keyword_results.scores)
        ]

        # Apply alpha weighting by duplicating lists
        # This effectively weights the contribution of each method
        results_for_fusion = []

        # Add semantic results with alpha weight
        if self.alpha > 0:
            # Repeat semantic results to increase their weight
            semantic_weight = int(self.alpha * 10)  # Scale to integer for duplication
            results_for_fusion.extend([semantic_list] * max(1, semantic_weight))

        # Add keyword results with (1-alpha) weight
        if self.alpha < 1:
            keyword_weight = int((1 - self.alpha) * 10)
            results_for_fusion.extend([keyword_list] * max(1, keyword_weight))

        # Perform RRF fusion
        fused_results = reciprocal_rank_fusion(results_for_fusion, k=self.rrf_k)

        # 4. Build final result set
        # Create doc_id -> document mapping
        all_docs: dict[str, EmbeddedDocument] = {}

        for doc in semantic_results.documents:
            all_docs[doc.doc_id] = doc

        for doc in keyword_results.documents:
            if doc.doc_id not in all_docs:
                all_docs[doc.doc_id] = doc

        # Extract top-k documents in RRF order
        final_documents = []
        final_scores = []

        for doc_id, rrf_score in fused_results[:k]:
            if doc_id in all_docs:
                final_documents.append(all_docs[doc_id])
                final_scores.append(rrf_score)

        logger.info(
            f"Hybrid search retrieved {len(final_documents)} documents "
            f"(semantic: {len(semantic_results.documents)}, "
            f"keyword: {len(keyword_results.documents)}, "
            f"fused: {len(final_documents)})"
        )

        return QueryResult(
            documents=final_documents,
            scores=final_scores,
            query=query,
            metadata={
                "search_type": "hybrid",
                "alpha": self.alpha,
                "rrf_k": self.rrf_k,
                "semantic_count": len(semantic_results.documents),
                "keyword_count": len(keyword_results.documents),
                "total_results": len(final_documents),
            },
        )
