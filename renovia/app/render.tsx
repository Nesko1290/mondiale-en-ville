import { useEffect, useState } from "react";
import { View, Text, Pressable, ActivityIndicator, Alert } from "react-native";
import { Image } from "expo-image";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Button";
import { useApp } from "@/lib/store";
import { requestRender } from "@/lib/api";
import { getSignedUrl } from "@/lib/storage";
import { styleLabel } from "@/lib/format";

type Mode = "avant" | "apres";

export default function RenderScreen() {
  const [mode, setMode] = useState<Mode>("apres");
  const [variant, setVariant] = useState<number>(0);
  const [busy, setBusy] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const project = useApp((s) => s.currentProject);
  const [beforeUrl, setBeforeUrl] = useState<string | null>(null);
  const [afterUrl, setAfterUrl] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!project?.id) {
        setBusy(false);
        setErrorMsg("Projet introuvable.");
        return;
      }
      try {
        if (project.photoUri && !project.photoUri.startsWith("http")) {
          if (project.photoUri.includes("/")) {
            try {
              const url = await getSignedUrl(project.photoUri);
              if (!cancelled) setBeforeUrl(url);
            } catch {
              if (!cancelled) setBeforeUrl(project.photoUri);
            }
          } else if (!cancelled) {
            setBeforeUrl(project.photoUri);
          }
        }

        const out = await requestRender({
          projectId: project.id,
          style: project.style,
        });
        if (cancelled) return;
        useApp.getState().setRenderedUri(out.renderedPath);
        setAfterUrl(out.renderedUrl);
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Echec du rendu";
        if (!cancelled) setErrorMsg(msg);
      } finally {
        if (!cancelled) setBusy(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [project?.id, project?.style, project?.photoUri]);

  const caption = project?.style
    ? `Style ${styleLabel(project.style).toLowerCase()} – Beige sable`
    : "Style moderne – Beige sable";

  const previewUrl = mode === "avant" ? beforeUrl : afterUrl;

  return (
    <Screen
      dark
      padded={false}
      footer={
        <View className="gap-2">
          <Button
            label="Modifier le style"
            variant="secondary"
            onPress={() => router.back()}
          />
          <Button
            label="Continuer"
            variant="primary"
            disabled={busy || !!errorMsg}
            onPress={() => router.push("/analysis")}
          />
        </View>
      }
    >
      <View className="flex-row items-center justify-between px-5 py-3">
        <Pressable
          onPress={() => router.back()}
          hitSlop={12}
          className="w-10 h-10 items-center justify-center"
        >
          <Ionicons name="close" size={26} color="#F6F1E8" />
        </Pressable>

        <View className="flex-row bg-sand rounded-pill p-1">
          <Pressable
            onPress={() => setMode("avant")}
            className={`px-4 h-8 rounded-pill items-center justify-center ${
              mode === "avant" ? "bg-ink" : ""
            }`}
          >
            <Text
              className={`text-sm font-medium ${
                mode === "avant" ? "text-cream" : "text-ink"
              }`}
            >
              Avant
            </Text>
          </Pressable>
          <Pressable
            onPress={() => setMode("apres")}
            className={`px-4 h-8 rounded-pill items-center justify-center ${
              mode === "apres" ? "bg-ink" : ""
            }`}
          >
            <Text
              className={`text-sm font-medium ${
                mode === "apres" ? "text-cream" : "text-ink"
              }`}
            >
              Après
            </Text>
          </Pressable>
        </View>

        <View className="w-10" />
      </View>

      <View className="mx-5 mt-2 rounded-card overflow-hidden bg-ink-700 aspect-[3/5] items-center justify-center">
        {previewUrl ? (
          <Image
            source={{ uri: previewUrl }}
            style={{ width: "100%", height: "100%" }}
            contentFit="cover"
            transition={200}
          />
        ) : busy ? (
          <View className="items-center gap-3">
            <ActivityIndicator color="#F6F1E8" />
            <Text className="text-cream text-sm">Génération en cours…</Text>
          </View>
        ) : errorMsg ? (
          <View className="items-center gap-2 px-6">
            <Ionicons name="alert-circle-outline" size={32} color="#F6F1E8" />
            <Text className="text-cream text-center text-sm">{errorMsg}</Text>
          </View>
        ) : (
          <Text className="text-cream text-3xl font-semibold">
            {mode === "avant" ? "Avant" : "Après"}
          </Text>
        )}
      </View>

      <Text className="text-cream text-center mt-5 text-sm">{caption}</Text>

      <View className="flex-row justify-center mt-3 gap-2">
        {[0, 1, 2, 3].map((i) => (
          <Pressable
            key={i}
            onPress={() => setVariant(i)}
            className={`h-16 w-20 rounded-md bg-ink-700 ${
              variant === i ? "border-2 border-sand" : ""
            }`}
          />
        ))}
      </View>
    </Screen>
  );
}
