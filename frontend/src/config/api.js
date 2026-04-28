/**
 * NavAI - API Configuration
 * Backend server connection settings.
 *
 * To configure: Set your backend IP before starting the app.
 * - Real device: Use your computer's LAN IP (e.g., 192.168.1.x)
 * - Android emulator: Use '10.0.2.2'
 * - iOS simulator: Use 'localhost'
 */

// Change this IP to your backend server's LAN IP
const API_BASE_URL = "http://10.196.233.82:8000";

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
