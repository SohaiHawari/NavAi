# �� NavAI: Hybrid AI-Powered Navigation & Voice Q&A Assistant

> **For the Visually Impaired** — Real-time object detection, text reading, and intelligent voice responses.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![React Native](https://img.shields.io/badge/React_Native-Expo-purple?logo=react)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-yellow)
![License](https://img.shields.io/badge/License-MIT-red)

---

## �� Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Screenshots](#screenshots)
- [Performance](#performance)

---

## �� Overview

NavAI is a mobile application that helps visually impaired users understand their surroundings through voice interaction. Users can ask questions like *"What is in front of me?"* or *"Read this sign"*, and the system responds with an intelligent spoken answer.

**Pipeline:** Voice → STT → Intent Recognition → Camera → YOLO + OCR → Context → LLM → TTS

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| �� Voice Commands | Speak questions naturally |
| �� Real-time Vision | YOLOv8 object detection |
| �� Text Reading | EasyOCR for signs & labels |
| �� AI Answers | LLM-powered natural responses |
| �� Spoken Output | Text-to-Speech feedback |
| ⚠️ Obstacle Alerts | Warns about nearby obstacles |
| �� Multi-language | English + Hindi support |
| �� Context Memory | Remembers previous interactions |
| �� Offline Fallback | Works without internet (limited) |

---

## ��️ Architecture

```
User Voice → STT → Intent Recognition → Camera Capture
    ↓
  [YOLOv8 Detection] + [EasyOCR]
    ↓
  Context Builder → LLM Q&A Engine → TTS → Spoken Answer
```

---

## ��️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React Native (Expo) |
| **Backend** | Python FastAPI |
| **Object Detection** | YOLOv8 (Ultralytics) |
| **OCR** | EasyOCR |
| **LLM** | Groq (LLaMA 3.1) / OpenAI |
| **STT/TTS** | Native device APIs |
| **Intent Recognition** | Hybrid regex + keyword NLP |

---

## �� Project Structure

```
NavAI/
├── backend/
│   ├── main.py               # FastAPI application (8 endpoint handlers)
│   ├── config.py              # Configuration & env loading
│   ├── requirements.txt       # Python dependencies
│   ├── test_pipeline.py       # Comprehensive test suite (8 suites)
│   ├── .env.example           # Environment template
│   ├── models/
│   │   └── detector.py        # YOLOv8 object detection + obstacle check
│   ├── ocr/
│   │   └── ocr_engine.py      # EasyOCR text extraction
│   ├── qna/
│   │   └── qna_engine.py      # LLM Q&A engine + fallback
│   ├── speech/
│   │   └── speech_engine.py   # STT/TTS (desktop testing)
│   └── utils/
│       ├── context_builder.py  # Context JSON builder
│       ├── intent_recognizer.py # Hybrid intent classification
│       ├── image_utils.py      # Image processing utilities
│       ├── history.py          # Conversation history manager
│       └── response_formatter.py # API response formatting
├── frontend/
│   ├── App.js                 # Main React Native app
│   ├── package.json           # Node dependencies
│   ├── app.json               # Expo configuration
│   ├── babel.config.js        # Babel configuration
│   ├── index.js               # Entry point
│   └── src/
│       ├── config/api.js      # Backend URL config
│       ├── services/
│       │   ├── api.js         # API service layer
│       │   └── voice.js       # Voice recognition service
│       └── components/
│           ├── MicButton.js       # Animated mic button
│           ├── StatusBadge.js     # State indicator
│           ├── AnswerCard.js      # AI response display
│           ├── TopBar.js          # Header with branding
│           ├── QuickActions.js    # Shortcut action buttons
│           └── OnboardingOverlay.js # First-launch guide
├── .gitignore                 # Git ignore rules
├── SETUP_GUIDE.md             # Installation guide
├── ARCHITECTURE.md            # System architecture
├── TEST_CASES.md              # Test cases & metrics
├── VIVA_PREPARATION.md        # Viva Q&A guide
└── README.md                  # This file
```

---

## �� Quick Start

### Backend
```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env  # Add your Groq API key
python main.py
```

### Frontend
```bash
cd frontend
npm install
npx expo start
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.

---

## �� API Reference

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/` | GET | — | Health status |
| `/process` | POST | image + question | Full pipeline result |
| `/detect` | POST | image | Object detections |
| `/ocr` | POST | image | Extracted text |
| `/qna` | POST | question + context | AI answer |
| `/intent` | POST | question | Recognized intent |
| `/obstacles` | POST | image | Obstacle safety check |
| `/history` | GET | count (query param) | Conversation history |
| `/history` | DELETE | — | Clear history |

---

## �� Performance

| Metric | Value |
|--------|-------|
| Object Detection (mAP@0.5) | ~78% |
| OCR Accuracy | ~90% |
| Intent Recognition | 95% |
| End-to-End Latency | < 3 sec |
| Detection FPS (CPU) | ~8 FPS |

---

## �� Team

**Final Year B.E. Project — 2025-26**

---

## �� License

This project is for academic purposes. MIT License.
