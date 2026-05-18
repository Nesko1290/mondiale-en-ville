import type { Artisan, Estimate, Project, WallAnalysis } from "./types";

export const mockProjects: Project[] = [
  {
    id: "p1",
    title: "Salon moderne",
    type: "peinture_murale",
    style: "moderne",
    rooms: 4,
    surfaceM2: 25,
    status: "en_cours",
    createdAt: "2024-05-01",
  },
  {
    id: "p2",
    title: "Salle de bain",
    type: "carrelage",
    rooms: 2,
    surfaceM2: 12,
    status: "estime",
    createdAt: "2024-04-22",
  },
];

export const mockArtisans: Artisan[] = [
  {
    id: "a1",
    name: "Peinture & Fils Sàrl",
    city: "Genève",
    rating: 4.9,
    reviewsCount: 126,
    about:
      "Entreprise familiale avec 15 ans d'expérience. Spécialisée dans les travaux de peinture intérieure.",
    verified: true,
    portfolio: [],
  },
  {
    id: "a2",
    name: "Renov'Art SA",
    city: "Lausanne",
    rating: 4.7,
    reviewsCount: 84,
    about: "Artisans certifiés, finitions haut de gamme, intervention rapide.",
    verified: true,
    portfolio: [],
  },
];

export const mockAnalysis: WallAnalysis = {
  imageQuality: "bonne",
  cracks: "Aucune fissure majeure détectée",
  holes: "1 petit trou détecté",
  humidity: "Aucun signe d'humidité",
  existingFinish: "Peinture en bon état",
  recommendation:
    "Reboucher le trou et ponçage léger avant peinture.",
};

export const mockEstimate: Estimate = {
  lines: [
    { label: "Préparation des murs", amountChf: 450 },
    { label: "Peinture (2 couches)", amountChf: 1250 },
    { label: "Matériaux", amountChf: 300 },
    { label: "Déplacement", amountChf: 150 },
  ],
  totalChf: 2150,
  depositChf: 215,
};
