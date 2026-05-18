import { useEffect } from "react";
import { router } from "expo-router";
import { View } from "react-native";

export default function AuthCallback() {
  useEffect(() => {
    router.replace("/(tabs)");
  }, []);
  return <View className="flex-1 bg-cream" />;
}
