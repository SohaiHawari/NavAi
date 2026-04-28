# NavAI - Complete Setup Guide

## Prerequisites

### System Requirements
- **Python** 3.9+ (tested on 3.11 and 3.13)
- **Node.js** 18+ and npm
- **Expo CLI** (installed via npx)
- **Android Studio** (for Android emulator) OR a physical Android/iOS device
- **Git** (optional but recommended)

---

## Step 1: Clone / Navigate to Project

```bash
cd "C:\Users\DELL\Desktop\BE Project\NavAI"
```

---

## Step 2: Backend Setup

### 2.1 Create Python Virtual Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2.2 Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note:** First run will download YOLOv8 weights (~6MB for nano model) and EasyOCR models (~100MB). This is automatic.

### 2.3 Configure Environment Variables
```bash
# Copy the example env file
copy .env.example .env
```

Edit `.env` and add your API key:
```env
# Option A: Use Groq (FREE tier - recommended for students)
LLM_PROVIDER=groq
GROQ_API_KEY=your-key-from-console.groq.com

# Option B: Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-from-platform.openai.com
```

**Getting a FREE Groq API key:**
1. Go to https://console.groq.com
2. Sign up with Google/GitHub
3. Go to API Keys → Create new key
4. Copy and paste into `.env`

> **Note:** The system works WITHOUT an API key using the rule-based fallback engine. Add a key for natural language answers.

### 2.4 Run Tests First
```bash
python test_pipeline.py
```

Expected output: `8/8 test suites passed — ALL TESTS PASSED!`

### 2.5 Start the Backend Server
```bash
python main.py
```

Server starts at: `http://0.0.0.0:8000`
API docs at: `http://localhost:8000/docs`

---

## Step 3: Frontend Setup

### 3.1 Install Dependencies
```bash
cd ../frontend
npm install
```

### 3.2 Configure Backend URL

Edit `src/config/api.js`:
```javascript
// For Android emulator:
const API_BASE_URL = "http://10.0.2.2:8000";

// For physical device (use your PC's local IP):
const API_BASE_URL = "http://192.168.1.XXX:8000";
```

**Find your PC's IP:**
```bash
# Windows
ipconfig

# macOS/Linux
ifconfig
```

### 3.3 Start the App
```bash
npx expo start
```

Then:
- Press `a` for Android emulator
- Scan QR code with Expo Go app on physical device

---

## Step 4: Testing the Full System

1. Start backend: `python main.py` (in backend folder)
2. Start frontend: `npx expo start` (in frontend folder)
3. Open app on device/emulator
4. Complete the onboarding walkthrough (4 steps)
5. Tap the mic button → a demo question is asked automatically
6. Or tap "Describe" / "Read Text" / "Obstacles" quick action buttons
7. The app captures a photo, sends to backend, and speaks the result

---

## Step 5: API Documentation (Swagger)

After starting the backend, visit `http://localhost:8000/docs` to see:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check — verify all modules loaded |
| `/process` | POST | **Main pipeline** — image + question → full result |
| `/detect` | POST | Object detection only |
| `/ocr` | POST | Text extraction only |
| `/qna` | POST | Q&A generation only |
| `/intent` | POST | Intent recognition only |
| `/obstacles` | POST | Quick obstacle/safety check |
| `/history` | GET | View conversation history |
| `/history` | DELETE | Clear conversation history |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server won't start | Check Python version: `python --version` (need 3.9+) |
| YOLO download fails | Check internet connection; model downloads on first run |
| Camera not working | Ensure camera permissions are granted in device settings |
| Can't connect to server | Check IP address in `api.js`; ensure PC and phone are on same WiFi |
| Groq API error | Verify API key at https://console.groq.com |
| pip install fails | Try: `pip install --upgrade pip` then retry |
| "No module named 'groq'" | Run: `pip install groq openai` |
| Tests fail | Ensure you're in the `backend/` directory when running tests |
| Expo build error | Run: `npx expo doctor` to check for issues |
| Voice not working | Native STT requires a physical device; demo mode works in emulator |

---

## Project Structure

```
NavAI/
├── backend/                        # Python FastAPI server
│   ├── main.py                     # 9 API endpoints
│   ├── config.py                   # Environment configuration
│   ├── requirements.txt            # Python dependencies
│   ├── test_pipeline.py            # 8 test suites (run to verify)
│   ├── .env / .env.example         # API keys configuration
│   ├── models/detector.py          # YOLOv8 object detection
│   ├── ocr/ocr_engine.py           # EasyOCR text extraction
│   ├── qna/qna_engine.py           # LLM + fallback Q&A
│   ├── speech/speech_engine.py     # Desktop STT/TTS
│   └── utils/
│       ├── context_builder.py      # Vision context JSON builder
│       ├── intent_recognizer.py    # Hybrid NLP intent classifier
│       ├── image_utils.py          # Image processing helpers
│       ├── history.py              # Conversation memory
│       └── response_formatter.py   # API response formatting
├── frontend/                       # React Native (Expo) app
│   ├── App.js                      # Main app with voice + camera
│   ├── src/components/             # 6 UI components
│   ├── src/services/               # API + Voice services
│   └── src/config/                 # Backend URL config
└── docs/                           # Documentation
    ├── README.md
    ├── ARCHITECTURE.md
    ├── TEST_CASES.md
    ├── SETUP_GUIDE.md
    └── VIVA_PREPARATION.md
```
