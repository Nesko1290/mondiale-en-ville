import { Pressable, Text, ActivityIndicator, View } from "react-native";
import { ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

type Props = {
  label: string;
  onPress?: () => void;
  variant?: Variant;
  loading?: boolean;
  disabled?: boolean;
  icon?: ReactNode;
  fullWidth?: boolean;
};

export function Button({
  label,
  onPress,
  variant = "primary",
  loading,
  disabled,
  icon,
  fullWidth = true,
}: Props) {
  const base =
    "h-14 rounded-pill items-center justify-center flex-row px-6";
  const styles: Record<Variant, string> = {
    primary: "bg-ink",
    secondary: "bg-sand",
    ghost: "bg-transparent border border-line",
  };
  const textStyles: Record<Variant, string> = {
    primary: "text-cream font-semibold text-base",
    secondary: "text-ink font-semibold text-base",
    ghost: "text-ink font-semibold text-base",
  };
  const isDisabled = disabled || loading;
  return (
    <Pressable
      onPress={onPress}
      disabled={isDisabled}
      className={`${base} ${styles[variant]} ${fullWidth ? "w-full" : ""} ${
        isDisabled ? "opacity-60" : ""
      }`}
    >
      {loading ? (
        <ActivityIndicator color={variant === "primary" ? "#F6F1E8" : "#0B1320"} />
      ) : (
        <View className="flex-row items-center gap-2">
          {icon}
          <Text className={textStyles[variant]}>{label}</Text>
        </View>
      )}
    </Pressable>
  );
}
