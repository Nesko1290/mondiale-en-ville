import { useEffect, useState } from "react";
import { ActivityIndicator, View, Text, ScrollView } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useApp } from "@/lib/store";
import { getArtisan } from "@/lib/api";
import type { Database } from "@/lib/supabase";
import type { Artisan } from "@/lib/types";

type ArtisanRow = Database["public"]["Tables"]["artisans"]["Row"];

export default function ArtisanDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const setArtisan = useApp((s) => s.setArtisan);
  const [artisan, setArtisanRow] = useState<ArtisanRow | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        if (!id) return;
        const row = await getArtisan(id);
        if (active) setArtisanRow(row);
      } catch (e) {
        console.log("getArtisan error", e);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [id]);

  if (loading) {
    return (
      <Screen scroll={false}>
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator color="#0B1320" />
        </View>
      </Screen>
    );
  }

  if (!artisan) {
    return (
      <Screen scroll={false}>
        <Header back />
        <View className="flex-1 items-center justify-center">
          <Text className="text-ink text-base">Artisan introuvable</Text>
        </View>
      </Screen>
    );
  }

  const onChoose = () => {
    const mapped: Artisan = {
      id: artisan.id,
      name: artisan.name,
      city: artisan.city ?? "",
      rating: artisan.rating,
      reviewsCount: artisan.reviews_count,
      about: artisan.about ?? "",
      verified: artisan.verified,
      avatarUri: artisan.avatar_url ?? undefined,
      portfolio: artisan.portfolio ?? [],
    };
    setArtisan(mapped);
    router.push("/booking");
  };

  return (
    <Screen
      footer={<Button label="Choisir cet artisan" onPress={onChoose} />}
    >
      <Header back />

      <View className="flex-row items-center gap-4 mt-2">
        <View className="w-16 h-16 rounded-full bg-cream-200" />
        <View className="flex-1">
          <Text className="text-lg font-semibold text-ink">{artisan.name}</Text>
          <View className="flex-row items-center gap-1 mt-1">
            <Ionicons name="star" size={14} color="#F59E0B" />
            <Text className="text-ink text-sm font-medium">{artisan.rating}</Text>
            <Text className="text-muted text-sm">
              ({artisan.reviews_count} avis)
            </Text>
          </View>
          <Text className="text-muted text-sm mt-0.5">{artisan.city}</Text>
        </View>
      </View>

      <View className="mt-6">
        <Text className="text-ink font-semibold mb-2">À propos</Text>
        <Text className="text-muted leading-5">{artisan.about}</Text>
      </View>

      <View className="mt-6">
        <Text className="text-ink font-semibold mb-3">Réalisations</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View className="flex-row gap-3">
            <View className="w-24 h-24 rounded-lg bg-cream-200" />
            <View className="w-24 h-24 rounded-lg bg-cream-200" />
            <View className="w-24 h-24 rounded-lg bg-cream-200" />
          </View>
        </ScrollView>
      </View>

      <View className="mt-6">
        <Text className="text-ink font-semibold mb-3">Avis clients</Text>
        <Card>
          <View className="flex-row items-center gap-3">
            <View className="w-10 h-10 rounded-full bg-cream-200" />
            <View className="flex-1">
              <Text className="text-ink font-medium">Sophie M.</Text>
              <View className="flex-row gap-0.5 mt-0.5">
                <Ionicons name="star" size={12} color="#F59E0B" />
                <Ionicons name="star" size={12} color="#F59E0B" />
                <Ionicons name="star" size={12} color="#F59E0B" />
                <Ionicons name="star" size={12} color="#F59E0B" />
                <Ionicons name="star" size={12} color="#F59E0B" />
              </View>
            </View>
          </View>
          <Text className="text-muted text-sm mt-3 leading-5">
            Travail impeccable, équipe très professionnelle !
          </Text>
        </Card>
      </View>
    </Screen>
  );
}
