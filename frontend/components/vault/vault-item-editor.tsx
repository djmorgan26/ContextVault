"use client"

import { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { X } from "@/components/icons"
import type { VaultItem, VaultItemType, Tag } from "@/lib/types"

interface VaultItemEditorProps {
  open: boolean
  onClose: () => void
  onSave: (data: { title: string; content: string; type: VaultItemType; tags: string[] }) => void
  item?: VaultItem | null
  tags: Tag[]
}

export function VaultItemEditor({ open, onClose, onSave, item, tags }: VaultItemEditorProps) {
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [type, setType] = useState<VaultItemType>("note")
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [newTag, setNewTag] = useState("")

  useEffect(() => {
    if (item) {
      setTitle(item.title)
      setContent(item.content || "")
      setType(item.type)
      setSelectedTags(item.tags.map((t) => t.name))
    } else {
      setTitle("")
      setContent("")
      setType("note")
      setSelectedTags([])
    }
  }, [item, open])

  const handleSave = () => {
    if (!title.trim()) return
    onSave({ title, content, type, tags: selectedTags })
  }

  const addTag = (tagName: string) => {
    if (tagName && !selectedTags.includes(tagName)) {
      setSelectedTags([...selectedTags, tagName])
    }
    setNewTag("")
  }

  const removeTag = (tagName: string) => {
    setSelectedTags(selectedTags.filter((t) => t !== tagName))
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{item ? "Edit Item" : "Create New Item"}</DialogTitle>
          <DialogDescription>
            {item ? "Update your vault item" : "Add a new item to your secure vault"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Enter title..." />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="type">Type</Label>
              <Select value={type} onValueChange={(v) => setType(v as VaultItemType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="note">Note</SelectItem>
                  <SelectItem value="medical_record">Medical Record</SelectItem>
                  <SelectItem value="preference">Preference</SelectItem>
                  <SelectItem value="measurement">Measurement</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags</Label>
              <Select value="" onValueChange={addTag}>
                <SelectTrigger>
                  <SelectValue placeholder="Add tag..." />
                </SelectTrigger>
                <SelectContent>
                  {tags
                    .filter((t) => !selectedTags.includes(t.name))
                    .map((tag) => (
                      <SelectItem key={tag.id} value={tag.name}>
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-2 rounded-full" style={{ backgroundColor: tag.color }} />
                          {tag.name}
                        </div>
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {selectedTags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {selectedTags.map((tagName) => {
                const tag = tags.find((t) => t.name === tagName)
                return (
                  <Badge
                    key={tagName}
                    style={{
                      backgroundColor: tag ? `${tag.color}20` : undefined,
                      color: tag?.color,
                    }}
                  >
                    {tagName}
                    <button type="button" onClick={() => removeTag(tagName)} className="ml-1 hover:text-destructive">
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )
              })}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="content">Content</Label>
            <Textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter content..."
              className="min-h-[200px] font-mono text-sm"
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!title.trim()}>
            {item ? "Save Changes" : "Create Item"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
