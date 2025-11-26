"use client"

import { useState, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, Search, FileText, Heart, Activity, Folder, Tag, Filter, Upload } from "@/components/icons"
import { VaultItemCard } from "@/components/vault/vault-item-card"
import { VaultItemEditor } from "@/components/vault/vault-item-editor"
import { VaultItemDetail } from "@/components/vault/vault-item-detail"
import { FileUploadDialog } from "@/components/vault/file-upload-dialog"
import type { VaultItem, VaultItemType, Tag as TagType } from "@/lib/types"

// Demo data for vault items
const DEMO_ITEMS: VaultItem[] = [
  {
    id: "1",
    type: "medical_record",
    title: "Blood Pressure Reading - November 2024",
    content:
      "Systolic: 118 mmHg\nDiastolic: 76 mmHg\nPulse: 72 bpm\n\nNotes: Reading taken at rest, morning measurement. Within normal range.",
    source: "epic",
    tags: [{ id: "t1", name: "medical", color: "#ef4444", created_at: "" }],
    created_at: "2024-11-20T10:30:00Z",
    updated_at: "2024-11-20T10:30:00Z",
  },
  {
    id: "2",
    type: "medical_record",
    title: "Lab Results - Lipid Panel",
    content:
      "Total Cholesterol: 185 mg/dL (Desirable: <200)\nHDL: 55 mg/dL (Good: >40)\nLDL: 110 mg/dL (Near optimal: 100-129)\nTriglycerides: 100 mg/dL (Normal: <150)\n\nOverall: Good lipid profile, continue current lifestyle habits.",
    source: "epic",
    tags: [
      { id: "t1", name: "medical", color: "#ef4444", created_at: "" },
      { id: "t2", name: "labs", color: "#3b82f6", created_at: "" },
    ],
    created_at: "2024-11-15T14:00:00Z",
    updated_at: "2024-11-15T14:00:00Z",
  },
  {
    id: "3",
    type: "note",
    title: "Health Goals for 2025",
    content:
      "1. Maintain blood pressure below 120/80\n2. Exercise 4x per week (currently 3x)\n3. Improve sleep to 7-8 hours consistently\n4. Reduce processed food intake\n5. Annual checkup scheduled for March\n\nProgress: On track with most goals. Need to focus on sleep quality.",
    source: "manual",
    tags: [{ id: "t3", name: "goals", color: "#22c55e", created_at: "" }],
    created_at: "2024-11-10T09:00:00Z",
    updated_at: "2024-11-22T16:45:00Z",
  },
  {
    id: "4",
    type: "measurement",
    title: "Weekly Activity Summary - Week 47",
    content:
      "Steps: 52,340 (avg 7,477/day)\nActive minutes: 245 min\nCalories burned: 2,840 kcal\nFlights climbed: 28\nResting heart rate: 62 bpm\n\nNote: Exceeded step goal 5/7 days. Good week overall.",
    source: "fitbit",
    tags: [{ id: "t4", name: "fitness", color: "#f59e0b", created_at: "" }],
    created_at: "2024-11-24T00:00:00Z",
    updated_at: "2024-11-24T00:00:00Z",
  },
  {
    id: "5",
    type: "preference",
    title: "AI Context Preferences",
    content:
      "When discussing health:\n- I prefer metric units for weight, imperial for height\n- Focus on actionable insights over raw data\n- My primary health goal is cardiovascular fitness\n- I have no known allergies\n- I take no regular medications\n\nCommunication style:\n- Direct and concise responses\n- Include source references when discussing medical topics",
    source: "manual",
    tags: [{ id: "t5", name: "preferences", color: "#8b5cf6", created_at: "" }],
    created_at: "2024-10-01T08:00:00Z",
    updated_at: "2024-11-18T11:30:00Z",
  },
  {
    id: "6",
    type: "file",
    title: "Annual Physical Exam Report",
    content:
      "PDF document containing full annual physical examination results from October 2024. Includes vitals, blood work, and physician notes.",
    source: "manual",
    tags: [
      { id: "t1", name: "medical", color: "#ef4444", created_at: "" },
      { id: "t6", name: "documents", color: "#64748b", created_at: "" },
    ],
    created_at: "2024-10-15T00:00:00Z",
    updated_at: "2024-10-15T00:00:00Z",
  },
]

const DEMO_TAGS: TagType[] = [
  { id: "t1", name: "medical", color: "#ef4444", item_count: 3, created_at: "" },
  { id: "t2", name: "labs", color: "#3b82f6", item_count: 1, created_at: "" },
  { id: "t3", name: "goals", color: "#22c55e", item_count: 1, created_at: "" },
  { id: "t4", name: "fitness", color: "#f59e0b", item_count: 1, created_at: "" },
  { id: "t5", name: "preferences", color: "#8b5cf6", item_count: 1, created_at: "" },
  { id: "t6", name: "documents", color: "#64748b", item_count: 1, created_at: "" },
]

const typeIcons: Record<VaultItemType, typeof FileText> = {
  note: FileText,
  file: Folder,
  medical_record: Heart,
  preference: Tag,
  measurement: Activity,
  other: FileText,
}

export function VaultDashboard() {
  const [items, setItems] = useState<VaultItem[]>(DEMO_ITEMS)
  const [tags] = useState<TagType[]>(DEMO_TAGS)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedType, setSelectedType] = useState<string>("all")
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [selectedItem, setSelectedItem] = useState<VaultItem | null>(null)
  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<VaultItem | null>(null)
  const [isUploadOpen, setIsUploadOpen] = useState(false)

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchesSearch =
        searchQuery === "" ||
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.content?.toLowerCase().includes(searchQuery.toLowerCase())

      const matchesType = selectedType === "all" || item.type === selectedType

      const matchesTags =
        selectedTags.length === 0 || selectedTags.every((tagName) => item.tags.some((t) => t.name === tagName))

      return matchesSearch && matchesType && matchesTags
    })
  }, [items, searchQuery, selectedType, selectedTags])

  const handleCreateItem = (data: { title: string; content: string; type: VaultItemType; tags: string[] }) => {
    const newItem: VaultItem = {
      id: `item-${Date.now()}`,
      type: data.type,
      title: data.title,
      content: data.content,
      source: "manual",
      tags: data.tags.map((name) => ({
        id: `tag-${name}`,
        name,
        color: tags.find((t) => t.name === name)?.color || "#64748b",
        created_at: new Date().toISOString(),
      })),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    setItems([newItem, ...items])
    setIsEditorOpen(false)
  }

  const handleUpdateItem = (data: { title: string; content: string; type: VaultItemType; tags: string[] }) => {
    if (!editingItem) return
    const updatedItem: VaultItem = {
      ...editingItem,
      title: data.title,
      content: data.content,
      type: data.type,
      tags: data.tags.map((name) => ({
        id: `tag-${name}`,
        name,
        color: tags.find((t) => t.name === name)?.color || "#64748b",
        created_at: new Date().toISOString(),
      })),
      updated_at: new Date().toISOString(),
    }
    setItems(items.map((i) => (i.id === editingItem.id ? updatedItem : i)))
    setEditingItem(null)
    setSelectedItem(updatedItem)
  }

  const handleDeleteItem = (id: string) => {
    setItems(items.filter((i) => i.id !== id))
    setSelectedItem(null)
  }

  const handleFileUpload = (file: File, title: string, uploadTags: string[]) => {
    const newItem: VaultItem = {
      id: `file-${Date.now()}`,
      type: "file",
      title,
      content: `Uploaded file: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`,
      source: "manual",
      tags: uploadTags.map((name) => ({
        id: `tag-${name}`,
        name,
        color: tags.find((t) => t.name === name)?.color || "#64748b",
        created_at: new Date().toISOString(),
      })),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    setItems([newItem, ...items])
    setIsUploadOpen(false)
  }

  const toggleTagFilter = (tagName: string) => {
    setSelectedTags((prev) => (prev.includes(tagName) ? prev.filter((t) => t !== tagName) : [...prev, tagName]))
  }

  // Stats for overview
  const stats = useMemo(
    () => ({
      total: items.length,
      medical: items.filter((i) => i.type === "medical_record").length,
      notes: items.filter((i) => i.type === "note").length,
      files: items.filter((i) => i.type === "file").length,
    }),
    [items],
  )

  return (
    <div className="flex h-full">
      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">Your Vault</h1>
              <p className="text-muted-foreground">{stats.total} items securely stored</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => setIsUploadOpen(true)}>
                <Upload className="mr-2 h-4 w-4" />
                Upload
              </Button>
              <Button onClick={() => setIsEditorOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                New Item
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Items</CardTitle>
                <Folder className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Medical Records</CardTitle>
                <Heart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.medical}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Notes</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.notes}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Files</CardTitle>
                <Upload className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.files}</div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="mb-6 flex flex-wrap items-center gap-4">
            <div className="relative flex-1 min-w-[200px] max-w-md">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search vault..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>

            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-[160px]">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="note">Notes</SelectItem>
                <SelectItem value="medical_record">Medical</SelectItem>
                <SelectItem value="file">Files</SelectItem>
                <SelectItem value="measurement">Measurements</SelectItem>
                <SelectItem value="preference">Preferences</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex flex-wrap items-center gap-2">
              {tags.map((tag) => (
                <Badge
                  key={tag.id}
                  variant={selectedTags.includes(tag.name) ? "default" : "outline"}
                  className="cursor-pointer"
                  style={{
                    backgroundColor: selectedTags.includes(tag.name) ? tag.color : undefined,
                    borderColor: tag.color,
                  }}
                  onClick={() => toggleTagFilter(tag.name)}
                >
                  {tag.name}
                </Badge>
              ))}
            </div>
          </div>

          {/* Items Grid */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredItems.map((item) => (
              <VaultItemCard key={item.id} item={item} onClick={() => setSelectedItem(item)} />
            ))}
          </div>

          {filteredItems.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Folder className="h-12 w-12 text-muted-foreground/50" />
              <h3 className="mt-4 text-lg font-medium">No items found</h3>
              <p className="mt-1 text-muted-foreground">
                {searchQuery || selectedType !== "all" || selectedTags.length > 0
                  ? "Try adjusting your filters"
                  : "Create your first vault item to get started"}
              </p>
              <Button className="mt-4" onClick={() => setIsEditorOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create Item
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Detail Panel */}
      {selectedItem && (
        <VaultItemDetail
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
          onEdit={() => {
            setEditingItem(selectedItem)
          }}
          onDelete={() => handleDeleteItem(selectedItem.id)}
        />
      )}

      {/* Editor Modal */}
      <VaultItemEditor
        open={isEditorOpen || !!editingItem}
        onClose={() => {
          setIsEditorOpen(false)
          setEditingItem(null)
        }}
        onSave={editingItem ? handleUpdateItem : handleCreateItem}
        item={editingItem}
        tags={tags}
      />

      {/* Upload Dialog */}
      <FileUploadDialog
        open={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUpload={handleFileUpload}
        tags={tags}
      />
    </div>
  )
}
