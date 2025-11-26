# /add-feature - Add New Feature to ContextVault

Guided workflow for adding a new feature following project patterns.

## Steps

1. **Feature Planning**:
   - Ask user: What feature are we adding?
   - Determine components needed:
     - Backend API endpoint?
     - Database model/migration?
     - Frontend component?
     - Epic FHIR integration?

2. **Check Existing Patterns**:
   - Review similar features in codebase
   - Check security requirements (encryption needed?)
   - Identify reusable code

3. **Implementation Order**:
   - Database schema (if needed)
   - Backend logic (FastAPI route/service)
   - Encryption handling (if vault data)
   - Frontend component (if UI change)
   - Tests

4. **Security Review**:
   - Any PII/PHI involved? → Must encrypt
   - Input validation implemented?
   - Authorization checks in place?

5. **Documentation**:
   - Update API docs (if endpoint added)
   - Add to README if user-facing
   - Run `/capture` to document implementation

6. **Testing**:
   - Manual test the feature
   - Check error cases
   - Verify encryption (if applicable)
