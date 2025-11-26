"use client"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { VaultLogo, Database, MessageSquare, Settings, LogOut, Moon, Sun, User } from "@/components/icons"
import { useAuth } from "@/lib/auth-context"
import { useTheme } from "next-themes"

type View = "vault" | "chat" | "settings"

interface AppSidebarProps {
  currentView: View
  onViewChange: (view: View) => void
}

export function AppSidebar({ currentView, onViewChange }: AppSidebarProps) {
  const { user, logout } = useAuth()
  const { theme, setTheme } = useTheme()

  const navItems = [
    { id: "vault" as const, icon: Database, label: "Vault" },
    { id: "chat" as const, icon: MessageSquare, label: "AI Chat" },
    { id: "settings" as const, icon: Settings, label: "Settings" },
  ]

  return (
    <TooltipProvider delayDuration={0}>
      <aside className="flex h-full w-16 flex-col border-r border-border bg-sidebar">
        {/* Logo */}
        <div className="flex h-16 items-center justify-center border-b border-sidebar-border">
          <VaultLogo className="h-8 w-8 text-sidebar-primary" />
        </div>

        {/* Navigation */}
        <nav className="flex flex-1 flex-col items-center gap-2 py-4">
          {navItems.map((item) => (
            <Tooltip key={item.id}>
              <TooltipTrigger asChild>
                <Button
                  variant={currentView === item.id ? "secondary" : "ghost"}
                  size="icon"
                  onClick={() => onViewChange(item.id)}
                  className={cn("h-10 w-10", currentView === item.id && "bg-sidebar-accent text-sidebar-primary")}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="sr-only">{item.label}</span>
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">{item.label}</TooltipContent>
            </Tooltip>
          ))}
        </nav>

        {/* Theme Toggle & User Menu */}
        <div className="flex flex-col items-center gap-2 border-t border-sidebar-border py-4">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="h-10 w-10"
              >
                <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                <span className="sr-only">Toggle theme</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Toggle theme</TooltipContent>
          </Tooltip>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-10 w-10 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.picture_url || "/placeholder.svg"} alt={user?.name} />
                  <AvatarFallback>
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent side="right" align="end" className="w-56">
              <div className="px-2 py-1.5">
                <p className="text-sm font-medium">{user?.name || "User"}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => onViewChange("settings")}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-destructive">
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>
    </TooltipProvider>
  )
}
