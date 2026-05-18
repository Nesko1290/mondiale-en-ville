import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useApp } from "@/lib/store";
import { mockArtisans } from "@/lib/mock";

type StepStatus = "done" | "current" | "pending";

type StepProps = {
  status: StepStatus;
};

function StepCircle({ status }: StepProps) {
  if (status === "done") {
    return (
      <View className="w-8 h-8 rounded-full bg-sand items-center justify-center">
        <Ionicons name="checkmark" size={18} color="#0B1320" />
      </View>
    );
  }
  if (status === "current") {
    return (
      <View className="w-8 h-8 rounded-full border-2 border-sand bg-cream items-center justify-center" />
    );
  }
  return <View className="w-8 h-8 rounded-full bg-cream-200" />;
}

function StepLine({ active }: { active: boolean }) {
  return (
    <View
      className={`h-0.5 flex-1 ${active ? "bg-sand" : "bg-line"}`}
    />
  );
}

export default function TrackingScreen() {
  const artisan = useApp((s) => s.selectedArtisan);
  const artisanName = artisan?.name ?? mockArtisans[0].name;

  return (
    <Screen
      footer={
        <Button
          label="Voir les détails"
          variant="ghost"
          onPress={() => router.push("/done")}
        />
      }
    >
      <Header back />

      <Text className="text-2xl font-semibold text-ink mt-2 mb-6">
        Suivi de votre projet
      </Text>

      <View className="flex-row items-center mb-2">
        <StepCircle status="done" />
        <StepLine active />
        <StepCircle status="done" />
        <StepLine active />
        <StepCircle status="current" />
        <StepLine active={false} />
        <StepCircle status="pending" />
      </View>

      <View className="flex-row justify-between mb-1">
        <View className="items-start" style={{ width: 80 }}>
          <Text className="text-ink text-xs font-medium">Réservé</Text>
          <Text className="text-muted text-xs">15 mai 2024</Text>
        </View>
        <View className="items-end" style={{ width: 90 }}>
          <Text className="text-ink text-xs font-medium">En préparation</Text>
        </View>
      </View>

      <View className="flex-row gap-2 mt-4 mb-6">
        <View className="bg-sand rounded-pill px-4 py-2">
          <Text className="text-ink text-sm font-medium">En cours</Text>
        </View>
        <View className="border border-line rounded-pill px-4 py-2">
          <Text className="text-muted text-sm font-medium">Terminé</Text>
        </View>
      </View>

      <Card className="mb-4">
        <View className="flex-row items-center">
          <View className="flex-1">
            <Text className="text-muted text-xs">Votre artisan</Text>
            <Text className="text-ink font-medium mt-0.5">{artisanName}</Text>
          </View>
          <View className="flex-row gap-2">
            <Pressable className="bg-cream-200 rounded-full w-10 h-10 items-center justify-center">
              <Ionicons name="call" size={18} color="#0B1320" />
            </Pressable>
            <Pressable className="bg-cream-200 rounded-full w-10 h-10 items-center justify-center">
              <Ionicons name="chatbubble" size={18} color="#0B1320" />
            </Pressable>
          </View>
        </View>
      </Card>

      <Card>
        <Text className="text-muted text-xs">Prochain rendez-vous</Text>
        <Text className="text-ink font-medium mt-1">
          Mercredi 15 mai 2024 à 10:00
        </Text>
      </Card>
    </Screen>
  );
}
