export type ProjectType =
  | "peinture_murale"
  | "papier_peint"
  | "carrelage"
  | "enduit"
  | "boiserie"
  | "autre";

export type ProjectStyle = "moderne" | "minimaliste" | "classique" | "scandinave";

export type ProjectStatus =
  | "brouillon"
  | "analyse"
  | "estime"
  | "reserve"
  | "en_cours"
  | "termine";

export type Project = {
  id: string;
  title: string;
  type: ProjectType;
  style?: ProjectStyle;
  rooms: number;
  surfaceM2?: number;
  photoUri?: string;
  renderedUri?: string;
  status: ProjectStatus;
  createdAt: string;
};

export type Artisan = {
  id: string;
  name: string;
  city: string;
  rating: number;
  reviewsCount: number;
  avatarUri?: string;
  about: string;
  verified: boolean;
  portfolio: string[];
};

export type EstimateLine = {
  label: string;
  amountChf: number;
};

export type Estimate = {
  lines: EstimateLine[];
  totalChf: number;
  depositChf: number;
};

export type WallAnalysis = {
  imageQuality: "bonne" | "moyenne" | "faible";
  cracks: string;
  holes: string;
  humidity: string;
  existingFinish: string;
  recommendation?: string;
};

export type Booking = {
  id: string;
  projectId: string;
  artisanId: string;
  scheduledAt: string;
  depositPaid: boolean;
  status: ProjectStatus;
};
