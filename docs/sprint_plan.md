# ContextVault - Sprint Plan

> Organized implementation roadmap: Epic → Feature → User Story → Sprint
> Based on: docs/epics_features_stories.md
> Updated: 2025-01-26

---

## Overview

**Total Duration:** 9 sprints (18 weeks)
**Sprint Length:** 2 weeks each
**Team Size:** 1-2 developers (assumed)

### Sprint Organization Philosophy
- **Sprints 1-3:** Foundation (backend infrastructure, security, database)
- **Sprints 4-5:** Core Features (auth, vault CRUD)
- **Sprint 6:** Epic Integration (medical records)
- **Sprint 7:** AI Integration (client-side + containers)
- **Sprint 8:** Testing & Quality
- **Sprint 9:** Production Readiness & Frontend Polish

---

## Sprint 1: Foundation & Security Core (Week 1-2)

**Goal:** Establish production-ready backend foundation with bulletproof encryption

**Epic 1: Foundation & Infrastructure [P0]**
**Epic 2: Security & Encryption [P0]**

### Stories (Priority Order)

#### Feature 1.1: Project Structure & Tooling
- [ ] **1.1.1** Backend directory structure (2h)
- [ ] **1.1.4** Install dependencies (30min)
- [ ] **1.1.2** Code formatting/linting (1h)
- [ ] **1.1.3** Makefile commands (1h)

#### Feature 1.2: Configuration Management
- [ ] **1.2.1** Centralized config with Pydantic Settings (2h)

#### Feature 2.1: Encryption Service (CRITICAL PATH)
- [ ] **2.1.1** Master key derivation (4h)
- [ ] **2.1.2** AES-256-GCM encryption (3h)
- [ ] **2.1.3** Tamper detection (2h)
- [ ] **2.1.4** 100% encryption tests (4h)

#### Feature 2.2: JWT Authentication
- [ ] **2.2.1** Access token creation (2h)
- [ ] **2.2.2** Token validation dependency (2h)
- [ ] **2.2.3** Refresh token hashing (1h)

**Sprint Deliverable:**
- Backend structure with working encryption
- JWT token system
- All encryption tests passing (100% coverage)

**Total Estimate:** 24.5 hours

---

## Sprint 2: Database Schema & Setup (Week 3-4)

**Goal:** Create complete database schema with migrations

**Epic 1: Foundation & Infrastructure [P0]** (continued)
**Epic 3: Database Schema [P0]**

### Stories

#### Feature 1.3: Database Setup
- [ ] **1.3.1** Async database connection pooling (2h)
- [ ] **1.3.2** Alembic migration management (1h)

#### Feature 3.1: Database Models
- [ ] **3.1.1** All SQLAlchemy models (6h)
  - User, VaultItem, Tag, Integration, IntegrationToken, Session
- [ ] **3.1.2** Pydantic schemas for API validation (4h)

#### Feature 3.2: Initial Migration
- [ ] **3.2.1** Initial schema migration (4h)
  - All 7 tables, 5 enums, indexes, foreign keys

**Sprint Deliverable:**
- Database models and schemas
- Initial migration runs successfully on Railway Postgres
- Can create/query all tables

**Total Estimate:** 17 hours

---

## Sprint 3: Authentication System (Week 5-6)

**Goal:** Implement Google OAuth login and session management

**Epic 4: Authentication System [P0]**

### Stories

#### Feature 4.1: Google OAuth Flow
- [ ] **4.1.1** Google OAuth login endpoint (3h)
- [ ] **4.1.2** Google OAuth callback handler (6h)
  - User creation, session management, JWT issuance
- [ ] **4.1.3** Refresh token endpoint (3h)
- [ ] **4.1.4** Logout endpoint (1h)
- [ ] **4.1.5** Profile endpoint (1h)

#### Feature 4.2: Authentication Service Layer
- [ ] **4.2.1** AuthService class (4h)
  - Separate business logic from routes

**Sprint Deliverable:**
- Full Google OAuth login flow
- Session management with refresh tokens
- Protected routes using `Depends(get_current_user)`

**Total Estimate:** 18 hours

**Note:** Epic SMART OAuth (6.1.1) already complete in `fastapi_epic_smart.py`

---

## Sprint 4: Vault Management Core (Week 7-8)

**Goal:** Core vault CRUD operations with encryption

**Epic 5: Vault Management [P0]**

### Stories

#### Feature 5.1: Vault Item CRUD
- [ ] **5.1.1** Create vault item (4h)
- [ ] **5.1.2** View specific vault item (2h)
- [ ] **5.1.3** List vault items (4h)
  - Pagination, filters, search
- [ ] **5.1.4** Update vault item (3h)
- [ ] **5.1.5** Delete vault item (soft delete) (2h)

#### Feature 5.2: Vault Service Layer
- [ ] **5.2.1** VaultService class (6h)
  - Encryption/decryption transparency

**Sprint Deliverable:**
- Full vault CRUD API
- All content encrypted at rest
- Pagination and filtering working

**Total Estimate:** 21 hours

---

## Sprint 5: Vault Features & Tags (Week 9-10)

**Goal:** Complete vault feature set with organization

**Epic 5: Vault Management [P0]** (continued)

### Stories

#### Feature 5.3: Tag Management
- [ ] **5.3.1** Create tags (2h)
- [ ] **5.3.2** List tags (2h)
- [ ] **5.3.3** Rename/delete tags (3h)
- [ ] **5.3.4** Filter vault items by tags (2h)

#### Feature 5.4: File Upload
- [ ] **5.4.1** PDF upload and encryption (6h)
  - Extract text, encrypt file content

**Sprint Deliverable:**
- Tag-based organization
- PDF upload and storage
- Full vault feature set complete

**Total Estimate:** 15 hours

---

## Sprint 6: Epic MyChart Integration (Week 11-12)

**Goal:** Sync medical records from Epic MyChart

**Epic 6: Epic MyChart Integration [P0]**

### Stories

#### Feature 6.1: Epic OAuth Connection
- [ ] **6.1.1** Epic OAuth connect endpoint (4h) - **COMPLETE** ✓
- [ ] **6.1.2** Epic OAuth callback (6h) - **IN PROGRESS**
  - Token storage, validation, encryption
- [ ] **6.1.3** Disconnect Epic (1h)

#### Feature 6.2: FHIR Data Sync
- [ ] **6.2.1** Auto-sync medical records (8h)
  - Fetch Patient, Observations, transform to vault items
- [ ] **6.2.2** Manual sync trigger (2h)
- [ ] **6.2.3** Sync status endpoint (3h)

#### Feature 6.3: FHIR Transformations
- [ ] **6.3.1** Observation transformations (6h)
  - Blood pressure, labs, vitals → readable vault items
- [ ] **6.3.2** Patient demographics (2h)

#### Feature 6.4: Token Refresh
- [ ] **6.4.1** Auto-refresh Epic tokens (4h)

#### Feature 6.5: Epic Service Layer
- [ ] **6.5.1** EpicService class (8h)
  - FHIR transformations, token management

**Sprint Deliverable:**
- Full Epic integration
- Medical records synced to vault
- Background sync jobs working

**Total Estimate:** 44 hours (adjust timeline if needed)

---

## Sprint 7: AI Chat Integration (Week 13-14)

**Goal:** Safe local AI with client-side primary, ephemeral containers fallback

**Epic 7: AI Chat Integration [P0]**
**Epic 7.4: Container Security [P0]** (NEW)
**Epic 7.5: Context Safety [P0]** (NEW)
**Epic 7.7: Client-Side AI [P0]** (NEW)

### Stories (REVISED ORDER based on plan)

#### Week 1: Client-Side AI (Primary Path)
- [ ] **7.5.1** Filter sensitive metadata (2h) - **CRITICAL FIRST**
  - Prevent PHI leakage
- [ ] **7.7.1** WebLLM integration (8h) - **PRIMARY PATH**
  - Browser-based LLM, WebGPU detection
- [ ] **11.3.1** Chat UI with streaming (6h)
  - Mode selector (Vault vs Cloud-Assisted)

#### Week 2: Ephemeral Containers (Fallback Path)
- [ ] **7.4.2** Container security hardening (3h)
  - tmpfs, no capabilities, network=none
- [ ] **7.4.1** Container lifecycle (4h)
  - Create, stream, destroy in finally
- [ ] **7.1.1** Chat API endpoint (6h)
  - SSE streaming, context retrieval
- [ ] **7.1.2** Context retrieval (4h)
  - Keyword matching, 5 item limit

#### Support Features
- [ ] **7.2.1** Ollama service client (4h)
- [ ] **7.3.1** Context service (3h)
- [ ] **7.5.2** Audit trail (3h) - **HIPAA REQUIRED**
- [ ] **7.4.4** Orphaned container cleanup (2h)

**Sprint Deliverable:**
- Client-side AI working (Vault Mode)
- Ephemeral container fallback (Cloud-Assisted)
- Full audit trail
- Context retrieval with metadata filtering

**Total Estimate:** 45 hours

---

## Sprint 8: Testing & Quality Assurance (Week 15-16)

**Goal:** Comprehensive test coverage and CI/CD pipeline

**Epic 8: Testing & Quality Assurance [P0]**
**Epic 8.2.3: AI Security Tests [P0]** (NEW)

### Stories

#### Feature 8.1: Unit Tests
- [ ] **8.1.1** Encryption tests - 100% coverage (4h)
- [ ] **8.1.2** JWT authentication tests (3h)

#### Feature 8.2: Integration Tests
- [ ] **8.2.1** Vault API tests (6h)
  - CRUD, encryption, ownership checks
- [ ] **8.2.2** Epic API tests (6h)
  - OAuth, sync, token encryption

#### Feature 8.2.3: AI Security Tests (NEW)
- [ ] Test metadata exclusion (2h)
- [ ] Test cross-user container isolation (2h)
- [ ] Test container cleanup (1h)

#### Feature 8.3: Test Infrastructure
- [ ] **8.3.1** Test fixtures and utilities (4h)
- [ ] **8.3.2** Pytest configuration (1h)

#### Feature 8.4: CI/CD Pipeline
- [ ] **8.4.1** Automated linting (2h)
- [ ] **8.4.2** Automated tests with coverage (3h)
- [ ] **8.4.3** Security scanning (2h)

**Sprint Deliverable:**
- 75%+ code coverage
- CI/CD pipeline running on all PRs
- All security tests passing

**Total Estimate:** 36 hours

---

## Sprint 9: Production Readiness & Frontend (Week 17-18)

**Goal:** Deploy-ready backend + React frontend foundation

**Epic 10: Production Readiness [P1]**
**Epic 11: Frontend Integration [P0]**

### Week 1: Production Hardening

#### Feature 10.1: Error Handling
- [ ] **10.1.1** Error messages (4h)
- [ ] **10.1.2** Structured logging (3h)
- [ ] **10.1.3** Audit logging (3h)

#### Feature 10.2: Security Hardening
- [ ] **10.2.1** CORS and security headers (2h)
- [ ] **10.2.2** Rate limiting (3h)

#### Feature 10.3: Performance
- [ ] **10.3.1** Connection pooling, pagination, indexes (3h)

#### Feature 10.4: Health Checks
- [ ] **10.4.1** Health check endpoints (1h)

#### Feature 10.5: Environment Management
- [ ] **10.5.1** Dev/prod environment separation (2h)

#### Feature 10.6: Deployment
- [ ] **10.6.1** Production Dockerfile and migrations (4h)

#### Feature 10.7: Backup & Recovery
- [ ] **10.7.1** Encrypted backups (4h)

### Week 2: Frontend Foundation

#### Feature 11.1: Authentication UI
- [ ] **11.1.1** Google OAuth login button (4h)
- [ ] **11.1.2** Auto token refresh (3h)
- [ ] **11.1.3** Logout (1h)

#### Feature 11.2: Vault UI
- [ ] **11.2.1** Vault CRUD UI (8h)
- [ ] **11.2.2** Vault editor (6h)
- [ ] **11.2.3** Tag filtering (4h)

#### Feature 11.3: Chat UI
- [ ] **11.3.2** Chat context filtering (2h)

#### Feature 11.4: Frontend Infrastructure
- [ ] **11.4.1** React + Vite + TypeScript setup (3h)
- [ ] **11.4.2** Auth state management (4h)

**Sprint Deliverable:**
- Production-ready backend deployed
- React frontend with auth, vault, and chat
- HIPAA compliance ready

**Total Estimate:** 59 hours

---

## Post-MVP Sprints (Optional)

### Sprint 10: Developer Experience (Week 19-20)

**Epic 9: Developer Experience Enhancements [P2]**

- [ ] **9.1.1** Docker development (4h)
- [ ] **9.2.1** API documentation (2h)
- [ ] **9.3.1** Database seeding scripts (3h)

### Sprint 11: AI Polish & Advanced Features (Week 21-22)

**Epic 7.6: AI-Specific Threats [P1]** (NEW)
**Epic 7.7: Client-Side AI** (continued)

- [ ] **7.6.1** Prompt injection protection (2h)
- [ ] **7.6.2** AI rate limiting (2h)
- [ ] **7.6.3** Hallucination disclaimer (1h)
- [ ] **7.7.2** Model selection UI (3h)
- [ ] **7.2.2** AI privacy settings (2h)
- [ ] **7.5.3** Context size limits (1h)

---

## Sprint Dependencies & Critical Path

### Critical Path (Must complete in order)
```
Sprint 1 (Foundation + Encryption)
  ↓
Sprint 2 (Database)
  ↓
Sprint 3 (Authentication)
  ↓
Sprint 4 (Vault Core)
  ↓
Sprint 5 (Vault Features)
  ↓
Sprint 7 (AI - requires vault data)
  ↓
Sprint 8 (Testing - verifies all above)
  ↓
Sprint 9 (Production + Frontend)
```

### Parallel Work Opportunities
- **Sprint 6 (Epic Integration)** can run parallel to Sprint 5 if 2 developers
- **Sprint 9 Frontend** can start earlier if backend APIs stable

---

## Sprint Capacity Planning

### Assumptions
- 1 developer = 20 productive hours/week
- 2-week sprint = 40 hours capacity
- Buffer 20% for meetings, bugs, unknowns = 32 hours effective

### Sprint Hour Breakdown
| Sprint | Estimated Hours | At Capacity? | Notes |
|--------|----------------|--------------|-------|
| 1 | 24.5 | ✅ Under | Good starter sprint |
| 2 | 17 | ✅ Under | Light sprint, good for learning |
| 3 | 18 | ✅ Under | OAuth complexity may add time |
| 4 | 21 | ✅ Under | Core feature sprint |
| 5 | 15 | ✅ Under | Tag features straightforward |
| 6 | 44 | ⚠️ Over | **Split into 2 sprints if needed** |
| 7 | 45 | ⚠️ Over | **AI complexity - may need 2 sprints** |
| 8 | 36 | ⚠️ Tight | Testing sprint, manageable |
| 9 | 59 | ❌ Over | **Split: Production (Week 1) + Frontend (Week 2)** |

### Recommended Adjustments
- **Sprint 6:** Split into 6A (OAuth + sync) and 6B (transformations + service layer)
- **Sprint 7:** Already split into Week 1 (client-side) + Week 2 (containers)
- **Sprint 9:** Already split into Week 1 (production) + Week 2 (frontend)

**Adjusted Total:** 11 sprints (22 weeks) for full MVP

---

## Definition of Done (All Sprints)

### Code Quality
- [ ] Code passes `ruff check` with no errors
- [ ] Code formatted with `ruff format`
- [ ] All new code has docstrings
- [ ] No hardcoded secrets or sensitive data

### Testing
- [ ] Unit tests written for new functions
- [ ] Integration tests for new API endpoints
- [ ] All tests passing locally
- [ ] CI/CD pipeline passing

### Security
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Encryption used for sensitive data
- [ ] Authentication required for protected routes

### Documentation
- [ ] API endpoints documented in OpenAPI/Swagger
- [ ] README updated if user-facing changes
- [ ] Migration scripts tested

### Deployment
- [ ] Works in dev environment
- [ ] Environment variables documented
- [ ] Database migrations run successfully

---

## Sprint Retrospective Questions

After each sprint, answer:
1. What went well?
2. What could be improved?
3. What did we learn about ContextVault's architecture?
4. Any security concerns discovered?
5. Adjustments needed for next sprint?

---

## Risk Management by Sprint

### Sprint 1 Risks
- **Risk:** Encryption implementation bugs
- **Mitigation:** 100% test coverage requirement, external security review

### Sprint 3 Risks
- **Risk:** Google OAuth sandbox limitations
- **Mitigation:** Test with real Google account early

### Sprint 6 Risks
- **Risk:** Epic API rate limits or sandbox issues
- **Mitigation:** Mock Epic responses, test with Epic sandbox credentials

### Sprint 7 Risks
- **Risk:** WebGPU browser compatibility issues
- **Mitigation:** Feature detection, graceful fallback to containers
- **Risk:** Ollama container startup too slow (>5s)
- **Mitigation:** Accept trade-off, document in privacy policy

### Sprint 8 Risks
- **Risk:** Coverage goals not met (<75%)
- **Mitigation:** Add tests incrementally throughout earlier sprints

### Sprint 9 Risks
- **Risk:** Railway/Render deployment issues
- **Mitigation:** Deploy staging environment in Sprint 8

---

## Success Metrics

### Sprint 1-3 Success
- Backend server starts without errors
- User can log in with Google OAuth
- JWT tokens issued and validated

### Sprint 4-5 Success
- User can create encrypted vault items
- Vault items decrypt correctly for owner only
- Tags filter vault items

### Sprint 6 Success
- Epic OAuth flow completes
- Medical records synced to vault
- FHIR data readable in vault

### Sprint 7 Success
- AI chat responds with vault context
- Client-side AI works in Chrome/Edge
- Ephemeral containers destroy after request
- Audit log shows AI access

### Sprint 8 Success
- 75%+ code coverage
- CI/CD pipeline green
- No high-severity vulnerabilities

### Sprint 9 Success
- Backend deployed to Render
- Frontend deployed to Vercel
- End-to-end flow works in production

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Set up project board** (GitHub Projects, Jira, etc.)
3. **Create tickets** for all Sprint 1 stories
4. **Schedule Sprint 1 kickoff**
5. **Begin Epic 1 & 2 implementation**

---

**Generated:** 2025-01-26
**Based on:** docs/epics_features_stories.md (100+ user stories, 11 epics)
**Maintained by:** Development team
**Review cadence:** After each sprint retrospective
