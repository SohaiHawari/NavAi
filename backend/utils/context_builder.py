"""
NavAI - Context Builder Module
Combines detection and OCR results into a structured context JSON.
"""

import logging
from typing import Optional

logger = logging.getLogger("NavAI.ContextBuilder")


class ContextBuilder:
    """
    Builds structured context from detection and OCR results.

    Combines object detections, extracted text, and spatial information
    into a unified context dictionary for the QnA engine.
    """

    def __init__(self):
        """Initialize the context builder."""
        self.previous_context: Optional[dict] = None  # Memory feature

    def build(
        self,
        detections: list,
        ocr_results: list,
        intent: dict = None,
    ) -> dict:
        """
        Build structured context JSON from vision module outputs.

        Args:
            detections: List of object detection results
            ocr_results: List of OCR text results
            intent: Recognized intent dictionary

        Returns:
            Structured context dictionary:
            {
                "objects": [
                    {"label": "person", "position": "center", "distance": "close"}
                ],
                "texts": [
                    {"text": "EXIT", "position": "center"}
                ],
                "positions": {
                    "person": "center",
                    "chair": "right"
                },
                "obstacles": [...],
                "summary": "2 objects detected, 1 text region found",
                "intent": "scene_description"
            }
        """
        context = {
            "objects": [],
            "texts": [],
            "positions": {},
            "obstacles": [],
            "summary": "",
            "intent": intent.get("intent", "general") if intent else "general",
        }

        # Process object detections
        for det in detections:
            obj = {
                "label": det["label"],
                "position": det.get("position", "unknown"),
                "distance": det.get("distance", "unknown"),
                "confidence": det.get("confidence", 0),
            }
            context["objects"].append(obj)

            # Build position map
            label = det["label"]
            if label not in context["positions"]:
                context["positions"][label] = det.get("position", "unknown")

            # Check for obstacles (center + close)
            if (
                det.get("position") == "center"
                and det.get("distance") in ["very close", "close"]
            ):
                context["obstacles"].append({
                    "label": label,
                    "distance": det.get("distance"),
                    "warning": f"Caution: {label} directly ahead, {det.get('distance')}!",
                })

        # Process OCR results
        for ocr in ocr_results:
            text_entry = {
                "text": ocr.get("text", ""),
                "position": ocr.get("position", "unknown"),
                "confidence": ocr.get("confidence", 0),
            }
            context["texts"].append(text_entry)

        # Generate summary
        obj_count = len(context["objects"])
        text_count = len(context["texts"])
        obstacle_count = len(context["obstacles"])

        summary_parts = []
        if obj_count > 0:
            summary_parts.append(f"{obj_count} object(s) detected")
        if text_count > 0:
            summary_parts.append(f"{text_count} text region(s) found")
        if obstacle_count > 0:
            summary_parts.append(f"⚠️ {obstacle_count} obstacle(s) in path")

        context["summary"] = ", ".join(summary_parts) if summary_parts else "No objects or text detected"

        # Store for memory/context awareness
        self.previous_context = context

        logger.info(f"Context built: {context['summary']}")
        return context

    def get_changes(self, new_context: dict) -> dict:
        """
        Compare with previous context to detect changes.
        Useful for the memory-based context awareness bonus feature.

        Args:
            new_context: Newly built context

        Returns:
            Dictionary of changes (new objects, removed objects)
        """
        if self.previous_context is None:
            return {"new_objects": [], "removed_objects": [], "changed": False}

        prev_labels = set(
            obj["label"] for obj in self.previous_context.get("objects", [])
        )
        curr_labels = set(
            obj["label"] for obj in new_context.get("objects", [])
        )

        new_objects = list(curr_labels - prev_labels)
        removed_objects = list(prev_labels - curr_labels)

        return {
            "new_objects": new_objects,
            "removed_objects": removed_objects,
            "changed": bool(new_objects or removed_objects),
        }
