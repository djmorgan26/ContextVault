"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { AppSidebar } from "@/components/app-sidebar"
import { VaultDashboard } from "@/components/vault/vault-dashboard"
import { ChatInterface } from "@/components/chat/chat-interface"
import { SettingsPage } from "@/components/settings/settings-page"

type View = "vault" | "chat" | "settings"

export function AppShell() {
  const [currentView, setCurrentView] = useState<View>("vault")

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar currentView={currentView} onViewChange={setCurrentView} />
      <main className="flex-1 overflow-auto">
        <div className={cn(currentView !== "vault" && "hidden")}>
          <VaultDashboard />
        </div>
        <div className={cn(currentView !== "chat" && "hidden")}>
          <ChatInterface />
        </div>
        <div className={cn(currentView !== "settings" && "hidden")}>
          <SettingsPage />
        </div>
      </main>
    </div>
  )
}
