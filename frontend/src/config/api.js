/**
 * NavAI - API Configuration
 * Backend server connection settings.
 */

// ⚠️ CHANGE THIS to your backend server IP address
// Use your computer's local IP when testing on a real device
// Use 'localhost' or '10.0.2.2' for Android emulator
const API_BASE_URL = "http://10.30.53.123:8000";

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  ENDPOINTS: {
    HEALTH: "/",
    DETECT: "/detect",
    OCR: "/ocr",
    QNA: "/qna",
    PROCESS: "/process",
    INTENT: "/intent",
  },
  TIMEOUT: 30000, // 30 seconds (extra time for tunnel + AI processing)
};

export default API_CONFIG;
