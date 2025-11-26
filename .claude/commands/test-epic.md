# /test-epic - Test Epic SMART Integration

Test the Epic SMART on FHIR integration with sandbox credentials.

## Steps

1. **Check environment setup**:
   - Verify `EPIC_CLIENT_ID`, `EPIC_REDIRECT_URI`, `EPIC_ISSUER` are set
   - Confirm Ollama is running if needed

2. **Start FastAPI backend**:
   ```bash
   python fastapi_epic_smart.py
   ```

3. **Test OAuth flow**:
   - Navigate to `/authorize` endpoint
   - Follow Epic sandbox login
   - Verify callback receives authorization code
   - Check token exchange succeeds

4. **Test FHIR queries**:
   - Query patient data
   - Fetch clinical observations
   - Verify encryption of vault data

5. **Report results**:
   - OAuth flow: ✓/✗
   - FHIR queries: ✓/✗
   - Data encryption: ✓/✗
   - Any errors encountered
