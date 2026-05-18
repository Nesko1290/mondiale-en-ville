import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Screen } from "@/components/Screen";
import { useApp } from "@/lib/store";

export default function CaptureScreen() {
  const setPhoto = useApp((s) => s.setPhoto);
  const startProject = useApp((s) => s.startProject);

  const onShutter = () => {
    startProject();
    setPhoto("mock://photo");
    router.push("/project-type");
  };

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
          <Pressable hitSlop={12} className="w-10 h-10 items-center justify-center">
            <Ionicons name="flash-outline" size={24} color="#F6F1E8" />
          </Pressable>
        </View>

        <View className="flex-1 justify-center">
          {/* TODO: wire expo-camera */}
          <View className="bg-ink-700 aspect-square rounded-card mx-5 items-center justify-center">
            <View className="bg-ink-800/80 px-4 py-2 rounded-pill">
              <Text className="text-cream text-xs">
                Prenez une photo nette du mur ou de la pièce
              </Text>
            </View>
          </View>
        </View>

        <View className="flex-row items-center justify-between px-8 pb-10 pt-6">
          <Text className="text-cream text-sm w-16">Photo</Text>
          <Pressable
            onPress={onShutter}
            className="w-20 h-20 rounded-full bg-sand items-center justify-center"
          >
            <View className="w-16 h-16 rounded-full border-2 border-ink/20" />
          </Pressable>
          <Text className="text-cream text-sm w-16 text-right">Conseils</Text>
        </View>
      </View>
    </Screen>
  );
}
