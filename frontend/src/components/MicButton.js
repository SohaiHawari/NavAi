/**
 * NavAI - Animated Microphone Button Component
 * Main interaction button with pulse animation and state-based colors.
 */
import React, { useEffect, useRef } from "react";
import {
  TouchableOpacity,
  Animated,
  StyleSheet,
  View,
  Platform,
} from "react-native";
import { MaterialIcons } from "@expo/vector-icons";

const STATE_COLORS = {
  idle: "#6C63FF",
  listening: "#FF6584",
  processing: "#FFC107",
  speaking: "#00E676",
  error: "#FF5252",
};

const MicButton = ({ appState, onPress, size = 80 }) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (appState === "listening") {
      // Pulse + glow animation while listening
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.25,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      );
      const glow = Animated.loop(
        Animated.sequence([
          Animated.timing(glowAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(glowAnim, {
            toValue: 0.3,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      );
      pulse.start();
      glow.start();
      return () => {
        pulse.stop();
        glow.stop();
      };
    } else if (appState === "processing") {
      // Slow rotation effect for processing
      const spin = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 0.95,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      );
      spin.start();
      return () => spin.stop();
    } else {
      pulseAnim.setValue(1);
      glowAnim.setValue(0);
    }
  }, [appState]);

  const color = STATE_COLORS[appState] || STATE_COLORS.idle;

  const iconName =
    appState === "speaking"
      ? "stop"
      : appState === "processing"
      ? "hourglass-top"
      : "mic";

  return (
    <View style={styles.wrapper}>
      {/* Outer glow ring */}
      {appState === "listening" && (
        <Animated.View
          style={[
            styles.glowRing,
            {
              width: size + 40,
              height: size + 40,
              borderRadius: (size + 40) / 2,
              borderColor: color,
              opacity: glowAnim,
            },
          ]}
        />
      )}

      {/* Button */}
      <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
        <TouchableOpacity
          style={[
            styles.button,
            {
              width: size,
              height: size,
              borderRadius: size / 2,
              backgroundColor: color,
            },
          ]}
          onPress={onPress}
          activeOpacity={0.7}
          accessibilityLabel="Voice command button"
          accessibilityHint="Double tap to start listening for voice commands"
          accessibilityRole="button"
        >
          <MaterialIcons name={iconName} size={size * 0.45} color="#FFF" />
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    alignItems: "center",
    justifyContent: "center",
  },
  button: {
    justifyContent: "center",
    alignItems: "center",
    elevation: 10,
    shadowColor: "#6C63FF",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
  },
  glowRing: {
    position: "absolute",
    borderWidth: 2,
    ...Platform.select({
      ios: {
        shadowOpacity: 0.6,
        shadowRadius: 20,
      },
      android: {
        elevation: 5,
      },
    }),
  },
});

export default MicButton;
