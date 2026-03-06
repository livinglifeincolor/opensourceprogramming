const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

interface AuthResponse {
  message: string;
  error?: string;
  user?: {
    id: number;
    username: string;
    email: string;
    created_at?: string;
  };
}

async function request(
  endpoint: string,
  options: RequestInit = {},
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });
  return res.json();
}

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<AuthResponse> {
  return request("/api/auth/logout", { method: "POST" });
}

export async function getMe(): Promise<AuthResponse> {
  return request("/api/auth/me");
}
