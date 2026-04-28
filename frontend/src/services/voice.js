/**
 * NavAI - Voice Recognition Service
 * Wraps @react-native-voice/voice for speech-to-text.
 * Falls back to simulated demo input when Voice module is unavailable
 * (e.g., in Expo Go or web).
 */

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
    this.isAvailable = false;
    this.Voice = null;
    this.onResultCallback = null;
    this.onErrorCallback = null;
    this.onStartCallback = null;
    this.onEndCallback = null;

    this._initVoice();
  }

  _initVoice() {
    try {
      const mod = require("@react-native-voice/voice");
      const V = mod?.default || mod;
      if (V && typeof V.start === "function" && typeof V.onSpeechStart !== "undefined") {
        this.Voice = V;
        this.isAvailable = true;
        this._setupListeners();
      }
    } catch (e) {
      // Native module not available
    }
    if (!this.isAvailable) {
      console.log("Voice: using demo mode (native STT unavailable)");
    }
  }

  _setupListeners() {
    try {
      this.Voice.onSpeechStart = () => {
        this.isListening = true;
        if (this.onStartCallback) this.onStartCallback();
      };

      this.Voice.onSpeechEnd = () => {
        this.isListening = false;
        if (this.onEndCallback) this.onEndCallback();
      };

      this.Voice.onSpeechResults = (event) => {
        const results = event?.value || [];
        if (results.length > 0 && this.onResultCallback) {
          this.onResultCallback(results[0]);
        }
      };

      this.Voice.onSpeechError = (event) => {
        this.isListening = false;
        console.error("Voice error:", event?.error);
        if (this.onErrorCallback) this.onErrorCallback(event?.error);
      };
    } catch (e) {
      this.isAvailable = false;
      this.Voice = null;
    }
  }

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

  async start(language = "en-US") {
    if (this.isAvailable && this.Voice) {
      try {
        await this.Voice.start(language);
        this.isListening = true;
      } catch (e) {
        console.log("Voice native failed, switching to demo mode");
        this.isAvailable = false;
        this.Voice = null;
        this._fallbackDemo();
      }
    } else {
      this._fallbackDemo();
    }
  }

  async stop() {
    if (this.isAvailable && this.Voice && this.isListening) {
      try {
        await this.Voice.stop();
      } catch (e) {
        // ignore
      }
    }
    this.isListening = false;
  }

  async cancel() {
    if (this.isAvailable && this.Voice) {
      try {
        await this.Voice.cancel();
      } catch (e) {
        // ignore
      }
    }
    this.isListening = false;
  }

  async destroy() {
    if (this.isAvailable && this.Voice) {
      try {
        await this.Voice.destroy();
      } catch (e) {
        // ignore
      }
    }
    this.onResultCallback = null;
    this.onErrorCallback = null;
    this.onStartCallback = null;
    this.onEndCallback = null;
  }

  _fallbackDemo() {
    this.isListening = true;
    if (this.onStartCallback) this.onStartCallback();

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
