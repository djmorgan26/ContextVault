# Context Vault 🔒

> Your private AI assistant with access to your personal data — all encrypted and stored locally.

**Privacy-first personal intelligence system** that combines secure local data storage with AI capabilities. Chat with an AI that understands your medical records, notes, and personal preferences — without ever sharing your data with third parties.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)

## ✨ Features

- 🔐 **End-to-End Encryption** - Your data encrypted with your own keys
- 🤖 **Local AI** - Ollama runs on your device, no cloud AI providers
- 🏥 **Epic MyChart Integration** - Automatically sync medical records
- 📝 **Personal Vault** - Store notes, files, preferences securely
- 💬 **Privacy-First Chat** - AI that references your data without storing it
- 🚀 **Web + Mobile** - Responsive PWA works everywhere

## 🏗️ Architecture

```
React Frontend (Vercel)  ←→  FastAPI Backend (Render)  ←→  PostgreSQL (Railway)
                                      ↓
                            Ephemeral Ollama Containers
                            (Destroyed after each use)
```

**Privacy Model:** Vault data never enters persistent storage in LLM containers. Ephemeral containers process requests in RAM only, then are immediately destroyed.

## 🚀 Quick Start

### Prerequisites

- **Docker** (for containerized setup)
- **Python 3.11+** and **Node.js 18+** (for local development)
- **Ollama** (for local AI) - [Install from ollama.com](https://ollama.com)
- **Google OAuth credentials** ✅ (already configured)
- **Railway Postgres database** ✅ (already set up)

### 1. Clone Repository

```bash
git clone https://github.com/djmorgan26/ContextVault.git
cd ContextVault
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# (Google OAuth and database credentials already provided)
nano .env

# Generate secret keys
openssl rand -base64 32  # Use for APP_SECRET_KEY
openssl rand -base64 32  # Use for JWT_SECRET_KEY
```

### 3. Start Ollama

```bash
# Start Ollama server
ollama serve

# Download model (in another terminal)
ollama pull llama3.1:8b
```

### 4. Run with Docker Compose (Recommended)

```bash
# Start all services
docker-compose up

# Or in background
docker-compose up -d
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 5. OR Run Locally (Without Docker)

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## 📚 Documentation

Comprehensive documentation available in `docs/`:

- **[Architecture Overview](docs/architecture.md)** - System design and components
- **[Database Schema](docs/database_schema.md)** - Complete ERD and table definitions
- **[API Endpoints](docs/api_endpoints.md)** - Full REST API documentation
- **[Security Architecture](docs/security_architecture.md)** - Encryption and privacy details
- **[User Onboarding](docs/user_onboarding.md)** - User flows and UX specs
- **[Testing Strategy](docs/testing_strategy.md)** - Unit, integration, and E2E tests
- **[Deployment Guide](docs/deployment.md)** - Production deployment to Vercel + Render

## 🔧 Development

### Project Structure

```
ContextVault/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config, security, database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── services/    # Business logic
│   │   └── schemas/     # Pydantic models
│   ├── migrations/      # Alembic migrations
│   ├── tests/           # Pytest tests
│   └── requirements.txt
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom hooks
│   │   ├── lib/         # Utilities
│   │   └── App.tsx
│   ├── tests/           # Vitest tests
│   └── package.json
├── docs/                # Documentation
├── .env.example         # Environment variables template
├── docker-compose.yml   # Docker services
└── README.md           # This file
```

### Run Tests

**Backend:**
```bash
cd backend
pytest tests/ --cov=app
```

**Frontend:**
```bash
cd frontend
npm run test
```

**E2E:**
```bash
npx playwright test
```

### Code Style

**Python:**
```bash
# Format
ruff format app/

# Lint
ruff check app/
```

**TypeScript:**
```bash
# Format
npm run format

# Lint
npm run lint
```

## 🚢 Deployment

### Production Setup

1. **Backend (Render)**
   - Auto-deploys from `main` branch
   - URL: https://contextvault-api.onrender.com

2. **Frontend (Vercel)**
   - Auto-deploys from `main` branch
   - URL: https://contextvault.vercel.app

3. **Database (Railway)**
   - PostgreSQL hosted on Railway
   - Automated daily backups

See [Deployment Guide](docs/deployment.md) for detailed instructions.

### Environment Variables

**Backend (Render):**
- `DATABASE_URL` - Railway Postgres connection string
- `APP_SECRET_KEY` - Encryption key derivation
- `JWT_SECRET_KEY` - JWT signing key
- `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` - Google OAuth
- `EPIC_CLIENT_ID` - Epic FHIR credentials

**Frontend (Vercel):**
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_GOOGLE_OAUTH_CLIENT_ID` - Google OAuth client ID

## 🔐 Security

### Key Security Features

- **AES-256-GCM Encryption** - All vault data encrypted at rest
- **PBKDF2 Key Derivation** - User-specific encryption keys (100k iterations)
- **Ephemeral LLM Containers** - No persistent data in AI processing
- **OAuth 2.0 Authentication** - Secure Google login
- **JWT Access Tokens** - Short-lived (30 min) with refresh rotation
- **HTTPS Everywhere** - TLS 1.3 for all communication

### Threat Model

**Protected Against:**
- Database breaches (data encrypted)
- Compromised backend (keys never stored)
- Container escape (no persistent data)
- Network sniffing (HTTPS)
- Token theft (short expiry + rotation)

See [Security Architecture](docs/security_architecture.md) for full details.

## 🏥 Epic Integration

### Connect Epic MyChart

1. Navigate to Settings → Integrations
2. Click "Connect Epic MyChart"
3. Log in to your Epic MyChart account
4. Authorize access to medical records
5. Records automatically sync to your vault

**Supported Epic Data:**
- Patient information
- Clinical observations (vitals, lab results)
- Medications (future)
- Immunizations (future)

### Epic Sandbox Testing

The app is configured with Epic's sandbox environment for testing. Use test patients from [open.epic.com](https://open.epic.com/).

**Production:** Submit to [Epic App Orchard](https://apporchard.epic.com/) for production access.

## 🧪 Testing Epic Integration

**Epic Sandbox Credentials:** Already configured in `.env.example`

**Test Flow:**
1. Start app locally
2. Go to Settings → Connect Epic
3. Use Epic sandbox test patient
4. Verify records sync to vault
5. Chat with AI about medical data

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Review Checklist

- [ ] Tests pass (`pytest` and `npm test`)
- [ ] Code formatted (`ruff format`, `npm run format`)
- [ ] No new security vulnerabilities (`safety check`, `npm audit`)
- [ ] Documentation updated if needed
- [ ] Environment variables added to `.env.example`

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Epic Systems** - SMART on FHIR standard and sandbox access
- **Ollama** - Local LLM infrastructure
- **shadcn/ui** - Beautiful, accessible component library
- **FastAPI** - Modern Python web framework
- **React** - UI library

## 📞 Support

- **Documentation:** See `docs/` folder
- **Issues:** [GitHub Issues](https://github.com/djmorgan26/ContextVault/issues)
- **Discussions:** [GitHub Discussions](https://github.com/djmorgan26/ContextVault/discussions)

## 🗺️ Roadmap

### MVP (Current)
- [x] Google OAuth authentication
- [x] Encrypted vault storage
- [x] Epic MyChart integration
- [ ] Local Ollama chat
- [ ] File upload (PDF, images)
- [ ] Tag-based organization

### Phase 2
- [ ] Vector embeddings for better context retrieval
- [ ] Fitbit integration
- [ ] Apple Health import
- [ ] Chat history (optional, encrypted)
- [ ] Multi-model support

### Phase 3
- [ ] Mobile apps (React Native)
- [ ] On-device LLM for mobile (MLX/llama.cpp)
- [ ] End-to-end encryption (zero-knowledge)
- [ ] P2P sync across devices
- [ ] SOC 2 compliance

---

**Built with privacy in mind. Your data, your control.** 🔒
