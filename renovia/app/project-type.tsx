import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { useApp } from "@/lib/store";
import type { ProjectType } from "@/lib/types";

type Option = { value: ProjectType; label: string };

const OPTIONS: Option[] = [
  { value: "peinture_murale", label: "Peinture murale" },
  { value: "papier_peint", label: "Papier peint" },
  { value: "carrelage", label: "Carrelage" },
  { value: "enduit", label: "Enduit / Béton ciré" },
  { value: "boiserie", label: "Boiserie / Lambris" },
  { value: "autre", label: "Autre" },
];

export default function ProjectTypeScreen() {
  const setType = useApp((s) => s.setType);
  const [selected, setSelected] = useState<ProjectType | null>(null);

  const onSelect = (v: ProjectType) => {
    setSelected(v);
    setType(v);
  };

  return (
    <Screen
      footer={
        <Button
          label="Suivant"
          disabled={!selected}
          onPress={() => router.push("/style")}
        />
      }
    >
      <Header back onBack={() => router.back()} />
      <Text className="text-ink text-2xl font-semibold mt-2 mb-6">
        Quel type de projet ?
      </Text>
      <View className="gap-3">
        {OPTIONS.map((opt) => {
          const isSelected = selected === opt.value;
          return (
            <Pressable
              key={opt.value}
              onPress={() => onSelect(opt.value)}
              className={`h-16 rounded-card flex-row items-center px-3 ${
                isSelected ? "bg-cream-200 border-2 border-sand" : "bg-white border border-line"
              }`}
            >
              <View className="w-12 h-12 bg-cream-200 rounded-md" />
              <Text className="text-ink text-base font-semibold flex-1 ml-3">
                {opt.label}
              </Text>
              <Ionicons name="chevron-forward" size={20} color="#6B7280" />
            </Pressable>
          );
        })}
      </View>
    </Screen>
  );
}
