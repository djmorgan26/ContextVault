# Vercel Deployment Guide for Context Vault

## Current Status
✅ `vercel.json` created with correct configuration
✅ Environment variables use `NEXT_PUBLIC_*` prefix (correct for Next.js)
✅ Next.js build configuration verified

## Next Steps to Fix Vercel Deployment

### 1. Update Vercel Project Settings

Go to your Vercel dashboard: https://vercel.com/dashboard

1. **Select your project** (or create new one if needed)
2. Go to **Settings** → **General**
3. Under **Root Directory**, set it to: `frontend`
4. **Framework Preset** should auto-detect as "Next.js" (if not, select it manually)
5. **Build Command**: Leave as default (Vercel will auto-detect `npm run build`)
6. **Output Directory**: Leave as default (`.next` for Next.js)
7. **Install Command**: Leave as default (`npm install`)

### 2. Set Environment Variables

Go to **Settings** → **Environment Variables** and add:

```bash
NEXT_PUBLIC_API_URL=https://contextvault-api.onrender.com
```

**Important Notes:**
- Use `NEXT_PUBLIC_*` prefix (not `VITE_*`) - this is required for Next.js
- Replace the API URL with your actual backend URL if different
- If you have Google OAuth, you may also need:
  ```
  NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
  ```

### 3. Verify Build Settings

In **Settings** → **General**, verify:
- **Node.js Version**: Should be 18.x or higher (Next.js 16 requires Node 18+)
- **Build Command**: `npm run build` (runs from `frontend/` directory)
- **Output Directory**: `.next` (auto-detected for Next.js)

### 4. Redeploy

After updating settings:
1. Go to **Deployments** tab
2. Click the **"..."** menu on the latest deployment
3. Select **"Redeploy"**
4. Or simply push a new commit to trigger a new deployment

### 5. Check Deployment Logs

If deployment still fails:
1. Click on the failed deployment
2. Check the **Build Logs** tab
3. Look for errors like:
   - Missing dependencies
   - TypeScript errors (though these are ignored in config)
   - Environment variable issues
   - Build command failures

## Common Issues & Solutions

### Issue: "Cannot find module" errors
**Solution**: Make sure `rootDirectory` is set to `frontend` in Vercel settings

### Issue: Environment variables not working
**Solution**: 
- Ensure they use `NEXT_PUBLIC_*` prefix
- Redeploy after adding new variables
- Check that variables are set for the correct environment (Production/Preview/Development)

### Issue: Build fails with TypeScript errors
**Solution**: Your `next.config.mjs` already has `ignoreBuildErrors: true`, so this shouldn't be an issue. If it persists, check the actual error in logs.

### Issue: API calls failing
**Solution**: 
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings on your backend
- Ensure backend is deployed and accessible

## Testing the Deployment

After successful deployment:

1. **Check the live URL**: Visit your Vercel deployment URL
2. **Test API connection**: Open browser console and check for API errors
3. **Verify environment variables**: Check Network tab to see if API calls are going to the right URL

## File Structure Reference

```
ContextVault/
├── vercel.json          ← Tells Vercel to use frontend/ directory
├── frontend/
│   ├── package.json     ← Next.js dependencies
│   ├── next.config.mjs  ← Next.js configuration
│   ├── app/             ← Next.js App Router
│   └── ...
```

## Quick Checklist

- [ ] Root Directory set to `frontend` in Vercel dashboard
- [ ] Framework preset is "Next.js"
- [ ] Environment variable `NEXT_PUBLIC_API_URL` is set
- [ ] Node.js version is 18+ (check in Vercel settings)
- [ ] Latest commit pushed to GitHub
- [ ] Deployment triggered and building
- [ ] Build logs show no errors
- [ ] Live site is accessible

## Need Help?

If deployments are still failing:
1. Check the exact error in Vercel build logs
2. Verify all environment variables are set
3. Ensure `vercel.json` is committed to your repository
4. Try redeploying from the Vercel dashboard

