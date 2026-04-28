/**
 * NavAI - Quick Action Buttons Component
 * Provides shortcut buttons for common queries.
 */
import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { MaterialIcons } from "@expo/vector-icons";

const ACTIONS = [
  {
    id: "describe",
    icon: "visibility",
    label: "Describe",
    question: "Describe my surroundings",
    color: "#6C63FF",
  },
  {
    id: "read",
    icon: "text-fields",
    label: "Read Text",
    question: "Read any text you can see",
    color: "#FF6584",
  },
  {
    id: "obstacle",
    icon: "warning",
    label: "Obstacles",
    question: "Are there any obstacles in my path?",
    color: "#FFC107",
  },
];

const QuickActions = ({ onAction, disabled }) => {
  return (
    <View style={styles.container}>
      {ACTIONS.map((action) => (
        <TouchableOpacity
          key={action.id}
          style={[styles.button, disabled && styles.disabled]}
          onPress={() => !disabled && onAction(action.question)}
          activeOpacity={0.7}
          accessibilityLabel={action.label}
          accessibilityHint={`Asks: ${action.question}`}
          disabled={disabled}
        >
          <View style={[styles.iconCircle, { backgroundColor: action.color + "20" }]}>
            <MaterialIcons name={action.icon} size={22} color={action.color} />
          </View>
          <Text style={styles.label}>{action.label}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  button: {
    alignItems: "center",
    gap: 6,
  },
  disabled: {
    opacity: 0.4,
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: "center",
    alignItems: "center",
  },
  label: {
    color: "rgba(255, 255, 255, 0.7)",
    fontSize: 11,
    fontWeight: "600",
    letterSpacing: 0.3,
  },
});

export default QuickActions;
