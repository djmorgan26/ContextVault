# /deploy-check - Pre-Deployment Checklist

Run pre-deployment checks for ContextVault before pushing to production.

## Steps

1. **Security Audit**:
   - Check for exposed secrets in code
   - Verify `.env` is in `.gitignore`
   - Confirm encryption keys are properly derived
   - Check JWT token expiry settings

2. **Environment Variables**:
   - Compare `.env.example` with actual `.env`
   - Ensure all required vars documented
   - Verify production credentials ready (Render/Vercel)

3. **Code Quality**:
   - Run Python linting: `ruff check fastapi_epic_smart.py`
   - Check for TODO/FIXME comments
   - Review error handling patterns

4. **Documentation**:
   - Verify README.md is current
   - Check API docs match implementation
   - Update deployment guide if needed

5. **Database**:
   - Check Railway Postgres connection
   - Verify migration status (if using Alembic)
   - Confirm backup strategy

6. **Report**:
   - List any blockers
   - Security concerns
   - Missing documentation
   - Ready to deploy: Yes/No
