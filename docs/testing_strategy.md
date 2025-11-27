# Context Vault - Testing Strategy

## Testing Pyramid

```
          ┌─────────┐
          │   E2E   │  10% - Critical user flows
          └─────────┘
        ┌─────────────┐
        │ Integration │  30% - API + Database + Services
        └─────────────┘
      ┌─────────────────┐
      │   Unit Tests    │  60% - Functions, utilities, components
      └─────────────────┘
```

## Testing Goals

- **MVP Target**: 70% code coverage
- **Production Target**: 85% code coverage (excluding UI)
- **Critical Paths**: 100% coverage (auth, encryption, integrations)

---

## Unit Tests

### Backend (Python + pytest)

**Scope:**

- Encryption/decryption functions
- Key derivation
- Token generation/validation
- Pydantic models
- Utility functions

**Example:**

```python
# tests/test_encryption.py
import pytest
from app.core.encryption import encrypt_content, decrypt_content, derive_master_key

def test_encryption_cycle():
    """Test encrypt → decrypt returns original."""
    master_key = derive_master_key("google_id_123", "app_secret", b"salt" * 4)
    plaintext = "My sensitive data"

    encrypted = encrypt_content(plaintext, master_key)
    decrypted = decrypt_content(encrypted, master_key)

    assert decrypted == plaintext
    assert encrypted != plaintext  # Actually encrypted

def test_decryption_with_wrong_key_fails():
    """Test decryption with wrong key raises error."""
    key1 = derive_master_key("user1", "secret", b"salt1" * 4)
    key2 = derive_master_key("user2", "secret", b"salt2" * 4)

    encrypted = encrypt_content("data", key1)

    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_content(encrypted, key2)

def test_key_derivation_is_deterministic():
    """Same inputs produce same key."""
    key1 = derive_master_key("google_id", "secret", b"salt" * 4)
    key2 = derive_master_key("google_id", "secret", b"salt" * 4)
    assert key1 == key2

def test_key_derivation_different_for_different_users():
    """Different users get different keys."""
    key1 = derive_master_key("user1", "secret", b"salt" * 4)
    key2 = derive_master_key("user2", "secret", b"salt" * 4)
    assert key1 != key2
```

**Run:**

```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

### Frontend (Next.js + Vitest + React Testing Library)

**Scope:**

- Next.js client/server components (render tests)
- Custom hooks
- Utility functions
- API client

**Example:**

```typescript
// src/components/VaultDashboard.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import VaultDashboard from "./VaultDashboard";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

describe("VaultDashboard", () => {
  it("shows empty state when no items", async () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <VaultDashboard />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/your vault is empty/i)).toBeInTheDocument();
    });
  });

  it("displays vault items when present", async () => {
    // Mock API response
    vi.mock("../lib/api", () => ({
      getVaultItems: () =>
        Promise.resolve({
          items: [
            { id: "1", title: "Test Note", type: "note", tags: ["test"] },
          ],
        }),
    }));

    render(<VaultDashboard />);

    await waitFor(() => {
      expect(screen.getByText("Test Note")).toBeInTheDocument();
    });
  });
});
```

**Run:**

```bash
cd frontend
npm run test
```

---

## Integration Tests

### Backend API Tests (pytest + httpx)

**Scope:**

- Full API endpoints with database
- Authentication flow
- Vault CRUD operations
- Integration syncs

**Example:**

```python
# tests/integration/test_vault_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_and_retrieve_vault_item(auth_headers):
    """Test creating vault item and retrieving it."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create item
        response = await client.post(
            "/api/vault/items",
            json={
                "type": "note",
                "title": "Test Note",
                "content": "Secret content",
                "tags": ["test"]
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        item_id = response.json()["id"]

        # Retrieve item
        response = await client.get(
            f"/api/vault/items/{item_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        item = response.json()
        assert item["title"] == "Test Note"
        assert item["content"] == "Secret content"  # Decrypted
        assert "test" in item["tags"]

@pytest.mark.asyncio
async def test_cannot_access_other_users_items(auth_headers, other_user_item_id):
    """Test authorization: user cannot access another user's vault items."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/vault/items/{other_user_item_id}",
            headers=auth_headers
        )
        assert response.status_code == 404  # Not found (not 403, to prevent enumeration)
```

**Fixtures:**

```python
# tests/conftest.py
import pytest
from app.core.database import SessionLocal
from app.models import User

@pytest.fixture
async def test_user(db: Session):
    """Create test user."""
    user = User(
        google_id="test_google_id",
        email="test@example.com",
        name="Test User",
        encryption_salt=os.urandom(32).hex()
    )
    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers for test user."""
    token = create_access_token(test_user.id, test_user.email)
    return {"Authorization": f"Bearer {token}"}
```

---

## End-to-End Tests

### Playwright (Critical User Flows)

**Scope:**

- Google OAuth login
- Upload file → Chat about it
- Epic connection → View medical data
- Create note → Search → Find it

**Example:**

```typescript
// e2e/critical-flows.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Critical User Flows", () => {
  test("Upload file and chat about it", async ({ page }) => {
    // Login (mock OAuth for testing)
    await page.goto("http://localhost:5173");
    await page.click("text=Sign in with Google");
    // ... mock OAuth flow ...

    // Upload file
    await page.click("text=Upload File");
    await page.setInputFiles(
      'input[type="file"]',
      "./test-data/medical_report.pdf"
    );
    await expect(page.locator("text=File uploaded")).toBeVisible();

    // Navigate to chat
    await page.click("text=Chat");

    // Ask about uploaded file
    await page.fill(
      'textarea[placeholder*="message"]',
      "Summarize my medical report"
    );
    await page.press("textarea", "Enter");

    // Wait for AI response
    await expect(page.locator("text=Based on your medical report")).toBeVisible(
      { timeout: 10000 }
    );

    // Verify context indicator
    await expect(page.locator("text=Used 1 vault item")).toBeVisible();
  });

  test("Epic integration flow", async ({ page }) => {
    // Login
    await page.goto("http://localhost:5173/settings");

    // Connect Epic
    await page.click("text=Connect Epic MyChart");
    await page.click('button:has-text("Connect Epic MyChart")');

    // Mock Epic OAuth (in real test, use Epic sandbox)
    // ...

    // Verify connection
    await expect(page.locator("text=Epic MyChart: Connected")).toBeVisible();

    // Check vault for synced items
    await page.goto("http://localhost:5173/vault");
    await expect(
      page.locator('[data-source="epic"]')
    ).toHaveCount(/* expected count */);
  });
});
```

**Run:**

```bash
npx playwright test
```

---

## Manual Testing Checklist

### Pre-Release (Before Each Deploy)

**Authentication:**

- [ ] Google OAuth login works (dev and prod)
- [ ] Access token refresh works
- [ ] Logout clears session
- [ ] Expired token shows login prompt

**Vault Operations:**

- [ ] Upload PDF file (extract text works)
- [ ] Upload image (OCR works if implemented)
- [ ] Create note with markdown
- [ ] Edit vault item
- [ ] Delete vault item (soft delete)
- [ ] Search finds items by title
- [ ] Filter by tags works
- [ ] Pagination works (51+ items)

**Chat:**

- [ ] Chat with empty vault (graceful handling)
- [ ] Chat about vault data (context retrieval works)
- [ ] Streaming response works
- [ ] Context indicator shows correct items
- [ ] Error handling (Ollama down)

**Integrations:**

- [ ] Epic OAuth flow completes
- [ ] Epic sync retrieves records
- [ ] Epic data appears in vault
- [ ] Epic disconnect removes tokens

**Security:**

- [ ] Cannot access other users' vault items (try guessing IDs)
- [ ] SQL injection attempts fail (try in search)
- [ ] XSS attempts sanitized (try in note content)
- [ ] Rate limiting works (spam requests)

**Mobile (PWA):**

- [ ] Responsive on iPhone (Safari)
- [ ] Responsive on Android (Chrome)
- [ ] PWA install prompt appears
- [ ] Offline vault viewing works

**Performance:**

- [ ] First contentful paint < 2s
- [ ] Chat first token < 3s
- [ ] File upload (5MB) < 5s
- [ ] Search results < 500ms

---

## Performance Testing

### Load Testing (Locust)

**Scenario:** 100 concurrent users

```python
# locustfile.py
from locust import HttpUser, task, between

class ContextVaultUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before tests."""
        # Mock login or use test token
        self.client.headers["Authorization"] = f"Bearer {self.get_token()}"

    @task(3)
    def list_vault_items(self):
        """Most common operation."""
        self.client.get("/api/vault/items")

    @task(1)
    def create_vault_item(self):
        """Create note."""
        self.client.post("/api/vault/items", json={
            "type": "note",
            "title": "Load test note",
            "content": "Test content",
            "tags": ["test"]
        })

    @task(1)
    def chat(self):
        """Chat with AI."""
        self.client.post("/api/chat", json={
            "message": "Hello, how are you?"
        })
```

**Run:**

```bash
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089, set users=100
```

**Targets:**

- 100 concurrent users
- Median response time < 500ms
- 95th percentile < 2s
- Error rate < 1%

---

## Security Testing

### Automated Scans

**Dependency Vulnerabilities:**

```bash
# Python
pip install safety
safety check

# Node.js
npm audit
npm audit fix
```

**SAST (Static Analysis):**

```bash
# Python
pip install bandit
bandit -r app/ -f json -o security-report.json

# TypeScript
npm install --save-dev eslint-plugin-security
eslint src/ --ext .ts,.tsx
```

### Manual Security Tests

**Authentication:**

- [ ] Try accessing API without token (expect 401)
- [ ] Try using expired token (expect 401)
- [ ] Try using another user's token (expect 403)

**Authorization:**

- [ ] Try accessing vault item with guessed ID (expect 404)
- [ ] Try modifying another user's item (expect 403/404)

**Injection:**

- [ ] SQL injection in search: `'; DROP TABLE users; --`
- [ ] XSS in note content: `<script>alert('xss')</script>`
- [ ] Path traversal in file upload: `../../../etc/passwd`

**Cryptography:**

- [ ] Verify encrypted data in database is not readable
- [ ] Verify decryption with wrong key fails
- [ ] Verify token replay attack prevented

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Start services
        run: docker-compose up -d

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Test Data Management

### Seed Data for Development

```python
# backend/scripts/seed_db.py
from app.core.database import SessionLocal
from app.models import User, VaultItem, Tag
import uuid

def seed_test_data():
    """Create test user and sample vault items."""
    db = SessionLocal()

    # Create test user
    user = User(
        id=uuid.uuid4(),
        google_id="test_user_1",
        email="test@example.com",
        name="Test User",
        encryption_salt=os.urandom(32).hex()
    )
    db.add(user)
    db.commit()

    # Create tags
    tags = [
        Tag(user_id=user.id, name="medical", color="#FF5733"),
        Tag(user_id=user.id, name="personal", color="#3498DB"),
    ]
    db.add_all(tags)
    db.commit()

    # Create vault items (need to encrypt content)
    # ...

    db.close()
    print("Test data seeded!")

if __name__ == "__main__":
    seed_test_data()
```

**Run:**

```bash
cd backend
python scripts/seed_db.py
```

---

## Testing Timeline

### Phase 1 (MVP)

- Week 1-2: Set up testing infrastructure (pytest, vitest, playwright)
- Week 3-6: Write tests alongside features (TDD where possible)
- Week 7: E2E tests for critical flows
- Week 8: Security testing and load testing

### Ongoing

- Every PR: Run unit + integration tests (CI)
- Every deploy: Run E2E tests (staging)
- Weekly: Manual smoke tests (production)
- Monthly: Full security scan

---

**Next Steps:**

1. Set up pytest and vitest
2. Write tests for encryption service first (critical)
3. Add tests to CI/CD pipeline
4. Maintain 70%+ coverage throughout development
