# Story 2.4: Classification IA et Extraction de Metadonnees

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur (Fatima),
I want que l'IA classifie automatiquement chaque document par type et pre-remplisse les metadonnees (date, montant, entites),
so that 90% de mes documents sont classes sans intervention manuelle.

## Acceptance Criteria

1. Given un document dont le texte a ete extrait par OCR
   When le worker IA (queue `ai`) traite le document
   Then le systeme classifie le document parmi les types configures : facture, contrat, courrier, deliberation, arrete, ordonnance, compte-rendu, bon de commande, bulletin de paie, document d'identite (FR8)

2. And le systeme extrait les metadonnees cles : date, montant, entites nommees, numero de reference (FR9)

3. And un score de confiance est attribue (0-100%)

4. And le resultat est envoye au frontend via WebSocket (evenement `classification.result` avec type, confidence, metadonnees)

5. And le document apparait dans l'ImportProgressList avec un ClassificationResult et un ConfidenceBadge

6. And les badges de confiance suivent les seuils : vert (>=85%), orange (50-84%), rouge (<50%)

7. And le traitement complet (OCR + IA) d'un document s'effectue en moins de 5 secondes (NFR7)

8. And en cas d'echec de classification, le document est marque "Non reconnu" avec badge rouge

## Tasks / Subtasks

- [ ] Task 1: Implementer le pipeline de classification sur la queue `ai` (AC: 1, 3, 7, 8)
  - [ ] 1.1 Brancher la suite de traitement apres OCR vers `intelligence.classify_document`
  - [ ] 1.2 Persister statut et details de classification (type, confidence, erreur)
  - [ ] 1.3 Garantir un echec non bloquant (etat "non_reconnu" + continuation du lot)

- [ ] Task 2: Extraire et normaliser les metadonnees (AC: 2, 7)
  - [ ] 2.1 Implementer `intelligence.extract_metadata` avec schema stable (date, montant, entites, reference)
  - [ ] 2.2 Ajouter normalisation/validation des champs (formats date, numeriques montant)
  - [ ] 2.3 Instrumenter durees et seuils pour verification NFR7

- [ ] Task 3: Exposer les resultats en temps reel au frontend (AC: 4, 5, 6)
  - [ ] 3.1 Publier l'evenement WebSocket `classification.result` en snake_case
  - [ ] 3.2 Integrer les payloads dans ImportProgressList et ClassificationResult
  - [ ] 3.3 Implementer ConfidenceBadge conforme aux seuils vert/orange/rouge et labels lisibles

- [ ] Task 4: Garantir UX et accessibilite des etats de confiance (AC: 5, 6)
  - [ ] 4.1 Assurer affichage couleur + icone + texte (pas couleur seule)
  - [ ] 4.2 Maintenir interactions "1 clic" pour correction moyenne confiance (prepare story 2.5)
  - [ ] 4.3 Ajouter `aria-live="polite"` sur zones dynamiques de progression/resultat

- [ ] Task 5: Couvrir par tests unitaires/integration/E2E (AC: 1-8)
  - [ ] 5.1 Tests backend: succes/echec classification, extraction metadata, statut non_reconnu
  - [ ] 5.2 Tests websocket: emission et format de `classification.result`
  - [ ] 5.3 Tests frontend: mapping seuils badges, rendu ClassificationResult, etats accesibles
  - [ ] 5.4 Test E2E parcours Fatima (upload -> OCR -> IA -> badges -> resume)

## Dev Notes

### Story Foundation

- Epic: Epic 2 - Capture Intelligente et Classification IA
- Story key: 2-4-classification-ia-et-extraction-de-metadonnees
- Objectif business: realiser le "moment wow" de classement automatique avec confiance visuelle et pre-remplissage metadata
- FR couverts: FR8, FR9
- NFR impactes: NFR7 (OCR + IA < 5s/doc), NFR31/NFR33/NFR34 (UX accessible)

### Developer Context (Most Critical)

- Ne pas reinventer le pipeline: reutiliser la chaine existante upload tus -> OCR queue `ocr` -> IA queue `ai` -> UI WebSocket.
- Ne pas changer les conventions de communication: evenements `<domaine>.<action>`, payload JSON snake_case, structures coherentes backend/frontend.
- Reutiliser les composants UX imposes: `ImportProgressList`, `ClassificationResult`, `ConfidenceBadge`.
- Garder la frontiere de scope: story 2.4 couvre classification + extraction + affichage confiance; la validation/correction utilisateur approfondie est en story 2.5.
- En cas d'incertitude modele, prioriser robustesse produit: resultat "non_reconnu" explicite plutot qu'une fausse classification silencieuse.

### Technical Requirements

- Celery tasks cibles:
  - `intelligence.classify_document` sur queue `ai`
  - `intelligence.extract_metadata` sur queue `ai`
- WebSocket event obligatoire:
  - `classification.result` payload attendu: `{"document_id": "...", "type": "facture", "confidence": 0.97, "metadata": {...}}`
- Seuils de confiance obligatoires:
  - Haute: >= 85
  - Moyenne: 50-84
  - Basse: < 50
- Champs metadata minimaux: `date`, `montant`, `entites`, `numero_reference`
- Etat d'echec: classification non reconnue + badge rouge + flux non bloquant

### Architecture Compliance

- Structure backend cible:
  - `backend/igar/apps/intelligence/models.py`
  - `backend/igar/apps/intelligence/services.py`
  - `backend/igar/apps/intelligence/tasks.py`
  - `backend/igar/apps/capture/services.py` (orchestration pipeline)
- Structure frontend cible:
  - `frontend/src/components/documents/ClassificationResult.tsx`
  - `frontend/src/components/documents/ConfidenceBadge.tsx`
  - `frontend/src/components/capture/ImportProgressList.tsx`
  - `frontend/src/hooks/useWebSocket.ts`
- Regles de nommage:
  - snake_case uniforme DB/API/WebSocket/Celery
  - taches Celery format `<app_django>.<verbe_action>`

### Library / Framework Requirements

- Backend verrouille par architecture:
  - Django 5.2 + DRF + Celery + Redis + PostgreSQL + Elasticsearch
  - Channels 4.3.2 (installed=latest detecte)
  - Celery 5.4.0 installe (latest detecte 5.6.3; pas d'upgrade opportuniste dans cette story)
- Frontend verrouille par architecture:
  - React 18 + Ant Design 6 + TanStack Query
  - npm latest observes: antd 6.3.5, @tanstack/react-query 5.99.0
- Decision: rester sur les versions lockees du projet, sans migration transversale dans cette story.

### File Structure Requirements

- Ajouter/modifier uniquement les zones attendues (pas de derive structurelle hors architecture)
- Privilegier extension des modules existants sur creation de nouvelles apps
- Respecter monorepo: `backend/`, `frontend/`, `infrastructure/`

### Testing Requirements

- Backend unit:
  - classification valide retourne type + confidence + metadata
  - extraction metadata normalisee
  - fallback `non_reconnu` et pipeline non interrompu
- Backend integration:
  - enchainement OCR termine -> AI queue -> websocket result
  - objectifs de temps mesurables pour NFR7 (instrumentation + assertions pragmatiques)
- Frontend unit/component:
  - mapping des seuils de confiance en badges vert/orange/rouge
  - rendu des etats `auto-validated`, `needs-review`, `manual-required`
  - accessibilite: texte + icone + aria labels
- E2E:
  - parcours import Fatima avec reception de `classification.result` et compteur resume mis a jour

### Previous Story Intelligence

- Story 2.3 a etabli les fondations a ne pas casser:
  - OCR sur queue `ocr` via backend Mayan/Tesseract
  - progression WS coherente pendant pipeline
  - gestion erreur OCR non bloquante
  - logs structures et garde-fous de securite sur chemins/tailles
- Reprise obligatoire pour 2.4:
  - conserver style d'instrumentation, structure des tests capture, et conventions d'evenements
  - brancher la classification APRES succes/echec OCR sans bloquer les lots

### Git Intelligence Summary

- Derniers commits pertinents:
  - `2ca73968e90` chore(bmad): synchroniser artefacts stories 1.5-1.6 et 2.1-2.3 + statut sprint
  - `9606df9298d` feat(frontend): livrer stories BMAD 1.5, 1.6, 2.1-2.2 (2FA, admin RBAC, import resumable)
  - `36ede3ed7e6` feat(frontend): Extend auth state management and Axios interceptor (Story 1-4)
  - `58c9f066da0` feat(backend): Implement JWT authentication endpoints
- Insight: la base frontend import/realtime est recente; 2.4 doit etendre sans rupture des patterns etablis.

### Latest Tech Information

- Verification locale effectuee:
  - `channels`: installed 4.3.2, latest 4.3.2
  - `celery`: installed 5.4.0, latest 5.6.3
  - `@tanstack/react-query`: latest 5.99.0
  - `antd`: latest 6.3.5
- Strategie story:
  - ne pas migrer de versions ici
  - appliquer les bonnes pratiques des versions lockees et documenter tout ecart

### Project Context Reference

- Aucun fichier `project-context.md` detecte dans le workspace.
- Sources utilisees: epics, architecture, prd, ux spec, story precedente 2.3, historique git recent.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.4, Story 2.5)
- `_bmad-output/planning-artifacts/architecture.md` (communication patterns, Celery queues, structures monorepo)
- `_bmad-output/planning-artifacts/prd.md` (FR8, FR9, objectifs precision)
- `_bmad-output/planning-artifacts/ux-design-specification.md` (journey Fatima, badges confiance, composants critiques)
- `_bmad-output/implementation-artifacts/2-3-pipeline-ocr-extraction-de-texte.md`

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- create-story execute depuis sprint-status (premiere story backlog detectee en ordre: 2-4-classification-ia-et-extraction-de-metadonnees)
- analyse effectuee sur epics, architecture, prd, ux spec, story precedente 2.3, et historique git recent
- veille versions backend/frontend effectuee localement (pip index + npm view)

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created
- Story 2.4 preparee avec garde-fous anti-regression et conventions d'architecture explicites
- Conventions critiques verrouillees: queue `ai`, websocket `classification.result`, payload snake_case
- Exigences UX/accessibilite detaillees pour ConfidenceBadge et ClassificationResult
- Story status definie a `ready-for-dev`

### File List

- `_bmad-output/implementation-artifacts/2-4-classification-ia-et-extraction-de-metadonnees.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
