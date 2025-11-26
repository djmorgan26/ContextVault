
import os
import base64
import hashlib
import secrets
import json
import logging
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from jose import jwt, jwk
from jose.utils import base64url_decode
from dotenv import load_dotenv

load_dotenv()
LOG_PATH = os.environ.get("EPIC_SMART_LOG_PATH", "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_PATH, mode="a"),
    ],
)
logger = logging.getLogger("epic-smart")

app = FastAPI()

# --- CONFIG: provide these via env vars ---
CLIENT_ID = os.environ.get("EPIC_CLIENT_ID")  # from open.epic (sandbox) or App Orchard (prod)
CLIENT_SECRET = os.environ.get("EPIC_CLIENT_SECRET")  # confidential clients only (not for PKCE public clients)
REDIRECT_URI = os.environ.get("EPIC_REDIRECT_URI", "http://localhost:8000/callback")
# If using open.epic sandbox, set ISSUER to https://fhir.epic.com/interconnect-fhir-oauth/oauth2
# For production tenants, use the issuer returned in the SMART launch or discovery.
ISSUER = os.environ.get("EPIC_ISSUER", "https://fhir.epic.com/interconnect-fhir-oauth/oauth2")
# Optionally set FHIR_BASE; when launching from EHR you usually get 'iss' or 'fhirBaseUrl' in the launch context.
FHIR_BASE = os.environ.get("EPIC_FHIR_BASE", "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4")

# Simple in-memory store for state <-> pkce/verifier. Replace with DB in prod
STATE_STORE = {}

# --- Helper functions ---

def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().rstrip("=")
    return code_verifier, code_challenge

async def fetch_oidc_config(issuer: str):
    url = issuer.rstrip("/") + "/.well-known/openid-configuration"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

async def fetch_jwks(jwks_uri: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(jwks_uri, timeout=10)
        r.raise_for_status()
        return r.json()

def validate_id_token(id_token: str, jwks: dict, issuer: str, audience: str):
    # Use python-jose for JWT validation: this function verifies signature & audience/iss/exp.
    # Note: python-jose requires building a key for the appropriate kid. Here we delegate to jose.jwt.decode.
    try:
        claims = jwt.decode(id_token, jwks, audience=audience, issuer=issuer, options={"verify_at_hash": False})
        return claims
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"id_token validation failed: {str(e)}")

# --- Routes ---

@app.get("/login")
async def login(
    response: Response,
    redirect_to: Optional[str] = None,
    iss: Optional[str] = None,
    launch: Optional[str] = None,
    fhir_base: Optional[str] = None,
):
    """
    Start the SMART on FHIR OAuth2 Authorization Code + PKCE flow.
    - redirect_to: optional URL to return to after login state is complete (stored in state)
    - iss: FHIR base URL supplied by the EHR launch (SMART requirement)
    - launch: opaque launch context provided by Epic when using launch-scoped apps
    - fhir_base: override for aud/FHIR base when running standalone (defaults to env)
    """
    if not CLIENT_ID:
        raise HTTPException(status_code=500, detail="EPIC_CLIENT_ID not configured in environment")

    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)

    # Save state mapping to verifier + optional redirect
    STATE_STORE[state] = {"code_verifier": code_verifier, "nonce": nonce, "redirect_to": redirect_to}

    oidc = await fetch_oidc_config(ISSUER)
    auth_endpoint = oidc["authorization_endpoint"]

    # Minimal scopes: openid required for id_token; request specific patient scopes you need.
    scopes = [
        "openid",
        "profile",
        "patient/Patient.read",
        "patient/Observation.read",
        "offline_access",
    ]
    if launch:
        scopes.insert(2, "launch/patient")
    scope_str = " ".join(scopes)

    # Use the runtime-provided FHIR base / issuer when launching from Epic, otherwise fallback to env default.
    effective_fhir_base = (fhir_base or iss or FHIR_BASE).rstrip("/")

    # If launching from EHR, SMART typical params include 'launch' and 'iss' (handled by the EHR launch flow).
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": scope_str,
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        # 'aud' sometimes required by certain Epic deployments to indicate FHIR server
        "aud": effective_fhir_base
    }
    if iss:
        params["iss"] = iss
    if launch:
        params["launch"] = launch

    url = auth_endpoint + "?" + urlencode(params)
    logger.info(
        "Redirecting to Epic auth endpoint %s with params=%s",
        auth_endpoint,
        params,
    )
    return RedirectResponse(url)

@app.get("/callback")
async def callback(request: Request):
    """
    Callback endpoint that Epic/MyChart will redirect to with ?code=...&state=...
    Exchange the code for tokens and validate id_token.
    """
    params = dict(request.query_params)
    logger.info("Callback received with params=%s", params)
    if "error" in params:
        raise HTTPException(status_code=400, detail=f"OAuth error: {params.get('error_description') or params['error']}")
    code = params.get("code")
    state = params.get("state")
    if not code or not state or state not in STATE_STORE:
        raise HTTPException(status_code=400, detail="Missing or invalid state/code")

    stored = STATE_STORE.pop(state)
    code_verifier = stored["code_verifier"]

    oidc = await fetch_oidc_config(ISSUER)
    token_endpoint = oidc["token_endpoint"]
    jwks_uri = oidc.get("jwks_uri")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": code_verifier
    }
    # Include client_secret if confidential client
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET

    logger.info(
        "Exchanging code for tokens at %s payload_keys=%s",
        token_endpoint,
        list(data.keys()),
    )
    async with httpx.AsyncClient() as client:
        r = await client.post(
            token_endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        if r.status_code >= 400:
            logger.error(
                "Token exchange failed status=%s body=%s",
                r.status_code,
                r.text,
            )
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {r.text}")
        token_resp = r.json()
    logger.info("Token exchange succeeded keys=%s", list(token_resp.keys()))

    # Validate id_token if present
    id_token = token_resp.get("id_token")
    if id_token and jwks_uri:
        jwks = await fetch_jwks(jwks_uri)
        # jose.jwt.decode can accept jwks directly in some versions; otherwise you must pick the right key by 'kid'.
        try:
            claims = jwt.decode(id_token, jwks, audience=CLIENT_ID, issuer=ISSUER)
        except Exception as e:
            # For some sandboxes jwks validation may be limited; still log/raise in prod
            raise HTTPException(status_code=400, detail=f"id_token validation failed: {e}")

    # Persist tokens securely (DB, encrypted vault). Example returns tokens for demo only.
    # token_resp contains access_token, refresh_token (if issued), expires_in, token_type, scope
    return JSONResponse(token_resp)

@app.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access_token using a refresh_token (if Epic issued one).
    """
    oidc = await fetch_oidc_config(ISSUER)
    token_endpoint = oidc["token_endpoint"]
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": CLIENT_ID}
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        r = await client.post(token_endpoint, data=data, headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=10)
        if r.status_code >= 400:
            raise HTTPException(status_code=400, detail=f"Refresh failed: {r.text}")
        return JSONResponse(r.json())

async def call_fhir(access_token: str, path: str):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/fhir+json"}
    url = FHIR_BASE.rstrip("/") + "/" + path.lstrip("/")
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()

@app.get("/patient")
async def get_patient(access_token: str, patient_id: Optional[str] = None):
    """
    Fetch Patient resource. If patient_id omitted, attempt to use fhirUser claim from id_token flow (not implemented here).
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access_token")
    # If patient_id not passed, you may parse id_token.fhirUser to get resource URL.
    if patient_id:
        path = f"Patient/{patient_id}"
    else:
        # Example: use /Patient?identifier=... or return error
        raise HTTPException(status_code=400, detail="Pass patient_id for this demo")
    return await call_fhir(access_token, path)

@app.get("/observations")
async def get_observations(access_token: str, patient_id: str):
    """
    Fetch Observations for patient: GET [base]/Observation?patient={id}&_count=50
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access_token")
    path = f"Observation?patient={patient_id}&_count=50"
    return await call_fhir(access_token, path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_epic_smart:app", host="0.0.0.0", port=8000, reload=True)
