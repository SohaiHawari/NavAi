"""
NavAI Backend - FastAPI Application
Main entry point for the AI-powered navigation assistant API.
"""

import json
import ssl
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from models.detector import ObjectDetector
from ocr.ocr_engine import OCREngine
from qna.qna_engine import QnAEngine
from utils.context_builder import ContextBuilder
from utils.intent_recognizer import IntentRecognizer
from utils.image_utils import load_image_from_upload
from utils.history import ConversationHistory
from utils.response_formatter import (
    format_success,
    format_error,
    format_detection_summary,
    format_obstacle_warnings,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("NavAI")

# Global module instances
detector: ObjectDetector = None
ocr_engine: OCREngine = None
qna_engine: QnAEngine = None
context_builder: ContextBuilder = None
intent_recognizer: IntentRecognizer = None
history: ConversationHistory = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global detector, ocr_engine, qna_engine, context_builder, intent_recognizer, history

    logger.info("�� Initializing NavAI modules...")

    # Validate configuration early
    try:
        settings.validate()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.warning(f"⚠️ Config validation: {e} — LLM will use fallback mode")

    # Temporarily bypass SSL for YOLO model auto-download
    _original_ssl_ctx = ssl._create_default_https_context
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

    # Initialize all modules
    detector = ObjectDetector(
        model_path=settings.YOLO_MODEL,
        confidence=settings.YOLO_CONFIDENCE
    )
    logger.info("✅ Object Detector initialized")

    # Restore SSL verification
    ssl._create_default_https_context = _original_ssl_ctx

    ocr_engine = OCREngine(languages=settings.OCR_LANGUAGES)
    logger.info("✅ OCR Engine initialized")

    qna_engine = QnAEngine(
        provider=settings.LLM_PROVIDER,
        api_key=(
            settings.OPENAI_API_KEY
            if settings.LLM_PROVIDER == "openai"
            else settings.GROQ_API_KEY
        ),
        model=(
            settings.OPENAI_MODEL
            if settings.LLM_PROVIDER == "openai"
            else settings.GROQ_MODEL
        ),
    )
    logger.info("✅ QnA Engine initialized")

    context_builder = ContextBuilder()
    intent_recognizer = IntentRecognizer()
    history = ConversationHistory()
    logger.info("✅ All modules ready!")

    yield

    # Cleanup
    logger.info("�� Shutting down NavAI...")


# Create FastAPI app
app = FastAPI(
    title="NavAI API",
    description="AI-Powered Navigation and Voice Q&A Assistant for the Visually Impaired",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "NavAI API",
        "version": "1.0.0",
        "modules": {
            "detector": detector is not None,
            "ocr": ocr_engine is not None,
            "qna": qna_engine is not None,
        },
    }


# ──────────────────────────────────────────────
# Object Detection Endpoint
# ──────────────────────────────────────────────
@app.post("/detect", tags=["Vision"])
async def detect_objects(image: UploadFile = File(...)):
    """
    Detect objects in an uploaded image using YOLOv8.

    Returns detected objects with labels, confidence scores,
    and spatial positions (left/center/right).
    """
    start = time.time()
    try:
        img = await load_image_from_upload(image)
        results = detector.detect(img)
        latency = round((time.time() - start) * 1000, 2)

        return JSONResponse(format_success(
            data={
                "detections": results,
                "count": len(results),
                "summary": format_detection_summary(results),
            },
            latency_ms=latency,
        ))
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# OCR Endpoint
# ──────────────────────────────────────────────
@app.post("/ocr", tags=["Vision"])
async def extract_text(image: UploadFile = File(...)):
    """
    Extract text from an uploaded image using EasyOCR.

    Returns detected text with confidence scores.
    """
    start = time.time()
    try:
        img = await load_image_from_upload(image)
        results = ocr_engine.extract_text(img)
        latency = round((time.time() - start) * 1000, 2)

        return JSONResponse(format_success(
            data={
                "texts": results,
                "count": len(results),
                "combined_text": " ".join(r["text"] for r in results),
            },
            latency_ms=latency,
        ))
    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# QnA Endpoint
# ──────────────────────────────────────────────
@app.post("/qna", tags=["AI"])
async def answer_question(
    question: str = Form(...),
    context: str = Form(...),
):
    """
    Generate a natural language answer based on the question and visual context.

    - **question**: The user's spoken question
    - **context**: JSON string of detected objects and text
    """
    start = time.time()
    try:
        answer = await qna_engine.generate_answer(question, context)
        latency = round((time.time() - start) * 1000, 2)

        return JSONResponse(format_success(
            data={
                "question": question,
                "answer": answer,
            },
            latency_ms=latency,
        ))
    except Exception as e:
        logger.error(f"QnA error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# Combined Pipeline Endpoint (MAIN)
# ──────────────────────────────────────────────
@app.post("/process", tags=["Pipeline"])
async def process_query(
    image: UploadFile = File(...),
    question: str = Form(...),
):
    """
    Complete NavAI pipeline:
    1. Recognize intent from question
    2. Detect objects in image (YOLOv8)
    3. Extract text via OCR
    4. Build structured context
    5. Generate AI answer
    6. Store in conversation history
    7. Return formatted response

    This is the primary endpoint used by the mobile app.
    """
    start = time.time()
    try:
        # Step 1: Recognize intent
        intent = intent_recognizer.recognize(question)
        logger.info(f"�� Intent: {intent['intent']} | Question: {question}")

        # Step 2: Load image
        img = await load_image_from_upload(image)

        # Step 3: Run detection & OCR based on intent
        detections = []
        ocr_results = []

        if intent["intent"] in ["scene_description", "object_query", "obstacle_detection", "navigation", "general"]:
            detections = detector.detect(img)
            logger.info(f"�� Detected {len(detections)} objects")

        if intent["intent"] in ["text_reading", "scene_description", "navigation", "general"]:
            ocr_results = ocr_engine.extract_text(img)
            logger.info(f"�� Extracted {len(ocr_results)} text regions")

        # Step 4: Build context
        context = context_builder.build(
            detections=detections,
            ocr_results=ocr_results,
            intent=intent,
        )
        logger.info(f"�� Context: {context['summary']}")

        # Step 5: Generate answer
        answer = await qna_engine.generate_answer(question, json.dumps(context, default=str))

        # Step 6: Calculate metrics
        latency = round((time.time() - start) * 1000, 2)

        # Step 7: Store in history
        history.add_entry(
            question=question,
            answer=answer,
            intent=intent,
            detection_count=len(detections),
            ocr_count=len(ocr_results),
            latency_ms=latency,
        )

        return JSONResponse(format_success(
            data={
                "intent": intent,
                "detections": detections,
                "ocr_texts": ocr_results,
                "context": context,
                "question": question,
                "answer": answer,
                "detection_summary": format_detection_summary(detections),
                "obstacle_warnings": format_obstacle_warnings(context.get("obstacles", [])),
            },
            latency_ms=latency,
        ))

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        latency = round((time.time() - start) * 1000, 2)
        return JSONResponse(
            format_error(str(e), latency_ms=latency),
            status_code=500,
        )


# ──────────────────────────────────────────────
# Intent Recognition Endpoint
# ──────────────────────────────────────────────
@app.post("/intent", tags=["NLP"])
async def recognize_intent(question: str = Form(...)):
    """Recognize the intent of a user question."""
    intent = intent_recognizer.recognize(question)
    return JSONResponse(format_success(data={"intent": intent}))


# ──────────────────────────────────────────────
# Conversation History Endpoints
# ──────────────────────────────────────────────
@app.get("/history", tags=["History"])
async def get_history(count: int = 10):
    """Get recent conversation history."""
    entries = history.get_recent(count)
    summary = history.get_summary()
    return JSONResponse(format_success(
        data={"entries": entries, "summary": summary}
    ))


@app.delete("/history", tags=["History"])
async def clear_history():
    """Clear conversation history."""
    history.clear()
    qna_engine.clear_history()
    return JSONResponse(format_success(
        data={"message": "History cleared"},
        message="History cleared successfully",
    ))


# ──────────────────────────────────────────────
# Obstacle Check Endpoint
# ──────────────────────────────────────────────
@app.post("/obstacles", tags=["Safety"])
async def check_obstacles(image: UploadFile = File(...)):
    """
    Quickly check for obstacles in the user's path.

    Focuses on objects in the center zone that are close.
    Designed for fast safety checks.
    """
    start = time.time()
    try:
        img = await load_image_from_upload(image)
        obstacles = detector.detect_obstacles(img)
        latency = round((time.time() - start) * 1000, 2)

        warning_text = format_obstacle_warnings(obstacles)

        return JSONResponse(format_success(
            data={
                "obstacles": obstacles,
                "count": len(obstacles),
                "warning": warning_text or "Path appears clear.",
                "is_safe": len(obstacles) == 0,
            },
            latency_ms=latency,
        ))
    except Exception as e:
        logger.error(f"Obstacle check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# Run Server
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
