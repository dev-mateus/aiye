"""
Modelos Pydantic para validação de requisições e respostas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AskRequest(BaseModel):
    """Requisição de pergunta."""
    question: str = Field(..., min_length=3, max_length=1000, description="Pergunta do usuário")


class Source(BaseModel):
    """Fonte/referência de um chunk recuperado."""
    title: str = Field(..., description="Título do documento")
    page_start: int = Field(..., description="Página inicial")
    page_end: int = Field(..., description="Página final")
    uri: str = Field(..., description="URI/caminho do PDF original")
    score: Optional[float] = Field(None, description="Score de similaridade")


class AskResponse(BaseModel):
    """Resposta completa com resposta, fontes e metadados."""
    answer: str = Field(..., description="Resposta gerada a partir dos contextos")
    sources: list[Source] = Field(default_factory=list, description="Lista de fontes citadas")
    meta: dict = Field(default_factory=dict, description="Metadados adicionais (latência, top_k, etc.)")


class FeedbackRequest(BaseModel):
    """Requisição de feedback do usuário."""
    question: str = Field(..., min_length=1, max_length=1000, description="Pergunta original")
    answer: str = Field(..., min_length=1, description="Resposta recebida")
    rating: int = Field(..., ge=1, le=5, description="Avaliação de 1 a 5 estrelas")
    comment: Optional[str] = Field(None, max_length=500, description="Comentário opcional do usuário")
