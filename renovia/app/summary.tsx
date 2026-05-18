import { useState } from "react";
import { View, Text, Alert } from "react-native";
import { router } from "expo-router";
import { useStripe } from "@stripe/stripe-react-native";
import { Screen } from "@/components/Screen";
import { Header } from "@/components/Header";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useApp } from "@/lib/store";
import { chf } from "@/lib/format";
import { mockArtisans, mockEstimate } from "@/lib/mock";
import { createDepositIntent, markDepositPaid } from "@/lib/api";

const WEEKDAYS = [
  "Dimanche",
  "Lundi",
  "Mardi",
  "Mercredi",
  "Jeudi",
  "Vendredi",
  "Samedi",
];
const MONTHS = [
  "janvier",
  "février",
  "mars",
  "avril",
  "mai",
  "juin",
  "juillet",
  "août",
  "septembre",
  "octobre",
  "novembre",
  "décembre",
];

function formatFr(iso: string | null): string {
  if (!iso) return "Mercredi 15 mai 2024 à 10:00";
  const d = new Date(iso);
  const day = WEEKDAYS[d.getDay()];
  const month = MONTHS[d.getMonth()];
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${day} ${d.getDate()} ${month} ${d.getFullYear()} à ${hh}:${mm}`;
}

type RowProps = {
  label: string;
  value: string;
  trailing?: string;
  first?: boolean;
};

function Row({ label, value, trailing, first }: RowProps) {
  return (
    <View
      className={first ? "" : "border-t border-line pt-3 mt-3"}
    >
      <Text className="text-muted text-sm">{label}</Text>
      <View className="flex-row items-baseline gap-1">
        <Text className="text-ink font-medium">{value}</Text>
        {trailing ? (
          <Text className="text-muted text-xs">{trailing}</Text>
        ) : null}
      </View>
    </View>
  );
}

export default function SummaryScreen() {
  const artisan = useApp((s) => s.selectedArtisan);
  const scheduledAt = useApp((s) => s.scheduledAt);
  const bookingId = useApp((s) => s.bookingId);
  const estimate = useApp((s) => s.estimate);
  const artisanName = artisan?.name ?? mockArtisans[0].name;
  const totalChf = estimate?.totalChf ?? mockEstimate.totalChf;
  const depositChf = estimate?.depositChf ?? mockEstimate.depositChf;

  const { initPaymentSheet, presentPaymentSheet } = useStripe();
  const [paying, setPaying] = useState(false);

  const onPay = async () => {
    if (!bookingId) {
      Alert.alert("Erreur", "Réservation introuvable.");
      return;
    }
    setPaying(true);
    try {
      const intent = await createDepositIntent(bookingId);
      const { error: initErr } = await initPaymentSheet({
        merchantDisplayName: "Renovia",
        paymentIntentClientSecret: intent.clientSecret,
        customerEphemeralKeySecret: intent.ephemeralKey,
        customerId: intent.customer,
        allowsDelayedPaymentMethods: false,
        returnURL: "renovia://payment-return",
      });
      if (initErr) throw new Error(initErr.message);

      const { error: payErr } = await presentPaymentSheet();
      if (payErr) {
        if (payErr.code !== "Canceled") {
          Alert.alert("Paiement", payErr.message);
        }
        return;
      }
      await markDepositPaid(bookingId);
      router.push("/tracking");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Paiement impossible";
      Alert.alert("Erreur", msg);
    } finally {
      setPaying(false);
    }
  };

  return (
    <Screen
      footer={
        <Button label="Payer l'acompte" loading={paying} onPress={onPay} />
      }
    >
      <Header back />

      <Text className="text-2xl font-semibold text-ink mt-2 mb-4">
        Récapitulatif
      </Text>

      <Card>
        <Row label="Projet" value="Peinture murale – Salon" first />
        <Row label="Surface estimée" value="25 m²" />
        <Row label="Artisan" value={artisanName} />
        <Row label="Date" value={formatFr(scheduledAt)} />
        <Row label="Estimation" value={chf(totalChf)} trailing="TTC" />
      </Card>

      <View
        className="rounded-card p-4 mt-4"
        style={{ backgroundColor: "#EFE8D9" }}
      >
        <Text className="text-muted text-sm">Acompte (10%)</Text>
        <Text className="text-ink text-2xl font-semibold mt-1">
          {chf(depositChf)}
        </Text>
        <Text className="text-muted text-sm mt-2">
          L'acompte est déduit du montant final.
        </Text>
      </View>
    </Screen>
  );
}
