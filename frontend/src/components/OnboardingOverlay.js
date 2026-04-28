/**
 * NavAI - Onboarding Overlay Component
 * First-launch guide that teaches users how to use the app.
 */
import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
  SafeAreaView,
} from "react-native";
import { MaterialIcons, Ionicons } from "@expo/vector-icons";

const { width, height } = Dimensions.get("window");

const STEPS = [
  {
    icon: "eye",
    iconLib: "Ionicons",
    title: "Welcome to NavAI",
    description:
      "Your AI-powered navigation assistant. I help you understand your surroundings through voice interaction.",
    color: "#6C63FF",
  },
  {
    icon: "mic",
    iconLib: "MaterialIcons",
    title: "Voice Commands",
    description:
      'Tap the microphone button and ask questions like "What is in front of me?" or "Read this sign".',
    color: "#FF6584",
  },
  {
    icon: "camera-alt",
    iconLib: "MaterialIcons",
    title: "Camera Detection",
    description:
      "Point your camera at your surroundings. I will detect objects, read text, and warn you about obstacles.",
    color: "#FFC107",
  },
  {
    icon: "volume-up",
    iconLib: "MaterialIcons",
    title: "Spoken Responses",
    description:
      "I will speak my answers aloud so you can keep your eyes free. Tap the mic again to stop or ask another question.",
    color: "#00E676",
  },
];

const OnboardingOverlay = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const current = STEPS[step];

  const handleNext = () => {
    if (step < STEPS.length - 1) {
      setStep(step + 1);
    } else {
      onComplete();
    }
  };

  const renderIcon = () => {
    if (current.iconLib === "Ionicons") {
      return <Ionicons name={current.icon} size={64} color={current.color} />;
    }
    return <MaterialIcons name={current.icon} size={64} color={current.color} />;
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Skip button */}
        <TouchableOpacity style={styles.skipBtn} onPress={onComplete}>
          <Text style={styles.skipText}>Skip</Text>
        </TouchableOpacity>

        {/* Icon */}
        <View style={[styles.iconCircle, { backgroundColor: current.color + "15" }]}>
          {renderIcon()}
        </View>

        {/* Text */}
        <Text style={styles.title}>{current.title}</Text>
        <Text style={styles.description}>{current.description}</Text>

        {/* Progress dots */}
        <View style={styles.dots}>
          {STEPS.map((_, i) => (
            <View
              key={i}
              style={[
                styles.dot,
                {
                  backgroundColor: i === step ? current.color : "rgba(255,255,255,0.2)",
                  width: i === step ? 24 : 8,
                },
              ]}
            />
          ))}
        </View>

        {/* Next button */}
        <TouchableOpacity
          style={[styles.nextBtn, { backgroundColor: current.color }]}
          onPress={handleNext}
        >
          <Text style={styles.nextText}>
            {step === STEPS.length - 1 ? "Get Started" : "Next"}
          </Text>
          <MaterialIcons
            name={step === STEPS.length - 1 ? "check" : "arrow-forward"}
            size={20}
            color="#FFF"
          />
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "#0A0E27",
    zIndex: 100,
  },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 40,
  },
  skipBtn: {
    position: "absolute",
    top: 20,
    right: 20,
    padding: 10,
  },
  skipText: {
    color: "rgba(255, 255, 255, 0.5)",
    fontSize: 15,
    fontWeight: "500",
  },
  iconCircle: {
    width: 140,
    height: 140,
    borderRadius: 70,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 40,
  },
  title: {
    color: "#FFFFFF",
    fontSize: 28,
    fontWeight: "800",
    textAlign: "center",
    marginBottom: 14,
    letterSpacing: 0.5,
  },
  description: {
    color: "rgba(255, 255, 255, 0.6)",
    fontSize: 16,
    lineHeight: 24,
    textAlign: "center",
    marginBottom: 40,
  },
  dots: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 40,
  },
  dot: {
    height: 8,
    borderRadius: 4,
  },
  nextBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 16,
  },
  nextText: {
    color: "#FFF",
    fontSize: 17,
    fontWeight: "700",
  },
});

export default OnboardingOverlay;
