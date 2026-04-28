"""
NavAI - Conversation History Manager
Stores and retrieves past Q&A interactions for the memory feature.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("NavAI.History")

# Maximum history entries kept in memory
MAX_HISTORY = 50


class ConversationHistory:
    """
    In-memory conversation history manager.

    Stores recent questions, answers, intents, and detection summaries
    to enable context-aware follow-up responses.
    """

    def __init__(self, max_entries: int = MAX_HISTORY):
        """
        Initialize the history manager.

        Args:
            max_entries: Maximum entries to keep in memory
        """
        self.entries: list = []
        self.max_entries = max_entries
        logger.info(f"History manager initialized (max={max_entries})")

    def add_entry(
        self,
        question: str,
        answer: str,
        intent: dict,
        detection_count: int = 0,
        ocr_count: int = 0,
        latency_ms: float = 0,
    ):
        """
        Add a new conversation entry.

        Args:
            question: User's spoken question
            answer: AI-generated answer
            intent: Recognized intent dictionary
            detection_count: Number of objects detected
            ocr_count: Number of text regions extracted
            latency_ms: Processing latency in milliseconds
        """
        entry = {
            "id": len(self.entries) + 1,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "intent": intent.get("intent", "general") if intent else "general",
            "confidence": intent.get("confidence", 0) if intent else 0,
            "detection_count": detection_count,
            "ocr_count": ocr_count,
            "latency_ms": latency_ms,
        }

        self.entries.append(entry)

        # Trim if over limit
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]

        logger.info(f"History entry #{entry['id']} added")

    def get_recent(self, count: int = 10) -> list:
        """
        Get the most recent conversation entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent entries (newest first)
        """
        return list(reversed(self.entries[-count:]))

    def get_summary(self) -> dict:
        """
        Get a summary of conversation history.

        Returns:
            Summary dictionary with stats
        """
        if not self.entries:
            return {
                "total_queries": 0,
                "avg_latency_ms": 0,
                "most_common_intent": "none",
                "total_objects_detected": 0,
            }

        # Count intents
        intent_counts = {}
        total_latency = 0
        total_objects = 0

        for entry in self.entries:
            intent = entry.get("intent", "general")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            total_latency += entry.get("latency_ms", 0)
            total_objects += entry.get("detection_count", 0)

        most_common = max(intent_counts, key=intent_counts.get)

        return {
            "total_queries": len(self.entries),
            "avg_latency_ms": round(total_latency / len(self.entries), 2),
            "most_common_intent": most_common,
            "total_objects_detected": total_objects,
            "intent_distribution": intent_counts,
        }

    def clear(self):
        """Clear all history."""
        self.entries = []
        logger.info("Conversation history cleared")

    def search(self, keyword: str) -> list:
        """
        Search history by keyword in questions or answers.

        Args:
            keyword: Search keyword

        Returns:
            Matching entries
        """
        keyword_lower = keyword.lower()
        return [
            entry
            for entry in self.entries
            if keyword_lower in entry["question"].lower()
            or keyword_lower in entry["answer"].lower()
        ]
