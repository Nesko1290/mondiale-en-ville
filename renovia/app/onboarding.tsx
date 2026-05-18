import { View, Text } from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";

export default function OnboardingScreen() {
  return (
    <Screen
      footer={
        <Button label="Suivant" onPress={() => router.replace("/login")} />
      }
    >
      <Header back onBack={() => router.back()} />
      <Text className="text-ink text-3xl font-serif mt-2">Renovia</Text>
      <Text className="text-ink text-2xl font-semibold mt-4">
        Visualisez le potentiel de chaque pièce.
      </Text>
      <Text className="text-muted text-base mt-3">
        Prenez une photo et laissez l'IA transformer votre intérieur.
      </Text>
      {/* Phone-with-photo mockup placeholder */}
      <View className="bg-white rounded-card h-96 mt-6" />
    </Screen>
  );
}
