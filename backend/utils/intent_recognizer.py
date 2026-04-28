"""
NavAI - Intent Recognition Module
Detects user intent from spoken questions using hybrid rule-based + NLP approach.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("NavAI.Intent")


# Intent patterns (rule-based component)
INTENT_PATTERNS = {
    "scene_description": [
        r"what.*(see|around|front|surroundings|environment|nearby|here)",
        r"describe.*(scene|view|surroundings|what.*see|environment)",
        r"tell me.*(about|what).*(around|here|see|front)",
        r"what.*(is|are).*(there|here|around)",
        r"can you (see|describe|tell)",
        r"look around",
        r"where am i",
        r"what.*happening",
    ],
    "object_query": [
        r"is there.*(a|an|any)",
        r"do you (see|detect|notice|find)",
        r"can you (find|spot|see)",
        r"where.*(is|are) (the|a|an)",
        r"how many",
        r"any.*(person|people|chair|table|door|car|vehicle|stairs)",
        r"find.*(a|an|the)",
        r"locate",
    ],
    "text_reading": [
        r"read.*(text|sign|board|label|name|notice|this|that)",
        r"what.*(say|written|text|sign|board|reads)",
        r"any.*(text|sign|writing|label|notice)",
        r"can you read",
        r"read (this|that|it)",
        r"what does.*(say|read)",
    ],
    "obstacle_detection": [
        r"(is|are) (it|the path|way).*(safe|clear|blocked|free)",
        r"any.*(obstacle|block|danger|hazard)",
        r"obstacle.*(ahead|front|path|nearby)",
        r"can i (walk|go|move|proceed)",
        r"is.*(safe|clear) (to|ahead|forward)",
        r"warning|danger|careful|watch out",
    ],
    "navigation": [
        r"(where|which way|how).*(go|walk|turn|exit|door|entrance)",
        r"guide me",
        r"take me to",
        r"direction.*(to|for)",
        r"how (do i|to) (get|reach|find)",
        r"show me.*(way|path|direction)",
    ],
}

# Confidence keywords that boost intent matching
INTENT_KEYWORDS = {
    "scene_description": {"see", "look", "around", "front", "describe", "scene", "surroundings", "view", "environment"},
    "object_query": {"find", "detect", "chair", "person", "table", "door", "car", "where", "locate", "spot"},
    "text_reading": {"read", "text", "sign", "written", "says", "board", "label", "notice"},
    "obstacle_detection": {"obstacle", "safe", "clear", "blocked", "danger", "hazard", "careful", "warning"},
    "navigation": {"direction", "guide", "navigate", "turn", "exit", "entrance", "way", "path"},
}


class IntentRecognizer:
    """
    Hybrid intent recognizer using rule-based patterns + keyword matching.

    Recognizes intents:
    - scene_description: User wants to know about surroundings
    - object_query: User is looking for specific objects
    - text_reading: User wants to read signs/text
    - obstacle_detection: User wants safety information
    - navigation: User needs directions
    - general: Default/catch-all intent
    """

    def __init__(self):
        """Initialize the intent recognizer."""
        self.patterns = INTENT_PATTERNS
        self.keywords = INTENT_KEYWORDS
        logger.info("Intent Recognizer initialized")

    def recognize(self, question: str) -> dict:
        """
        Recognize intent from a user question.

        Uses a two-phase approach:
        1. Regex pattern matching (high confidence)
        2. Keyword overlap scoring (medium confidence)

        Args:
            question: User's spoken question (text)

        Returns:
            Intent dictionary:
            {
                "intent": "scene_description",
                "confidence": 0.85,
                "method": "pattern",
                "requires_camera": True,
                "requires_ocr": True,
                "original_question": "what is in front of me?"
            }
        """
        question_lower = question.lower().strip()

        # Phase 1: Pattern matching
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return self._build_result(
                        intent=intent,
                        confidence=0.9,
                        method="pattern",
                        question=question,
                    )

        # Phase 2: Keyword matching
        words = set(re.findall(r'\w+', question_lower))
        best_intent = "general"
        best_score = 0

        for intent, kws in self.keywords.items():
            overlap = len(words & kws)
            score = overlap / max(len(kws), 1)

            if score > best_score:
                best_score = score
                best_intent = intent

        if best_score > 0.1:
            return self._build_result(
                intent=best_intent,
                confidence=round(min(best_score + 0.3, 0.85), 2),
                method="keyword",
                question=question,
            )

        # Default: general intent
        return self._build_result(
            intent="general",
            confidence=0.5,
            method="default",
            question=question,
        )

    def _build_result(
        self,
        intent: str,
        confidence: float,
        method: str,
        question: str,
    ) -> dict:
        """
        Build a structured intent result.

        Also determines which modules are needed based on intent.
        """
        # Determine required modules
        camera_intents = {
            "scene_description", "object_query", "text_reading",
            "obstacle_detection", "navigation", "general"
        }
        ocr_intents = {"text_reading", "scene_description", "general"}

        result = {
            "intent": intent,
            "confidence": confidence,
            "method": method,
            "requires_camera": intent in camera_intents,
            "requires_ocr": intent in ocr_intents,
            "requires_detection": intent in {
                "scene_description", "object_query",
                "obstacle_detection", "navigation", "general"
            },
            "original_question": question,
        }

        logger.info(
            f"Intent: {intent} (conf={confidence}, method={method}) "
            f"| Q: {question[:50]}..."
        )
        return result
