"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, Heart, Activity, Folder, Tag, Clock } from "@/components/icons"
import type { VaultItem, VaultItemType } from "@/lib/types"
import { formatDistanceToNow } from "date-fns"

const typeIcons: Record<VaultItemType, typeof FileText> = {
  note: FileText,
  file: Folder,
  medical_record: Heart,
  preference: Tag,
  measurement: Activity,
  other: FileText,
}

const sourceLabels: Record<string, string> = {
  manual: "Manual",
  epic: "Epic MyChart",
  fitbit: "Fitbit",
  apple_health: "Apple Health",
  import: "Imported",
}

interface VaultItemCardProps {
  item: VaultItem
  onClick: () => void
}

export function VaultItemCard({ item, onClick }: VaultItemCardProps) {
  const Icon = typeIcons[item.type] || FileText
  const timeAgo = formatDistanceToNow(new Date(item.updated_at), { addSuffix: true })

  return (
    <Card className="cursor-pointer transition-colors hover:bg-accent/50" onClick={onClick}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <div>
              <CardTitle className="line-clamp-1 text-base">{item.title}</CardTitle>
              <p className="text-xs text-muted-foreground">{sourceLabels[item.source] || item.source}</p>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="line-clamp-2 text-sm text-muted-foreground">{item.content?.slice(0, 120)}...</p>
        <div className="mt-3 flex items-center justify-between">
          <div className="flex flex-wrap gap-1">
            {item.tags.slice(0, 2).map((tag) => (
              <Badge
                key={tag.id}
                variant="secondary"
                className="text-xs"
                style={{ backgroundColor: `${tag.color}20`, color: tag.color }}
              >
                {tag.name}
              </Badge>
            ))}
            {item.tags.length > 2 && (
              <Badge variant="secondary" className="text-xs">
                +{item.tags.length - 2}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {timeAgo}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
