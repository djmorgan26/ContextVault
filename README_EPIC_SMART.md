
FASTAPI SMART on FHIR (Epic/MyChart) Example - README
===================================================

Files created:
- /mnt/data/fastapi_epic_smart.py  (FastAPI app)

Dependencies (install locally):
  pip install fastapi "uvicorn[standard]" httpx python-jose cryptography

Environment variables you must set (example):
  export EPIC_CLIENT_ID=<your_client_id_from_open.epic_or_app_orchard>
  export EPIC_CLIENT_SECRET=<your_client_secret_if_confidential>
  export EPIC_REDIRECT_URI="http://localhost:8000/callback"
  export EPIC_ISSUER="https://fhir.epic.com/interconnect-fhir-oauth/oauth2"
  export EPIC_FHIR_BASE="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"  # sandbox default

How to run (development/sandbox):
  1) Set the env vars above (use open.epic sandbox client id if building against sandbox)
  2) python /mnt/data/fastapi_epic_smart.py
  3) Open http://localhost:8000/login to start the auth flow (this redirects to Epic sandbox's auth page)

What the app does (summary):
  - /login : redirects user to Epic's OAuth authorize URL (uses PKCE & saves code_verifier in memory)
  - /callback: receives authorization code, exchanges for tokens, validates id_token (if present), returns token JSON
  - /refresh: POST refresh_token to get new access token
  - /patient : simple example to GET Patient/{id} from FHIR (requires access_token as query param in this demo)
  - /observations: GET Observation?patient={id}

App Registration steps (sandbox -> production):
1) Sandbox testing (open.epic):
   - Visit https://open.epic.com/ and sign up / log in. Use the Launchpad (https://open.epic.com/Launchpad) to test SMART launch flows and to get a sandbox client_id. (See: Epic on FHIR docs and Open Epic). See https://open.epic.com/ and https://fhir.epic.com/ for sandbox info.  (Epic docs: open.epic / FHIR sandbox).

2) Register your application (Epic on FHIR client registration):
   - Go to https://fhir.epic.com/ -> Developer -> My Apps (or 'Client Registration') and create a new app.
   - Add exact Redirect URI(s) (e.g., http://localhost:8000/callback) - redirect URIs must match exactly.
   - Choose SMART on FHIR version (R4) and select scopes you need (e.g., openid fhirUser patient/Patient.read patient/Observation.read offline_access).
   - Save and copy the Non-Production Client ID to EPIC_CLIENT_ID for testing. (See Epic Developer Apps pages).

3) Production & App Orchard (for production/MyChart connections to real patients):
   - To make your app available to Epic customers and get production access, register as a developer on Epic App Orchard: https://apporchard.epic.com/ (App Orchard has account tiers and a submission & security review process).
   - Fill out App Orchard listing, privacy & support details, and request the exact resources/scopes you need. Epic/health systems may require additional approvals and contracts (HIPAA, BAAs, business review).
   - After App Orchard and customer approval, you will receive production Client IDs (per tenant) or the customer will approve your app to connect to their Epic instance.

Important implementation notes & gotchas:
- Always use PKCE for public clients (mobile/web). For confidential backends you can use client_secret, but storing secrets securely is critical.
- Validate id_tokens and signatures using jwks_uri from the issuer's .well-known/openid-configuration.
- Tenant endpoints & behavior vary — when launched from EHR you often receive 'launch' and 'iss' parameters enabling tenant-specific flows. Use runtime discovery from the issuer.
- Refresh token availability & lifetime may differ by tenant — plan to ask users to re-authorize if refresh is not available.
- Test thoroughly in the sandbox (open.epic) before moving to App Orchard/production.

References / useful docs:
- Epic on FHIR / Documentation & Client Registration: https://fhir.epic.com/Documentation?docId=testpatients. (Epic docs & sandbox info). citeturn0search0turn1search9
- Open Epic sandbox / Launchpad: https://open.epic.com/Launchpad. citeturn1search1
- Example openid-configuration for Epic (discovery endpoint & jwks): https://fhir.epic.com/interconnect-fhir-oauth/oauth2/.well-known/openid-configuration. citeturn0search4
- SMART App Launch spec (scopes & launch context): https://build.fhir.org/ig/HL7/smart-app-launch/app-launch.html. citeturn0search15
- App Orchard & production onboarding (high-level): https://apporchard.epic.com/ (see App Orchard for production registration). citeturn1search10

Security reminder:
  - This demo stores PKCE code_verifier/state in memory and returns tokens in the response for clarity. DO NOT use this pattern in production.
  - Persist tokens encrypted (Azure Key Vault, AWS KMS, etc.), rotate client secrets, secure redirect URIs, and perform regular security reviews.

