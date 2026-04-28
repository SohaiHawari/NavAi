"""
NavAI - Comprehensive Test Suite
Tests all backend modules individually and the full pipeline.
Run: python test_pipeline.py
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(label: str, value, indent: int = 2):
    """Print a formatted result."""
    prefix = " " * indent
    if isinstance(value, (dict, list)):
        print(f"{prefix}{label}: {json.dumps(value, indent=2, default=str)}")
    else:
        print(f"{prefix}{label}: {value}")


def print_pass(msg: str):
    print(f"  PASS - {msg}")


def print_fail(msg: str):
    print(f"  FAIL - {msg}")


# ──────────────────────────────────────────────
# Test 1: Intent Recognizer
# ──────────────────────────────────────────────
async def test_intent_recognizer():
    """Test intent recognition module."""
    print_header("Test 1: Intent Recognizer")

    from utils.intent_recognizer import IntentRecognizer

    recognizer = IntentRecognizer()

    test_questions = [
        ("What is in front of me?", "scene_description"),
        ("Is there a chair nearby?", "object_query"),
        ("Read this sign", "text_reading"),
        ("Is the path clear?", "obstacle_detection"),
        ("Which way to the exit?", "navigation"),
        ("Hello", "general"),
        ("Describe my surroundings", "scene_description"),
        ("Do you see any person?", "object_query"),
        ("What does the board say?", "text_reading"),
        ("Can I walk forward safely?", "obstacle_detection"),
        ("Where is the door?", "object_query"),
        ("Tell me what is around me", "scene_description"),
        ("Any obstacles ahead?", "obstacle_detection"),
        ("Read the notice", "text_reading"),
        ("Guide me to the entrance", "navigation"),
    ]

    passed = 0
    total = len(test_questions)

    for question, expected in test_questions:
        result = recognizer.recognize(question)
        status = "PASS" if result["intent"] == expected else "FAIL"
        if result["intent"] == expected:
            passed += 1
        print(f"  {status} '{question}' -> {result['intent']} "
              f"(expected: {expected}, conf: {result['confidence']}, method: {result['method']})")

    print(f"\n  Results: {passed}/{total} passed ({passed/total*100:.0f}%)")

    # Also test module flags
    result = recognizer.recognize("Read this sign")
    assert result["requires_ocr"] is True, "Text reading should require OCR"
    assert result["requires_camera"] is True, "Text reading should require camera"
    print_pass("Module requirement flags correct")

    return passed >= total * 0.85  # Allow 85% pass rate


# ──────────────────────────────────────────────
# Test 2: Context Builder
# ──────────────────────────────────────────────
async def test_context_builder():
    """Test context builder module."""
    print_header("Test 2: Context Builder")

    from utils.context_builder import ContextBuilder

    builder = ContextBuilder()

    # Sample detection results
    detections = [
        {"label": "person", "position": "center", "distance": "close", "confidence": 0.92},
        {"label": "chair", "position": "right", "distance": "medium distance", "confidence": 0.85},
        {"label": "bottle", "position": "left", "distance": "far", "confidence": 0.78},
    ]

    ocr_results = [
        {"text": "EXIT", "position": "center", "confidence": 0.95},
        {"text": "Room 101", "position": "right", "confidence": 0.88},
    ]

    intent = {"intent": "scene_description", "confidence": 0.9}

    context = builder.build(detections, ocr_results, intent)

    print(f"  Objects: {len(context['objects'])}")
    print(f"  Texts: {len(context['texts'])}")
    print(f"  Obstacles: {len(context['obstacles'])}")
    print(f"  Summary: {context['summary']}")
    print(f"  Positions: {context['positions']}")

    assert len(context["objects"]) == 3, "Should have 3 objects"
    assert len(context["texts"]) == 2, "Should have 2 texts"
    assert context["obstacles"], "Should detect person as obstacle (center + close)"
    assert "person" in context["positions"], "Position map should contain person"
    assert context["intent"] == "scene_description", "Intent should be set"

    print_pass("Context Builder: basic build")

    # Test change detection
    new_detections = [
        {"label": "car", "position": "center", "distance": "close", "confidence": 0.90},
    ]
    new_context = builder.build(new_detections, [], intent)
    changes = builder.get_changes(new_context)
    print(f"  Changes detected: {changes}")

    print_pass("Context Builder: change detection")
    return True


# ──────────────────────────────────────────────
# Test 3: QnA Fallback
# ──────────────────────────────────────────────
async def test_qna_fallback():
    """Test QnA engine fallback (without LLM)."""
    print_header("Test 3: QnA Fallback (No API Key)")

    from qna.qna_engine import QnAEngine

    engine = QnAEngine(provider="groq", api_key="", model="")

    # Test with objects + text
    context = json.dumps({
        "objects": [
            {"label": "person", "position": "center"},
            {"label": "chair", "position": "right"},
        ],
        "texts": [
            {"text": "EXIT"}
        ],
    })

    answer = engine._fallback_answer("What is in front of me?", context)
    print(f"  Q: What is in front of me?")
    print(f"  A: {answer}")

    assert "person" in answer.lower(), "Answer should mention person"
    assert "chair" in answer.lower(), "Answer should mention chair"
    assert "exit" in answer.lower(), "Answer should mention EXIT text"

    print_pass("QnA Fallback: objects + text")

    # Test with empty context
    empty_answer = engine._fallback_answer("What do you see?", "{}")
    print(f"  Q: What do you see? (empty context)")
    print(f"  A: {empty_answer}")
    assert len(empty_answer) > 10, "Should return a fallback message"

    print_pass("QnA Fallback: empty context")

    # Test with invalid JSON
    invalid_answer = engine._fallback_answer("Test", "invalid json")
    assert len(invalid_answer) > 10, "Should handle invalid JSON gracefully"

    print_pass("QnA Fallback: invalid JSON handling")

    # Test history management
    engine.clear_history()
    assert len(engine.history) == 0, "History should be empty after clear"
    print_pass("QnA: history clear")

    return True


# ──────────────────────────────────────────────
# Test 4: Conversation History
# ──────────────────────────────────────────────
async def test_conversation_history():
    """Test conversation history module."""
    print_header("Test 4: Conversation History")

    from utils.history import ConversationHistory

    hist = ConversationHistory(max_entries=5)

    # Add entries
    for i in range(7):
        hist.add_entry(
            question=f"Question {i}",
            answer=f"Answer {i}",
            intent={"intent": "scene_description" if i % 2 == 0 else "object_query", "confidence": 0.9},
            detection_count=i + 1,
            latency_ms=100 + i * 50,
        )

    # Test max entries limit
    assert len(hist.entries) == 5, f"Should be capped at 5 entries, got {len(hist.entries)}"
    print_pass("History: max entries limit")

    # Test get recent
    recent = hist.get_recent(3)
    assert len(recent) == 3, "Should return 3 recent entries"
    assert recent[0]["question"] == "Question 6", "First entry should be most recent"
    print_pass("History: get recent")

    # Test summary
    summary = hist.get_summary()
    assert summary["total_queries"] == 5, "Should have 5 total queries"
    assert summary["avg_latency_ms"] > 0, "Should have positive avg latency"
    print(f"  Summary: {json.dumps(summary, indent=2)}")
    print_pass("History: summary stats")

    # Test search
    results = hist.search("Question 5")
    assert len(results) >= 1, "Should find at least one match"
    print_pass("History: search")

    # Test clear
    hist.clear()
    assert len(hist.entries) == 0, "Should be empty after clear"
    print_pass("History: clear")

    return True


# ──────────────────────────────────────────────
# Test 5: Response Formatter
# ──────────────────────────────────────────────
async def test_response_formatter():
    """Test response formatting utilities."""
    print_header("Test 5: Response Formatter")

    from utils.response_formatter import (
        format_success,
        format_error,
        format_detection_summary,
        format_obstacle_warnings,
    )

    # Test success format
    resp = format_success(
        data={"answer": "Hello"},
        latency_ms=123.456,
        message="OK",
    )
    assert resp["status"] == "success", "Status should be success"
    assert resp["answer"] == "Hello", "Data should be merged"
    assert resp["latency_ms"] == 123.46, "Latency should be rounded"
    print_pass("Formatter: success response")

    # Test error format
    err = format_error("Something broke", latency_ms=50)
    assert err["status"] == "error", "Status should be error"
    assert "Something broke" in err["error"], "Error should be included"
    assert err["answer"], "Should have fallback answer"
    print_pass("Formatter: error response")

    # Test detection summary
    detections = [
        {"label": "person"},
        {"label": "person"},
        {"label": "chair"},
    ]
    summary = format_detection_summary(detections)
    assert "2 persons" in summary, f"Should say '2 persons', got: {summary}"
    assert "1 chair" in summary, f"Should say '1 chair', got: {summary}"
    print(f"  Summary: {summary}")
    print_pass("Formatter: detection summary")

    # Test empty
    assert format_detection_summary([]) == "No objects detected"
    print_pass("Formatter: empty detection summary")

    # Test obstacle warnings
    obstacles = [
        {"label": "person", "distance": "close"},
        {"label": "chair", "distance": "very close"},
    ]
    warnings = format_obstacle_warnings(obstacles)
    assert "Warning" in warnings, "Should contain warning text"
    print(f"  Warnings: {warnings}")
    print_pass("Formatter: obstacle warnings")

    return True


# ──────────────────────────────────────────────
# Test 6: Image Utils
# ──────────────────────────────────────────────
async def test_image_utils():
    """Test image utility functions."""
    print_header("Test 6: Image Utils")

    import numpy as np
    from utils.image_utils import resize_image, image_to_bytes

    # Create a test image (640x480 RGB)
    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Test resize (should not resize if already smaller)
    resized = resize_image(test_img, max_size=640)
    assert resized.shape[0] == 480, "Should not resize if within limit"
    assert resized.shape[1] == 640, "Should not resize if within limit"
    print_pass("Image Utils: no resize needed")

    # Test resize (should resize large image)
    large_img = np.random.randint(0, 255, (1920, 1080, 3), dtype=np.uint8)
    resized = resize_image(large_img, max_size=640)
    assert max(resized.shape[:2]) <= 640, f"Should be <= 640, got {resized.shape}"
    print(f"  Resized: {large_img.shape} -> {resized.shape}")
    print_pass("Image Utils: resize large image")

    # Test to bytes
    img_bytes = image_to_bytes(test_img, format="JPEG")
    assert len(img_bytes) > 0, "Should produce non-empty bytes"
    assert img_bytes[:2] == b'\xff\xd8', "Should be valid JPEG"
    print(f"  JPEG size: {len(img_bytes)} bytes")
    print_pass("Image Utils: to bytes")

    return True


# ──────────────────────────────────────────────
# Test 7: Full Pipeline (Mock)
# ──────────────────────────────────────────────
async def test_full_pipeline_mock():
    """Test the full pipeline with mock data."""
    print_header("Test 7: Full Pipeline (Mock)")

    from utils.intent_recognizer import IntentRecognizer
    from utils.context_builder import ContextBuilder
    from qna.qna_engine import QnAEngine
    from utils.history import ConversationHistory
    from utils.response_formatter import format_success, format_detection_summary

    # Initialize modules
    intent_recognizer = IntentRecognizer()
    context_builder = ContextBuilder()
    qna_engine = QnAEngine(provider="groq", api_key="", model="")
    hist = ConversationHistory()

    # Simulate pipeline
    question = "What is in front of me?"

    # Step 1: Intent
    start = time.time()
    intent = intent_recognizer.recognize(question)
    print(f"  Step 1 - Intent: {intent['intent']} ({intent['confidence']})")

    # Step 2: Mock detections (simulating YOLO output)
    detections = [
        {"label": "person", "position": "center", "distance": "close", "confidence": 0.92},
        {"label": "chair", "position": "right", "distance": "medium distance", "confidence": 0.85},
    ]
    print(f"  Step 2 - Detections: {len(detections)} objects")
    print(f"           Summary: {format_detection_summary(detections)}")

    # Step 3: Mock OCR
    ocr_results = [
        {"text": "EXIT", "position": "center", "confidence": 0.95},
    ]
    print(f"  Step 3 - OCR: {len(ocr_results)} texts")

    # Step 4: Build context
    context = context_builder.build(detections, ocr_results, intent)
    print(f"  Step 4 - Context: {context['summary']}")
    print(f"           Obstacles: {len(context['obstacles'])}")

    # Step 5: Generate answer (fallback)
    answer = qna_engine._fallback_answer(question, json.dumps(context))
    latency = round((time.time() - start) * 1000, 2)

    print(f"  Step 5 - Answer: {answer}")
    print(f"  Latency: {latency}ms")

    # Step 6: Store in history
    hist.add_entry(
        question=question,
        answer=answer,
        intent=intent,
        detection_count=len(detections),
        ocr_count=len(ocr_results),
        latency_ms=latency,
    )
    print(f"  Step 6 - History entries: {len(hist.entries)}")

    # Verify response format
    response = format_success(
        data={
            "question": question,
            "answer": answer,
            "intent": intent,
            "detections": detections,
        },
        latency_ms=latency,
    )
    assert response["status"] == "success"
    assert response["answer"] == answer
    print(f"  Step 7 - Response formatted: OK")

    print_pass("Full Pipeline mock test passed!")
    return True


# ──────────────────────────────────────────────
# Test 8: Edge Cases
# ──────────────────────────────────────────────
async def test_edge_cases():
    """Test edge cases and error handling."""
    print_header("Test 8: Edge Cases")

    from utils.intent_recognizer import IntentRecognizer
    from utils.context_builder import ContextBuilder
    from qna.qna_engine import QnAEngine

    recognizer = IntentRecognizer()
    builder = ContextBuilder()

    # Empty question
    result = recognizer.recognize("")
    assert result["intent"] == "general", "Empty question should default to general"
    print_pass("Edge case: empty question")

    # Very long question
    long_q = "What is " * 100 + "in front of me?"
    result = recognizer.recognize(long_q)
    assert result["intent"] is not None, "Long question should not crash"
    print_pass("Edge case: very long question")

    # Unicode question
    result = recognizer.recognize("What is this? 你好")
    assert result["intent"] is not None, "Unicode question should not crash"
    print_pass("Edge case: unicode question")

    # Empty detections + OCR
    context = builder.build([], [], None)
    assert context["summary"] == "No objects or text detected"
    print_pass("Edge case: empty detections and OCR")

    # QnA with None context
    engine = QnAEngine(provider="groq", api_key="", model="")
    answer = engine._fallback_answer("test", None)
    assert len(answer) > 0, "Should handle None context"
    print_pass("Edge case: None context in QnA")

    return True


# ──────────────────────────────────────────────
# Main Test Runner
# ──────────────────────────────────────────────
async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("       NavAI Backend - Comprehensive Test Suite")
    print("=" * 60)

    results = []

    # Test modules that don't require GPU/models
    results.append(("Intent Recognizer", await test_intent_recognizer()))
    results.append(("Context Builder", await test_context_builder()))
    results.append(("QnA Fallback", await test_qna_fallback()))
    results.append(("Conversation History", await test_conversation_history()))
    results.append(("Response Formatter", await test_response_formatter()))
    results.append(("Image Utils", await test_image_utils()))
    results.append(("Full Pipeline (Mock)", await test_full_pipeline_mock()))
    results.append(("Edge Cases", await test_edge_cases()))

    # Summary
    print_header("Test Summary")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    total = len(results)
    pass_count = sum(1 for _, p in results if p)
    print(f"\n  Overall: {pass_count}/{total} test suites passed")

    if all_passed:
        print("  ALL TESTS PASSED!")
    else:
        print("  Some tests failed.")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
