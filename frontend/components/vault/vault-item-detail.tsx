"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
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
import { X, Edit, Trash2, Clock, Database } from "@/components/icons"
import type { VaultItem } from "@/lib/types"
import { format } from "date-fns"

const sourceLabels: Record<string, string> = {
  manual: "Manually Created",
  epic: "Epic MyChart",
  fitbit: "Fitbit",
  apple_health: "Apple Health",
  import: "Imported",
}

interface VaultItemDetailProps {
  item: VaultItem
  onClose: () => void
  onEdit: () => void
  onDelete: () => void
}

export function VaultItemDetail({ item, onClose, onEdit, onDelete }: VaultItemDetailProps) {
  return (
    <div className="flex h-full w-[400px] flex-col border-l border-border bg-card">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border p-4">
        <h2 className="font-semibold">Item Details</h2>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={onEdit}>
            <Edit className="h-4 w-4" />
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="ghost" size="icon" className="text-destructive">
                <Trash2 className="h-4 w-4" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete Item</AlertDialogTitle>
                <AlertDialogDescription>
                  Are you sure you want to delete "{item.title}"? This action can be undone within 90 days.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={onDelete} className="bg-destructive text-destructive-foreground">
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          <h3 className="text-lg font-semibold">{item.title}</h3>

          <div className="mt-2 flex flex-wrap gap-1">
            {item.tags.map((tag) => (
              <Badge key={tag.id} style={{ backgroundColor: `${tag.color}20`, color: tag.color }}>
                {tag.name}
              </Badge>
            ))}
          </div>

          <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Database className="h-4 w-4" />
              {sourceLabels[item.source]}
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {format(new Date(item.updated_at), "PPp")}
            </div>
          </div>

          <Separator className="my-4" />

          <div className="prose prose-sm dark:prose-invert max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{item.content}</pre>
          </div>

          {item.metadata && Object.keys(item.metadata).length > 0 && (
            <>
              <Separator className="my-4" />
              <div>
                <h4 className="mb-2 text-sm font-medium">Metadata</h4>
                <pre className="rounded-md bg-muted p-2 text-xs">{JSON.stringify(item.metadata, null, 2)}</pre>
              </div>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
