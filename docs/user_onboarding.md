# Context Vault - User Onboarding Flows

## First-Time User Journey

### Landing Page → Signed In (5 minutes)

```
Step 1: Landing Page
├─ Hero: "Your Personal AI Vault"
├─ Value props: Privacy, Local AI, Medical records
├─ [Get Started] button
└─ [Sign in with Google] button

Step 2: Google OAuth (30 seconds)
├─ Redirect to Google consent screen
├─ User authorizes email/profile access
├─ Redirect back to app
└─ Account created automatically

Step 3: Welcome & Setup Wizard (2-3 minutes)
├─ Screen 1: "Welcome to Context Vault"
│   ├─ Brief intro to features
│   ├─ Privacy explanation
│   └─ [Next] button
├─ Screen 2: "Choose Your Privacy Level"
│   ├─ ○ Maximum Privacy (Local AI) [Recommended]
│   ├─ ○ Quick Start (Hosted AI temporarily)
│   └─ [Next] button
├─ Screen 3: "AI Setup" (if Local AI chosen)
│   ├─ Check Docker: ✓ Installed
│   ├─ Check Ollama: ✗ Not found
│   ├─ [Install Ollama] button → opens ollama.com
│   ├─ Once installed: [Download Model]
│   ├─ Progress bar: Downloading llama3.1:8b... 45%
│   └─ [Skip for now] button
└─ Screen 4: "Test Your AI"
    ├─ Simple chat interface
    ├─ Pre-filled: "Hello, introduce yourself"
    ├─ AI responds: "I'm your private AI assistant..."
    ├─ ✓ Everything working!
    └─ [Start Using Context Vault] button

Step 4: Main Dashboard
├─ Empty state: "Your vault is empty"
├─ Quick actions:
│   ├─ [Upload a file]
│   ├─ [Create a note]
│   └─ [Connect Epic MyChart]
└─ Tutorial tooltips (dismissible)
```

### Onboarding Checklist

Displayed in sidebar until all complete:

```
□ Upload your first file
□ Create a note
□ Connect Epic MyChart (optional)
□ Chat with your AI
□ Organize with tags
```

---

## User Flows by Feature

### Upload File to Vault

```
1. User clicks [Upload File] or drags file to dashboard
   ├─ File selector appears (or drag-drop zone highlights)
   └─ Supported: PDF, JPG, PNG, TXT (max 10MB)

2. User selects file (e.g., medical_report.pdf)
   ├─ Upload starts immediately
   ├─ Progress bar shows: Uploading... 34%
   └─ Backend: Parse, encrypt, store

3. File uploaded successfully
   ├─ Toast notification: "✓ File uploaded: medical_report.pdf"
   ├─ Modal appears: "Add details"
   │   ├─ Title: [Pre-filled from filename]
   │   ├─ Tags: [Add tags...] (autocomplete existing tags)
   │   └─ [Save] button
   └─ File appears in vault dashboard

4. User can now:
   ├─ View file (decrypted, shown in browser)
   ├─ Edit title/tags
   ├─ Delete file
   └─ Ask AI about file content
```

### Create Note

```
1. User clicks [Create Note]
   ├─ Modal appears with markdown editor
   │   ├─ Title field
   │   ├─ Content editor (rich markdown)
   │   └─ Tags field
   └─ Toolbar: Bold, Italic, List, Code, Link

2. User writes note
   ├─ Auto-save every 10 seconds (draft)
   └─ Live markdown preview

3. User clicks [Save]
   ├─ Note encrypted and stored
   ├─ Toast: "✓ Note saved"
   └─ Appears in vault dashboard
```

### Connect Epic MyChart

```
1. User clicks [Connect Epic] in Settings → Integrations

2. Modal appears: "Connect Epic MyChart"
   ├─ "Access your medical records from Epic-powered providers"
   ├─ "We'll sync: Patient info, Observations, Medications"
   ├─ Privacy note: "Data encrypted and never shared"
   └─ [Connect Epic MyChart] button

3. User clicks button
   ├─ Redirected to Epic OAuth
   └─ Epic login page appears

4. User logs into Epic MyChart
   ├─ Enters username/password (or SSO)
   └─ Epic 2FA if enabled

5. Epic shows consent screen
   ├─ "Context Vault wants to access:"
   │   ├─ □ Patient information
   │   ├─ □ Clinical observations
   │   └─ □ Medications
   ├─ [Allow] or [Deny]
   └─ User clicks [Allow]

6. Redirected back to Context Vault
   ├─ Loading screen: "Connecting to Epic..."
   └─ Success screen: "✓ Connected!"

7. Background sync starts
   ├─ Progress indicator in dashboard
   ├─ "Syncing Epic records... 12 of 45"
   └─ Takes 10-60 seconds

8. Sync complete
   ├─ Toast: "✓ Synced 45 records from Epic MyChart"
   ├─ Medical records appear in vault
   │   ├─ Tagged automatically: "medical", "epic"
   │   └─ Source indicator: Epic logo
   └─ Settings shows: Epic ✓ Connected
```

### Chat with AI

```
1. User navigates to Chat page
   ├─ ChatGPT-style interface
   ├─ Sidebar: Recent conversations
   └─ Main: Chat input

2. User types message:
   "What were my blood pressure readings last month?"

3. Backend searches vault
   ├─ Query: tags=["medical"], search="blood pressure", date_range=last_month
   ├─ Finds 3 relevant vault items
   └─ Builds prompt with context

4. Ephemeral container spins up
   ├─ Loading indicator: "Thinking..."
   ├─ Takes 1-3 seconds (first request)
   └─ Subsequent requests faster (<1s)

5. AI responds (streaming)
   ├─ Text appears word-by-word
   ├─ "Based on your medical records from Epic, you had 3 blood pressure readings last month:"
   ├─ "• Jan 5: 120/80 mmHg"
   ├─ "• Jan 12: 118/78 mmHg"
   └─ "• Jan 20: 122/82 mmHg"

6. Context indicator shown
   ├─ "📎 Used 3 vault items"
   ├─ Click to expand: shows which items referenced
   │   ├─ Blood Pressure Reading - Jan 5 (Epic)
   │   ├─ Blood Pressure Reading - Jan 12 (Epic)
   │   └─ Blood Pressure Reading - Jan 20 (Epic)
   └─ User can click items to view full content

7. User continues conversation
   ├─ Follow-up: "Is that normal?"
   ├─ AI responds with context maintained
   └─ Container recycled after N requests
```

### Organize with Tags

```
1. User views vault item

2. User clicks "Add tag" or tag icon
   ├─ Dropdown appears with autocomplete
   ├─ Shows existing tags:
   │   ├─ medical (23 items)
   │   ├─ personal (12 items)
   │   └─ important (8 items)
   ├─ User types: "blood-pressure"
   └─ Creates new tag if doesn't exist

3. Tag added to item
   ├─ Badge appears on item card
   └─ Toast: "✓ Tag added"

4. User clicks tag anywhere
   ├─ Filters vault to show all items with that tag
   └─ URL updates: /vault?tags=blood-pressure

5. User can manage tags in Settings
   ├─ View all tags
   ├─ Rename tags (updates all items)
   ├─ Delete tags (removes from all items)
   └─ Change tag colors
```

---

## Setup Wizard Details

### Screen 1: Welcome

```
┌─────────────────────────────────────────────┐
│  Welcome to Context Vault! 🔒              │
│                                             │
│  Your private AI assistant with access to  │
│  your personal data — all encrypted and    │
│  stored locally.                           │
│                                             │
│  ✓ Chat with AI about your vault           │
│  ✓ Sync medical records from Epic          │
│  ✓ Everything stays on your device         │
│                                             │
│                      [Next →]               │
└─────────────────────────────────────────────┘
```

### Screen 2: Privacy Choice

```
┌─────────────────────────────────────────────┐
│  Choose Your Privacy Level                  │
│                                             │
│  ○ Maximum Privacy (Recommended)            │
│    Run AI locally on your computer          │
│    • Requires Docker + Ollama               │
│    • Model download: ~5GB                   │
│    • Everything 100% private                │
│                                             │
│  ○ Quick Start                              │
│    Use hosted AI temporarily                │
│    • No setup required                      │
│    • Switch to local later in Settings      │
│    • Data encrypted, but AI is hosted       │
│                                             │
│              [← Back]    [Next →]           │
└─────────────────────────────────────────────┘
```

### Screen 3: AI Setup (Maximum Privacy)

```
┌─────────────────────────────────────────────┐
│  Setting Up Local AI                        │
│                                             │
│  Checking requirements...                   │
│  ✓ Docker installed                         │
│  ✗ Ollama not found                         │
│                                             │
│  [Install Ollama]                           │
│  Opens ollama.com with instructions         │
│                                             │
│  Once installed, we'll download the AI      │
│  model (~5GB, takes 5-10 minutes)           │
│                                             │
│              [← Back]    [Skip]             │
└─────────────────────────────────────────────┘

(After Ollama installed)

┌─────────────────────────────────────────────┐
│  Downloading AI Model                       │
│                                             │
│  llama3.1:8b (4.9 GB)                       │
│  ████████████░░░░░░░░░░░░ 2.3 GB / 4.9 GB   │
│  ~5 minutes remaining                       │
│                                             │
│  Why this model?                            │
│  • Best balance of speed and quality        │
│  • Fits on most computers (8GB+ RAM)        │
│  • Can change model later in Settings       │
│                                             │
│                      [Cancel]               │
└─────────────────────────────────────────────┘
```

### Screen 4: Test Chat

```
┌─────────────────────────────────────────────┐
│  Test Your AI                               │
│                                             │
│  ┌────────────────────────────────────────┐ │
│  │ You: Hello, introduce yourself          │ │
│  │                                         │ │
│  │ AI: I'm your private AI assistant,     │ │
│  │ designed to help you interact with     │ │
│  │ your personal data vault. Everything   │ │
│  │ we discuss stays on your device and    │ │
│  │ is never shared with anyone else.      │ │
│  └────────────────────────────────────────┘ │
│                                             │
│  ✓ AI is working!                           │
│                                             │
│              [Start Using Context Vault]    │
└─────────────────────────────────────────────┘
```

---

## Empty States

### Vault Dashboard (No Items Yet)

```
┌─────────────────────────────────────────────┐
│  Your vault is empty                        │
│                                             │
│  🗂️  Start building your personal vault      │
│                                             │
│  [📤 Upload a file]                         │
│  PDF, images, documents                     │
│                                             │
│  [📝 Create a note]                         │
│  Store ideas, preferences, context          │
│                                             │
│  [🏥 Connect Epic MyChart]                  │
│  Sync your medical records                  │
└─────────────────────────────────────────────┘
```

### Chat (No Vault Data)

```
┌─────────────────────────────────────────────┐
│  No vault data yet                          │
│                                             │
│  💬 You can chat with the AI, but it won't  │
│     have any context about your personal    │
│     data until you add items to your vault. │
│                                             │
│  [Go to Vault] to add your first item       │
└─────────────────────────────────────────────┘
```

### Integrations (None Connected)

```
┌─────────────────────────────────────────────┐
│  Available Integrations                     │
│                                             │
│  Epic MyChart          [Connect]            │
│  Access medical records                     │
│                                             │
│  Fitbit                [Connect]            │
│  Sync activity and health data              │
│                                             │
│  Apple Health          [Upload Export]      │
│  Import health data from iOS                │
└─────────────────────────────────────────────┘
```

---

## Tutorial Tooltips

Shown on first visit to each page, dismissible:

**Dashboard:**

- "Click here to upload files like PDFs, medical reports, or images"
- "Create notes to store preferences, context, or ideas"
- "Use tags to organize your vault items"

**Chat:**

- "Ask questions about your vault data"
- "The AI only uses your private data, never shared"
- "Click the 📎 icon to see which vault items were used"

**Settings:**

- "Connect integrations to automatically sync data"
- "Change your AI model here if you want a faster or more powerful option"

---

## Error States & Recovery

### Ollama Not Running

```
┌─────────────────────────────────────────────┐
│  ⚠️  Ollama Not Running                     │
│                                             │
│  The local AI service isn't available.      │
│                                             │
│  Please start Ollama:                       │
│  $ ollama serve                             │
│                                             │
│  [Retry]    [Use Hosted AI Instead]         │
└─────────────────────────────────────────────┘
```

### Epic Sync Failed

```
┌─────────────────────────────────────────────┐
│  ⚠️  Epic Sync Failed                       │
│                                             │
│  We couldn't sync your medical records.     │
│                                             │
│  Possible reasons:                          │
│  • Epic connection expired                  │
│  • Network issue                            │
│  • Epic server error                        │
│                                             │
│  [Try Again]    [Reconnect Epic]            │
└─────────────────────────────────────────────┘
```

### File Upload Failed

```
┌─────────────────────────────────────────────┐
│  ⚠️  Upload Failed                          │
│                                             │
│  report.pdf (12 MB) - File too large        │
│  Maximum file size: 10 MB                   │
│                                             │
│  [Try Another File]                         │
└─────────────────────────────────────────────┘
```

---

## Mobile Experience Considerations

### PWA Install Prompt

```
┌─────────────────────────────────────────────┐
│  Install Context Vault                      │
│                                             │
│  📱 Add to your home screen for quick       │
│     access and offline vault viewing        │
│                                             │
│  [Add to Home Screen]    [Not Now]          │
└─────────────────────────────────────────────┘
```

### Mobile Navigation

- Bottom navigation bar (Chat, Vault, Settings)
- Hamburger menu for secondary actions
- Swipe gestures (swipe left on item to delete)
- Touch-optimized buttons (min 44x44 px)

### Mobile-Specific Features

- Camera upload (take photo → upload to vault)
- Offline vault viewing (cached in IndexedDB)
- Push notifications for sync completion
- Biometric auth (Face ID, Touch ID) for unlock

---

## Accessibility Considerations

- Keyboard navigation (Tab, Enter, Escape)
- Screen reader support (ARIA labels)
- High contrast mode support
- Reduced motion option (disable animations)
- Font size adjustable
- All interactive elements have visible focus states

---

## User Preferences (Settings)

```
Settings
├── Account
│   ├── Email: user@example.com
│   ├── Name: John Doe
│   └── [Sign Out]
├── Privacy
│   ├── AI Mode: ○ Local  ○ Hosted
│   ├── Chat History: □ Enable (off by default)
│   └── Analytics: □ Anonymous usage stats
├── AI Model
│   ├── Current: llama3.1:8b
│   ├── Available models: [list]
│   └── [Download New Model]
├── Integrations
│   ├── Epic MyChart: ✓ Connected
│   ├── Fitbit: Disconnected
│   └── Apple Health: [Upload Export]
├── Data
│   ├── [Export All Data] (GDPR)
│   ├── [Delete All Data]
│   └── Storage used: 1.2 GB / 5 GB
└── About
    ├── Version: 1.0.0
    ├── [Documentation]
    ├── [Privacy Policy]
    └── [Terms of Service]
```

---

**Next Steps:**

1. Design UI mockups for each screen
2. Implement onboarding wizard (Next.js client components)
3. Add empty states to all pages
4. Create tutorial tooltip system
5. Test user flow end-to-end
