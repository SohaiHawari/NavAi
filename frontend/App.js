/**
 * NavAI - Main App Component
 * AI-Powered Navigation & Voice Q&A Assistant for the Visually Impaired
 *
 * Pipeline: Voice → STT → Intent → Camera → YOLO+OCR → Context → LLM → TTS
 */
import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Animated,
  SafeAreaView,
  StatusBar,
  Alert,
  Platform,
  Vibration,
  AccessibilityInfo,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as Speech from "expo-speech";
import * as Haptics from "expo-haptics";
import { MaterialIcons, Ionicons } from "@expo/vector-icons";

// Components
import TopBar from "./src/components/TopBar";
import StatusBadge from "./src/components/StatusBadge";
import AnswerCard from "./src/components/AnswerCard";
import MicButton from "./src/components/MicButton";
import QuickActions from "./src/components/QuickActions";
import OnboardingOverlay from "./src/components/OnboardingOverlay";

// Services
import NavAIService from "./src/services/api";
import VoiceService from "./src/services/voice";

const { width, height } = Dimensions.get("window");

// App States
const STATES = {
  IDLE: "idle",
  LISTENING: "listening",
  PROCESSING: "processing",
  SPEAKING: "speaking",
  ERROR: "error",
};

export default function App() {
  // ─── State ───────────────────────────────────────
  const [appState, setAppState] = useState(STATES.IDLE);
  const [lastAnswer, setLastAnswer] = useState("");
  const [lastQuestion, setLastQuestion] = useState("");
  const [serverOnline, setServerOnline] = useState(false);
  const [detectionCount, setDetectionCount] = useState(0);
  const [ocrCount, setOcrCount] = useState(0);
  const [latency, setLatency] = useState(0);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [permission, requestPermission] = useCameraPermissions();

  // ─── Refs ────────────────────────────────────────
  const cameraRef = useRef(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  // ─── Initialization ──────────────────────────────
  useEffect(() => {
    checkServer();

    // Re-check server health every 10 seconds
    const healthInterval = setInterval(checkServer, 10000);

    // Fade in the UI
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 800,
      useNativeDriver: true,
    }).start();

    // Setup voice service callbacks
    VoiceService.onResult((text) => {
      setLastQuestion(text);
      processWithCamera(text);
    }).onError((err) => {
      console.error("Voice error:", err);
      setAppState(STATES.ERROR);
      speak("Sorry, I could not hear you. Please try again.");
    });

    // Announce app ready for accessibility
    AccessibilityInfo.announceForAccessibility(
      "NavAI is ready. Tap the microphone button to ask a question."
    );

    // Cleanup on unmount
    return () => {
      clearInterval(healthInterval);
      VoiceService.destroy();
      Speech.stop();
    };
  }, []);

  // ─── Server Health Check ─────────────────────────
  const checkServer = async () => {
    const online = await NavAIService.checkHealth();
    setServerOnline(online);
    if (!online) {
      console.log("Backend server is offline");
    }
  };

  // ─── TTS (Text-to-Speech) ────────────────────────
  const speak = useCallback((text) => {
    setAppState(STATES.SPEAKING);

    // Haptic feedback when speaking starts
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (e) {
      // Haptics may not be available in all environments
    }

    Speech.speak(text, {
      language: "en-US",
      pitch: 1.0,
      rate: 0.9,
      onDone: () => setAppState(STATES.IDLE),
      onError: () => setAppState(STATES.IDLE),
    });
  }, []);

  const stopSpeaking = useCallback(() => {
    Speech.stop();
    setAppState(STATES.IDLE);
  }, []);

  // ─── Voice Input ─────────────────────────────────
  const startListening = useCallback(() => {
    if (appState === STATES.SPEAKING) {
      stopSpeaking();
      return;
    }

    if (appState === STATES.PROCESSING) return;

    setAppState(STATES.LISTENING);

    // Haptic feedback
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (e) {}

    VoiceService.start("en-US");
  }, [appState, stopSpeaking]);

  // ─── Main Pipeline ───────────────────────────────
  const processWithCamera = useCallback(
    async (question) => {
      setAppState(STATES.PROCESSING);

      try {
        if (!cameraRef.current) {
          throw new Error("Camera not available");
        }

        // Capture photo
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.7,
          base64: false,
          skipProcessing: true,
        });

        // Always try the request - don't gate on serverOnline
        // Re-check health in background
        checkServer();

        // Send to backend pipeline
        const result = await NavAIService.processQuery(photo.uri, question);

        if (result.status === "success") {
          setServerOnline(true);
          setLastAnswer(result.answer);
          setDetectionCount(result.detections?.length || 0);
          setOcrCount(result.ocr_texts?.length || 0);
          setLatency(result.latency_ms || 0);

          // Announce obstacles first if any
          const obstacles = result.context?.obstacles || [];
          if (obstacles.length > 0) {
            const warnings = obstacles.map((o) => o.warning).join(". ");
            speak(warnings + ". " + result.answer);
          } else {
            speak(result.answer);
          }
        } else {
          throw new Error(result.error || "Processing failed");
        }
      } catch (error) {
        console.error("Pipeline error:", error);
        const errMsg =
          "Sorry, I had trouble processing that. Please try again.";
        setLastAnswer(errMsg);
        setAppState(STATES.ERROR);
        speak(errMsg);
      }
    },
    [speak]
  );

  // ─── Quick Action Handler ────────────────────────
  const handleQuickAction = useCallback(
    (question) => {
      if (appState === STATES.PROCESSING || appState === STATES.LISTENING)
        return;
      setLastQuestion(question);
      processWithCamera(question);
    },
    [appState, processWithCamera]
  );

  // ─── Replay Last Answer ─────────────────────────
  const replayAnswer = useCallback(() => {
    if (lastAnswer && appState !== STATES.SPEAKING) {
      speak(lastAnswer);
    }
  }, [lastAnswer, appState, speak]);

  // ─── Onboarding ──────────────────────────────────
  if (showOnboarding) {
    return (
      <OnboardingOverlay onComplete={() => setShowOnboarding(false)} />
    );
  }

  // ─── Permission Screen ──────────────────────────
  if (!permission) return <View style={styles.container} />;

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#0A0E27" />
        <View style={styles.permissionContainer}>
          <View style={styles.permissionIconCircle}>
            <MaterialIcons name="camera-alt" size={56} color="#6C63FF" />
          </View>
          <Text style={styles.permissionTitle}>Camera Access Needed</Text>
          <Text style={styles.permissionText}>
            NavAI needs camera access to detect objects and read text in
            your surroundings. Your privacy is important — images are
            processed in real-time and never stored.
          </Text>
          <TouchableOpacity
            style={styles.permissionBtn}
            onPress={requestPermission}
            accessibilityLabel="Grant camera permission"
          >
            <Text style={styles.permissionBtnText}>Grant Permission</Text>
            <MaterialIcons name="arrow-forward" size={18} color="#FFF" />
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // ─── Main UI ─────────────────────────────────────
  const isBusy =
    appState === STATES.PROCESSING || appState === STATES.LISTENING;

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0A0E27" />

      {/* Camera Preview - NO children inside CameraView */}
      <CameraView ref={cameraRef} style={StyleSheet.absoluteFill} facing="back" />

      {/* UI Overlay on top of camera using absolute positioning */}
      <View style={styles.overlay}>
        {/* Top Bar */}
        <Animated.View style={{ opacity: fadeAnim }}>
          <TopBar serverOnline={serverOnline} />
        </Animated.View>

        {/* Status Badge */}
        <StatusBadge appState={appState} />

        {/* Spacer */}
        <View style={styles.spacer} />

        {/* Answer Card */}
        <AnswerCard
          question={lastQuestion}
          answer={lastAnswer}
          detectionCount={detectionCount}
          ocrCount={ocrCount}
          latency={latency}
          onReplay={replayAnswer}
        />

        {/* Bottom Controls */}
        <View style={styles.bottomControls}>
          {/* Quick Action Buttons */}
          <QuickActions onAction={handleQuickAction} disabled={isBusy} />

          {/* Main Mic Button */}
          <View style={styles.micRow}>
            <MicButton
              appState={appState}
              onPress={startListening}
              size={80}
            />
          </View>

          {/* Hint Text */}
          <Text style={styles.hintText}>
            {VoiceService.isAvailable
              ? "Tap mic to speak"
              : "Tap mic for demo query"}
          </Text>
        </View>
      </View>
    </View>
  );
}

// ─── Styles ──────────────────────────────────────
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0A0E27",
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "space-between",
  },
  spacer: {
    flex: 1,
  },
  // Bottom Controls
  bottomControls: {
    paddingBottom: Platform.OS === "android" ? 24 : 36,
    paddingTop: 16,
    backgroundColor: "rgba(10, 14, 39, 0.82)",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    gap: 16,
  },
  micRow: {
    alignItems: "center",
    marginVertical: 4,
  },
  hintText: {
    color: "rgba(255, 255, 255, 0.3)",
    fontSize: 12,
    textAlign: "center",
    fontWeight: "500",
  },
  // Permission Screen
  permissionContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 40,
  },
  permissionIconCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: "rgba(108, 99, 255, 0.1)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 24,
  },
  permissionTitle: {
    color: "#FFF",
    fontSize: 26,
    fontWeight: "800",
    marginBottom: 12,
    letterSpacing: 0.5,
  },
  permissionText: {
    color: "rgba(255, 255, 255, 0.55)",
    fontSize: 15,
    textAlign: "center",
    lineHeight: 23,
    marginBottom: 32,
  },
  permissionBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    backgroundColor: "#6C63FF",
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 16,
  },
  permissionBtnText: {
    color: "#FFF",
    fontSize: 16,
    fontWeight: "700",
  },
});
