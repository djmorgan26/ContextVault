"use client"

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import type { User, AuthTokens } from "@/lib/types"

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: () => void
  logout: () => void
  refreshToken: () => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// In-memory token storage (more secure than localStorage)
let accessToken: string | null = null
let refreshTokenValue: string | null = null

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    if (!accessToken) {
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch("/api/auth/me", {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Token might be expired, try refresh
        const refreshed = await refreshToken()
        if (!refreshed) {
          setUser(null)
          accessToken = null
          refreshTokenValue = null
        }
      }
    } catch {
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refreshToken = async (): Promise<boolean> => {
    if (!refreshTokenValue) return false

    try {
      const response = await fetch("/api/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshTokenValue }),
      })

      if (response.ok) {
        const data: AuthTokens = await response.json()
        accessToken = data.access_token
        if (data.refresh_token) {
          refreshTokenValue = data.refresh_token
        }
        await fetchUser()
        return true
      }
    } catch {
      // Refresh failed
    }

    return false
  }

  const login = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = "/api/auth/google/login"
  }

  const logout = async () => {
    try {
      if (refreshTokenValue) {
        await fetch("/api/auth/logout", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: refreshTokenValue }),
        })
      }
    } catch {
      // Ignore logout errors
    } finally {
      accessToken = null
      refreshTokenValue = null
      setUser(null)
    }
  }

  // Handle OAuth callback tokens from URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get("access_token")
    const refresh = urlParams.get("refresh_token")

    if (token && refresh) {
      accessToken = token
      refreshTokenValue = refresh
      // Clean URL
      window.history.replaceState({}, "", window.location.pathname)
      fetchUser()
    } else {
      // Check for existing session (demo mode)
      const demoUser = sessionStorage.getItem("demo_user")
      if (demoUser) {
        setUser(JSON.parse(demoUser))
        setIsLoading(false)
      } else {
        setIsLoading(false)
      }
    }
  }, [fetchUser])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export function getAccessToken() {
  return accessToken
}
