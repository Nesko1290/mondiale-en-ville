import { View, Text } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";

type IconName = keyof typeof Ionicons.glyphMap;

type Badge = {
  icon: IconName;
  label: string;
};

const BADGES: Badge[] = [
  { icon: "person-outline", label: "Artisans vérifiés" },
  { icon: "shield-checkmark-outline", label: "Avis clients contrôlés" },
  { icon: "ribbon-outline", label: "Garantie Renovia" },
  { icon: "pricetag-outline", label: "Prix transparents" },
];

export default function ArtisansScreen() {
  return (
    <Screen
      footer={
        <Button
          label="Continuer"
          onPress={() => router.push("/artisan/a1")}
        />
      }
    >
      <Header back />
      <Text className="text-ink text-2xl font-semibold mt-2">
        Renovia sélectionne les meilleurs artisans pour votre projet.
      </Text>

      <Card className="mt-5 bg-cream-200 border-2 border-sand">
        <Text className="text-ink font-semibold text-base">
          Meilleur choix pour votre projet
        </Text>
        <Text className="text-muted text-sm mt-1">
          Qualité, fiabilité et disponibilité
        </Text>
      </Card>

      <View className="mt-5">
        {BADGES.map((badge) => (
          <View
            key={badge.label}
            className="flex-row items-center gap-3 py-3"
          >
            <Ionicons name={badge.icon} size={22} color="#C9A876" />
            <Text className="text-ink text-base">{badge.label}</Text>
          </View>
        ))}
      </View>
    </Screen>
  );
}
