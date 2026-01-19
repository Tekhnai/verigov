import { getAccessToken } from "./auth";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  return (await response.json()) as T;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string, tenantName: string) =>
    request<{ access_token: string; refresh_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, tenant_name: tenantName }),
    }),
  listTargets: () => request<Array<{ id: number; document: string; name_hint?: string }>>("/targets"),
  createTarget: (document: string, nameHint?: string) =>
    request<{ id: number }>("/targets", {
      method: "POST",
      body: JSON.stringify({ document, name_hint: nameHint, type: "CNPJ" }),
    }),
  runCheck: (targetId: number) => request(`/targets/${targetId}/check`, { method: "POST" }),
  getLatestReport: (targetId: number) =>
    request<{ summary_json: Record<string, string> }>(`/targets/${targetId}/report/latest`),
};
