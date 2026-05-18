import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Button";

type Mode = "avant" | "apres";

export default function RenderScreen() {
  const [mode, setMode] = useState<Mode>("apres");
  const [variant, setVariant] = useState<number>(0);

  return (
    <Screen
      dark
      padded={false}
      footer={
        <View className="gap-2">
          <Button
            label="Modifier le style"
            variant="secondary"
            onPress={() => router.back()}
          />
          <Button
            label="Continuer"
            variant="primary"
            onPress={() => router.push("/analysis")}
          />
        </View>
      }
    >
      <View className="flex-row items-center justify-between px-5 py-3">
        <Pressable
          onPress={() => router.back()}
          hitSlop={12}
          className="w-10 h-10 items-center justify-center"
        >
          <Ionicons name="close" size={26} color="#F6F1E8" />
        </Pressable>

        <View className="flex-row bg-sand rounded-pill p-1">
          <Pressable
            onPress={() => setMode("avant")}
            className={`px-4 h-8 rounded-pill items-center justify-center ${
              mode === "avant" ? "bg-ink" : ""
            }`}
          >
            <Text
              className={`text-sm font-medium ${
                mode === "avant" ? "text-cream" : "text-ink"
              }`}
            >
              Avant
            </Text>
          </Pressable>
          <Pressable
            onPress={() => setMode("apres")}
            className={`px-4 h-8 rounded-pill items-center justify-center ${
              mode === "apres" ? "bg-ink" : ""
            }`}
          >
            <Text
              className={`text-sm font-medium ${
                mode === "apres" ? "text-cream" : "text-ink"
              }`}
            >
              Après
            </Text>
          </Pressable>
        </View>

        <View className="w-10" />
      </View>

      <View className="mx-5 mt-2 rounded-card overflow-hidden bg-ink-700 aspect-[3/5] items-center justify-center">
        <Text className="text-cream text-3xl font-semibold">
          {mode === "avant" ? "Avant" : "Après"}
        </Text>
      </View>

      <Text className="text-cream text-center mt-5 text-sm">
        Style moderne – Beige sable
      </Text>

      <View className="flex-row justify-center mt-3 gap-2">
        {[0, 1, 2, 3].map((i) => (
          <Pressable
            key={i}
            onPress={() => setVariant(i)}
            className={`h-16 w-20 rounded-md bg-ink-700 ${
              variant === i ? "border-2 border-sand" : ""
            }`}
          />
        ))}
      </View>
    </Screen>
  );
}
