import { View, Text, ScrollView, Pressable } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Card } from "@/components/Card";
import { mockProjects } from "@/lib/mock";

export default function HomeScreen() {
  return (
    <ScrollView className="flex-1 bg-cream" contentContainerStyle={{ paddingBottom: 24 }}>
      <View className="px-5 pt-4">
        <View className="flex-row items-center justify-between">
          <Text className="text-ink text-lg font-semibold">Bonjour 👋</Text>
          <Pressable hitSlop={12} className="w-10 h-10 items-center justify-center">
            <Ionicons name="search" size={22} color="#0B1320" />
          </Pressable>
        </View>
        <Text className="text-ink text-2xl font-semibold mt-2">
          Quel est votre projet aujourd'hui ?
        </Text>

        <Text className="text-ink text-base font-semibold mt-6 mb-3">
          Démarrer un projet
        </Text>
        <Pressable
          onPress={() => router.push("/capture")}
          className="bg-cream-200 rounded-card p-5 flex-row items-center justify-between"
        >
          <View className="flex-1 pr-3">
            <Text className="text-ink text-base font-semibold">
              Prenez une photo et visualisez
            </Text>
            <Text className="text-muted text-sm mt-1">
              Transformez votre intérieur en un instant.
            </Text>
          </View>
          <View className="w-12 h-12 rounded-full bg-sand items-center justify-center">
            <Ionicons name="camera" size={22} color="#0B1320" />
          </View>
        </Pressable>

        <View className="flex-row items-center justify-between mt-7 mb-3">
          <Text className="text-ink text-base font-semibold">Mes projets</Text>
          <Pressable hitSlop={8}>
            <Text className="text-muted text-sm">Voir tout</Text>
          </Pressable>
        </View>
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ paddingHorizontal: 20, gap: 12 }}
      >
        {mockProjects.map((p) => (
          <Card key={p.id} className="w-40">
            <View className="h-32 bg-cream-200 rounded-md mb-3" />
            <Text className="text-ink text-sm font-semibold" numberOfLines={1}>
              {p.title}
            </Text>
            <Text className="text-muted text-xs mt-1">{p.rooms} pièces</Text>
          </Card>
        ))}
      </ScrollView>
    </ScrollView>
  );
}
