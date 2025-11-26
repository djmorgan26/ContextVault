"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Shield,
  Lock,
  Database,
  Link2,
  Unlink,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  Heart,
  Activity,
  Apple,
  Download,
  Trash2,
  Loader2,
} from "@/components/icons"
import { useAuth } from "@/lib/auth-context"
import type { Integration, IntegrationStatus } from "@/lib/types"
import { toast } from "sonner"

// Demo integrations
const DEMO_INTEGRATIONS: Integration[] = [
  {
    id: "1",
    provider: "epic",
    status: "connected",
    metadata: { patient_id: "DEMO-123", records_synced: 23 },
    last_sync_at: "2024-11-24T08:00:00Z",
    created_at: "2024-10-15T00:00:00Z",
  },
  {
    id: "2",
    provider: "fitbit",
    status: "connected",
    metadata: { scopes: ["activity", "heartrate", "sleep"] },
    last_sync_at: "2024-11-25T00:00:00Z",
    created_at: "2024-11-01T00:00:00Z",
  },
  {
    id: "3",
    provider: "apple_health",
    status: "disconnected",
    created_at: "2024-11-10T00:00:00Z",
  },
]

const statusConfig: Record<IntegrationStatus, { label: string; color: string; icon: typeof CheckCircle }> = {
  connected: { label: "Connected", color: "text-green-500", icon: CheckCircle },
  disconnected: { label: "Disconnected", color: "text-muted-foreground", icon: Unlink },
  error: { label: "Error", color: "text-destructive", icon: AlertCircle },
  syncing: { label: "Syncing...", color: "text-primary", icon: RefreshCw },
}

const providerConfig = {
  epic: {
    name: "Epic MyChart",
    description: "Access your medical records from Epic-connected healthcare providers",
    icon: Heart,
    color: "#8B5CF6",
  },
  fitbit: {
    name: "Fitbit",
    description: "Sync activity, sleep, and heart rate data from your Fitbit devices",
    icon: Activity,
    color: "#00B0B9",
  },
  apple_health: {
    name: "Apple Health",
    description: "Import health data exported from the Apple Health app",
    icon: Apple,
    color: "#000000",
  },
}

export function SettingsPage() {
  const { user, logout } = useAuth()
  const [integrations, setIntegrations] = useState<Integration[]>(DEMO_INTEGRATIONS)
  const [syncing, setSyncing] = useState<string | null>(null)

  const handleConnect = (provider: string) => {
    toast.success(`Connecting to ${providerConfig[provider as keyof typeof providerConfig].name}...`)
    // In real app, this would redirect to OAuth
    setTimeout(() => {
      setIntegrations((prev) =>
        prev.map((i) =>
          i.provider === provider
            ? { ...i, status: "connected" as IntegrationStatus, last_sync_at: new Date().toISOString() }
            : i,
        ),
      )
      toast.success("Connected successfully!")
    }, 1500)
  }

  const handleDisconnect = (provider: string) => {
    setIntegrations((prev) =>
      prev.map((i) => (i.provider === provider ? { ...i, status: "disconnected" as IntegrationStatus } : i)),
    )
    toast.success("Integration disconnected")
  }

  const handleSync = async (provider: string) => {
    setSyncing(provider)
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setIntegrations((prev) =>
      prev.map((i) => (i.provider === provider ? { ...i, last_sync_at: new Date().toISOString() } : i)),
    )
    setSyncing(null)
    toast.success("Sync complete!")
  }

  const handleExport = () => {
    toast.success("Preparing export... This may take a moment.")
    setTimeout(() => {
      toast.success("Export ready for download!")
    }, 2000)
  }

  return (
    <div className="h-full overflow-auto">
      <div className="mx-auto max-w-4xl p-6">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold">Settings</h1>
          <p className="text-muted-foreground">Manage your account, integrations, and privacy settings</p>
        </div>

        {/* Account Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Account
            </CardTitle>
            <CardDescription>Your account information and security</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{user?.name || "Demo User"}</p>
                <p className="text-sm text-muted-foreground">{user?.email || "demo@contextvault.app"}</p>
              </div>
              <Badge variant="secondary">
                <Lock className="mr-1 h-3 w-3" />
                Encrypted
              </Badge>
            </div>

            <Separator />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Two-Factor Authentication</Label>
                  <p className="text-sm text-muted-foreground">Protected via Google Account</p>
                </div>
                <Badge variant="outline" className="text-green-500 border-green-500">
                  <CheckCircle className="mr-1 h-3 w-3" />
                  Enabled
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Encryption Status</Label>
                  <p className="text-sm text-muted-foreground">AES-256-GCM with PBKDF2 key derivation</p>
                </div>
                <Badge variant="outline" className="text-green-500 border-green-500">
                  <Lock className="mr-1 h-3 w-3" />
                  Active
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Integrations Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Link2 className="h-5 w-5" />
              Integrations
            </CardTitle>
            <CardDescription>Connect external services to sync data to your vault</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {integrations.map((integration) => {
              const config = providerConfig[integration.provider as keyof typeof providerConfig]
              const status = statusConfig[integration.status]
              const StatusIcon = status.icon
              const ProviderIcon = config.icon

              return (
                <div key={integration.id} className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex items-center gap-4">
                    <div
                      className="flex h-12 w-12 items-center justify-center rounded-lg"
                      style={{ backgroundColor: `${config.color}15` }}
                    >
                      <ProviderIcon className="h-6 w-6" style={{ color: config.color }} />
                    </div>
                    <div>
                      <p className="font-medium">{config.name}</p>
                      <p className="text-sm text-muted-foreground">{config.description}</p>
                      {integration.status === "connected" && integration.last_sync_at && (
                        <p className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          Last synced: {new Date(integration.last_sync_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className={`flex items-center gap-1 ${status.color}`}>
                      <StatusIcon className="h-4 w-4" />
                      <span className="text-sm">{status.label}</span>
                    </div>

                    {integration.status === "connected" ? (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleSync(integration.provider)}
                          disabled={syncing === integration.provider}
                        >
                          {syncing === integration.provider ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <RefreshCw className="h-4 w-4" />
                          )}
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleDisconnect(integration.provider)}>
                          <Unlink className="h-4 w-4" />
                        </Button>
                      </>
                    ) : (
                      <Button size="sm" onClick={() => handleConnect(integration.provider)}>
                        <Link2 className="mr-2 h-4 w-4" />
                        Connect
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* AI Settings */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              AI & Privacy
            </CardTitle>
            <CardDescription>Configure how AI interacts with your data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Ephemeral Processing</Label>
                <p className="text-sm text-muted-foreground">AI containers are destroyed after each session</p>
              </div>
              <Switch checked disabled />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Default AI Model</Label>
                <p className="text-sm text-muted-foreground">Choose the model for chat interactions</p>
              </div>
              <Select defaultValue="llama3.1">
                <SelectTrigger className="w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="llama3.1">Llama 3.1 8B</SelectItem>
                  <SelectItem value="mistral">Mistral 7B</SelectItem>
                  <SelectItem value="phi3">Phi-3 Mini</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Save Chat History</Label>
                <p className="text-sm text-muted-foreground">Store encrypted chat history for context</p>
              </div>
              <Switch />
            </div>
          </CardContent>
        </Card>

        {/* Data Management */}
        <Card>
          <CardHeader>
            <CardTitle className="text-destructive">Data Management</CardTitle>
            <CardDescription>Export or delete your data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Export All Data</Label>
                <p className="text-sm text-muted-foreground">Download all your vault items as JSON</p>
              </div>
              <Button variant="outline" onClick={handleExport}>
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-destructive">Delete Account</Label>
                <p className="text-sm text-muted-foreground">Permanently delete your account and all data</p>
              </div>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Account</AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. All your vault items, integrations, and settings will be permanently
                      deleted.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={() => {
                        toast.success("Account deleted")
                        logout()
                      }}
                      className="bg-destructive text-destructive-foreground"
                    >
                      Delete Account
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
