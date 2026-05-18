import { create } from "zustand";
import type { Artisan, Estimate, Project, ProjectStyle, ProjectType, WallAnalysis } from "./types";

type AppState = {
  currentProject: Partial<Project> | null;
  estimate: Estimate | null;
  analysis: WallAnalysis | null;
  selectedArtisan: Artisan | null;
  scheduledAt: string | null;

  startProject: () => void;
  setPhoto: (uri: string) => void;
  setType: (type: ProjectType) => void;
  setStyle: (style: ProjectStyle) => void;
  setRenderedUri: (uri: string) => void;
  setAnalysis: (analysis: WallAnalysis) => void;
  setEstimate: (estimate: Estimate) => void;
  setArtisan: (artisan: Artisan) => void;
  setSchedule: (iso: string) => void;
  reset: () => void;
};

export const useApp = create<AppState>((set) => ({
  currentProject: null,
  estimate: null,
  analysis: null,
  selectedArtisan: null,
  scheduledAt: null,

  startProject: () =>
    set({
      currentProject: {
        id: String(Date.now()),
        status: "brouillon",
        rooms: 1,
        createdAt: new Date().toISOString(),
      },
    }),
  setPhoto: (uri) =>
    set((s) => ({ currentProject: { ...(s.currentProject ?? {}), photoUri: uri } })),
  setType: (type) =>
    set((s) => ({ currentProject: { ...(s.currentProject ?? {}), type } })),
  setStyle: (style) =>
    set((s) => ({ currentProject: { ...(s.currentProject ?? {}), style } })),
  setRenderedUri: (uri) =>
    set((s) => ({ currentProject: { ...(s.currentProject ?? {}), renderedUri: uri } })),
  setAnalysis: (analysis) => set({ analysis }),
  setEstimate: (estimate) => set({ estimate }),
  setArtisan: (artisan) => set({ selectedArtisan: artisan }),
  setSchedule: (iso) => set({ scheduledAt: iso }),
  reset: () =>
    set({
      currentProject: null,
      estimate: null,
      analysis: null,
      selectedArtisan: null,
      scheduledAt: null,
    }),
}));
