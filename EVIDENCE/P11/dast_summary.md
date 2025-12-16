# P11 — DAST (OWASP ZAP Baseline)

## Target
- Service: Notes API (FastAPI)
- URL: http://localhost:8000
- Scan type: ZAP Baseline

## Findings summary
- High: 0
- Medium: 0
- Low: X
- Informational: Y

Most findings are informational and related to:
- Missing security headers
- Cookie flags (not applicable — no auth/session cookies)

## Triage
Selected alerts:
1. Missing Content-Security-Policy
   - Risk accepted for current stage
   - Service is API-only, no browser-rendered content

## Actions
- Security headers will be added before public exposure
- ZAP baseline kept in CI for regression detection

## Usage
DAST results are used as part of:
- security section in final DS
- regular CI security validation
