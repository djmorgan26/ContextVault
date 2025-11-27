// Core types for Context Vault application

export type VaultItemType = "note" | "file" | "medical_record" | "preference" | "measurement" | "other"
export type VaultItemSource = "manual" | "epic" | "fitbit" | "apple_health" | "import"
export type IntegrationProvider = "epic" | "fitbit" | "apple_health"
export type IntegrationStatus = "connected" | "disconnected" | "error" | "syncing"

export interface User {
  id: string
  email: string
  name: string
  picture_url?: string
  preferences: UserPreferences
  created_at: string
}

export interface UserPreferences {
  theme?: "light" | "dark" | "system"
  default_model?: string
}

export interface Tag {
  id: string
  name: string
  color: string
  item_count?: number
  created_at: string
}

export interface VaultItem {
  id: string
  type: VaultItemType
  title: string
  content?: string
  metadata?: Record<string, unknown>
  source: VaultItemSource
  source_id?: string
  tags: Tag[]
  created_at: string
  updated_at: string
}

export interface VaultItemCreate {
  type: VaultItemType
  title: string
  content: string
  tags?: string[]
  metadata?: Record<string, unknown>
}

export interface Integration {
  id: string
  provider: IntegrationProvider
  status: IntegrationStatus
  metadata?: Record<string, unknown>
  last_sync_at?: string
  last_sync_error?: string
  created_at: string
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  vault_items?: string[]
  timestamp: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[]
  pagination: {
    page: number
    per_page: number
    total_items: number
    total_pages: number
  }
}
