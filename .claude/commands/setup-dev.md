# /setup-dev - Development Environment Setup

Set up local development environment for ContextVault.

## Steps

1. **Prerequisites Check**:
   - Python 3.11+ installed?
   - Docker installed (optional)?
   - Ollama installed?

2. **Environment Configuration**:
   - Copy `.env.example` to `.env`
   - Generate secret keys:
     ```bash
     openssl rand -base64 32  # APP_SECRET_KEY
     openssl rand -base64 32  # JWT_SECRET_KEY
     ```
   - Verify Epic sandbox credentials in `.env`

3. **Python Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. **Ollama Setup**:
   ```bash
   # Start Ollama
   ollama serve

   # Pull model (in another terminal)
   ollama pull llama3.1:8b
   ```

5. **Database Setup**:
   - Verify Railway Postgres connection string in `.env`
   - Run migrations (if using Alembic)

6. **Verification**:
   - Start FastAPI: `python fastapi_epic_smart.py`
   - Check http://localhost:8000/docs
   - Confirm Ollama accessible

7. **Report Setup Status**:
   - List any failures or missing steps
   - Provide next steps for user
