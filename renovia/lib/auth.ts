import { useEffect, useState } from "react";
import { Platform } from "react-native";
import type { Session } from "@supabase/supabase-js";
import * as AppleAuthentication from "expo-apple-authentication";
import * as WebBrowser from "expo-web-browser";
import * as Linking from "expo-linking";
import { supabase } from "./supabase";

WebBrowser.maybeCompleteAuthSession();

export function useSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => {
      setSession(s);
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  return { session, loading };
}

export async function signInWithApple(): Promise<void> {
  if (Platform.OS !== "ios") {
    throw new Error("Sign in with Apple n'est disponible que sur iOS.");
  }
  const credential = await AppleAuthentication.signInAsync({
    requestedScopes: [
      AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
      AppleAuthentication.AppleAuthenticationScope.EMAIL,
    ],
  });
  if (!credential.identityToken) {
    throw new Error("Pas de token Apple reçu.");
  }
  const { error } = await supabase.auth.signInWithIdToken({
    provider: "apple",
    token: credential.identityToken,
  });
  if (error) throw error;
}

export async function signInWithGoogle(): Promise<void> {
  const redirectTo = Linking.createURL("auth-callback");
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo,
      skipBrowserRedirect: true,
    },
  });
  if (error) throw error;
  if (!data?.url) throw new Error("Pas d'URL OAuth retournée par Supabase.");

  const result = await WebBrowser.openAuthSessionAsync(data.url, redirectTo);
  if (result.type !== "success" || !result.url) {
    throw new Error("Connexion Google annulée.");
  }

  const params = parseFragment(result.url);
  const access_token = params.access_token;
  const refresh_token = params.refresh_token;
  if (!access_token || !refresh_token) {
    throw new Error("Tokens manquants dans la redirection.");
  }
  const { error: setErr } = await supabase.auth.setSession({
    access_token,
    refresh_token,
  });
  if (setErr) throw setErr;
}

export async function signOut(): Promise<void> {
  await supabase.auth.signOut();
}

function parseFragment(url: string): Record<string, string> {
  const hashIndex = url.indexOf("#");
  if (hashIndex === -1) return {};
  const fragment = url.slice(hashIndex + 1);
  return Object.fromEntries(
    fragment
      .split("&")
      .map((kv) => kv.split("="))
      .map(([k, v]) => [k, decodeURIComponent(v ?? "")])
  );
}
