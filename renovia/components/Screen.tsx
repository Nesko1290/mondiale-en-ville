import { SafeAreaView } from "react-native-safe-area-context";
import { View, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import { ReactNode } from "react";

type Props = {
  children: ReactNode;
  footer?: ReactNode;
  scroll?: boolean;
  dark?: boolean;
  padded?: boolean;
};

export function Screen({
  children,
  footer,
  scroll = true,
  dark = false,
  padded = true,
}: Props) {
  const bg = dark ? "bg-ink" : "bg-cream";
  const Body = scroll ? ScrollView : View;
  return (
    <SafeAreaView className={`flex-1 ${bg}`} edges={["top", "left", "right"]}>
      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <Body
          className={`flex-1 ${padded ? "px-5" : ""}`}
          contentContainerStyle={scroll ? { paddingBottom: 24 } : undefined}
        >
          {children}
        </Body>
        {footer ? (
          <View className={`px-5 pb-6 pt-2 ${dark ? "bg-ink" : "bg-cream"}`}>
            {footer}
          </View>
        ) : null}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
