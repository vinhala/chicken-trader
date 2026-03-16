function resolveApiBase(): string {
  const configured = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (configured && configured.trim()) {
    return configured;
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    const protocol = window.location.protocol === "https:" ? "https" : "http";
    if (host === "app.localhost") {
      return `${protocol}://api.localhost/api`;
    }
    if (host.startsWith("app.")) {
      return `${protocol}://api.${host.slice(4)}/api`;
    }
  }

  return "/api";
}

const base = resolveApiBase();

async function parseResponseBody(res: Response): Promise<any> {
  const contentType = (res.headers.get("content-type") || "").toLowerCase();
  const bodyText = await res.text();

  if (!bodyText) {
    return {};
  }
  if (contentType.includes("application/json")) {
    try {
      return JSON.parse(bodyText);
    } catch {
      return { raw: bodyText };
    }
  }
  return { raw: bodyText };
}

export async function api(path: string, opts: RequestInit = {}) {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${base}${path}`, { ...opts, headers });
  const payload = await parseResponseBody(res);
  if (res.status === 401) {
    localStorage.removeItem("token");
  }
  if (!res.ok) {
    throw new Error(payload.detail || payload.raw || `Request failed: ${res.status}`);
  }
  return payload;
}
