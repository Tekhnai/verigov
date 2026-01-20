import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./auth";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function refreshSession(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return false;
  }

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    return false;
  }

  const data = (await response.json()) as { access_token: string; refresh_token: string };
  setTokens(data.access_token, data.refresh_token);
  return true;
}

async function parseErrorMessage(response: Response): Promise<string> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      const data = await response.json();
      if (data && typeof data.detail === "string") {
        return data.detail;
      }
      if (data) {
        return JSON.stringify(data);
      }
    } catch {
      // fall through to text
    }
  }

  try {
    const text = await response.text();
    if (text) {
      return text;
    }
  } catch {
    // ignore
  }

  return "Request failed";
}

async function request<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
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
    if (
      response.status === 401 &&
      retry &&
      !path.startsWith("/auth/login") &&
      !path.startsWith("/auth/register") &&
      !path.startsWith("/auth/refresh")
    ) {
      const refreshed = await refreshSession();
      if (refreshed) {
        return request<T>(path, options, false);
      }
      clearTokens();
      window.location.href = "/login";
      throw new Error("Sessao expirada. Entre novamente.");
    }

    const message = await parseErrorMessage(response);
    throw new Error(message);
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
  listTargets: () =>
    request<
      Array<{
        id: number;
        document: string;
        name_hint?: string | null;
        created_at?: string;
      }>
    >("/targets"),
  createTarget: (document: string, nameHint?: string) =>
    request<{
      id: number;
      document: string;
      name_hint?: string | null;
      created_at?: string;
    }>("/targets", {
      method: "POST",
      body: JSON.stringify({ document, name_hint: nameHint, type: "CNPJ" }),
    }),
  runCheck: (targetId: number) => request(`/targets/${targetId}/check`, { method: "POST" }),
  getLatestReport: (targetId: number) =>
    request<{ summary_json: Record<string, any> }>(`/targets/${targetId}/report/latest`),
};
