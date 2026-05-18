import { useRef, useState } from "react";
import { ActivityIndicator, Text, View, Pressable } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Button";
import { useApp } from "@/lib/store";
import { uploadProjectPhoto } from "@/lib/storage";

export default function CaptureScreen() {
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [busy, setBusy] = useState(false);

  const onShutter = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const photo = await cameraRef.current?.takePictureAsync({ quality: 0.8 });
      if (photo) {
        const state = useApp.getState();
        if (!state.currentProject) {
          state.startProject();
        }
        useApp.getState().setPhoto(photo.uri);
        try {
          const path = await uploadProjectPhoto(photo.uri);
          useApp.getState().setPhoto(path);
        } catch (e) {
          console.log("uploadProjectPhoto error", e);
        }
        router.push("/project-type");
      }
    } finally {
      setBusy(false);
    }
  };

  if (!permission) {
    return (
      <Screen dark padded={false} scroll={false}>
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator color="#F6F1E8" />
        </View>
      </Screen>
    );
  }

  if (!permission.granted) {
    return (
      <Screen dark padded scroll={false}>
        <View className="flex-1 items-center justify-center gap-6">
          <Text className="text-cream text-base text-center">
            Autorisation caméra requise
          </Text>
          <Button label="Autoriser" onPress={() => requestPermission()} fullWidth={false} />
        </View>
      </Screen>
    );
  }

  return (
    <Screen dark padded={false} scroll={false}>
      <View className="flex-1">
        <View className="flex-row items-center justify-between px-5 py-3">
          <Pressable
            onPress={() => router.back()}
            hitSlop={12}
            className="w-10 h-10 items-center justify-center"
          >
            <Ionicons name="close" size={26} color="#F6F1E8" />
          </Pressable>
          {/* TODO flash toggle */}
          <Pressable hitSlop={12} className="w-10 h-10 items-center justify-center">
            <Ionicons name="flash-outline" size={24} color="#F6F1E8" />
          </Pressable>
        </View>

        <View className="flex-1 justify-center">
          <View className="aspect-square mx-5 rounded-card overflow-hidden">
            <CameraView
              ref={cameraRef}
              facing="back"
              style={{ flex: 1 }}
            />
          </View>
        </View>

        <View className="flex-row items-center justify-between px-8 pb-10 pt-6">
          <Text className="text-cream text-sm w-16">Photo</Text>
          <Pressable
            onPress={onShutter}
            disabled={busy}
            className="w-20 h-20 rounded-full bg-sand items-center justify-center"
          >
            {busy ? (
              <ActivityIndicator color="#0B1320" />
            ) : (
              <View className="w-16 h-16 rounded-full border-2 border-ink/20" />
            )}
          </Pressable>
          <Text className="text-cream text-sm w-16 text-right">Conseils</Text>
        </View>
      </View>
    </Screen>
  );
}
