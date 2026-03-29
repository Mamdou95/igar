# Story 1.4: Authentification JWT et Interface de Connexion

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **utilisateur**,
I want **me connecter a Igar avec mon identifiant et mot de passe via une page de connexion securisee**,
so that **j'accede a mon espace documentaire de maniere authentifiee et protegee**.

## Acceptance Criteria

1. **Given** un utilisateur avec un compte existant dans le systeme **When** il saisit ses identifiants sur la page de connexion (`LoginPage`) **Then** le systeme verifie les identifiants via l'API `/api/v1/auth/login/`
2. **And** en cas de succes, un access token JWT (TTL 15 min) et un refresh token (cookie `httpOnly`) sont emis (NFR14)
3. **And** l'utilisateur est redirige vers la vue Documents
4. **And** en cas d'echec, un message d'erreur humain est affiche (format RFC 7807) sans reveler si c'est l'identifiant ou le mot de passe incorrect
5. **And** le refresh token renouvelle automatiquement l'access token expire via l'intercepteur Axios
6. **And** la deconnexion invalide les tokens et redirige vers la page de connexion
7. **And** la page de connexion respecte le theme "Ocean Profond" et est accessible au clavier (WCAG 2.1 AA)
8. **And** toutes les communications sont en TLS 1.3 (NFR11)
9. **And** une protection anti-CSRF est active sur les operations de mutation (NFR16)

## Tasks / Subtasks

- [ ] Task 1: Implementer les endpoints d'authentification JWT backend (AC: #1, #2, #4, #8, #9)
  - [ ] 1.1 Ajouter endpoint `POST /api/v1/auth/login/` avec validation des credentials (DRF + SimpleJWT)
  - [ ] 1.2 Configurer emission access token (15 min) + refresh token en cookie `httpOnly`/`secure`/`samesite`
  - [ ] 1.3 Uniformiser les erreurs en RFC 7807 sans fuite d'information sensible
  - [ ] 1.4 Integrer protection anti-CSRF sur mutations et verifier comportement login/refresh/logout

- [ ] Task 2: Implementer la gestion de session frontend (AC: #2, #3, #5, #6)
  - [ ] 2.1 Etendre `authStore` pour stocker l'etat d'authentification et actions login/logout
  - [ ] 2.2 Configurer interceptors Axios pour refresh automatique et rejection controlee en cas d'echec
  - [ ] 2.3 Mettre en place garde de routes (redirection vers `/login` si non authentifie)
  - [ ] 2.4 Gerer la deconnexion complete (etat local, cookie refresh, redirection)

- [ ] Task 3: Construire l'interface de connexion et feedback UX (AC: #1, #3, #4, #7)
  - [ ] 3.1 Implementer formulaire `LoginPage` (identifiant, mot de passe, submit, loading)
  - [ ] 3.2 Afficher messages d'erreur explicites et non-ambiguite securitaire
  - [ ] 3.3 Respecter tokens visuels Ocean Profond et navigation clavier complete
  - [ ] 3.4 Ajouter etats vide/chargement/erreur conformes aux patterns UX

- [ ] Task 4: Ajouter tests et validations transverses (AC: #1-#9)
  - [ ] 4.1 Tests unitaires backend (login succes/echec, format erreur, cookie refresh)
  - [ ] 4.2 Tests integration backend/frontend (refresh token, logout, redirections)
  - [ ] 4.3 Tests frontend (RTL/Vitest) sur formulaire login + guard routes
  - [ ] 4.4 Verification lint, accessibilite clavier, build et non-regression

## Dev Notes

### Story Foundation

- Story source: `_bmad-output/planning-artifacts/epics.md` (section Story 1.4)
- Epic: **Epic 1 - Acces Securise & Gestion des Permissions**
- Business intent: etablir un acces securise a la plateforme avant 2FA (Story 1.5) et RBAC/cloisonnement avance (Story 1.6)

### Technical Requirements (Developer Guardrails)

1. **Authentication baseline**
- Backend sur Django/DRF avec `djangorestframework-simplejwt`.
- Access token JWT: expiration 15 min (NFR14).
- Refresh token transporte en cookie `httpOnly`; ne jamais exposer le refresh token au JavaScript applicatif.

2. **Security and API behavior**
- Communication HTTPS/TLS 1.3 obligatoire en environnements integres (NFR11).
- Protection anti-CSRF active pour les endpoints de mutation (NFR16).
- Reponses d'erreur API au format RFC 7807 (Problem Details).
- Ne pas distinguer publiquement "utilisateur inconnu" vs "mot de passe incorrect".

3. **Frontend auth flow**
- Reutiliser la base Story 1.3: `api/client.ts`, `authStore`, `router.tsx`, `LoginPage`.
- Intercepteur Axios: tentative de refresh a l'expiration access token, puis retry unique de requete initiale.
- Garde route: acces non-authentifie redirige vers `/login`; login reussi redirige vers `/documents`.

4. **UX and accessibility**
- Conserver theme Ocean Profond + densite compacte.
- Formulaire login entierement navigable clavier (tab order, focus visible, submit Enter).
- Messages d'erreur comprehensibles, non techniques, sans fuite d'information sensible.

5. **Boundaries and non-goals**
- Cette story couvre login/logout/refresh JWT et UX de connexion.
- 2FA/TOTP sera traite en Story 1.5 (ne pas anticiper de logique complete 2FA ici).
- RBAC/cloisonnement avance sera traite en Story 1.6.

### Architecture Compliance

- Respecter la separation monorepo: `backend/`, `frontend/`, `infrastructure/`.
- Conserver conventions de nommage et structure de l'architecture (`snake_case` backend, PascalCase composants frontend).
- S'aligner sur `/api/v1/` pour le versioning API et RFC 7807 pour les erreurs.
- Toute logique metier de securite cote serveur; le frontend orchestre l'experience utilisateur et les etats.

### Library and Framework Requirements

- Backend: Django 5.2, Django REST Framework, `djangorestframework-simplejwt`.
- Frontend: React + TypeScript, React Router v6, Zustand, Axios, Ant Design.
- Tests backend: `pytest`, `pytest-django`.
- Tests frontend: `vitest`, `@testing-library/react`, `eslint-plugin-jsx-a11y`.

### File Structure Requirements

Cible minimale a couvrir/mettre a jour:

- `backend/igar/...` modules auth API (views/serializers/urls/settings selon implementation existante)
- `frontend/src/api/client.ts`
- `frontend/src/stores/authStore.ts`
- `frontend/src/router.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/App.tsx` (si guard global necessaire)
- `frontend/src/i18n/locales/fr.json`
- `frontend/src/i18n/locales/en.json`
- tests backend auth (dans arborescence tests existante)
- tests frontend auth (Vitest/RTL)

### Testing Requirements

- Couvrir au minimum les cas backend: login success, login failure, refresh success/failure, logout.
- Couvrir au minimum les cas frontend: soumission login, message erreur, redirection post-login, redirection si non-authentifie.
- Verifier format des erreurs API RFC 7807.
- Verifier accessibilite clavier du formulaire login.
- Executer lint/tests/build sur les zones modifiees et prevenir regressions.

### Previous Story Intelligence (1.3)

- Le socle frontend est deja en place (Vite, Router, i18n, stores, client Axios, layout/pages).
- `LoginPage`, `authStore` et `api/client.ts` existent deja et doivent etre etendus, pas recrees.
- Le theme Ocean Profond et la structure UI sont operationnels; conserver la coherence visuelle.
- La Story 1.3 a valide lint/tests/build frontend, servant de baseline pour non-regression.

### Git Intelligence Summary

- Le contexte projet precedent mentionne un commit de reference historique `ce4d77f` pour le socle backend.
- Prioriser les patterns deja presents dans le repository plutot que d'introduire une nouvelle architecture auth parallele.

### Latest Tech Information

- Cette execution ne dispose pas d'acces web direct.
- Les choix de versions et pratiques sont alignes sur les artefacts projet valides (epics, architecture, UX).
- En cas de divergence de versions, privilegier compatibilite avec decisions d'architecture existantes.

### Project Context Reference

- Aucun fichier `project-context.md` detecte dans le workspace.
- Contexte utilise: `epics.md`, `architecture.md`, `ux-design-specification.md`, `1-3-interface-utilisateur-de-base-et-theme-igar.md`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.4]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication Patterns]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Experience Principles]
- [Source: _bmad-output/implementation-artifacts/1-3-interface-utilisateur-de-base-et-theme-igar.md]

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- Workflow: `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- Engine: `_bmad/core/tasks/workflow.xml`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story auto-selected from first backlog item in sprint status: `1-4-authentification-jwt-et-interface-de-connexion`.
- Story status set to `ready-for-dev`.

### File List

- `_bmad-output/implementation-artifacts/1-4-authentification-jwt-et-interface-de-connexion.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
