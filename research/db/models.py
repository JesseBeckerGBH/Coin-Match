"""
Research Engine Database Models

SQLAlchemy models for research_documents, math_candidates,
experiment_runs, and promotion_decisions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ResearchDocument(Base):
    """Discovered and ingested research documents."""
    __tablename__ = "research_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False)  # paper, blog, repo, benchmark, guide
    published_at = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    clean_text = Column(Text, nullable=True)
    trust_score = Column(Float, default=0.0)
    novelty_score = Column(Float, default=0.0)

    candidates = relationship("MathCandidate", back_populates="document")


class MathCandidate(Base):
    """Extracted mathematical methods and formulas."""
    __tablename__ = "math_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("research_documents.id"), nullable=False)
    method_name = Column(Text, nullable=False)
    math_family = Column(String(100), nullable=True)  # ranking, reliability, retrieval, etc.
    use_case = Column(Text, nullable=True)
    formula_text = Column(Text, nullable=True)
    relevance_score = Column(Float, default=0.0)
    data_readiness_score = Column(Float, default=0.0)
    novelty_class = Column(String(50), default="unknown")  # new, new_application, known
    benchmark_potential_score = Column(Float, default=0.0)
    explainability_score = Column(Float, default=0.0)
    status = Column(String(50), default="discovered")  # discovered, scored, queued, benchmarked, promoted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("ResearchDocument", back_populates="candidates")
    experiments = relationship("ExperimentRun", back_populates="candidate")
    decisions = relationship("PromotionDecision", back_populates="candidate")

    __table_args__ = (
        Index("ix_math_candidates_status", "status"),
        Index("ix_math_candidates_document_id", "document_id"),
    )


class ExperimentRun(Base):
    """Benchmark experiment executions."""
    __tablename__ = "experiment_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("math_candidates.id"), nullable=False)
    baseline_name = Column(Text, nullable=False)
    variant_name = Column(Text, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    metrics_json = Column(JSONB, default=dict)
    passed = Column(Boolean, nullable=True)

    candidate = relationship("MathCandidate", back_populates="experiments")

    __table_args__ = (
        Index("ix_experiment_runs_candidate_id", "candidate_id"),
    )


class PromotionDecision(Base):
    """Promotion gate decisions for candidates."""
    __tablename__ = "promotion_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("math_candidates.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # promote, stage-only, watchlist, reject
    rationale = Column(Text, nullable=True)
    benchmark_strength = Column(Float, default=0.0)
    deployment_risk = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("MathCandidate", back_populates="decisions")

    __table_args__ = (
        Index("ix_promotion_decisions_candidate_id", "candidate_id"),
    )
