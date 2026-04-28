/**
 * NavAI - Top Bar Component
 * Header with logo, server status indicator, and settings.
 */
import React from "react";
import { View, Text, StyleSheet, Platform, TouchableOpacity } from "react-native";
import { Ionicons, MaterialIcons } from "@expo/vector-icons";

const TopBar = ({ serverOnline, onSettingsPress }) => {
  return (
    <View style={styles.container}>
      {/* Logo */}
      <View style={styles.logoRow}>
        <View style={styles.iconContainer}>
          <Ionicons name="eye" size={22} color="#6C63FF" />
        </View>
        <View>
          <Text style={styles.logoText}>NavAI</Text>
          <Text style={styles.tagline}>Vision Assistant</Text>
        </View>
      </View>

      {/* Right side */}
      <View style={styles.rightRow}>
        {/* Server Status */}
        <View
          style={styles.serverStatus}
          accessibilityLabel={`Server ${serverOnline ? "online" : "offline"}`}
        >
          <View
            style={[
              styles.serverDot,
              { backgroundColor: serverOnline ? "#00E676" : "#FF5252" },
            ]}
          />
          <Text
            style={[
              styles.serverText,
              { color: serverOnline ? "#00E676" : "#FF5252" },
            ]}
          >
            {serverOnline ? "Online" : "Offline"}
          </Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: Platform.OS === "android" ? 42 : 12,
    paddingBottom: 12,
    backgroundColor: "rgba(10, 14, 39, 0.75)",
  },
  logoRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  iconContainer: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: "rgba(108, 99, 255, 0.15)",
    justifyContent: "center",
    alignItems: "center",
  },
  logoText: {
    color: "#FFFFFF",
    fontSize: 20,
    fontWeight: "800",
    letterSpacing: 1.2,
  },
  tagline: {
    color: "rgba(255, 255, 255, 0.4)",
    fontSize: 10,
    fontWeight: "500",
    letterSpacing: 0.5,
    marginTop: -1,
  },
  rightRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  serverStatus: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    backgroundColor: "rgba(255, 255, 255, 0.06)",
  },
  serverDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  serverText: {
    fontSize: 11,
    fontWeight: "600",
  },
});

export default TopBar;
