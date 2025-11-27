import { getAccessToken } from "@/lib/auth-context"
import type { VaultItem, VaultItemCreate, Tag, Integration, PaginatedResponse, User } from "@/lib/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ""

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken()

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Auth API
export const authAPI = {
  getMe: () => fetchAPI<User>("/api/auth/me"),
}

// Vault API
export const vaultAPI = {
  listItems: (params?: {
    page?: number
    per_page?: number
    type?: string
    tags?: string[]
    search?: string
  }) => {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.set("page", params.page.toString())
    if (params?.per_page) searchParams.set("per_page", params.per_page.toString())
    if (params?.type) searchParams.set("type", params.type)
    if (params?.tags) params.tags.forEach((t) => searchParams.append("tags", t))
    if (params?.search) searchParams.set("search", params.search)

    return fetchAPI<PaginatedResponse<VaultItem>>(`/api/vault/items?${searchParams}`)
  },

  getItem: (id: string) => fetchAPI<VaultItem>(`/api/vault/items/${id}`),

  createItem: (data: VaultItemCreate) =>
    fetchAPI<VaultItem>("/api/vault/items", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateItem: (id: string, data: Partial<VaultItemCreate>) =>
    fetchAPI<VaultItem>(`/api/vault/items/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteItem: (id: string) => fetchAPI<void>(`/api/vault/items/${id}`, { method: "DELETE" }),

  uploadFile: async (file: File, title: string, tags?: string[]) => {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("title", title)
    if (tags) formData.append("tags", tags.join(","))

    const token = getAccessToken()
    const response = await fetch(`${API_BASE}/api/vault/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    })

    if (!response.ok) throw new Error("Upload failed")
    return response.json() as Promise<VaultItem>
  },

  listTags: () => fetchAPI<{ tags: Tag[] }>("/api/vault/tags"),

  createTag: (name: string, color?: string) =>
    fetchAPI<Tag>("/api/vault/tags", {
      method: "POST",
      body: JSON.stringify({ name, color }),
    }),

  deleteTag: (id: string) => fetchAPI<void>(`/api/vault/tags/${id}`, { method: "DELETE" }),
}

// Integration API
export const integrationAPI = {
  list: () => fetchAPI<{ integrations: Integration[] }>("/api/integrations"),

  connectEpic: () => {
    window.location.href = `${API_BASE}/api/integrations/epic/connect`
  },

  disconnectEpic: () => fetchAPI<void>("/api/integrations/epic", { method: "DELETE" }),

  syncEpic: () =>
    fetchAPI<{ status: string; job_id: string }>("/api/integrations/epic/sync", {
      method: "POST",
    }),

  connectFitbit: () => {
    window.location.href = `${API_BASE}/api/integrations/fitbit/connect`
  },

  disconnectFitbit: () => fetchAPI<void>("/api/integrations/fitbit", { method: "DELETE" }),
}

// Chat API (SSE streaming)
export function streamChat(
  message: string,
  contextTags?: string[],
  onChunk: (chunk: string) => void = () => {},
  onContext: (items: string[]) => void = () => {},
  onDone: () => void = () => {},
  onError: (error: Error) => void = () => {},
) {
  const token = getAccessToken()

  fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify({
      message,
      context_tags: contextTags,
    }),
  })
    .then(async (response) => {
      if (!response.ok) throw new Error("Chat request failed")
      if (!response.body) throw new Error("No response body")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.chunk) onChunk(data.chunk)
              if (data.vault_items) onContext(data.vault_items)
              if (data.done) onDone()
            } catch {
              // Ignore parse errors
            }
          }
        }
      }
      onDone()
    })
    .catch(onError)
}
