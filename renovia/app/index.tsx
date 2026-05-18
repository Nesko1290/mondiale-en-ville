import { View, Text, ActivityIndicator } from "react-native";
import { router } from "expo-router";
import { useEffect } from "react";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Button";
import { useSession } from "@/lib/auth";

export default function SplashScreen() {
  const { session, loading } = useSession();

  useEffect(() => {
    if (!loading && session) {
      router.replace("/(tabs)");
    }
  }, [loading, session]);

  return (
    <Screen
      dark
      scroll={false}
      footer={
        loading ? (
          <View className="items-center py-2">
            <ActivityIndicator color="#F6F1E8" />
          </View>
        ) : session ? null : (
          <View className="gap-3">
            <Button label="Commencer" onPress={() => router.push("/onboarding")} />
            <Button
              label="Se connecter"
              variant="ghost"
              onPress={() => router.push("/login")}
            />
            <Text className="text-cream/60 text-xs text-center mt-2">
              🇨🇭 Conçue en Suisse
            </Text>
          </View>
        )
      }
    >
      <View className="flex-1 items-center justify-center py-10">
        <Text className="text-cream text-5xl font-serif mb-3">Renovia</Text>
        <View className="items-center mb-8">
          <Text className="text-cream/70 text-lg">Visualisez.</Text>
          <Text className="text-cream/70 text-lg">Estimez.</Text>
          <Text className="text-cream/70 text-lg">Réalisez.</Text>
        </View>
        <View className="bg-ink-800 rounded-card w-full" style={{ height: 280 }} />
      </View>
    </Screen>
  );
}
