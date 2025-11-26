"use client"

import { useState, useEffect } from "react"
import { AuthProvider, useAuth } from "@/lib/auth-context"
import { LoginPage } from "@/components/login-page"
import { AppShell } from "@/components/app-shell"
import { Spinner } from "@/components/ui/spinner"

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Spinner className="h-8 w-8" />
          <p className="text-muted-foreground">Loading Context Vault...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginPage />
  }

  return <AppShell />
}

export default function HomePage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
