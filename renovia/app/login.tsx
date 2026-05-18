import { Platform, Alert, View, Text } from "react-native";
import * as AppleAuthentication from "expo-apple-authentication";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Button";
import { Header } from "@/components/Header";
import { signInWithApple, signInWithGoogle } from "@/lib/auth";
import { useState } from "react";

export default function LoginScreen() {
  const [loading, setLoading] = useState(false);

  const handleApple = async () => {
    try {
      setLoading(true);
      await signInWithApple();
      router.replace("/(tabs)");
    } catch (e) {
      const message = e instanceof Error ? e.message : "Connexion impossible.";
      Alert.alert("Erreur", message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    try {
      setLoading(true);
      await signInWithGoogle();
      router.replace("/(tabs)");
    } catch (e) {
      const message = e instanceof Error ? e.message : "Connexion impossible.";
      Alert.alert("Erreur", message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen
      scroll={false}
      footer={
        <View className="gap-3">
          {Platform.OS === "ios" ? (
            <View style={{ width: "100%", height: 56 }} className={loading ? "opacity-60" : ""}>
              <AppleAuthentication.AppleAuthenticationButton
                buttonType={
                  AppleAuthentication.AppleAuthenticationButtonType.SIGN_IN
                }
                buttonStyle={
                  AppleAuthentication.AppleAuthenticationButtonStyle.BLACK
                }
                cornerRadius={999}
                style={{ width: "100%", height: 56 }}
                onPress={loading ? undefined : handleApple}
              />
            </View>
          ) : null}
          <Button
            label="Continuer avec Google"
            variant="secondary"
            loading={loading}
            disabled={loading}
            icon={<Ionicons name="logo-google" size={18} color="#000000" />}
            onPress={handleGoogle}
          />
          <Text className="text-muted text-xs text-center mt-2">
            En continuant vous acceptez nos conditions générales.
          </Text>
        </View>
      }
    >
      <Header back onBack={() => router.back()} />
      <View className="flex-1 items-center justify-center">
        <Text className="text-4xl font-serif text-ink">Renovia</Text>
        <Text className="text-muted mt-3">Connectez-vous pour démarrer.</Text>
      </View>
    </Screen>
  );
}
