import { useState } from "react";
import { View, Text, Pressable, Alert } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useApp } from "@/lib/store";
import { createBooking } from "@/lib/api";

const DAY_LABELS = ["L", "M", "M", "J", "V", "S", "D"];
const TIME_SLOTS = ["08:00", "10:00", "14:00", "16:00"];

export default function BookingScreen() {
  const setSchedule = useApp((s) => s.setSchedule);
  const currentProject = useApp((s) => s.currentProject);
  const selectedArtisan = useApp((s) => s.selectedArtisan);
  const estimate = useApp((s) => s.estimate);
  const [selectedDay, setSelectedDay] = useState<number>(15);
  const [selectedTime, setSelectedTime] = useState<string>("10:00");
  const [saving, setSaving] = useState(false);

  const onContinue = async () => {
    const [h, m] = selectedTime.split(":").map((n) => parseInt(n, 10));
    const scheduledAt = new Date(2024, 4, selectedDay, h, m).toISOString();
    setSchedule(scheduledAt);

    const projectId = currentProject?.id;
    const artisanId = selectedArtisan?.id;
    if (!projectId || !artisanId) {
      Alert.alert("Erreur", "Projet ou artisan manquant.");
      return;
    }

    const totalChf = estimate?.totalChf ?? 2150;
    const depositChf = estimate?.depositChf ?? 215;

    setSaving(true);
    try {
      const row = await createBooking({
        projectId,
        artisanId,
        scheduledAt,
        totalChf,
        depositChf,
      });
      // TODO type bookingId on store
      useApp.setState((s) => ({ ...(s as any), bookingId: row.id }));
      router.push("/summary");
    } catch (e) {
      console.log("createBooking error", e);
      Alert.alert("Erreur", "Impossible de créer la réservation.");
    } finally {
      setSaving(false);
    }
  };

  const days: number[] = Array.from({ length: 31 }, (_, i) => i + 1);

  return (
    <Screen footer={<Button label="Continuer" loading={saving} onPress={onContinue} />}>
      <Header back />

      <Text className="text-2xl font-semibold text-ink mt-2 mb-4">
        Réservez votre projet
      </Text>

      <Card className="mb-4">
        <Text className="text-ink font-semibold mb-3">Date souhaitée</Text>

        <View className="flex-row items-center justify-between mb-3">
          <Pressable hitSlop={8} className="w-8 h-8 items-center justify-center">
            <Ionicons name="chevron-back" size={20} color="#0B1320" />
          </Pressable>
          <Text className="text-ink font-medium">Mai 2024</Text>
          <Pressable hitSlop={8} className="w-8 h-8 items-center justify-center">
            <Ionicons name="chevron-forward" size={20} color="#0B1320" />
          </Pressable>
        </View>

        <View className="flex-row justify-between mb-2">
          {DAY_LABELS.map((d, i) => (
            <View key={i} className="w-10 items-center">
              <Text className="text-muted text-xs">{d}</Text>
            </View>
          ))}
        </View>

        <View className="flex-row flex-wrap">
          {days.map((day) => {
            const selected = day === selectedDay;
            return (
              <Pressable
                key={day}
                onPress={() => setSelectedDay(day)}
                className={`w-10 h-10 rounded-full items-center justify-center mb-1 ${
                  selected ? "bg-ink" : ""
                }`}
                style={{ width: `${100 / 7}%` }}
              >
                <Text
                  className={`text-sm ${
                    selected ? "text-cream font-semibold" : "text-ink"
                  }`}
                >
                  {day}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </Card>

      <Card>
        <Text className="text-ink font-semibold mb-3">Heure souhaitée</Text>
        <View className="flex-row flex-wrap gap-2">
          {TIME_SLOTS.map((t) => {
            const selected = t === selectedTime;
            return (
              <Pressable
                key={t}
                onPress={() => setSelectedTime(t)}
                className={`rounded-pill px-4 py-2 ${
                  selected ? "bg-ink" : "bg-white border border-line"
                }`}
              >
                <Text
                  className={`text-sm ${
                    selected ? "text-cream font-semibold" : "text-ink"
                  }`}
                >
                  {t}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </Card>
    </Screen>
  );
}
