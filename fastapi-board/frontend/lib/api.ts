const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Post {
  id: number;
  title: string;
  content: string;
  created_at: string;
}

export interface PostCreate {
  title: string;
  content: string;
}

export interface PostUpdate {
  title?: string;
  content?: string;
}

export interface SearchResult {
  total: number;
  results: Post[];
}

export async function getPosts(page = 1, size = 10): Promise<Post[]> {
  const res = await fetch(
    `${API_URL}/api/posts?page=${page}&size=${size}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to fetch posts");
  return res.json();
}

export async function getPostsCount(): Promise<{ total: number }> {
  const res = await fetch(`${API_URL}/api/posts/count`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch count");
  return res.json();
}

export async function getPost(id: number): Promise<Post> {
  const res = await fetch(`${API_URL}/api/posts/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Post not found");
  return res.json();
}

export async function createPost(data: PostCreate): Promise<Post> {
  const res = await fetch(`${API_URL}/api/posts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create post");
  return res.json();
}

export async function updatePost(id: number, data: PostUpdate): Promise<Post> {
  const res = await fetch(`${API_URL}/api/posts/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update post");
  return res.json();
}

export async function deletePost(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/api/posts/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete post");
}

export async function searchPosts(
  q: string,
  page = 1,
  size = 10
): Promise<SearchResult> {
  const res = await fetch(
    `${API_URL}/api/posts/search?q=${encodeURIComponent(q)}&page=${page}&size=${size}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to search posts");
  return res.json();
}
