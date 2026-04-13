# Story 2.3: Pipeline OCR - Extraction de Texte

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur (Fatima),
I want que le systeme extraie automatiquement le texte des documents PDF et images via OCR,
so that le contenu devient recherchable et analysable par l'IA.

## Acceptance Criteria

1. Given un document PDF ou image uploade dans `igar-temp`
   When le pipeline de traitement est declenche
   Then un worker Celery (queue `ocr`) execute l'OCR via Tesseract 5

2. And le texte extrait est stocke en metadonnee associee au document

3. And le traitement OCR d'un document unitaire s'effectue en moins de 5 secondes (NFR7)

4. And la progression est envoyee via WebSocket (evenement `upload.progress`)

5. And les workers OCR s'executent dans des conteneurs isoles avec ressources limitees (NFR17)

6. And en cas d'echec OCR (document illisible, image trop basse resolution), le document est marque "OCR echoue" et continue dans le pipeline avec metadonnees vides

7. And les logs structures (structlog) tracent chaque traitement OCR avec document_uuid, duree, et statut

## Tasks / Subtasks

- [x] Task 1: Orchestrer le declenchement OCR depuis le flux capture (AC: 1, 4)
  - [x] 1.1 Etendre le traitement post-upload pour mapper l'objet capture vers un document/version traitable par OCR sans casser le flux Story 2.1/2.2
  - [x] 1.2 Enfiler explicitement le traitement OCR sur la queue `ocr` (reutiliser la queue Mayan existante)
  - [x] 1.3 Emmettre les evenements de progression `upload.progress` pour les etapes OCR (queued, processing, done, failed)

- [x] Task 2: Integrer Tesseract 5 via les composants OCR existants (AC: 1, 2, 3)
  - [x] 2.1 Reutiliser le backend OCR Mayan/Tesseract existant au lieu d'introduire une nouvelle librairie OCR
  - [x] 2.2 Garantir l'association du texte OCR extrait au document traite dans la structure de metadonnees cible
  - [x] 2.3 Instrumenter la duree de traitement par document (debut/fin) pour mesurer la cible NFR7

- [x] Task 3: Gestion d'erreurs OCR non bloquante (AC: 6, 7)
  - [x] 3.1 Capturer les erreurs OCR (langue manquante, image illisible, timeout) et marquer le document `ocr_failed`
  - [x] 3.2 Poursuivre le pipeline avec metadonnees OCR vides sans stopper le lot
  - [x] 3.3 Journaliser en structlog avec document_uuid, statut, duree_ms, cause_erreur

- [x] Task 4: Contrainte d'isolation et ressources workers (AC: 5)
  - [x] 4.1 Verifier/ajuster la definition des workers OCR dans l'infrastructure (limites CPU/MEM, isolation, restart policy)
  - [x] 4.2 Documenter les parametres de ressources retenus et leur justification vis-a-vis de NFR17

- [x] Task 5: Tests backend et integration (AC: 1-7)
  - [x] 5.1 Ajouter tests unitaires sur orchestration OCR: enfilement queue `ocr`, emission WS, mapping payload
  - [x] 5.2 Ajouter tests d'integration: OCR success/failure, persistance texte, statut `ocr_failed`, continuation pipeline
  - [x] 5.3 Ajouter tests de logs structures (champs obligatoires) et non-regression du hook capture

## Dev Notes

### Story Foundation

- Epic: Epic 2 - Capture Intelligente et Classification IA
- Story key: 2-3-pipeline-ocr-extraction-de-texte
- Objectif business: transformer les uploads en contenu textuel exploitable pour recherche et classification IA
- Dependances directes: Story 2.1 et Story 2.2 en review (socle upload, reprise, progression WS)

### Developer Context (Most Critical)

- Ne pas reinventer l'OCR: le fork Mayan contient deja la queue OCR, les tasks OCR et le backend Tesseract.
- Respecter la separation des canaux deja etablie:
  1. tus pour transfert binaire
  2. hook REST capture pour finalisation
  3. WebSocket pour progression utilisateur
- Le flux OCR doit etre non-bloquant pour l'UI et robuste aux erreurs documentaires.
- Ne pas introduire de nouvelle stack OCR (ex: service externe) sans besoin explicite.
- Le format evenement reste snake_case et conforme a `upload.progress`.

### Technical Requirements

- Queue OCR obligatoire: `ocr`.
- Backend OCR attendu: Tesseract 5 via backend Mayan existant.
- AC de robustesse: un echec OCR ne doit pas interrompre le lot complet.
- AC de performance: mesurer et tracer le temps de traitement pour verifier la cible < 5s/doc.
- Logs structures obligatoires: inclure au minimum document_uuid, statut, duree_ms, event_name, cause_erreur si echec.

### Architecture Compliance

- Reutiliser les composants OCR existants du fork:
  - `backend/mayan/apps/ocr/queues.py`
  - `backend/mayan/apps/ocr/tasks.py`
  - `backend/mayan/apps/ocr/managers.py`
  - `backend/mayan/apps/ocr/backends/tesseract.py`
- Routing/API conserve:
  - `/api/v1/` pour controle
  - `/ws/` pour progression
  - `/uploads/` pour transfert tus
- Continuer a stocker dans `igar-temp` avant les etapes d'archivage des epics suivants.

### Library / Framework Requirements

- Backend present et a reutiliser:
  - `channels` 4.3.2 (installe, latest detecte 4.3.2)
  - `celery` 5.4.0 (latest detecte 5.6.3, ne pas upgrader dans cette story)
  - OCR Mayan avec backend Tesseract (wrapper `sh.Command`)
- Frontend present et a conserver:
  - `react` 18.x
  - `antd` 6.x
  - `zustand` 5.x
- Decision: rester sur les versions lockees du projet; pas d'upgrade opportuniste dans cette story.

### File Structure Requirements

- Backend (extensions probables):
  - `backend/igar/apps/capture/services.py` (orchestration post-upload vers OCR)
  - `backend/igar/core/websocket.py` (si enrichissement events OCR)
  - `backend/tests/test_capture_services.py` (orchestration OCR)
  - `backend/tests/test_capture_websocket.py` (progress events OCR)
  - `backend/tests/test_capture_hook.py` (non-regression flux igar-temp)
- Fork OCR Mayan (a toucher seulement si necessaire):
  - `backend/mayan/apps/ocr/tasks.py`
  - `backend/mayan/apps/ocr/managers.py`
- Infrastructure:
  - verifier definitions workers OCR dans `infrastructure/docker-compose.yml` et/ou compose associes

### Testing Requirements

- Unit backend:
  - enfilement sur queue `ocr`
  - emission `upload.progress` pour etapes OCR
  - mapping du texte OCR vers metadonnees cible
- Integration backend:
  - scenario succes OCR (texte present)
  - scenario echec OCR (statut `ocr_failed`, metadonnees vides, pipeline continue)
  - validation logs structures
- Non-regression:
  - hook capture et persistence `igar-temp`
  - tests stories 2.1/2.2 deja en place

### Previous Story Intelligence

- Story 2.2 a stabilise:
  - progression WS `upload.progress`
  - gestion reconnexion/reprise
  - couverture backend capture/websocket et E2E import-flow
- Reutiliser les memes conventions d'evenements, de logs et de tests au lieu de creer un nouveau protocole.

### Git Intelligence Summary

- Historique local recent visible:
  - `36ede3e` feat(frontend): Extend auth state management and Axios interceptor (Story 1-4)
  - `58c9f06` feat(backend): Implement JWT authentication endpoints
- Insight: peu de commits recents sur OCR/capture; priorite a la coherence avec le code Story 2.1/2.2 deja present.

### Latest Tech Information

- Veille executee localement via pip index:
  - channels: installed 4.3.2, latest 4.3.2
  - celery: installed 5.4.0, latest 5.6.3
  - pytesseract: latest detecte 0.3.13 (non requis si backend OCR Mayan/Tesseract suffit)
- Decision implementation: s'appuyer sur la stack OCR Mayan/Tesseract deja integree au fork.

### Project Context Reference

- Aucun `project-context.md` detecte dans le workspace.
- Contextes utilises: epics, architecture, prd, ux spec, story 2.2, et modules OCR Mayan existants.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.3)
- `_bmad-output/planning-artifacts/architecture.md` (sections Intelligence & Classification, performance NFR, stack OCR)
- `_bmad-output/planning-artifacts/prd.md` (MVP capture/intelligence, FR7)
- `_bmad-output/planning-artifacts/ux-design-specification.md` (pipeline visible, feedback continu)
- `_bmad-output/implementation-artifacts/2-2-upload-resumable-et-progression-temps-reel.md`
- `backend/mayan/apps/ocr/queues.py`
- `backend/mayan/apps/ocr/tasks.py`
- `backend/mayan/apps/ocr/managers.py`
- `backend/mayan/apps/ocr/backends/tesseract.py`

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- create-story execute depuis sprint-status (premiere story backlog detectee en ordre: 2-3-pipeline-ocr-extraction-de-texte)
- analyse artefacts effectuee: epics, architecture, prd, ux, story precedente 2.2, modules OCR Mayan, git recent

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created
- Story 2.3 preparee pour implementation dev-story avec contraintes OCR explicites et garde-fous anti-regression
- Reuse path explicite defini: queue `ocr` + tasks OCR Mayan + WS `upload.progress`
- Risques majeurs adresses: echec OCR non bloquant, instrumentation performance, logs structures, isolation worker
- OCR capture implante: orchestration post-upload vers queue `ocr` + progression WS (`ocr_queued`, `ocr_processing`, `ocr_done`, `ocr_failed`)
- Champs OCR ajoutes au modele capture: `ocr_status`, `ocr_text`, `ocr_duration_ms`, `ocr_error`
- Tache Celery `task_capture_ocr_process` ajoutee avec backend OCR Mayan/Tesseract, gestion succes/echec et logs structures
- Limites ressources worker OCR ajoutees dans compose (`cpus`, `mem_limit`, `pids_limit`) pour NFR17
- Validation backend executee: `pytest tests/test_capture_hook.py tests/test_capture_services.py tests/test_capture_websocket.py tests/test_capture_tasks.py -q` (11/11)
- Remediation code-review (option 1) appliquee: validation stricte des chemins source OCR (allowlist de repertoires), sanitization des erreurs persistees, et limitation de la taille du texte OCR stocke
- Couverture de tests etendue sur ces garde-fous (chemin hors perimetre rejete, troncature OCR) et revalidation backend: `pytest tests/test_capture_hook.py tests/test_capture_services.py tests/test_capture_websocket.py tests/test_capture_tasks.py -q` (13/13)

### File List

- `_bmad-output/implementation-artifacts/2-3-pipeline-ocr-extraction-de-texte.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/igar/apps/capture/models.py`
- `backend/igar/apps/capture/services.py`
- `backend/igar/apps/capture/tasks.py`
- `backend/igar/apps/capture/migrations/0002_captureuploadrecord_ocr_fields.py`
- `backend/tests/test_capture_services.py`
- `backend/tests/test_capture_tasks.py`
- `infrastructure/docker-compose.yml`
