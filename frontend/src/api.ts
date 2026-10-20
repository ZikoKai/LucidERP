import { ref } from "vue";

export const apiKey = ref(sessionStorage.getItem("lucid-api-key") || "");
export function saveKey() {
  sessionStorage.setItem("lucid-api-key", apiKey.value);
}
export interface Line {
  id: number;
  product_id: number;
  quantite: number;
  prix_unitaire: string;
}
export interface Order {
  id: number;
  contact_id: number;
  date: string;
  statut: string;
  risk_score: number;
  risk_explanation: string;
  lines: Line[];
}
export interface Proposal {
  id: number;
  order_id: number | null;
  statut: string;
  payload: unknown;
  raisonnement: string;
  risk_score: number;
  risk_explanation: string;
  decide_par: string | null;
  decide_le: string | null;
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL || "http://localhost:8000"}${path}`,
    {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(apiKey.value ? { "X-API-Key": apiKey.value } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    },
  );
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      typeof error.detail === "string"
        ? error.detail
        : `Request failed (${response.status})`,
    );
  }
  return response.json() as Promise<T>;
}
export const total = (order: Order) =>
  order.lines.reduce(
    (sum, line) => sum + Number(line.prix_unitaire) * line.quantite,
    0,
  );
export const money = (value: number) =>
  value.toLocaleString("en", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
