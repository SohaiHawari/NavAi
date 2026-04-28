"""
NavAI - Response Formatter
Formats API responses consistently across all endpoints.
"""

import logging
from datetime import datetime

logger = logging.getLogger("NavAI.Formatter")


def format_success(
    data: dict,
    latency_ms: float = 0,
    message: str = "OK",
) -> dict:
    """
    Format a successful API response.

    Args:
        data: Response data dictionary
        latency_ms: Processing latency
        message: Status message

    Returns:
        Formatted response dictionary
    """
    response = {
        "status": "success",
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "latency_ms": round(latency_ms, 2),
        **data,
    }
    return response


def format_error(
    error: str,
    latency_ms: float = 0,
    code: str = "PROCESSING_ERROR",
) -> dict:
    """
    Format an error API response.

    Args:
        error: Error description string
        latency_ms: Processing latency
        code: Error code

    Returns:
        Formatted error response dictionary
    """
    return {
        "status": "error",
        "error_code": code,
        "error": str(error),
        "timestamp": datetime.now().isoformat(),
        "latency_ms": round(latency_ms, 2),
        "answer": "I'm sorry, I couldn't process that right now. Please try again.",
    }


def format_detection_summary(detections: list) -> str:
    """
    Create a human-readable summary from detections.

    Args:
        detections: List of detection dictionaries

    Returns:
        Summary string like "2 persons, 1 chair, 1 bottle"
    """
    if not detections:
        return "No objects detected"

    # Count occurrences of each label
    counts = {}
    for det in detections:
        label = det.get("label", "object")
        counts[label] = counts.get(label, 0) + 1

    parts = []
    for label, count in counts.items():
        if count > 1:
            # Simple pluralization
            plural = label + "s" if not label.endswith("s") else label
            parts.append(f"{count} {plural}")
        else:
            parts.append(f"1 {label}")

    return ", ".join(parts)


def format_obstacle_warnings(obstacles: list) -> str:
    """
    Format obstacle warnings as spoken text.

    Args:
        obstacles: List of obstacle dictionaries

    Returns:
        Warning string suitable for TTS
    """
    if not obstacles:
        return ""

    warnings = []
    for obs in obstacles:
        label = obs.get("label", "obstacle")
        distance = obs.get("distance", "nearby")
        warnings.append(f"Warning: {label} {distance} ahead")

    return ". ".join(warnings) + "."
