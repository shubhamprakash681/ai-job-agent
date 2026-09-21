# Candidate services package
from app.services.candidate.kb_loader import get_candidate_kb, CandidateKnowledgeBase
from app.services.candidate.evidence_engine import get_evidence_engine, EvidenceEngine
from app.services.candidate.kb_seeder import seed_candidate_kb

__all__ = [
    "get_candidate_kb",
    "CandidateKnowledgeBase",
    "get_evidence_engine",
    "EvidenceEngine",
    "seed_candidate_kb",
]

