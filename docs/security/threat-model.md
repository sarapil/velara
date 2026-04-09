# Threat Model — Velara Hospitality

## نموذج التهديدات — إدارة الضيافة

> Last updated: 2026-04-09
> Based on OWASP Top 10 (2021)

## OWASP Threat Analysis

| # | OWASP Category | Risk for Velara | Mitigation | Status |
|---|---------------|-----------------|------------|--------|
| A01 | Broken Access Control | **HIGH** — Guest PII (passport, credit card), room access, folio charges need strict role isolation | Frappe role permissions per DocType. VL Manager/VL Front Desk/VL Housekeeping roles. `frappe.only_for()` on sensitive methods like `assign_room`, `create_folio`. | ✅ Implemented |
| A02 | Cryptographic Failures | **MEDIUM** — Guest personal data (passport numbers, contact details) must be protected | Frappe handles encryption at rest. Sensitive fields use `Data` type (not exposed in list view). No custom crypto. | ✅ Framework |
| A03 | Injection (SQL/XSS) | **MEDIUM** — Guest names, reservation notes, room descriptions accept user input | All SQL parameterized (`%s`). `validate_availability()` uses parameterized query. Output sanitized. No `eval()`/`exec()`. | ✅ Implemented |
| A04 | Insecure Design | LOW — Thin controller pattern. Reservation validation chain enforced. | Validate methods: `validate_dates()`, `validate_guest()`, `validate_availability()` run on every save. | ✅ By design |
| A05 | Security Misconfiguration | LOW — Standard Frappe defaults. | Framework-managed CSRF, session cookies, HTTP headers. | ✅ Framework |
| A06 | Vulnerable Components | MEDIUM — Depends on frappe, erpnext, hrms, frappe_visual | Version-pinned. Semgrep CI scan. Dependabot alerts. | ✅ CI enforced |
| A07 | Auth Failures | LOW — No custom auth. | Framework login/sessions. Rate limiting. `@frappe.whitelist()` on APIs. | ✅ Framework |
| A08 | Data Integrity Failures | **HIGH** — Folio charges, room rates, reservation status transitions must be audit-trailed | Submit workflow for reservations. Folio charges immutable after settlement. Version tracking on all financial DocTypes. | ✅ Implemented |
| A09 | Logging & Monitoring | LOW — Standard Frappe logging. | Activity log for check-in/check-out. Error logging. No PII in logs. | ✅ Implemented |
| A10 | SSRF | LOW — No external API calls in current version. | If channel manager integration added: timeout, allowlist, validation. | N/A |

## Velara-Specific Threat Scenarios

### 1. Guest Data Breach
- **Threat**: Unauthorized access to guest passport/ID numbers, contact info
- **Impact**: GDPR/privacy violation, reputational damage
- **Control**: VL Guest fields restricted by role. List view hides sensitive fields. No bulk export without VL Manager role.

### 2. Room Availability Manipulation
- **Threat**: Double-booking via race condition or data tampering
- **Impact**: Guest dissatisfaction, overbooking
- **Control**: `validate_availability()` checks overlapping reservations with SQL lock. Submitted reservations only.

### 3. Folio Charge Inflation
- **Threat**: Unauthorized charges posted to guest folio
- **Impact**: Financial fraud, guest disputes
- **Control**: `create_folio()` restricted to VL Manager/System Manager via `frappe.only_for()`. Charges logged with user/timestamp.

### 4. Unauthorized Check-in/Check-out
- **Threat**: Staff bypassing required fields during check-in
- **Impact**: Unregistered guests, security liability
- **Control**: VL Check In validates guest identity, reservation status, and room assignment before processing.

## Audit Checklist

- [x] All `@frappe.whitelist()` endpoints have permission checks
- [x] No raw SQL with string interpolation
- [x] No `frappe.db.commit()` inside document events
- [x] No hardcoded credentials
- [x] Guest PII fields restricted by role
- [x] Folio operations restricted to VL Manager
- [x] Room availability validated with parameterized SQL
- [ ] Penetration test run (scheduled)
- [ ] Third-party security audit (planned for marketplace submission)
