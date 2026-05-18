import { View, Text } from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Button";

export default function SplashScreen() {
  return (
    <Screen
      dark
      scroll={false}
      footer={
        <View className="gap-3">
          <Button label="Commencer" onPress={() => router.push("/onboarding")} />
          <Button
            label="Se connecter"
            variant="ghost"
            onPress={() => router.push("/onboarding")}
          />
          <Text className="text-cream/60 text-xs text-center mt-2">
            🇨🇭 Conçue en Suisse
          </Text>
        </View>
      }
    >
      <View className="flex-1 items-center justify-center py-10">
        <Text className="text-cream text-5xl font-serif mb-3">Renovia</Text>
        <View className="items-center mb-8">
          <Text className="text-cream/70 text-lg">Visualisez.</Text>
          <Text className="text-cream/70 text-lg">Estimez.</Text>
          <Text className="text-cream/70 text-lg">Réalisez.</Text>
        </View>
        {/* Hero illustration placeholder */}
        <View className="bg-ink-800 rounded-card w-full" style={{ height: 280 }} />
      </View>
    </Screen>
  );
}
