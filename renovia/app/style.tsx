import { useState } from "react";
import { View, Text, Pressable, ScrollView } from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { useApp } from "@/lib/store";
import { updateProject } from "@/lib/api";
import type { ProjectStyle } from "@/lib/types";

type Filter = "tous" | "moderne" | "minimaliste" | "classique" | "scandinave";

type StyleTile = {
  value: ProjectStyle;
  caption: string;
  bg: string;
};

const FILTERS: { value: Filter; label: string }[] = [
  { value: "tous", label: "Tous" },
  { value: "moderne", label: "Moderne" },
  { value: "minimaliste", label: "Minimaliste" },
  { value: "classique", label: "Classique" },
  { value: "scandinave", label: "Scandinave" },
];

const TILES: StyleTile[] = [
  { value: "moderne", caption: "Moderne – Beige sable", bg: "bg-ink-700" },
  { value: "minimaliste", caption: "Minimaliste – Blanc cassé", bg: "bg-cream-200" },
  { value: "classique", caption: "Classique – Bois clair", bg: "bg-ink-800" },
  { value: "scandinave", caption: "Scandinave – Gris doux", bg: "bg-cream-50" },
];

export default function StyleScreen() {
  const setStyle = useApp((s) => s.setStyle);
  const currentProject = useApp((s) => s.currentProject);
  const [filter, setFilter] = useState<Filter>("tous");
  const [selected, setSelected] = useState<ProjectStyle | null>(null);
  const [saving, setSaving] = useState(false);

  const visibleTiles =
    filter === "tous" ? TILES : TILES.filter((t) => t.value === filter);

  const onNext = async () => {
    if (!selected) return;
    if (currentProject?.id) {
      setSaving(true);
      try {
        await updateProject(currentProject.id, { style: selected });
      } catch (e) {
        console.log("updateProject error", e);
      } finally {
        setSaving(false);
      }
    }
    router.push("/render");
  };

  return (
    <Screen
      footer={
        <Button
          label="Suivant"
          disabled={!selected}
          loading={saving}
          onPress={onNext}
        />
      }
    >
      <Header back />
      <Text className="text-ink text-2xl font-semibold mt-2">
        Quel style vous inspire ?
      </Text>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        className="mt-5"
        contentContainerStyle={{ gap: 8 }}
      >
        {FILTERS.map((f) => {
          const active = filter === f.value;
          return (
            <Pressable
              key={f.value}
              onPress={() => setFilter(f.value)}
              className={`h-10 px-4 rounded-pill items-center justify-center ${
                active
                  ? "bg-ink"
                  : "bg-white border border-line"
              }`}
            >
              <Text
                className={`text-sm font-medium ${
                  active ? "text-cream" : "text-ink"
                }`}
              >
                {f.label}
              </Text>
            </Pressable>
          );
        })}
      </ScrollView>

      <View className="flex-row flex-wrap mt-6 -mx-1">
        {visibleTiles.map((tile) => {
          const isSelected = selected === tile.value;
          return (
            <View key={tile.value} className="w-1/2 px-1 mb-4">
              <Pressable
                onPress={() => {
                  setSelected(tile.value);
                  setStyle(tile.value);
                }}
                className={`rounded-card overflow-hidden h-44 ${tile.bg} ${
                  isSelected ? "border-2 border-sand" : ""
                }`}
              />
              <Text className="text-ink text-sm mt-2">{tile.caption}</Text>
            </View>
          );
        })}
      </View>
    </Screen>
  );
}
