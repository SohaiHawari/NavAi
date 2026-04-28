/**
 * NavAI - Answer Card Component
 * Displays the AI response with question, answer, and metrics.
 */
import React, { useEffect, useRef } from "react";
import { View, Text, StyleSheet, Animated, TouchableOpacity } from "react-native";
import { MaterialIcons } from "@expo/vector-icons";

const AnswerCard = ({ question, answer, detectionCount, ocrCount, latency, onReplay }) => {
  const slideAnim = useRef(new Animated.Value(50)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (answer) {
      Animated.parallel([
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [answer]);

  if (!answer) return null;

  return (
    <Animated.View
      style={[
        styles.container,
        {
          transform: [{ translateY: slideAnim }],
          opacity: opacityAnim,
        },
      ]}
    >
      {/* Question */}
      {question ? (
        <View style={styles.questionRow}>
          <MaterialIcons name="record-voice-over" size={14} color="#6C63FF" />
          <Text style={styles.questionText} numberOfLines={2}>
            {question}
          </Text>
        </View>
      ) : null}

      {/* Answer */}
      <Text
        style={styles.answerText}
        accessibilityLabel={`Answer: ${answer}`}
        accessibilityRole="text"
      >
        {answer}
      </Text>

      {/* Metrics Row */}
      <View style={styles.metricsRow}>
        <View style={styles.metricItem}>
          <MaterialIcons name="search" size={13} color="rgba(255,255,255,0.4)" />
          <Text style={styles.metricText}>{detectionCount || 0} objects</Text>
        </View>
        {ocrCount > 0 && (
          <View style={styles.metricItem}>
            <MaterialIcons name="text-fields" size={13} color="rgba(255,255,255,0.4)" />
            <Text style={styles.metricText}>{ocrCount} texts</Text>
          </View>
        )}
        <View style={styles.metricItem}>
          <MaterialIcons name="speed" size={13} color="rgba(255,255,255,0.4)" />
          <Text style={styles.metricText}>{latency || 0}ms</Text>
        </View>

        {/* Replay Button */}
        {onReplay && (
          <TouchableOpacity
            style={styles.replayBtn}
            onPress={onReplay}
            accessibilityLabel="Replay answer"
          >
            <MaterialIcons name="replay" size={16} color="#6C63FF" />
          </TouchableOpacity>
        )}
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginHorizontal: 16,
    padding: 16,
    backgroundColor: "rgba(10, 14, 39, 0.88)",
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "rgba(108, 99, 255, 0.25)",
    backdropFilter: "blur(10px)",
  },
  questionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 8,
  },
  questionText: {
    color: "#6C63FF",
    fontSize: 13,
    fontWeight: "600",
    flex: 1,
  },
  answerText: {
    color: "#FFFFFF",
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "500",
    letterSpacing: 0.2,
  },
  metricsRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    marginTop: 12,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "rgba(255, 255, 255, 0.08)",
  },
  metricItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  metricText: {
    color: "rgba(255, 255, 255, 0.4)",
    fontSize: 11,
    fontWeight: "500",
  },
  replayBtn: {
    marginLeft: "auto",
    padding: 4,
  },
});

export default AnswerCard;
