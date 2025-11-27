# Vercel Deployment Setup - Fresh Start

## Step 1: Delete Existing Vercel Project

1. Go to https://vercel.com/dashboard
2. Find your `context-vault` project
3. Click on the project
4. Go to Settings (gear icon)
5. Scroll to bottom → "Delete Project"
6. Confirm deletion

## Step 2: Create New Vercel Project

1. Go to https://vercel.com/new
2. Import your GitHub repository: `djmorgan26/ContextVault`
3. **CRITICAL: Configure these settings:**

### Project Settings:
- **Framework Preset:** Next.js
- **Root Directory:** `frontend` ← CLICK "EDIT" and select `frontend/`
- **Build Command:** Leave as default (`npm run build`)
- **Output Directory:** Leave as default (`.next`)
- **Install Command:** Leave as default (`npm install`)

### Environment Variables (if needed):
- Add any `.env` variables your frontend needs here
- For now, can skip this step

## Step 3: Deploy

Click "Deploy" and watch the build logs.

## Expected Result

Build should succeed because:
- Root directory is `frontend/`, so Vercel runs commands inside that folder
- Path aliases `@/*` in `tsconfig.json` resolve to `./` (relative to frontend/)
- All imports like `@/lib/utils` will correctly find `frontend/lib/utils.ts`

## Troubleshooting

If build still fails with "Module not found" errors:

1. Check the build logs for the exact error
2. Verify "Root Directory" in Vercel project settings shows `frontend`
3. Check that `tsconfig.json` has `"baseUrl": "."` (already added)
4. Try redeploying (sometimes cache issues)

## Vercel Project Settings Location

After creating project:
- Dashboard → Your Project → Settings → General
- Look for "Root Directory" setting
- Should show `frontend/`
