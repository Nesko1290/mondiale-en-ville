import { View, Text } from "react-native";
import { Header } from "@/components/Header";

export default function ArtisansScreen() {
  return (
    <View className="flex-1 bg-cream px-5">
      <Header title="Artisans" />
      <View className="flex-1 items-center justify-center">
        <Text className="text-muted text-base">Bientôt disponible</Text>
      </View>
    </View>
  );
}
