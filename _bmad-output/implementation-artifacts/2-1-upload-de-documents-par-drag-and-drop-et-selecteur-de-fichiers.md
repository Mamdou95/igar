# Story 2.1: Upload de Documents par Drag and Drop et Selecteur de Fichiers

Status: review

## Story

As a utilisateur (Fatima),
I want deposer des documents par glisser-deposer (jusqu'a 500 fichiers) ou via un selecteur de fichiers/dossiers sur l'interface,
so that je peux importer rapidement tous mes documents sans friction.

## Acceptance Criteria

1. Given un utilisateur authentifie sur la vue Documents
   When il glisse des fichiers sur la fenetre
   Then le composant DropZoneOverlay apparait en plein ecran (fond semi-transparent, icone animee, texte "Deposez vos documents ici")

2. And au relachement, les fichiers sont acceptes en moins de 5 secondes pour un lot de 50 (NFR4)

3. And l'upload demarre via le protocole tus (resumable)

4. And le tab "Import en cours" s'active avec un badge compteur

5. And un bouton "Importer" est disponible en alternative pour le clavier/accessibilite

6. And le selecteur de fichiers accepte fichiers individuels et dossiers complets

7. And les formats acceptes incluent: PDF, Office (docx/xlsx/pptx), images (jpg/png/tiff), emails (.eml/.msg), audio, video, ZIP

8. And l'overlay disparait avec fade-out si l'utilisateur sort de la zone sans deposer

9. And l'overlay est accessible: le bouton "Importer" est toujours focusable au clavier

## Tasks / Subtasks

- [x] Task 1: Mettre en place le socle backend capture tus (AC: 2, 3, 6, 7)
  - [x] 1.1 Creer les routes capture dans `backend/igar/apps/capture/urls.py` et les brancher dans `backend/igar/urls.py` (actuellement commentees)
  - [x] 1.2 Creer endpoint `POST /api/v1/capture/tus-hook/` pour l'evenement `post-finish` de tusd
  - [x] 1.3 Valider et persister les metadonnees de fichier minimales (nom, taille, mime, upload_id, storage_key)
  - [x] 1.4 Retourner des erreurs RFC 7807 coherentes avec le gestionnaire existant (`igar/core/exception_handler.py`)
  - [x] 1.5 Ajouter controles anti-abus (taille max, type mime, quota par requete) sans casser l'acceptation des 500 fichiers

- [x] Task 2: Integrer le flux tusd -> MinIO igar-temp (AC: 2, 3, 7)
  - [x] 2.1 Garantir la compatibilite avec la config infra existante (`infrastructure/docker-compose.yml`, service `tusd`)
  - [x] 2.2 Documenter le contrat de hook attendu par tusd (`post-finish`) et la transformation vers le modele applicatif
  - [x] 2.3 Ajouter verification de coherence entre metadata hook et objet S3 (`igar-temp`)
  - [x] 2.4 Journaliser les echecs de hook avec contexte exploitable (upload_id, cause, retry)

- [x] Task 3: Construire l'experience frontend Import (AC: 1, 4, 5, 6, 8, 9)
  - [x] 3.1 Remplacer le placeholder actuel de `frontend/src/pages/ImportPage.tsx` par une page fonctionnelle
  - [x] 3.2 Creer `frontend/src/components/capture/DropZoneOverlay.tsx` (fade-in/fade-out, etats drag-enter/over/leave/drop)
  - [x] 3.3 Creer `frontend/src/components/capture/ImportTriggerButton.tsx` avec input fichier/dossier (keyboard-first)
  - [x] 3.4 Ajouter le store UI de session d'import (compteurs, etat overlay, lot courant) via Zustand
  - [x] 3.5 Brancher l'activation du badge "Import en cours" dans la navigation existante (ProLayout)

- [x] Task 4: Integrer le client tus cote frontend (AC: 2, 3, 6, 7)
  - [x] 4.1 Ajouter la dependance `tus-js-client` et un service dedie `frontend/src/api/capture.ts`
  - [x] 4.2 Implementer upload par fichier avec reprise automatique et strategie de retry
  - [x] 4.3 Supporter multi-selection et dossiers (si browser compatible) avec degradation propre
  - [x] 4.4 Mapper erreurs reseau/validation vers feedback utilisateur clair (toast + details)

- [x] Task 5: Accessibilite, UX et i18n (AC: 1, 5, 8, 9)
  - [x] 5.1 Conserver focus clavier sur bouton "Importer" pendant l'affichage overlay
  - [x] 5.2 Ajouter labels ARIA et annonces `aria-live` pour progression/etat import
  - [x] 5.3 Ajouter les cles i18n FR/EN pour textes d'overlay/import (`frontend/src/i18n/locales/*.json`)
  - [x] 5.4 Respecter design tokens/theme existants (Ocean Profond, densite compacte)

- [x] Task 6: Observabilite et robustesse (AC: 2, 3, 4)
  - [x] 6.1 Ajouter logs structures backend pour hooks tus et validation capture
  - [x] 6.2 Ajouter metriques minimales (imports recus, imports en echec, latence hook)
  - [x] 6.3 Gerer proprement les cas limites (fichier vide, metadata absente, mime inconnu)

- [x] Task 7: Tests backend/frontend/E2E (AC: 1-9)
  - [x] 7.1 Backend: tests API capture hook (happy path, payload invalide, type non supporte, erreur stockage)
  - [x] 7.2 Backend: tests contrat RFC 7807 pour erreurs capture
  - [x] 7.3 Frontend unit: tests `DropZoneOverlay` (affichage/fermeture/keyboard)
  - [x] 7.4 Frontend unit: tests service tus (retry, resume metadata, callbacks progression)
  - [x] 7.5 E2E: drag and drop lot 50 fichiers, bouton Import alternatif, verification badge tab

## Dev Notes

### Story Foundation

- Epic: Epic 2 - Capture Intelligente et Classification IA
- Story key: 2-1-upload-de-documents-par-drag-and-drop-et-selecteur-de-fichiers
- Objectif business: creer l'entree utilisateur principale du pipeline IA (magic moment de capture)
- Dependances aval: Story 2.2 (progression temps reel + reprise visible), Story 2.3 (OCR), Story 2.4 (classification)

### Developer Context (Most Critical)

- Ne pas reinventer le flux upload en utilisant des endpoints custom de transfert binaire: l'architecture cible impose tus + tusd + MinIO `igar-temp`.
- Etendre l'existant plutot que creer un nouveau layout/import route: la route frontend `/import` existe deja.
- Ne pas casser l'admin/auth deja en place (`/api/v1/auth/*`, `/api/v1/admin/*`).
- Le backend capture est le bon point d'extension: `backend/igar/apps/capture/` existe mais est vide (urls non branchees).
- Le proxy Nginx et tusd sont deja preconfigures (`/uploads/` -> `tusd:8080`) et doivent etre reutilises.

### Technical Requirements

- API versioning obligatoire: conserver `/api/v1/`.
- Format erreur obligatoire: RFC 7807 (Problem Details) via le handler central.
- Validation stricte des payloads de hook (event type, object key, metadata).
- Structure de nommage: snake_case uniforme backend/API/events.
- Journalisation JSON structuree pour tous les evenements capture critiques.

### Architecture Compliance

- Flux impose:
  1. Frontend `tus-js-client` envoie vers `/uploads/`.
  2. tusd ecrit dans MinIO bucket `igar-temp`.
  3. tusd appelle hook `POST /api/v1/capture/tus-hook/` (post-finish).
  4. Backend enregistre l'etat initial de document ingere.
- Ne pas introduire de websocket custom pour cette story si pas necessaire: la progression temps reel detaillee est couverte par Story 2.2.
- Respecter la separation des canaux: tus pour transfert, REST pour controle/metadonnees, WS pour events (plus tard).

### Library / Framework Requirements

- Frontend requis:
  - `tus-js-client` (latest npm observe: 4.3.1)
  - Stack existante a conserver: React 18, Ant Design 6, TanStack Query 5, Zustand
- Backend requis:
  - DRF + Django existants
  - Channels deja present dans requirements (pour stories suivantes)
- Infra:
  - Service `tusd` existant, image `tusproject/tusd:latest` (multi-arch detectee)

### File Structure Requirements

- Backend (extensions attendues):
  - `backend/igar/apps/capture/urls.py`
  - `backend/igar/apps/capture/views.py` (a creer)
  - `backend/igar/apps/capture/serializers.py` (a creer)
  - `backend/igar/apps/capture/services.py` (a creer)
  - `backend/igar/urls.py` (decommenter/ajouter include capture)
- Frontend (extensions attendues):
  - `frontend/src/pages/ImportPage.tsx` (remplacer placeholder)
  - `frontend/src/components/capture/DropZoneOverlay.tsx` (a creer)
  - `frontend/src/components/capture/ImportTriggerButton.tsx` (a creer)
  - `frontend/src/api/capture.ts` (a creer)
  - `frontend/src/stores/` (etat import)
- Infra (pas de redesign):
  - reutiliser `infrastructure/nginx/conf.d/igar.dev.conf`
  - reutiliser `infrastructure/docker-compose.yml`

### Testing Requirements

- Backend:
  - tests DRF sur endpoint hook tus (200/400/409/422)
  - tests de resilience payloads incomplets/invalides
  - tests de non-regression auth/admin routes
- Frontend:
  - Vitest + RTL pour comportements drag/drop et focus clavier
  - tests de service tus (reprise/retry)
- E2E:
  - scenario import lot 50 fichiers en < 5s (acceptation)
  - scenario acces clavier sans drag
- Accessibilite:
  - verification `aria-live`, focus visible, navigation clavier sans piege

### Latest Tech Information

- Veille npm effectuee:
  - `tus-js-client`: 4.3.1
  - `@tanstack/react-query`: 5.99.0
  - `antd`: 6.3.5
- Veille PyPI non concluante dans cet environnement (erreur SSL locale), donc conserver les versions compatibles du repo pour eviter une derive non verifiee.

### Project Context Reference

- Aucun fichier `project-context.md` detecte dans le workspace.
- Sources utilisees: epics, architecture, PRD, UX specification, etat reel du code (frontend/backend/infrastructure).

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.1)
- `_bmad-output/planning-artifacts/architecture.md` (sections upload resumable, API patterns, file structure)
- `_bmad-output/planning-artifacts/prd.md` (FR1, FR2, NFR4, NFR28)
- `_bmad-output/planning-artifacts/ux-design-specification.md` (DropZoneOverlay, Import flow, keyboard/accessibility)
- `frontend/src/pages/ImportPage.tsx`
- `frontend/src/router.tsx`
- `backend/igar/apps/capture/urls.py`
- `backend/igar/urls.py`
- `infrastructure/nginx/conf.d/igar.dev.conf`
- `infrastructure/docker-compose.yml`

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- Workflow create-story execute en mode automatise (sans interruption interactive)
- Dev-story: implementation capture backend + import frontend + tests unitaires cibles

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created
- Story target auto-detectee depuis sprint-status: `2-1-upload-de-documents-par-drag-and-drop-et-selecteur-de-fichiers`
- Story preparee pour execution dev-story
- Hook tus `POST /api/v1/capture/tus-hook/` implemente avec validation payload + persistence metadata + erreurs RFC7807
- App capture activee dans settings et routes API branchees (`/api/v1/capture/`)
- Experience Import frontend implementee: overlay drag/drop, bouton Importer clavier, progression par fichier, badge compteur tab Import
- Dependance `tus-js-client` ajoutee et service `startTusUpload()` implemente avec retry/resume
- Tests passes: backend `tests/test_capture_hook.py` + frontend `DropZoneOverlay.test.tsx`/`capture.test.ts` + build frontend
- Regression backend ciblee passee: `tests/test_capture_hook.py tests/test_admin_endpoints.py tests/test_auth_api.py`
- E2E Playwright ajoute et passant (`frontend/e2e/import-flow.spec.ts`) couvrant bouton clavier Importer, drag-and-drop lot 50 et verification du badge import

### File List

- `_bmad-output/implementation-artifacts/2-1-upload-de-documents-par-drag-and-drop-et-selecteur-de-fichiers.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/igar/settings/base.py`
- `backend/igar/urls.py`
- `backend/igar/core/exceptions.py`
- `backend/igar/apps/capture/models.py`
- `backend/igar/apps/capture/serializers.py`
- `backend/igar/apps/capture/services.py`
- `backend/igar/apps/capture/views.py`
- `backend/igar/apps/capture/urls.py`
- `backend/igar/apps/capture/migrations/__init__.py`
- `backend/igar/apps/capture/migrations/0001_initial.py`
- `backend/tests/test_capture_hook.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/pages/ImportPage.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/stores/captureStore.ts`
- `frontend/src/components/capture/DropZoneOverlay.tsx`
- `frontend/src/components/capture/ImportTriggerButton.tsx`
- `frontend/src/components/capture/capture.css`
- `frontend/src/components/capture/DropZoneOverlay.test.tsx`
- `frontend/src/api/capture.ts`
- `frontend/src/api/capture.test.ts`
- `frontend/src/i18n/locales/fr.json`
- `frontend/src/i18n/locales/en.json`
- `frontend/playwright.config.ts`
- `frontend/e2e/import-flow.spec.ts`
- `frontend/src/pages/E2EImportHarnessPage.tsx`
- `frontend/src/router.tsx`
