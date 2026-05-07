"""Memory service — core business logic for memory operations."""
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from backend.api.models.episode import Episode
from backend.api.models.fact import Fact
from backend.api.services.embedding import store_embedding, search_embeddings
from backend.api.services.extraction import get_extraction_service
from backend.api.services.context_generator import get_context_generator

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    # ── Episodes ─────────────────────────────────────────

    def store_episode(
        self,
        content: str,
        session_id: Optional[str] = None,
        role: str = "user",
        metadata: dict = None,
        auto_extract: bool = False,
    ) -> dict:
        """Store a new episode and optionally auto-extract facts.

        Args:
            auto_extract: If True, use LLM to extract facts from the episode.

        Returns:
            Dict with 'episode' and optionally 'extracted_facts'.
        """
        episode = Episode(
            tenant_id=self.tenant_id,
            session_id=session_id,
            content=content,
            role=role,
            metadata_=metadata or {},
        )
        self.db.add(episode)
        self.db.commit()
        self.db.refresh(episode)

        # Store in vector DB for semantic search
        store_embedding(
            tenant_id=self.tenant_id,
            doc_id=episode.id,
            text=content,
            metadata={
                "session_id": session_id or "",
                "role": role,
                "event_at": episode.event_at.isoformat() if episode.event_at else "",
            },
        )

        result = {"episode": episode, "extracted_facts": []}

        # Auto-extract facts if requested
        if auto_extract:
            extracted = self.extract_from_episode(episode)
            result["extracted_facts"] = extracted

        return result

    def list_episodes(
        self,
        session_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Episode]:
        """List episodes, optionally filtered by session."""
        query = self.db.query(Episode).filter(Episode.tenant_id == self.tenant_id)
        if session_id:
            query = query.filter(Episode.session_id == session_id)
        return query.order_by(Episode.event_at.desc()).offset(offset).limit(limit).all()

    def search_episodes(self, query: str, limit: int = 5) -> list[dict]:
        """Semantic search over episodes."""
        return search_embeddings(
            tenant_id=self.tenant_id,
            query=query,
            n_results=limit,
        )

    def extract_from_episode(self, episode: Episode) -> list[Fact]:
        """Extract facts from an episode using LLM and store them."""
        extractor = get_extraction_service()
        raw_facts = extractor.extract_facts(text=episode.content)

        stored_facts = []
        for rf in raw_facts:
            fact = self.add_fact(
                subject=rf["subject"],
                predicate=rf["predicate"],
                object_=rf["object"],
                confidence=rf.get("confidence", 0.8),
                source_episode_id=episode.id,
                metadata=rf.get("metadata", {}),
            )
            stored_facts.append(fact)
            logger.info(f"Extracted fact: {fact.subject} → {fact.predicate} → {fact.object_}")

        return stored_facts

    def extract_from_text(self, text: str, context_hint: str = "") -> list[dict]:
        """Extract facts from arbitrary text without storing an episode."""
        extractor = get_extraction_service()
        return extractor.extract_facts(text=text, context_hint=context_hint)

    # ── Facts ────────────────────────────────────────────

    def add_fact(
        self,
        subject: str,
        predicate: str,
        object_: str,
        confidence: float = 1.0,
        source_episode_id: Optional[str] = None,
        metadata: dict = None,
    ) -> Fact:
        """Add a new fact."""
        fact = Fact(
            tenant_id=self.tenant_id,
            subject=subject,
            predicate=predicate,
            object_=object_,
            confidence=confidence,
            source_episode_id=source_episode_id,
            metadata_=metadata or {},
        )
        self.db.add(fact)
        self.db.commit()
        self.db.refresh(fact)
        return fact

    def list_facts(self, valid_only: bool = True) -> list[Fact]:
        """List facts, optionally filtered to currently valid ones."""
        query = self.db.query(Fact).filter(Fact.tenant_id == self.tenant_id)
        if valid_only:
            query = query.filter(
                (Fact.valid_until.is_(None))
                | (Fact.valid_until > datetime.now(timezone.utc))
            )
        return query.order_by(Fact.created_at.desc()).all()

    def invalidate_fact(self, fact_id: str) -> Optional[Fact]:
        """Invalidate a fact (set valid_until to now)."""
        fact = (
            self.db.query(Fact)
            .filter(Fact.id == fact_id, Fact.tenant_id == self.tenant_id)
            .first()
        )
        if fact:
            fact.valid_until = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(fact)
        return fact

    def update_fact(
        self,
        fact_id: str,
        new_object: Optional[str] = None,
        new_confidence: Optional[float] = None,
    ) -> Optional[Fact]:
        """Update a fact by invalidating old and creating new version."""
        old_fact = (
            self.db.query(Fact)
            .filter(Fact.id == fact_id, Fact.tenant_id == self.tenant_id)
            .first()
        )
        if not old_fact:
            return None

        # Invalidate old
        old_fact.valid_until = datetime.now(timezone.utc)

        # Create new version
        new_fact = Fact(
            tenant_id=self.tenant_id,
            subject=old_fact.subject,
            predicate=old_fact.predicate,
            object_=new_object or old_fact.object_,
            confidence=new_confidence if new_confidence is not None else old_fact.confidence,
            source_episode_id=old_fact.source_episode_id,
            metadata_=old_fact.metadata_,
        )
        self.db.add(new_fact)
        self.db.commit()
        self.db.refresh(new_fact)
        return new_fact

    # ── Context ──────────────────────────────────────────

    def get_context(self, session_id: Optional[str] = None, use_llm: bool = False) -> dict:
        """Get current context summary (session_state.md equivalent).

        Args:
            session_id: Filter episodes by session
            use_llm: Use LLM for richer summary generation
        """
        facts = self.list_facts(valid_only=True)
        recent_episodes = self.list_episodes(session_id=session_id, limit=10)

        facts_summary = [
            {
                "subject": f.subject,
                "predicate": f.predicate,
                "object": f.object_,
                "confidence": f.confidence,
                "since": f.valid_from.isoformat() if f.valid_from else None,
                "metadata": f.metadata_ or {},
            }
            for f in facts
        ]

        generator = get_context_generator()
        summary = generator.generate(facts, recent_episodes, use_llm=use_llm)

        return {
            "active_facts_count": len(facts),
            "facts": facts_summary,
            "recent_episodes_count": len(recent_episodes),
            "summary": summary,
        }
