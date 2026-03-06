const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

// ──────────────────────── Types ──────────────────────────

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

export interface Post {
  id: number;
  title: string;
  content?: string;
  author: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

interface PostsResponse {
  posts: Post[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  error?: string;
}

interface PostResponse {
  post: Post;
  error?: string;
}

interface MutationResponse {
  message: string;
  error?: string;
}

// ──────────────────────── Request Helper ─────────────────

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });
  return res.json();
}

// ──────────────────────── Auth ───────────────────────────

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/logout", { method: "POST" });
}

export async function getMe(): Promise<AuthResponse> {
  return request<AuthResponse>("/api/auth/me");
}

// ──────────────────────── Posts ──────────────────────────

export async function getPosts(page: number = 1): Promise<PostsResponse> {
  return request<PostsResponse>(`/api/posts?page=${page}`);
}

export async function getPost(id: number): Promise<PostResponse> {
  return request<PostResponse>(`/api/posts/${id}`);
}

export async function createPost(
  title: string,
  content: string,
): Promise<MutationResponse> {
  return request<MutationResponse>("/api/posts", {
    method: "POST",
    body: JSON.stringify({ title, content }),
  });
}

export async function updatePost(
  id: number,
  title: string,
  content: string,
): Promise<MutationResponse> {
  return request<MutationResponse>(`/api/posts/${id}`, {
    method: "PUT",
    body: JSON.stringify({ title, content }),
  });
}

export async function deletePost(id: number): Promise<MutationResponse> {
  return request<MutationResponse>(`/api/posts/${id}`, {
    method: "DELETE",
  });
}
