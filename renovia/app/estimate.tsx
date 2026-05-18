import { useEffect } from "react";
import { View, Text } from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useApp } from "@/lib/store";
import { mockEstimate } from "@/lib/mock";
import { chf } from "@/lib/format";

export default function EstimateScreen() {
  const setEstimate = useApp((s) => s.setEstimate);

  useEffect(() => {
    setEstimate(mockEstimate);
  }, [setEstimate]);

  return (
    <Screen
      footer={
        <Button label="Continuer" onPress={() => router.push("/artisans")} />
      }
    >
      <Header back />
      <Text className="text-ink text-2xl font-semibold mt-2">
        Estimation de votre projet
      </Text>

      <Card className="mt-5">
        <Text className="text-ink font-semibold text-base">
          Détail des travaux
        </Text>
        <View className="mt-3">
          {mockEstimate.lines.map((line, i) => (
            <View
              key={line.label}
              className={`flex-row justify-between py-3 ${
                i > 0 ? "border-t border-line" : ""
              }`}
            >
              <Text className="text-ink">{line.label}</Text>
              <Text className="text-ink font-medium">{chf(line.amountChf)}</Text>
            </View>
          ))}
        </View>
      </Card>

      <Card className="mt-4">
        <View className="flex-row justify-between items-center">
          <Text className="text-ink font-semibold text-base">
            Total estimé
          </Text>
          <Text className="text-ink text-2xl font-semibold">
            {chf(mockEstimate.totalChf)}
          </Text>
        </View>
        <View className="bg-cream-200 rounded-pill px-2 py-0.5 self-end mt-2">
          <Text className="text-ink text-xs">TTC</Text>
        </View>
      </Card>

      <Text className="text-muted italic text-xs mt-4">
        Estimation indicative. Un devis final sera établi par Renovia.
      </Text>
    </Screen>
  );
}
