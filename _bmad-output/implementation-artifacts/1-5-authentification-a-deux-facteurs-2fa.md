# Story 1.5: Authentification a Deux Facteurs (2FA)

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **utilisateur**,
I want **configurer et utiliser l'authentification a deux facteurs (TOTP) pour securiser mon acces**,
so that **mon compte est protege meme si mon mot de passe est compromis** (FR44).

## Acceptance Criteria

1. **Given** un utilisateur authentifie par mot de passe
   **When** le 2FA n'est pas encore configure
   **Then** l'utilisateur est redirige vers l'ecran de configuration 2FA (affichage QR code TOTP compatible Google Authenticator / Authy)
   
2. **And** apres scan du QR code et saisie du code de verification, le 2FA est active

3. **And** lors des connexions suivantes, apres le mot de passe, un ecran demande le code TOTP

4. **And** le code TOTP est verifie cote serveur (django-otp)

5. **And** le 2FA est obligatoire pour TOUS les comptes sans exception (NFR13)

6. **And** l'administrateur peut reinitialiser le 2FA d'un utilisateur en cas de perte de l'appareil

7. **And** les tentatives de connexion echouees sont journalisees

8. **And** l'interface 2FA est accessible au clavier et compatible lecteurs d'ecran

## Tasks / Subtasks

- [x] Task 1: Integrer django-otp et django-two-factor-auth au backend (AC: #1, #4, #5)
  - [x] 1.1 Ajouter dependencies `django-otp` et `django-two-factor-auth` a requirements.txt
  - [x] 1.2 Configurer OTP_TOTP_ISSUER et OTP middleware dans settings (development.py, test.py, production.py)
  - [x] 1.3 Executer migrations OTP pour tables `otp_totp_totpdevice` et `otp_static_staticdevice`
  - [x] 1.4 Valider que `python manage.py migrate` s'execute sans erreur

- [x] Task 2: Implementer endpoints backend pour 2FA (AC: #1, #2, #4, #5, #6)
  - [x] 2.1 Creer endpoint `POST /api/v1/auth/2fa/setup/` qui genere une cle TOTP et retourne QR code base64
  - [x] 2.2 Creer endpoint `POST /api/v1/auth/2fa/confirm/` qui verifie le code utilisateur et active TOTP
  - [x] 2.3 Creer endpoint `POST /api/v1/auth/2fa/verify/` qui valide le code TOTP lors de la connexion
  - [x] 2.4 Creer endpoint `POST /api/v1/auth/2fa/disable/` (admin only) pour reinitialiser 2FA utilisateur (AC: #6)
  - [x] 2.5 Creer endpoint `POST /api/v1/auth/2fa/backup-codes/` pour generer codes de secours (optionnel post-MVP)
  - [x] 2.6 Integrer verification TOTP dans le flow de login (JWT login return status "2fa-required" si 2FA non-valide)
  - [x] 2.7 Ajouter logs structures (structlog) pour toutes tentatives 2FA reussies/echouees (AC: #7)
  - [x] 2.8 Uniformiser erreurs en RFC 7807 (ex: "otp-invalid" avec message humain)

- [x] Task 3: Moduler l'experience de connexion frontend (AC: #1, #2, #3, #8)
  - [x] 3.1 Modifier `LoginPage` pour afficher ecran 2FA Setup si user.otp_device == null
  - [x] 3.2 Creer composant `TwoFASetupPage` : affichage QR code + champ de verification TOTP
  - [x] 3.3 Creer composant `TwoFAInitPage` : interstitiel entre login password et redirect documents
  - [x] 3.4 Creer composant `TwoFAVerifyForm` : champ input 6 digits TOTP + bouton verify + messages d'erreur
  - [x] 3.5 Mettre a jour authStore pour tracker etat 2FA (pending, configured, verified)
  - [x] 3.6 Implenter guardes routes pour forcer completion 2FA setup avant acces aux documents
  - [x] 3.7 Todos components respectent le theme Ocean Profond et loads/error states

- [x] Task 4: Gerer le flow de connexion avec 2FA obligatoire (AC: #2, #3, #5)
  - [x] 4.1 Modifier endpoint `/api/v1/auth/login/` pour retourner {"access_token": "...", "2fa_required": true|false, "next_action": "setup|verify"}
  - [x] 4.2 Si 2fa_required=true et 2fa_setup=false (nouvel utilisateur) → redirect vers TwoFASetupPage
  - [x] 4.3 Si 2fa_required=true et 2fa_setup=true (user connu) → redirect vers TwoFAVerifyPage
  - [x] 4.4 Apres verification TOTP reussie → generer/renouveler JWT + redirect documents
  - [x] 4.5 Imposer 2FA pour TOUS les utilisateurs sans exception (NFR13)
  - [x] 4.6 Ajouter methode bypass admin pour dev/test (environment flag dev uniquement)

- [x] Task 5: Administrer 2FA pour utilisateurs (AC: #6)
  - [x] 5.1 Creer page admin `AdminUsersPage` avec liste users + colonne "2FA Status"
  - [x] 5.2 Ajouter action contextuelle "Reinitialiser 2FA" sur chaque utilisateur
  - [x] 5.3 Ajouter confirmation modale avant reinitialisation (message: "L'utilisateur devra reconfigurer son 2FA a la prochaine connexion")
  - [x] 5.4 Journaliser toute reinitialisation 2FA avec admin_id + user_id + horodatage dans audit trail
  - [x] 5.5 Afficher historique des reinitialisations pour chaque utilisateur

- [x] Task 6: Tester et valider 2FA (AC: #1-#8)
  - [x] 6.1 Tests backend: setup QR, confirm TOTP (success/failure), verify login (success/failure)
  - [x] 6.2 Tests backend: django-otp generation + verification + timing window (30s)
  - [x] 6.3 Tests backend: reset 2FA by admin + hooks integrity
  - [x] 6.4 Tests frontend: TwoFASetupPage rendering QR + form submission + redirect
  - [x] 6.5 Tests frontend: TwoFAVerifyForm input validation + throttle failed attempts
  - [x] 6.6 Tests accessibility: keyboard navigation dans forms 2FA + ARIA labels + focus management
  - [x] 6.7 Tests e2e: flow complet (login → 2FA setup → documents) via Playwright
  - [x] 6.8 Executer lint/tests/build sans erreur et valider non-regression

## Dev Notes

### Story Foundation

- Story source: `_bmad-output/planning-artifacts/epics.md` (section Story 1.5)
- Epic: **Epic 1 - Acces Securise & Gestion des Permissions**
- Business intent: renforcer la securite de l'authentification via TOTP 2FA obligatoire pour TOUS les utilisateurs (NFR13)
- Dependency: Story 1.4 (JWT backend/frontend) doit etre complete avant de commencer 1.5

### Technical Requirements (Developer Guardrails)

#### 1. 2FA Stack & Libraries
- Backend: `django-otp` (latest stable) + `django-two-factor-auth` (latest stable)
- Frontend: aucune library 2FA frontend; generer QR code cote serveur + barre input 6 digits cote client
- QR code: utiliser `qrcode` library Python (backend)
- TOTP: utiliser `pyotp` (dejà dependance de django-otp)
- Google Authenticator, Authy, Microsoft Authenticator (compatible TOTP standard)

#### 2. 2FA Configuration Checklist
- `OTP_TOTP_ISSUER = "Igar"` dans settings (affiche "Igar" dans Authenticator)
- `OTP_TOTP_INITIAL_TOLERANCE = 1` (accepte codes ±30 secondes, recommande pour tolerance usager)
- Migrations OTP: `python manage.py migrate otp_totp` + `python manage.py migrate otp_static`
- Configurer middleware: ajouter `django_otp.middleware.OTPMiddleware` en MIDDLEWARE liste
- Configurer `INSTALLED_APPS`: ajouter `django_otp`, `django_otp.plugins.otp_totp`, `django_otp.plugins.otp_static`

#### 3. API Contract & Business Rules
- Story 1-4 etablit JWT login; Story 1-5 ajoute 2FA verification entre JWT issued et documents access
- After password validation (existing flow): 
  - If user.otp_device exists AND is active → return `{"access_token": "...", "2fa_required": true, "next_action": "verify"}`
  - If user.otp_device is null → return `{"access_token": "...", "2fa_required": true, "next_action": "setup"}`
  - Frontend decide routing basé sur next_action
- Endpoint `/api/v1/auth/2fa/setup/` retourne: `{"secret": "...", "qr_code": "data:image/png;base64,..."}`
- Endpoint `/api/v1/auth/2fa/verify/` consomme: `{"otp_code": "123456"}` + verifie avec `django_otp.verify_totp(...)`
- Toutes les reponses erreur: format RFC 7807 avec types: `"otp-invalid"`, `"otp-already-setup"`, `"otp-setup-required"`

#### 4. Security Considerations
- Refresh token (JWT) doit rester valide meme apres setup/verification 2FA
- Tokens JWT n'incluent pas le statut OTP (eviter replay attacks); verifier OTP a chaque etape du flow
- Code TOTP expire apres 30s (standard TOTP); accepter ±30s (1 periodes adjacentes via INITIAL_TOLERANCE=1)
- Throttle failed OTP attempts: max 5 tentatives par minute (utiliser cache Django)
- Logs structures pour chaque tentative: user_id, attempt_timestamp, success|failure, otp_device_id
- Journaliser reinitialisations 2FA par admin dans audit trail (future Epic 5)

#### 5. Frontend 2FA Components
- `TwoFASetupPage`: 
  - Display QR code (img tag + src="{{qr_code_base64}}")
  - Input 6-digit TOTP (pattern: pattern="/^[0-9]{6}$/" + maxLength=6)
  - Button "Confirmer 2FA" (POST /api/v1/auth/2fa/confirm/)
  - On success: store `2fa_setup=true` dans state + redirect TwoFAVerifyPage
  - On error: afficher message d'erreur RFC 7807

- `TwoFAVerifyPage`:
  - Input 6-digit TOTP
  - Message "Entrez le code TOTP de votre application"
  - Button "Verifier & Acceder"
  - On success: store `2fa_verified=true` dans JWT + redirect /documents
  - On error: afficher message + decrement tentatives counter
  - Apres 5 echecs: afficher message "Trop de tentatives. Reconnectez-vous." + forcer reauth

- Both pages: theme Ocean Profond, loading skeleton, error toast/banner, accessible clavier (Tab/Shift+Tab/Entree)

#### 6. Boundaries & Non-Goals
- Story 1.5 couvre setup + verification TOTP (TOTP = algorithme TOTP RFC 6238; compatible Google Authenticator)
- NOT couvre: codes de secours (backup codes / one-time codes) — Phase 2 optionnel
- NOT couvre: WebAuthn / U2F — Phase 2+ (enterprise requirement)
- NOT couvre: SMS / email OTP — Phase 2+ (lower security, cote client dependencies)
- Admin 2FA reset couvre reinitialisation device (force user reconfigure + login); ne pas supprimer user account

### Architecture Compliance

- Monorepo: `backend/igar/apps/auth/`, `frontend/src/pages/TwoFASetupPage.tsx`, etc.
- Naming: `snake_case` backend modules, `PascalCase` React components
- API versioning: `/api/v1/auth/2fa/*` endpoints
- RFC 7807: error responses with `type`, `title`, `detail`, `status` fields
- Respect existing auth patterns from Story 1.4 (JWT flow, Axios interceptor, router guards)
- OTP storage: Django OTP models (`otp_totp_totpdevice`, `otp_static_staticdevice`)

### Library & Framework Requirements

- Backend: Django 5.2, DRF, `djangorestframework-simplejwt`, `django-otp`, `django-two-factor-auth`, `qrcode`, `pyotp`
- Frontend: React 18+, TypeScript, Zustand, Axios, React Router v6, Ant Design v6
- Tests: pytest, pytest-django, Vitest, @testing-library/react, Playwright

### File Structure Requirements

Cible minimale a couvrir/creer:

Backend:
- `backend/igar/apps/auth/views.py` — endpoints 2FA backend (setup, confirm, verify, disable)
- `backend/igar/apps/auth/serializers.py` — serializers pour 2FA requests/responses
- `backend/igar/apps/auth/urls.py` — routes `/api/v1/auth/2fa/*`
- `backend/igar/core/otp_handler.py` — business logic OTP (generation QR, verification TOTP)
- `backend/igar/settings/development.py`, `production.py`, `test.py` — OTP config
- `backend/igar/apps/auth/middleware.py` (optionnel) — throttle failed OTP attempts
- `backend/tests/test_auth_2fa.py` — tests unitaires + integration

Frontend:
- `frontend/src/pages/TwoFASetupPage.tsx` — UI setup 2FA
- `frontend/src/pages/TwoFAVerifyPage.tsx` — UI verify 2FA
- `frontend/src/components/TwoFAVerifyForm.tsx` — form reusable
- `frontend/src/api/auth.ts` — API functions (setup, confirm, verify, disable)
- `frontend/src/stores/authStore.ts` — extend avec 2fa_setup, 2fa_verified fields
- `frontend/src/pages/LoginPage.tsx` — update pour router conditionnellement apres login
- `frontend/src/router.tsx` — add guards pour forcer 2FA setup/verify
- `frontend/src/i18n/locales/fr.json`, `en.json` — labels 2FA
- `frontend/tests/TwoFASetupPage.test.tsx`, `TwoFAVerifyForm.test.tsx` — Vitest tests

### Testing Requirements

Backend:
- `test_auth_2fa.py`:
  - test setup_2fa_generates_qr_and_secret
  - test confirm_2fa_with_valid_code
  - test confirm_2fa_with_invalid_code
  - test verify_2fa_on_login_success
  - test verify_2fa_on_login_failure (multiple attempts)
  - test admin_reset_2fa_by_disable_device
  - test 2fa_is_mandatory_for_all_users
  - test logs_are_structured
  - test errors_follow_rfc7807
  - Coverage target: >90% on auth app

Frontend:
- `TwoFASetupPage.test.tsx`:
  - test renders QR code image
  - test form submission triggers API request
  - test success redirects to verify page
  - test error displays message
  - test keyboard accessible

- `TwoFAVerifyForm.test.tsx`:
  - test input 6-digit validation
  - test form submission triggers verify
  - test throttle on failed attempts
  - test success callback
  - test error message display

- E2E Playwright:
  - test complete flow: login → 2FA setup → verify → documents access
  - test user already setup 2FA → login → 2FA verify → documents access
  - test admin reset 2FA → user reconnect → forced setup

### Previous Story Intelligence (1.4)

- Story 1.4 implemented JWT backend + frontend auth flow (login/logout/refresh)
- `LoginPage`, `authStore`, `api/client.ts`, router guards already exist
- 2FA is ADDITION post-password-validation; reuse existing auth infrastructure
- JWT tokens n'incluent pas le statut 2FA (verifier en session/request middleware)
- Response du login endpoint (1.4) peut etre etendu avec `"2fa_required": true/false` + `"next_action": "setup|verify"`

### Git Intelligence Summary

- Igar project en v1.0 MVP
- Backend est fork Mayan EDMS 4.11 (Django 5.2)
- Frontend est Vite SPA (React 18, TypeScript)
- Story 1.4 code review completed; use as baseline pour Story 1.5 implementation
- Auth app patterns stabiles; 2FA est extension naturelle

### Latest Tech Information

- django-otp: latest stable ~= 1.2.4 (supports Django 5.2)
- django-two-factor-auth: latest stable ~= 1.15 (supports Django 5.2, python-phonenumbers optional)
- TOTP RFC 6238: standard ouvert, compatible Google Authenticator / Authy / Microsoft Authenticator / KeePass
- Tendance securite: TOTP prefere aux SMS/email OTP (resistant phishing); WebAuthn (Phase 2+) est prochaine evolution

### Project Context Reference

- Aucun fichier `project-context.md`.
- Contexte utilise: `epics.md`, `architecture.md`, `ux-design-specification.md`, `1-4-authentification-jwt-et-interface-de-connexion.md`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.5: Authentification a Deux Facteurs (2FA)]
- [Source: _bmad-output/planning-artifacts/architecture.md#2FA Library: django-otp + django-two-factor-auth]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#NFR13: 2FA obligatoire pour tous comptes]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication Patterns (RFC 7807)]
- [Source: _bmad-output/implementation-artifacts/1-4-authentification-jwt-et-interface-de-connexion.md]
- RFC 6238: TOTP (https://tools.ietf.org/html/rfc6238)
- RFC 7807: Problem Details for HTTP APIs (https://tools.ietf.org/html/rfc7807)

## Dev Agent Record

### Agent Model Used

Claude Haiku 4.5

### Debug Log References

- Workflow: `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- Engine: `_bmad/core/tasks/workflow.xml`
- Config: `_bmad/bmm/config.yaml`
- Execution date: 2026-03-29

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story auto-selected from first backlog item in sprint status: `1-5-authentification-a-deux-facteurs-2fa`.
- Story status set to `ready-for-dev`.
- Epic 1 status confirmed as `in-progress` (previous stories 1.1-1.4 completed/in review/done).
- Architecture & tech stack validated for django-otp + django-two-factor-auth.
- Previous story (1.4) learnings integrated for JWT + 2FA flow alignment.
- All acceptance criteria from epics mapped to tasks and dev guardrails.
- Authorization checks: 2FA mandatory for ALL users (NFR13) documented.
- Testing requirements comprehensive (backend pytest, frontend Vitest, E2E Playwright).

### Change Log

- Implemented 2FA backend flow with challenge token, setup, confirmation, verification, disable, backup codes, and admin user listing.
- Added frontend 2FA flow with dedicated setup/verification routes, shared OTP form, store state, and admin management UI.
- Added and validated backend tests and frontend Vitest coverage for the new 2FA flow.
- Updated sprint tracking to move story 1.5 through implementation and review readiness.

### File List

- `_bmad-output/implementation-artifacts/1-5-authentification-a-deux-facteurs-2fa.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/requirements/base.txt`
- `backend/igar/core/auth_urls.py`
- `backend/igar/core/auth_views.py`
- `backend/igar/core/exceptions.py`
- `backend/igar/settings/base.py`
- `backend/igar/settings/development.py`
- `backend/igar/settings/production.py`
- `backend/igar/settings/test.py`
- `backend/tests/test_auth_api.py`
- `backend/tests/test_auth_2fa.py`
- `frontend/src/api/auth.ts`
- `frontend/src/components/RouteGuards.tsx`
- `frontend/src/components/TwoFAVerifyForm.tsx`
- `frontend/src/components/TwoFAVerifyForm.test.tsx`
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/fr.json`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/pages/LoginPage.test.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/TwoFAInitPage.tsx`
- `frontend/src/pages/TwoFASetupPage.test.tsx`
- `frontend/src/pages/TwoFASetupPage.tsx`
- `frontend/src/pages/TwoFAVerifyPage.tsx`
- `frontend/src/router.tsx`
- `frontend/src/stores/authStore.ts`
