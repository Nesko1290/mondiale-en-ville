import { supabase, type Database } from "./supabase";
import type { Estimate, ProjectStyle, ProjectType, WallAnalysis } from "./types";

type ProjectRow = Database["public"]["Tables"]["projects"]["Row"];
type ArtisanRow = Database["public"]["Tables"]["artisans"]["Row"];
type BookingRow = Database["public"]["Tables"]["bookings"]["Row"];

export async function listProjects(): Promise<ProjectRow[]> {
  const { data, error } = await supabase
    .from("projects")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return data ?? [];
}

export async function createProject(input: {
  type: ProjectType;
  style?: ProjectStyle;
  photoPath?: string;
  surfaceM2?: number;
  rooms?: number;
  title?: string;
}): Promise<ProjectRow> {
  const { data: userRes } = await supabase.auth.getUser();
  const userId = userRes.user?.id;
  if (!userId) throw new Error("Utilisateur non connecté.");
  const { data, error } = await supabase
    .from("projects")
    .insert({
      user_id: userId,
      type: input.type,
      style: input.style ?? null,
      photo_path: input.photoPath ?? null,
      surface_m2: input.surfaceM2 ?? null,
      rooms: input.rooms ?? 1,
      title: input.title ?? null,
      status: "brouillon",
    })
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function updateProject(
  id: string,
  patch: Partial<{
    style: ProjectStyle;
    photo_path: string;
    rendered_path: string;
    estimate: Estimate;
    analysis: WallAnalysis;
    status: string;
    surface_m2: number;
    title: string;
  }>
): Promise<ProjectRow> {
  const { data, error } = await supabase
    .from("projects")
    .update({ ...patch, updated_at: new Date().toISOString() })
    .eq("id", id)
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function listArtisans(): Promise<ArtisanRow[]> {
  const { data, error } = await supabase
    .from("artisans")
    .select("*")
    .order("rating", { ascending: false });
  if (error) throw error;
  return data ?? [];
}

export async function getArtisan(id: string): Promise<ArtisanRow | null> {
  const { data, error } = await supabase
    .from("artisans")
    .select("*")
    .eq("id", id)
    .maybeSingle();
  if (error) throw error;
  return data;
}

export async function createBooking(input: {
  projectId: string;
  artisanId: string;
  scheduledAt: string;
  totalChf: number;
  depositChf: number;
}): Promise<BookingRow> {
  const { data: userRes } = await supabase.auth.getUser();
  const userId = userRes.user?.id;
  if (!userId) throw new Error("Utilisateur non connecté.");
  const { data, error } = await supabase
    .from("bookings")
    .insert({
      project_id: input.projectId,
      artisan_id: input.artisanId,
      user_id: userId,
      scheduled_at: input.scheduledAt,
      total_chf: input.totalChf,
      deposit_chf: input.depositChf,
      status: "reserve",
    })
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function requestRender(input: {
  projectId: string;
  style?: string;
}): Promise<{ renderedPath: string; renderedUrl: string | null }> {
  const { data, error } = await supabase.functions.invoke("render", {
    body: input,
  });
  if (error) throw error;
  if (!data?.renderedPath) throw new Error("Render response invalide");
  return data as { renderedPath: string; renderedUrl: string | null };
}

export function subscribeBooking(
  bookingId: string,
  onChange: (row: BookingRow) => void
): () => void {
  const channel = supabase
    .channel(`booking:${bookingId}`)
    .on(
      "postgres_changes",
      { event: "UPDATE", schema: "public", table: "bookings", filter: `id=eq.${bookingId}` },
      (payload) => onChange(payload.new as BookingRow)
    )
    .subscribe();
  return () => {
    supabase.removeChannel(channel);
  };
}
