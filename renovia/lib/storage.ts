import * as FileSystem from "expo-file-system";
import { decode as decodeBase64 } from "base64-arraybuffer";
import { PHOTO_BUCKET, supabase } from "./supabase";

export async function uploadProjectPhoto(localUri: string): Promise<string> {
  const { data: userRes } = await supabase.auth.getUser();
  const userId = userRes.user?.id;
  if (!userId) throw new Error("Utilisateur non connecté.");

  const ext = guessExt(localUri);
  const path = `${userId}/${Date.now()}.${ext}`;

  const base64 = await FileSystem.readAsStringAsync(localUri, {
    encoding: FileSystem.EncodingType.Base64,
  });
  const bytes = decodeBase64(base64);

  const { error } = await supabase.storage
    .from(PHOTO_BUCKET)
    .upload(path, bytes, {
      contentType: `image/${ext === "jpg" ? "jpeg" : ext}`,
      upsert: false,
    });
  if (error) throw error;
  return path;
}

export async function getSignedUrl(path: string, expiresInSec = 3600): Promise<string> {
  const { data, error } = await supabase.storage
    .from(PHOTO_BUCKET)
    .createSignedUrl(path, expiresInSec);
  if (error) throw error;
  return data.signedUrl;
}

function guessExt(uri: string): string {
  const m = uri.match(/\.([a-zA-Z0-9]+)(?:\?|$)/);
  const ext = (m?.[1] ?? "jpg").toLowerCase();
  return ext === "jpeg" ? "jpg" : ext;
}
