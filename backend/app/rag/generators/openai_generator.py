"""
Octopus AI Second Brain - OpenAI Generator
Answer generation using OpenAI's GPT models.
"""
from typing import Any

from ..interfaces import Generator, EmbeddedDocument
from ...core.logging import get_logger
from ...core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class OpenAIGenerator(Generator):
    """
    Generator using OpenAI's GPT models for answer generation.
    
    Creates contextual answers based on retrieved documents.
    """
    
    def __init__(
        self,
        model_name: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Initialize the OpenAI generator.
        
        Args:
            model_name: OpenAI model name (default from settings)
            temperature: Sampling temperature (default from settings)
            max_tokens: Maximum tokens in response (default from settings)
        """
        import openai
        
        self.model_name = model_name or settings.rag_generator.model_name
        self.temperature = temperature or settings.rag_generator.temperature
        self.max_tokens = max_tokens or settings.rag_generator.max_tokens
        
        # Initialize OpenAI client
        api_key = settings.openai_api_key
        if api_key:
            openai.api_key = api_key.get_secret_value()
        else:
            logger.warning("No OpenAI API key configured")
        
        self.client = openai.AsyncOpenAI(api_key=api_key.get_secret_value() if api_key else None)
        
        logger.info(
            f"Initialized OpenAIGenerator with model={self.model_name}, "
            f"temp={self.temperature}, max_tokens={self.max_tokens}"
        )
    
    async def generate_async(
        self,
        query: str,
        context_documents: list[EmbeddedDocument],
        **kwargs: Any,
    ) -> str:
        """
        Generate an answer based on query and context.
        
        Args:
            query: User query
            context_documents: Retrieved documents for context
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated answer text
        """
        # Build context from documents
        context_parts = []
        for i, doc in enumerate(context_documents, 1):
            source = doc.metadata.get("source", "Unknown")
            context_parts.append(f"[{i}] Source: {source}\n{doc.content}\n")
        
        context = "\n".join(context_parts)
        
        # Build prompt
        system_prompt = (
            "You are Octopus AI Second Brain, an AI assistant that helps users "
            "find and understand information from their personal knowledge base. "
            "Answer questions based on the provided context. If the context doesn't "
            "contain enough information, say so. Always cite your sources using [N] notation."
        )
        
        user_prompt = f"""Context from knowledge base:

{context}

Question: {query}

Please provide a clear, concise answer based on the context above. Cite your sources using [N] notation."""
        
        # Generate answer
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            
            answer = response.choices[0].message.content
            
            logger.info(f"Generated answer for query: {query[:50]}...")
            
            return answer or "I couldn't generate an answer."
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def generate(
        self,
        query: str,
        context_documents: list[EmbeddedDocument],
        **kwargs: Any,
    ) -> str:
        """
        Synchronously generate an answer.
        
        Args:
            query: User query
            context_documents: Retrieved documents for context
            **kwargs: Additional generation parameters
            
        Returns:
            Generated answer text
        """
        import asyncio
        return asyncio.run(self.generate_async(query, context_documents, **kwargs))
