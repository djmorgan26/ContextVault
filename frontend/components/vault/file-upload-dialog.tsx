"use client"

import type React from "react"

import { useState, useCallback } from "react"
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
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Upload, X, File } from "@/components/icons"
import type { Tag } from "@/lib/types"

interface FileUploadDialogProps {
  open: boolean
  onClose: () => void
  onUpload: (file: File, title: string, tags: string[]) => void
  tags: Tag[]
}

export function FileUploadDialog({ open, onClose, onUpload, tags }: FileUploadDialogProps) {
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState("")
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [isDragging, setIsDragging] = useState(false)

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile) {
        setFile(droppedFile)
        if (!title) setTitle(droppedFile.name.replace(/\.[^/.]+$/, ""))
      }
    },
    [title],
  )

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      if (!title) setTitle(selectedFile.name.replace(/\.[^/.]+$/, ""))
    }
  }

  const handleUpload = () => {
    if (file && title) {
      onUpload(file, title, selectedTags)
      setFile(null)
      setTitle("")
      setSelectedTags([])
    }
  }

  const addTag = (tagName: string) => {
    if (tagName && !selectedTags.includes(tagName)) {
      setSelectedTags([...selectedTags, tagName])
    }
  }

  const removeTag = (tagName: string) => {
    setSelectedTags(selectedTags.filter((t) => t !== tagName))
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload File</DialogTitle>
          <DialogDescription>
            Upload a document to your secure vault. Supported formats: PDF, images, text files.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Drop Zone */}
          <div
            className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
              isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
            }`}
            onDragOver={(e) => {
              e.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="flex items-center gap-3">
                <File className="h-10 w-10 text-primary" />
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setFile(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <>
                <Upload className="h-10 w-10 text-muted-foreground" />
                <p className="mt-2 text-sm text-muted-foreground">
                  Drag and drop a file, or{" "}
                  <label className="cursor-pointer text-primary hover:underline">
                    browse
                    <input
                      type="file"
                      className="hidden"
                      onChange={handleFileSelect}
                      accept=".pdf,.txt,.md,.jpg,.jpeg,.png,.gif"
                    />
                  </label>
                </p>
              </>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Enter title..." />
          </div>

          <div className="space-y-2">
            <Label>Tags</Label>
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
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleUpload} disabled={!file || !title}>
            Upload
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
