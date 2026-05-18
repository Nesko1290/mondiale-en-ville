import { useEffect } from "react";
import { View, Text } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useApp } from "@/lib/store";
import { mockAnalysis } from "@/lib/mock";

type Row = {
  label: string;
  sub: string;
};

function capitalize(s: string): string {
  if (!s) return s;
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export default function AnalysisScreen() {
  const setAnalysis = useApp((s) => s.setAnalysis);

  useEffect(() => {
    setAnalysis(mockAnalysis);
  }, [setAnalysis]);

  const rows: Row[] = [
    { label: "Qualité de l'image", sub: capitalize(mockAnalysis.imageQuality) },
    { label: "Fissures", sub: mockAnalysis.cracks },
    { label: "Trous / Impacts", sub: mockAnalysis.holes },
    { label: "Humidité", sub: mockAnalysis.humidity },
    { label: "Revêtement existant", sub: mockAnalysis.existingFinish },
  ];

  return (
    <Screen
      footer={
        <Button label="Continuer" onPress={() => router.push("/estimate")} />
      }
    >
      <Header back />
      <Text className="text-ink text-2xl font-semibold mt-2">
        Analyse du mur en cours...
      </Text>

      <Card className="mt-5">
        {rows.map((row, i) => (
          <View
            key={row.label}
            className={`flex-row items-start gap-3 ${i > 0 ? "mt-4" : ""}`}
          >
            <Ionicons name="checkmark-circle" size={22} color="#16A34A" />
            <View className="flex-1">
              <Text className="text-ink font-medium">{row.label}</Text>
              <Text className="text-muted text-sm mt-0.5">{row.sub}</Text>
            </View>
          </View>
        ))}
      </Card>

      <View className="bg-cream-200 rounded-card p-4 mt-5 flex-row gap-3">
        <Ionicons name="information-circle" size={22} color="#D97706" />
        <View className="flex-1">
          <Text className="text-ink font-semibold">
            Préparation recommandée
          </Text>
          <Text className="text-ink text-sm mt-1">
            {mockAnalysis.recommendation}
          </Text>
        </View>
      </View>
    </Screen>
  );
}
