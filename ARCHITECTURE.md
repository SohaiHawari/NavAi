# NavAI - System Architecture & Flow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOBILE APP (React Native)                │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Wake Word│→ │   STT    │→ │  Camera  │→ │   API Call   │  │
│  │ Detector │  │ (Voice)  │  │ Capture  │  │  to Backend  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────┬───────┘  │
│                                                     │          │
│  ┌──────────┐  ┌──────────────────────────────────┐ │          │
│  │   TTS    │← │  Display Answer + Status Update  │←┘          │
│  │ (Speak)  │  └──────────────────────────────────┘            │
│  └──────────┘                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND SERVER (FastAPI)                     │
│                                                                 │
│  ┌──────────────┐                                              │
│  │  /process    │  ← Main Pipeline Endpoint                    │
│  │  endpoint    │                                              │
│  └──────┬───────┘                                              │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                              │
│  │   Intent     │  Classifies question into:                   │
│  │ Recognizer   │  scene_description / object_query /          │
│  │              │  text_reading / obstacle_detection            │
│  └──────┬───────┘                                              │
│         │                                                       │
│    ┌────┴────┐                                                  │
│    ▼         ▼                                                  │
│  ┌──────┐ ┌──────┐                                             │
│  │ YOLO │ │ OCR  │  Run in parallel based on intent            │
│  │ v8   │ │Easy  │                                             │
│  └──┬───┘ └──┬───┘                                             │
│     │        │                                                  │
│     ▼        ▼                                                  │
│  ┌──────────────┐                                              │
│  │   Context    │  Combines: objects + text + positions         │
│  │   Builder    │  Outputs structured JSON                     │
│  └──────┬───────┘                                              │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                              │
│  │  QnA Engine  │  LLM generates natural answer                │
│  │ (Groq/OpenAI)│  Fallback: rule-based response               │
│  └──────┬───────┘                                              │
│         │                                                       │
│    ┌────┴────┐                                                  │
│    ▼         ▼                                                  │
│  ┌───────┐ ┌──────────┐                                        │
│  │History│ │ Response  │  Stores interactions + formats output  │
│  │Manager│ │ Formatter │                                        │
│  └───────┘ └──────────┘                                        │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                              │
│  │  JSON        │  Returns: answer, detections, latency        │
│  │  Response    │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Pipeline Flow

```
Step 1: WAKE WORD DETECTION
   User says "Hey NavAI"
   → Porcupine detects wake word (offline)
   → Activates listening mode
   
Step 2: SPEECH-TO-TEXT (STT)
   User speaks question: "What is in front of me?"
   → Google Speech API / Device native STT
   → Output: text string
   
Step 3: INTENT RECOGNITION
   Input: "What is in front of me?"
   → Regex pattern matching (Phase 1)
   → Keyword scoring (Phase 2)
   → Output: { intent: "scene_description", confidence: 0.9 }

Step 4: CAMERA CAPTURE
   → Auto-trigger camera based on intent
   → Capture single frame (JPEG, quality 0.7)
   → Send to backend with question

Step 5: OBJECT DETECTION (YOLOv8)
   Input: captured image
   → YOLOv8 nano model inference
   → Bounding boxes + class labels
   → Spatial position (left/center/right)
   → Distance estimate (close/medium/far)
   → Output: [{ label: "person", position: "center", distance: "close" }]

Step 6: OCR TEXT EXTRACTION (EasyOCR)
   Input: captured image
   → EasyOCR multi-language recognition
   → Extract text from signs/labels
   → Output: [{ text: "EXIT", position: "center" }]

Step 7: CONTEXT BUILDING
   Input: detections + OCR results + intent
   → Combine into structured JSON
   → Identify obstacles (center + close)
   → Output: {
       objects: [...],
       texts: [...],
       positions: { person: "center" },
       obstacles: [...]
     }

Step 8: AI QnA GENERATION
   Input: user question + context JSON
   → LLM prompt with system instructions
   → Generate concise, helpful answer
   → Fallback: rule-based description
   → Output: "A person is standing in front of you..."

Step 9: HISTORY & FORMATTING
   → Store query/answer in ConversationHistory
   → Format response via ResponseFormatter
   → Add detection_summary and obstacle_warnings

Step 10: TEXT-TO-SPEECH (TTS)
   Input: answer text
   → Device native TTS engine
   → Spoken audio output to user
```

## Module Dependency Diagram

```
                    ┌─────────┐
                    │  main.py│
                    │ (FastAPI│
                    │  App)   │
                    └────┬────┘
           ┌─────────┬──┴──┬──────────┬───────────┐
           ▼         ▼     ▼          ▼           ▼
     ┌──────────┐ ┌─────┐ ┌────┐ ┌───────┐ ┌─────────┐
     │ detector │ │ ocr │ │qna │ │ utils │ │ speech  │
     │ (YOLO)   │ │     │ │    │ │       │ │ (desktop│
     └──────────┘ └─────┘ └────┘ └───┬───┘ │ only)   │
                                      │     └─────────┘
                  ┌───────────┬───────┼───────────┬───────────┐
                  ▼           ▼       ▼           ▼           ▼
            ┌──────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
            │ context  │ │ intent │ │  image   │ │ history │ │ response │
            │ builder  │ │ recog. │ │  utils   │ │ manager │ │ formatter│
            └──────────┘ └────────┘ └──────────┘ └─────────┘ └──────────┘
```

## Frontend Component Architecture

```
                        ┌─────────┐
                        │  App.js │
                        └────┬────┘
          ┌──────────┬───────┼──────────┬──────────────┐
          ▼          ▼       ▼          ▼              ▼
    ┌──────────┐ ┌───────┐ ┌────────┐ ┌──────────┐ ┌───────────┐
    │  TopBar  │ │Status │ │Answer  │ │  Quick   │ │ Onboarding│
    │          │ │Badge  │ │Card    │ │ Actions  │ │ Overlay   │
    └──────────┘ └───────┘ └────────┘ └──────────┘ └───────────┘
          ▲                                    ▲
          │          ┌──────────┐              │
          │          │MicButton │              │
          │          └──────────┘              │
          │                                    │
    ┌─────┴───────────────────────────────────┴───┐
    │              Services Layer                   │
    │  ┌────────────────┐  ┌─────────────────────┐ │
    │  │  api.js        │  │  voice.js           │ │
    │  │  (NavAIService)│  │  (VoiceService)     │ │
    │  └────────────────┘  └─────────────────────┘ │
    └─────────────────────────────────────────────────┘
```

## API Endpoints (9 total)

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/` | GET | Health check | — | Server status + module health |
| `/process` | POST | **Main pipeline** | image + question | Full result with answer |
| `/detect` | POST | Object detection | image | Detections with positions |
| `/ocr` | POST | Text extraction | image | Extracted text regions |
| `/qna` | POST | Q&A generation | question + context | Natural language answer |
| `/intent` | POST | Intent recognition | question | Intent + confidence |
| `/obstacles` | POST | Safety check | image | Obstacle warnings |
| `/history` | GET | Get history | count (query) | Recent conversations |
| `/history` | DELETE | Clear history | — | Confirmation |

## Data Flow Example

```
User: "What is in front of me?"

→ Intent: scene_description (conf: 0.90)

→ YOLO detections:
  [person @ center, close, conf: 0.92]
  [chair @ right, medium, conf: 0.85]

→ OCR results:
  ["EXIT" @ center, conf: 0.95]

→ Context JSON:
  {
    "objects": [
      {"label": "person", "position": "center", "distance": "close"},
      {"label": "chair", "position": "right", "distance": "medium"}
    ],
    "texts": [{"text": "EXIT", "position": "center"}],
    "positions": {"person": "center", "chair": "right"},
    "obstacles": [{"label": "person", "distance": "close"}]
  }

→ LLM Answer:
  "A person is standing right in front of you, quite close.
   There's a chair to your right. I can also see an EXIT sign ahead."

→ History: entry stored (question, answer, intent, latency)
→ Response: formatted with detection_summary + obstacle_warnings
→ TTS speaks the answer to the user
```
