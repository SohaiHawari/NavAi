/**
 * NavAI - Status Badge Component
 * Displays the current app state with color-coded indicator.
 */
import React from "react";
import { View, Text, StyleSheet } from "react-native";

const STATE_LABELS = {
  idle: "Tap mic or say 'Hey NavAI'",
  listening: "Listening...",
  processing: "Analyzing your surroundings...",
  speaking: "Speaking response...",
  error: "Error occurred. Tap to retry.",
};

const STATE_COLORS = {
  idle: "#6C63FF",
  listening: "#FF6584",
  processing: "#FFC107",
  speaking: "#00E676",
  error: "#FF5252",
};

const StatusBadge = ({ appState }) => {
  const color = STATE_COLORS[appState] || STATE_COLORS.idle;
  const label = STATE_LABELS[appState] || STATE_LABELS.idle;

  return (
    <View style={styles.container}>
      <View
        style={[styles.badge, { backgroundColor: color + "25" }]}
        accessibilityLabel={`Status: ${label}`}
        accessibilityRole="text"
      >
        <View style={[styles.dot, { backgroundColor: color }]} />
        <Text style={[styles.text, { color }]}>{label}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    marginTop: 10,
  },
  badge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 18,
    paddingVertical: 9,
    borderRadius: 24,
    gap: 8,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  text: {
    fontSize: 14,
    fontWeight: "600",
    letterSpacing: 0.3,
  },
});

export default StatusBadge;
