# Story 2.2: Upload Resumable et Progression Temps Reel

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur (Fatima),
I want suivre la progression de l'upload en temps reel et que les uploads interrompus reprennent automatiquement,
so that je ne perds jamais de fichiers meme en cas de coupure reseau.

## Acceptance Criteria

1. Given un lot de fichiers en cours d'upload
   When l'upload est en cours
   Then le composant ImportProgressList affiche une barre de progression globale ("12/50 uploades") et une barre par fichier

2. And la progression est mise a jour en temps reel via WebSocket (Django Channels)

3. And si la connexion est interrompue, l'upload reprend automatiquement au point d'arret via le protocole tus (NFR28)

4. And un message "Connexion interrompue - reconnexion en cours..." s'affiche en banner persistant

5. And apres reconnexion, un toast confirme la reprise "Upload repris - aucun fichier perdu"

6. And les fichiers uploades sont stockes dans le bucket MinIO `igar-temp` (TTL 24h)

7. And l'utilisateur peut continuer a naviguer dans l'application pendant l'upload (non-bloquant)

## Tasks / Subtasks

- [x] Task 1: Etendre le modele d'etat import frontend pour la reprise et la progression globale (AC: 1, 3, 7)
  - [x] 1.1 Etendre `frontend/src/stores/captureStore.ts` avec etat de lot (totaux, progression globale, statut de connexion)
  - [x] 1.2 Ajouter la notion de resume/reconnecting dans les statuts fichier sans casser les statuts existants de Story 2.1
  - [x] 1.3 Garantir la persistance minimale de session d'upload pour supporter navigation non bloquante (route change sans perte d'etat)

- [x] Task 2: Implementer `ImportProgressList` et la banner de reconnexion (AC: 1, 4, 7)
  - [x] 2.1 Creer `frontend/src/components/capture/ImportProgressList.tsx` avec barre globale + barre par fichier
  - [x] 2.2 Afficher banner persistante de reconnexion quand le canal de progression est interrompu
  - [x] 2.3 Afficher toast de reprise a la reconnexion effective

- [x] Task 3: Integrer le canal WebSocket de progression (Django Channels) (AC: 2, 4, 5)
  - [x] 3.1 Implementer un hook `frontend/src/hooks/useUploadProgressSocket.ts` pour consommer les evenements `upload.progress`
  - [x] 3.2 Mapper les payloads WebSocket en snake_case vers le store capture
  - [x] 3.3 Gerer reconnexion exponentielle, dedup d'evenements et reprise d'etat apres reconnect

- [x] Task 4: Renforcer le client tus pour reprise automatique visible utilisateur (AC: 3, 5, 6)
  - [x] 4.1 Etendre `frontend/src/api/capture.ts` pour exposer callbacks de reprise/reconnexion explicites
  - [x] 4.2 Aligner retryDelays et comportement de reprise avec NFR28
  - [x] 4.3 Garantir compatibilite avec endpoint `/uploads/` (tusd) et metadonnees `storage_key` attendues backend

- [x] Task 5: Completer backend eventing et observabilite de progression (AC: 2, 6)
  - [x] 5.1 Introduire emission d'evenements de progression normalises `upload.progress` cote backend (channels layer)
  - [x] 5.2 Ajouter instrumentation/logs structures pour connexion WS, deconnexion, reprise, et publication d'evenements
  - [x] 5.3 Verifier que l'upload final reste persiste via hook `POST /api/v1/capture/tus-hook/` et bucket `igar-temp`

- [x] Task 6: Tests backend/frontend/E2E (AC: 1-7)
  - [x] 6.1 Frontend unit: tests `ImportProgressList` (progression globale/par fichier, banner reconnexion)
  - [x] 6.2 Frontend unit: tests hook socket (reconnexion, dedup, reprise)
  - [x] 6.3 Frontend unit: tests service tus (callbacks reprise, erreurs reseau)
  - [x] 6.4 Backend: tests emission event `upload.progress` et format payload
  - [x] 6.5 E2E: interruption reseau simulee pendant upload puis reprise sans perte + navigation non bloquante

## Dev Notes

### Story Foundation

- Epic: Epic 2 - Capture Intelligente et Classification IA
- Story key: 2-2-upload-resumable-et-progression-temps-reel
- Objectif business: fiabiliser le moment critique d'import massif avec feedback temps reel et resilience reseau
- Dependances: Story 2.1 terminee (socle upload tus + UI de base), prerequis pour Story 2.3+ (OCR/IA en pipeline)

### Developer Context (Most Critical)

- Ne pas reinventer le transport: conserver le flux tus existant (`tus-js-client` -> `/uploads/` -> `tusd` -> MinIO `igar-temp`).
- Ne pas introduire de polling REST pour la progression: l'architecture impose WebSocket via Django Channels pour `upload.progress`.
- Etendre les composants de Story 2.1 au lieu de recreer un nouvel ecran d'import.
- Le badge tab "Import en cours" est deja branche dans `AppLayout`; reutiliser ce pattern pour la progression globale.
- La reprise doit etre visible utilisateur (banner + toast) et non uniquement technique.

### Technical Requirements

- API / events en snake_case uniquement; convention evenement `<domaine>.<action>`.
- Progression temps reel via evenement `upload.progress` avec payload type:
  `{"document_id": "...", "progress": 0.65, "status": "uploading"}`.
- Respect NFR28: reprise automatique des uploads interrompus a la reconnexion, sans perte de donnees.
- Journalisation structuree obligatoire pour erreurs et transitions de connexion.
- Story scope: progression upload et reprise reseau uniquement (pas de logique OCR/IA metier ici).

### Architecture Compliance

- Garder separation des canaux:
  1. tus pour transfert binaire
  2. REST pour hook de finalisation/metadonnees
  3. WebSocket (Channels) pour progression temps reel
- Routing attendu conserve:
  - `/api/v1/` -> Django/DRF
  - `/ws/` -> Channels
  - `/uploads/` -> tusd
- Bucket temporaire: `igar-temp` (TTL 24h) avant transfert futur vers coffre fort (epics suivants).

### Library / Framework Requirements

- Frontend (deja present):
  - `react` ^18.3.1
  - `antd` ^6.3.4
  - `@tanstack/react-query` ^5.95.2
  - `zustand` ^5.0.12
  - `tus-js-client` ^4.3.1
- Backend (deja present):
  - `django` 4.2.x
  - `djangorestframework` 3.15.2
  - `channels` >= 4.1
  - `daphne` >= 4.1
  - `celery[redis]` >= 5.4

### File Structure Requirements

- Frontend (attendu):
  - `frontend/src/components/capture/ImportProgressList.tsx` (nouveau)
  - `frontend/src/hooks/useUploadProgressSocket.ts` (nouveau)
  - `frontend/src/pages/ImportPage.tsx` (extension)
  - `frontend/src/stores/captureStore.ts` (extension)
  - `frontend/src/api/capture.ts` (extension)
- Backend (attendu):
  - extension dans `backend/igar/apps/capture/` pour publication event WS
  - tests associes dans `backend/tests/`
- Infra: pas de redesign compose/nginx; reutiliser configuration actuelle.

### Testing Requirements

- Frontend unit (Vitest + RTL):
  - progression globale/par fichier et rendu non bloquant
  - etats reconnecting/resumed visibles (banner/toast)
  - hook WebSocket: reconnexion, dedup, robustesse payload
- Backend tests (pytest):
  - emission event `upload.progress`
  - format payload snake_case et non regression hook tus
- E2E (Playwright):
  - upload lot + coupure reseau simulee + reprise sans perte
  - navigation vers une autre page puis retour sans perte du suivi import

### Previous Story Intelligence

- Story 2.1 a deja pose:
  - UI import de base (`ImportPage`, `DropZoneOverlay`, `ImportTriggerButton`)
  - store Zustand `captureStore` (queued/uploading/uploaded/failed)
  - client tus (`startTusUpload`) avec retryDelays
  - endpoint hook backend `POST /api/v1/capture/tus-hook/` et persistence metadata
- A reutiliser tel quel et etendre incrementalement.
- Eviter de casser les tests existants 2.1 (unit + e2e import-flow).

### Git Intelligence Summary

- Historique local recent concentre sur Story 1-4 (auth frontend/backend), donc peu de guidance directe sur capture.
- Pattern commit utile conserve:
  - separation frontend/backend nette
  - tests associes par feature
  - nommage explicite des changements

### Latest Tech Information

- Versions verifiees dans le repo:
  - `tus-js-client` ^4.3.1
  - `@tanstack/react-query` ^5.95.2
  - `antd` ^6.3.4
  - `vitest` ^4.1.2
  - `@playwright/test` ^1.53.0
- Decision: rester sur les versions lockees du projet (pas d'upgrade opportuniste dans cette story).

### Project Context Reference

- Aucun fichier `project-context.md` detecte dans le workspace.
- Sources de contexte utilisees: `epics.md`, `architecture.md`, `prd.md`, `ux-design-specification.md`, story 2.1, code actuel frontend/backend.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.2)
- `_bmad-output/planning-artifacts/architecture.md` (API & Communication, Upload resumable, WebSocket events, file structure)
- `_bmad-output/planning-artifacts/prd.md` (FR5, FR6, NFR28)
- `_bmad-output/planning-artifacts/ux-design-specification.md` (Journey import en cours, feedback progression, reconnexion)
- `_bmad-output/implementation-artifacts/2-1-upload-de-documents-par-drag-and-drop-et-selecteur-de-fichiers.md`
- `frontend/src/pages/ImportPage.tsx`
- `frontend/src/stores/captureStore.ts`
- `frontend/src/api/capture.ts`
- `backend/igar/apps/capture/views.py`
- `backend/igar/apps/capture/services.py`

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- create-story execute depuis sprint-status (premiere story backlog detectee en ordre: 2-2-upload-resumable-et-progression-temps-reel)
- analyse artefacts effectuee: epics, architecture, prd, ux, story precedente 2.1, code actuel frontend/backend, git recent

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created
- Story 2.2 preparee pour implementation dev-story avec garde-fous architecture, scope clair, et plan de tests explicite
- Task 1 revisee et validee: progression globale corrigee (calcul par moyenne de progression), etat `resuming` durci
- Task 2 implementee et stabilisee: composant `ImportProgressList`, banner de reconnexion, toast de reprise, integration dans `ImportPage`
- Validation frontend ciblee executee: `captureStore.test.ts` (10/10) + `ImportProgressList.test.tsx` (10/10)
- Task 3 implementee: hook websocket `useUploadProgressSocket` avec reconnexion exponentielle, dedup par `event_id`, et mapping d'evenements vers le store
- Validation frontend ciblee executee: `useUploadProgressSocket.test.ts` (3/3) + non-regression capture (25/25 sur suites ciblees)
- Backend websocket prepare pour diffusion `upload.progress` (consumer dedie + route `/ws/uploads/progress/` + emission cote capture service)
- Task 4 implementee: callbacks explicites de reprise/reconnexion exposes par `startTusUpload`, retryDelays alignes NFR28, et metadata `storage_key` + `local_file_id`
- Integrations UI ajoutees dans `ImportPage`: passage `resuming` visible, bascule `isConnected/isReconnecting`, reprise marquee utilisateur
- Task 5 partiellement implementee: payload backend `upload.progress` normalise (incluant `document_id`) + logs structures sur publication et cycle WS
- Tests frontend executes et passants: `capture.test.ts`, `useUploadProgressSocket.test.ts`, `ImportProgressList.test.tsx`, `captureStore.test.ts` (27/27)
- Tests backend ajoutes (`tests/test_capture_services.py`) mais execution bloquee localement par dependance systeme manquante `libcairo` au boot Django
- Task 5 completee: couverture backend ajoutee sur cycle WS (connexion/deconnexion/forward) et verification persistence bucket `igar-temp`
- Validation backend executee et passante: `pytest tests/test_capture_hook.py tests/test_capture_services.py tests/test_capture_websocket.py -q` (8/8)
- Validation E2E executee et passante: `npm run e2e -- import-flow.spec.ts` (2/2), incluant interruption reseau simulee + reprise + navigation non bloquante

### File List

- `_bmad-output/implementation-artifacts/2-2-upload-resumable-et-progression-temps-reel.md`
- `frontend/src/stores/captureStore.ts`
- `frontend/src/stores/captureStore.test.ts`
- `frontend/src/components/capture/ImportProgressList.tsx`
- `frontend/src/components/capture/ImportProgressList.test.tsx`
- `frontend/src/pages/ImportPage.tsx`
- `frontend/src/hooks/useUploadProgressSocket.ts`
- `frontend/src/hooks/useUploadProgressSocket.test.ts`
- `frontend/src/api/capture.ts`
- `frontend/src/api/capture.test.ts`
- `backend/igar/core/websocket.py`
- `backend/igar/routing.py`
- `backend/igar/apps/capture/services.py`
- `backend/igar/settings/base.py`
- `backend/tests/test_capture_services.py`
- `backend/tests/test_capture_hook.py`
- `backend/tests/test_capture_websocket.py`
- `frontend/e2e/import-flow.spec.ts`
- `frontend/src/i18n/locales/fr.json`
- `frontend/src/i18n/locales/en.json`
