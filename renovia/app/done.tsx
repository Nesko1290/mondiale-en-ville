import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { useApp } from "@/lib/store";

export default function DoneScreen() {
  const reset = useApp((s) => s.reset);
  const [rating, setRating] = useState<number>(0);

  const onSend = () => {
    reset();
    router.replace("/(tabs)");
  };

  return (
    <Screen footer={<Button label="Envoyer" onPress={onSend} />}>
      <Header back />

      <View className="bg-cream-200 rounded-card p-6 items-center mt-2">
        <Text className="text-4xl">🎉</Text>
        <Text className="text-2xl font-semibold text-ink mt-2">
          Projet terminé !
        </Text>
        <Text className="text-muted text-center mt-2">
          Merci pour votre confiance. Votre avis compte beaucoup.
        </Text>
      </View>

      <View className="w-full h-48 rounded-card bg-cream-200 mt-4" />

      <View className="mt-6">
        <Text className="text-ink font-semibold mb-3">Votre avis</Text>
        <View className="flex-row gap-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <Pressable key={i} onPress={() => setRating(i)} hitSlop={4}>
              <Ionicons
                name={i <= rating ? "star" : "star-outline"}
                size={32}
                color="#F59E0B"
              />
            </Pressable>
          ))}
        </View>
      </View>

      <Pressable className="bg-white rounded-card h-24 p-3 mt-4 border border-line">
        <Text className="text-muted">Partagez votre expérience…</Text>
      </Pressable>
    </Screen>
  );
}
