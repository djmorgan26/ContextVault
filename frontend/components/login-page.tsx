"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { VaultLogo, Shield, Lock, Bot, Database } from "@/components/icons"
import { useAuth } from "@/lib/auth-context"

export function LoginPage() {
  const { login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)

  const handleDemoLogin = () => {
    // Demo mode - create a mock user session
    const demoUser = {
      id: "demo-user-001",
      email: "demo@contextvault.app",
      name: "Demo User",
      preferences: { theme: "dark" },
      created_at: new Date().toISOString(),
    }
    sessionStorage.setItem("demo_user", JSON.stringify(demoUser))
    window.location.reload()
  }

  const handleGoogleLogin = () => {
    setIsLoading(true)
    login()
  }

  const features = [
    {
      icon: Shield,
      title: "Privacy First",
      description: "Your data is encrypted with your own key. Not even we can read it.",
    },
    {
      icon: Lock,
      title: "Zero Knowledge",
      description: "AI processes your data in ephemeral containers that are destroyed after use.",
    },
    {
      icon: Database,
      title: "Secure Vault",
      description: "Store medical records, notes, and personal data with military-grade encryption.",
    },
    {
      icon: Bot,
      title: "Private AI",
      description: "Chat with AI that understands your context without compromising privacy.",
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <VaultLogo className="h-8 w-8 text-primary" />
            <span className="text-xl font-semibold">Context Vault</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Your Personal AI, <span className="text-primary">Your Private Data</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-muted-foreground">
            Store sensitive information securely. Chat with AI that understands your context. Your data never leaves
            your control.
          </p>

          {/* Login Card */}
          <Card className="mx-auto mt-10 max-w-md">
            <CardHeader>
              <CardTitle>Get Started</CardTitle>
              <CardDescription>Sign in to access your private vault</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button onClick={handleGoogleLogin} disabled={isLoading} className="w-full" size="lg">
                {isLoading ? (
                  "Redirecting..."
                ) : (
                  <>
                    <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Sign in with Google
                  </>
                )}
              </Button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">Or</span>
                </div>
              </div>

              <Button variant="outline" onClick={handleDemoLogin} className="w-full bg-transparent" size="lg">
                Try Demo Mode
              </Button>

              <p className="text-xs text-muted-foreground">
                Demo mode uses sample data stored locally in your browser.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Features Grid */}
        <div className="mx-auto mt-20 grid max-w-5xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <Card key={feature.title} className="bg-card/50">
              <CardHeader>
                <feature.icon className="h-10 w-10 text-primary" />
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Trust Indicators */}
        <div className="mx-auto mt-20 max-w-3xl text-center">
          <h2 className="text-2xl font-semibold">Enterprise-Grade Security</h2>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-8 text-muted-foreground">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <span>AES-256-GCM Encryption</span>
            </div>
            <div className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              <span>Zero-Knowledge Architecture</span>
            </div>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-primary" />
              <span>HIPAA Ready</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Context Vault - Privacy-first personal intelligence</p>
        </div>
      </footer>
    </div>
  )
}
