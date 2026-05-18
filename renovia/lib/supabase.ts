import "react-native-url-polyfill/auto";
import { createClient } from "@supabase/supabase-js";
import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const url = process.env.EXPO_PUBLIC_SUPABASE_URL;
const anonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

if (!url || !anonKey) {
  console.warn(
    "[Renovia] EXPO_PUBLIC_SUPABASE_URL / EXPO_PUBLIC_SUPABASE_ANON_KEY manquants. " +
      "Copier .env.example en .env et remplir les valeurs."
  );
}

const SecureStoreAdapter = {
  getItem: (key: string) => SecureStore.getItemAsync(key),
  setItem: (key: string, value: string) => SecureStore.setItemAsync(key, value),
  removeItem: (key: string) => SecureStore.deleteItemAsync(key),
};

export const supabase = createClient(url ?? "http://localhost", anonKey ?? "anon", {
  auth: {
    storage: Platform.OS === "web" ? undefined : SecureStoreAdapter,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

export type Database = {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          full_name: string | null;
          avatar_url: string | null;
          created_at: string;
        };
      };
      artisans: {
        Row: {
          id: string;
          name: string;
          city: string | null;
          about: string | null;
          rating: number;
          reviews_count: number;
          verified: boolean;
          avatar_url: string | null;
          portfolio: string[];
          created_at: string;
        };
      };
      projects: {
        Row: {
          id: string;
          user_id: string;
          title: string | null;
          type: string;
          style: string | null;
          rooms: number;
          surface_m2: number | null;
          photo_path: string | null;
          rendered_path: string | null;
          status: string;
          estimate: unknown;
          analysis: unknown;
          created_at: string;
          updated_at: string;
        };
      };
      bookings: {
        Row: {
          id: string;
          project_id: string;
          artisan_id: string;
          user_id: string;
          scheduled_at: string;
          deposit_paid: boolean;
          deposit_chf: number | null;
          total_chf: number | null;
          status: string;
          created_at: string;
        };
      };
      reviews: {
        Row: {
          id: string;
          booking_id: string;
          user_id: string;
          artisan_id: string;
          rating: number;
          comment: string | null;
          created_at: string;
        };
      };
    };
  };
};

export const PHOTO_BUCKET = "project-photos";
