export function chf(amount: number): string {
  const formatted = new Intl.NumberFormat("fr-CH", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
  return `CHF ${formatted}.-`;
}

export function projectTypeLabel(t: string): string {
  const map: Record<string, string> = {
    peinture_murale: "Peinture murale",
    papier_peint: "Papier peint",
    carrelage: "Carrelage",
    enduit: "Enduit / Béton ciré",
    boiserie: "Boiserie / Lambris",
    autre: "Autre",
  };
  return map[t] ?? t;
}

export function styleLabel(s: string): string {
  const map: Record<string, string> = {
    moderne: "Moderne",
    minimaliste: "Minimaliste",
    classique: "Classique",
    scandinave: "Scandinave",
  };
  return map[s] ?? s;
}
