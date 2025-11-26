"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Send, Bot, User, Sparkles, Tag, Loader2 } from "@/components/icons"
import type { ChatMessage, Tag as TagType } from "@/lib/types"

// Demo tags
const DEMO_TAGS: TagType[] = [
  { id: "t1", name: "medical", color: "#ef4444", created_at: "" },
  { id: "t3", name: "goals", color: "#22c55e", created_at: "" },
  { id: "t4", name: "fitness", color: "#f59e0b", created_at: "" },
  { id: "t5", name: "preferences", color: "#8b5cf6", created_at: "" },
]

// Simulated AI responses
const AI_RESPONSES: Record<string, string> = {
  "blood pressure": `Based on your recent vault data, your blood pressure reading from November 2024 shows:

**Systolic:** 118 mmHg
**Diastolic:** 76 mmHg
**Pulse:** 72 bpm

This reading is within the **normal range** (below 120/80). Your morning measurement was taken at rest, which is ideal for accurate readings. 

Looking at your health goals, you're on track with your target to maintain blood pressure below 120/80. Keep up the good work!`,

  "health goals": `I found your "Health Goals for 2025" in your vault. Here's a summary:

1. **Blood Pressure**: Maintain below 120/80 ✓ (Currently on track)
2. **Exercise**: Increase to 4x per week (Currently 3x)
3. **Sleep**: Improve to 7-8 hours consistently
4. **Diet**: Reduce processed food intake
5. **Annual Checkup**: Scheduled for March

**Progress Note:** You're doing well on most goals. The area needing most attention appears to be sleep quality. Would you like suggestions for improving sleep habits?`,

  activity: `Here's your weekly activity summary from Week 47:

| Metric | Value | Status |
|--------|-------|--------|
| Steps | 52,340 total (7,477/day avg) | ✓ Exceeded goal 5/7 days |
| Active Minutes | 245 min | Good |
| Calories Burned | 2,840 kcal | On target |
| Flights Climbed | 28 | Active |
| Resting Heart Rate | 62 bpm | Healthy |

This was a strong week overall! Your step count is excellent and aligns with your fitness goals.`,

  default: `I've reviewed your vault data and I'm here to help. I can see you have information about:

- Medical records (blood pressure, lab results)
- Health goals for 2025
- Activity tracking from Fitbit
- Personal preferences

What would you like to know more about? I can analyze trends, provide summaries, or help you understand your health data in context.`,
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: `Hello! I'm your private AI assistant. I have access to your secure vault and can help you understand your personal data.

**Your data never leaves your control** - I process everything in an ephemeral container that's destroyed after our conversation.

What would you like to know about your vault?`,
      timestamp: new Date().toISOString(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [contextTag, setContextTag] = useState<string>("all")
  const [usedContext, setUsedContext] = useState<string[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const getAIResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase()
    if (lowerQuery.includes("blood pressure") || lowerQuery.includes("bp")) {
      return AI_RESPONSES["blood pressure"]
    }
    if (lowerQuery.includes("goal") || lowerQuery.includes("2025")) {
      return AI_RESPONSES["health goals"]
    }
    if (lowerQuery.includes("activity") || lowerQuery.includes("step") || lowerQuery.includes("exercise")) {
      return AI_RESPONSES["activity"]
    }
    return AI_RESPONSES["default"]
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate context retrieval
    const contextItems = ["Blood Pressure Reading", "Health Goals", "Activity Summary"]
    setUsedContext(contextItems.slice(0, Math.floor(Math.random() * 3) + 1))

    // Simulate AI response with delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const aiMessage: ChatMessage = {
      id: `ai-${Date.now()}`,
      role: "assistant",
      content: getAIResponse(userMessage.content),
      vault_items: contextItems,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, aiMessage])
    setIsLoading(false)
    setUsedContext([])
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
            <Bot className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="font-semibold">AI Assistant</h1>
            <p className="text-sm text-muted-foreground">Private context from your vault</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Tag className="h-4 w-4 text-muted-foreground" />
          <Select value={contextTag} onValueChange={setContextTag}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Context filter" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Tags</SelectItem>
              {DEMO_TAGS.map((tag) => (
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

      {/* Messages */}
      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
        <div className="mx-auto max-w-3xl space-y-6">
          {messages.map((message) => (
            <div key={message.id} className={`flex gap-4 ${message.role === "user" ? "justify-end" : ""}`}>
              {message.role === "assistant" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                }`}
              >
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  {message.content.split("\n").map((line, i) => {
                    if (line.startsWith("**") && line.endsWith("**")) {
                      return (
                        <p key={i} className="font-semibold">
                          {line.replace(/\*\*/g, "")}
                        </p>
                      )
                    }
                    if (line.startsWith("|")) {
                      return null // Skip table lines for simplicity
                    }
                    if (line.match(/^\d+\./)) {
                      return (
                        <p key={i} className="ml-4">
                          {line}
                        </p>
                      )
                    }
                    return <p key={i}>{line || <br />}</p>
                  })}
                </div>

                {message.vault_items && message.vault_items.length > 0 && (
                  <div className="mt-3 flex items-center gap-2 border-t border-border/50 pt-2">
                    <span className="text-xs text-muted-foreground">Context used:</span>
                    {message.vault_items.slice(0, 2).map((item, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              {message.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-4">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <div className="max-w-[80%] rounded-lg bg-muted px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">
                    {usedContext.length > 0 ? `Analyzing ${usedContext.length} vault items...` : "Thinking..."}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="mx-auto flex max-w-3xl gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your vault data..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </form>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-muted-foreground">
          Your data is processed in ephemeral containers and never stored by AI systems.
        </p>
      </div>
    </div>
  )
}
