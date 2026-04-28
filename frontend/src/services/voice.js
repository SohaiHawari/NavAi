/**
 * NavAI - Voice Recognition Service
 * Wraps @react-native-voice/voice for speech-to-text.
 * Falls back to simulated demo input when Voice module is unavailable
 * (e.g., in Expo Go or web).
 */

let Voice = null;
try {
  Voice = require("@react-native-voice/voice").default;
} catch (e) {
  // Native module unavailable (Expo Go / web) — demo mode will be used
  console.log("Native Voice module unavailable, using demo mode");
}

// Demo questions used when native STT is unavailable
const DEMO_QUESTIONS = [
  "What is in front of me?",
  "Is there a chair nearby?",
  "Read the sign for me",
  "Is the path clear?",
  "Describe my surroundings",
  "Do you see any person?",
  "What does the board say?",
  "Can I walk forward safely?",
  "How many objects are there?",
  "What is to my left?",
];

class VoiceService {
  constructor() {
    this.isListening = false;
    this.isAvailable = !!Voice;
    this.onResultCallback = null;
    this.onErrorCallback = null;
    this.onStartCallback = null;
    this.onEndCallback = null;

    if (this.isAvailable) {
      this._setupListeners();
    }
  }

  /**
   * Set up native voice recognition event listeners.
   */
  _setupListeners() {
    Voice.onSpeechStart = () => {
      this.isListening = true;
      if (this.onStartCallback) this.onStartCallback();
    };

    Voice.onSpeechEnd = () => {
      this.isListening = false;
      if (this.onEndCallback) this.onEndCallback();
    };

    Voice.onSpeechResults = (event) => {
      const results = event?.value || [];
      if (results.length > 0 && this.onResultCallback) {
        this.onResultCallback(results[0]); // Best result
      }
    };

    Voice.onSpeechError = (event) => {
      this.isListening = false;
      console.error("Voice error:", event?.error);
      if (this.onErrorCallback) this.onErrorCallback(event?.error);
    };
  }

  /**
   * Register event callbacks.
   */
  onResult(callback) {
    this.onResultCallback = callback;
    return this;
  }

  onError(callback) {
    this.onErrorCallback = callback;
    return this;
  }

  onStart(callback) {
    this.onStartCallback = callback;
    return this;
  }

  onEnd(callback) {
    this.onEndCallback = callback;
    return this;
  }

  /**
   * Start listening for speech.
   * Uses native STT if available; falls back to demo mode.
   */
  async start(language = "en-US") {
    if (this.isAvailable) {
      try {
        await Voice.start(language);
        this.isListening = true;
      } catch (e) {
        console.error("Failed to start voice:", e);
        this._fallbackDemo();
      }
    } else {
      this._fallbackDemo();
    }
  }

  /**
   * Stop listening.
   */
  async stop() {
    if (this.isAvailable && this.isListening) {
      try {
        await Voice.stop();
      } catch (e) {
        console.error("Failed to stop voice:", e);
      }
    }
    this.isListening = false;
  }

  /**
   * Cancel listening without processing.
   */
  async cancel() {
    if (this.isAvailable) {
      try {
        await Voice.cancel();
      } catch (e) {
        console.error("Failed to cancel voice:", e);
      }
    }
    this.isListening = false;
  }

  /**
   * Cleanup listeners on unmount.
   */
  async destroy() {
    if (this.isAvailable) {
      try {
        await Voice.destroy();
      } catch (e) {
        // Ignore cleanup errors
      }
    }
    this.onResultCallback = null;
    this.onErrorCallback = null;
    this.onStartCallback = null;
    this.onEndCallback = null;
  }

  /**
   * Simulate voice recognition with a random demo question.
   * Used in Expo Go or when native STT is unavailable.
   */
  _fallbackDemo() {
    this.isListening = true;
    if (this.onStartCallback) this.onStartCallback();

    // Simulate listening delay
    setTimeout(() => {
      const randomQ =
        DEMO_QUESTIONS[Math.floor(Math.random() * DEMO_QUESTIONS.length)];
      this.isListening = false;

      if (this.onResultCallback) this.onResultCallback(randomQ);
      if (this.onEndCallback) this.onEndCallback();
    }, 1500);
  }
}

// Singleton export
export default new VoiceService();
