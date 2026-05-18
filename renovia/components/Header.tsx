import { View, Text, Pressable } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { ReactNode } from "react";

type Props = {
  title?: string;
  back?: boolean;
  right?: ReactNode;
  onBack?: () => void;
};

export function Header({ title, back, right, onBack }: Props) {
  return (
    <View className="flex-row items-center justify-between py-3">
      <View className="w-10">
        {back ? (
          <Pressable
            onPress={() => (onBack ? onBack() : router.back())}
            hitSlop={12}
            className="w-10 h-10 items-center justify-center"
          >
            <Ionicons name="close" size={26} color="#0B1320" />
          </Pressable>
        ) : null}
      </View>
      <Text className="text-ink font-semibold text-base">{title ?? ""}</Text>
      <View className="w-10 items-end">{right}</View>
    </View>
  );
}
