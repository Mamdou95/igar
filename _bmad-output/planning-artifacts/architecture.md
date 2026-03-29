---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/prd-validation-report.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2026-03-17'
project_name: 'Igar'
user_name: 'Masy'
date: '2026-03-17'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

57 FRs organisés en 8 domaines fonctionnels :

| Domaine | FRs | Implications architecturales |
| --- | --- | --- |
| Capture & Ingestion | FR1-FR6 | Pipeline d'ingestion multi-canal (drag & drop, IMAP, API REST), upload résilient, stockage temporaire |
| Intelligence & Classification | FR7-FR11 | Workers OCR/IA asynchrones, modèles de classification, extraction de métadonnées, feedback utilisateur |
| Visualisation & Consultation | FR12-FR19 | Visualiseur universel multi-format, rendu filigrane côté serveur, streaming audio/vidéo |
| Archivage & Immuabilité (SAE) | FR20-FR28 | Coffre-fort WORM (MinIO Object Lock), chiffrement SSE-C par document, empreintes SHA-256, certificats de scellement, vérification d'intégrité périodique |
| Recherche & Découverte | FR29-FR33 | Moteur full-text (Elasticsearch), indexation contenu OCR, surlignage contextuel, filtres combinés |
| Cycle de Vie & Conformité | FR34-FR40 | Automate de conservation, notifications proactives, double validation destruction, certificats de destruction, suppression logique RGPD |
| Gestion Utilisateurs & Sécurité | FR41-FR46 | RBAC, 2FA obligatoire, audit trail immuable, cloisonnement documentaire strict |
| API & Intégration | FR52-FR57 | API REST documentée OpenAPI 3.0, opérations CRUD + intégrité + certificats |

**Non-Functional Requirements:**

50 NFRs répartis en 8 catégories structurantes :

| Catégorie | NFRs | Contrainte architecturale dominante |
| --- | --- | --- |
| Performance | NFR1-NFR9 | FCP < 1,5s, recherche < 2s sur 100K docs, OCR < 5s/doc, surcoût SSE-C < 5% |
| Sécurité | NFR10-NFR20 | AES-256 SSE-C, TLS 1.3, séparation clés/données, 2FA, JWT 15min, CSP A+, workers sandboxés |
| Scalabilité | NFR21-NFR25 | 100 → 500 utilisateurs simultanés, 100K → 1M documents, scaling horizontal workers |
| Fiabilité | NFR26-NFR30 | 99,5% → 99,9% dispo, zéro perte de données, reprise upload, détection corruption < 24h |
| Accessibilité | NFR31-NFR35 | WCAG 2.1 AA, navigation clavier, lecteurs d'écran, contraste 4.5:1 |
| Intégration | NFR36-NFR40 | API REST RESTful, OpenAPI 3.0, réponse < 500ms, IMAP polling ≤ 5min |
| Maintenabilité | NFR41-NFR45 | Déploiement < 30min, MAJ < 15min downtime, logs JSON, healthcheck |
| Conformité | NFR46-NFR50 | NF Z42-013, RGPD, audit trail immuable signé, certificats de destruction scellés |

**Scale & Complexity:**

- Domaine primaire : Full-stack distribué (Backend Python/Django + Frontend React SPA + Infrastructure conteneurisée)
- Niveau de complexité : **Élevé / Enterprise**
- Composants architecturaux estimés : **10-12** (Frontend SPA, API Gateway/Django, Workers OCR, Workers IA, MinIO, PostgreSQL, Elasticsearch, Redis, Django Channels, Reverse Proxy, Système de licences, Service de filigrane)

### Technical Constraints & Dependencies

| Contrainte | Source | Impact architectural |
| --- | --- | --- |
| Fork Mayan EDMS (Python/Django) | PRD — décision technique | Architecture backend contrainte par l'architecture Mayan (Django ORM, DRF, Celery) |
| MinIO + Object Lock | PRD — immuabilité WORM | Couche d'abstraction S3 obligatoire, configuration Object Lock Compliance/Governance |
| SSE-C AES-256 | PRD — chiffrement par document | Gestion des clés dans PostgreSQL TDE, headers SSE-C à chaque requête S3 |
| React + Ant Design + Pro Components | UX Spec — choix frontend | SPA découplée, communication REST, WebSocket pour temps réel |
| Docker Compose / Kubernetes | PRD — déploiement | Architecture microservices conteneurisée, orchestration des dépendances |
| Cython + PyArmor | PRD — protection code | Build pipeline spécifique, contraintes de distribution, tests en mode protégé |
| On-premise / Hybride | PRD — modèle de déploiement | Pas de dépendance cloud obligatoire, installation locale, système de licences hardware-bound |

### Cross-Cutting Concerns Identified

| Préoccupation | Composants impactés | Stratégie architecturale requise |
| --- | --- | --- |
| **Sécurité & Chiffrement** | Tous (API, stockage, DB, frontend, workers) | Politique de sécurité unifiée, séparation des responsabilités, defense in depth |
| **Conformité NF Z42-013** | Stockage, cycle de vie, audit, destruction | Garanties d'intégrité à chaque couche, journalisation exhaustive, certificats |
| **Audit Trail Immuable** | API, stockage, auth, conformité | Journalisation centralisée signée cryptographiquement, chaîne de confiance |
| **Temps Réel (WebSocket)** | Frontend, Django Channels, workers, notifications | Canal bidirectionnel pour progression, notifications, statuts |
| **Multi-Format** | Visualiseur, OCR, indexation, stockage | Abstraction de format, conversion pérenne (PDF/A, TIFF), pipelines par type |
| **Scalabilité Horizontale** | Workers OCR/IA, Elasticsearch, MinIO | Découplage via file de messages (Celery/Redis), stateless workers |
| **RGPD vs WORM** | Stockage, métadonnées, conformité | Suppression logique avec masquage des données personnelles, conservation enveloppe |
| **Filigrane Dynamique** | Visualiseur, service de rendu serveur | Rendu côté serveur pour empêcher la désactivation client |

## Starter Template Evaluation

### Primary Technology Domain

**Full-stack distribué** avec deux fondations séparées :
- Backend : Fork Mayan EDMS 4.11 (Python/Django 5.2)
- Frontend : SPA React découplée consommant l'API REST Django

### Starter Options Considered

**Backend :**

| Option | Verdict | Raison |
| --- | --- | --- |
| Fork Mayan EDMS 4.11 | **Retenu** | Réutilise OCR, Elasticsearch, Celery, RBAC, API REST. Accélère le MVP de plusieurs mois |
| Django from scratch | Rejeté | Reconstruire ce que Mayan offre gratuitement (OCR distribué, search, DRF) serait un gaspillage |
| FastAPI | Rejeté | Pas d'écosystème GED existant, perte de l'avantage Mayan |

**Frontend :**

| Option | Verdict | Raison |
| --- | --- | --- |
| create-vite react-swc-ts + Ant Design v6 | **Retenu** | Template officiel, versions à jour, configuration maîtrisée |
| Ant Design Pro (UmiJS) | Rejeté | UmiJS ajoute une couche opaque, conventions imposées, moins flexible que Vite |
| Starters communautaires GitHub | Rejeté | Versions obsolètes, maintenance incertaine |

### Selected Starters

#### Backend : Fork Mayan EDMS 4.11

**Rationale :** Mayan EDMS 4.11 (Django 5.2) fournit 60-70% de l'infrastructure GED nécessaire (OCR, recherche, RBAC, API, workflows). Le fork permet de réutiliser cette base tout en construisant les modules SAE/WORM, IA avancée, et sécurité renforcée spécifiques à Igar.

**Initialization Command:**

```bash
git clone https://gitlab.com/mayan-edms/mayan-edms.git igar-backend
cd igar-backend
git checkout v4.11
git remote rename origin mayan-upstream
git remote add origin <igar-repo-url>
```

**Architectural Decisions Provided by Mayan:**

- **Language & Runtime:** Python 3.12+ / Django 5.2
- **API:** Django REST Framework (DRF) avec serializers, viewsets, permissions
- **Task Queue:** Celery + Redis (workers OCR distribués)
- **Search:** Elasticsearch intégré avec indexation full-text
- **OCR:** Tesseract 5 via workers Celery
- **Database:** PostgreSQL (ORM Django)
- **Auth:** RBAC natif (rôles, permissions, groupes)
- **Containerization:** Docker Compose avec services orchestrés

**Testing Backend:**

- **pytest** + **pytest-django** — Tests unitaires et d'intégration
- **Factory Boy** — Factories pour les modèles Django
- **pytest-xdist** — Exécution parallèle
- **Coverage.py** — Mesure de couverture de code

#### Frontend : Vite 8 + React + TypeScript + Ant Design v6

**Rationale :** Le template officiel `create-vite` avec React SWC TypeScript garantit des versions à jour et une configuration maîtrisée. Ant Design v6 + Pro Components couvrent ~70% des besoins UI (ProTable, ProLayout, ProForm). Zustand + TanStack Query est le standard 2026 pour le state management.

**Initialization Command:**

```bash
npm create vite@latest igar-frontend -- --template react-swc-ts
cd igar-frontend
npm install antd @ant-design/pro-components @ant-design/icons
npm install @tanstack/react-query zustand react-router-dom
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom playwright @playwright/test eslint-plugin-jsx-a11y
```

**Architectural Decisions:**

**Language & Runtime:**
- TypeScript 5.x strict mode
- React 18+ (compatible Ant Design v6)
- SWC pour la transpilation (plus rapide que Babel)

**UI Framework:**
- Ant Design v6 + Pro Components (ProTable, ProLayout, ProForm, ProDescriptions)
- Design Tokens via ConfigProvider pour le thème "Océan Profond"
- Composants custom wrappés (ConfidenceBadge, DocumentViewer, SealBadge, etc.)

**State Management:**
- **TanStack Query v5** — Server state (données API : documents, recherche, métadonnées, dashboard)
- **Zustand** — Client state (UI : sidebar, auth, préférences, filtres actifs)
- **Ant Design Form** — Form state (ProForm gère nativement l'état des formulaires)
- **React Router v6** — URL state (filtres recherche, pagination, onglet actif)

**Build Tooling:**
- Vite 8 avec Rolldown (builds 10-30x plus rapides)
- Tree-shaking optimal pour réduire le bundle Ant Design
- Path aliases TypeScript natifs (tsconfig paths)

**Testing Frontend:**
- **Vitest** + **React Testing Library** — Tests unitaires composants
- **Playwright** — Tests E2E des 5 journeys utilisateur critiques
- **axe-core** / **jest-axe** — Tests accessibilité automatisés (WCAG 2.1 AA)
- **Lighthouse CI** — Audit performance + accessibilité en CI
- **eslint-plugin-jsx-a11y** — Lint accessibilité dans le code JSX

**Code Organization:**
```
igar-frontend/
├── src/
│   ├── api/           # TanStack Query hooks + API client
│   ├── components/    # Composants custom Igar (wrappés Ant Design)
│   ├── layouts/       # ProLayout configuration
│   ├── pages/         # Vues par route (Documents, Import, Conformité, Admin)
│   ├── stores/        # Zustand stores (auth, ui, preferences)
│   ├── hooks/         # Custom React hooks
│   ├── utils/         # Utilitaires partagés
│   ├── types/         # Types TypeScript partagés
│   └── theme/         # Design tokens "Océan Profond"
├── tests/
│   ├── unit/          # Vitest + RTL
│   └── e2e/           # Playwright
└── public/
```

**Development Experience:**
- HMR instantané via Vite 8
- TypeScript strict pour la sécurité du typage
- React DevTools + TanStack Query DevTools + Zustand DevTools
- ESLint + Prettier pour le formatage

**Note:** L'initialisation de chaque fondation (fork Mayan + création frontend) devrait constituer les premières stories d'implémentation.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (bloquent l'implémentation) :**

- Data Architecture (cache, migrations, validation)
- Authentication & Security (JWT, 2FA, audit trail signé)
- API & Communication (WebSocket, reverse proxy, uploads résumables)
- Conversion de documents pour le visualiseur

**Important Decisions (façonnent l'architecture) :**

- Versioning API
- Gestion d'erreurs API (RFC 7807)
- Internationalisation
- Monitoring & Logging

**Deferred Decisions (Post-MVP) :**

- LDAP/AD/SSO SAML/OIDC (Phase 2)
- Horodatage qualifié eIDAS (Phase 2)
- Kubernetes orchestration (Phase 2)
- Mode SaaS optionnel (Phase 3)

### Data Architecture

| Décision | Choix | Version | Rationale | Affecte |
| --- | --- | --- | --- | --- |
| **Cache backend** | Django cache framework + Redis backend | Redis 7.x (déjà dans la stack Celery) | Réutilise Redis sans service supplémentaire. Cache des métadonnées chaudes, sessions, résultats de recherche fréquents. TanStack Query couvre le cache côté frontend | API, recherche, sessions |
| **Migrations** | Django Migrations (natif) | Django 5.2 | Cohérence avec Mayan EDMS. Système éprouvé pour PostgreSQL | Base de données, déploiement |
| **Validation des données** | DRF Serializers + Pydantic pour structures métier critiques | DRF 3.x, Pydantic 2.x | Serializers DRF pour la validation API (cohérence Mayan). Pydantic pour les structures internes critiques : certificats de scellement, politiques WORM, configurations de conformité, structures d'audit | API, conformité, certificats |

### Authentication & Security

| Décision | Choix | Version | Rationale | Affecte |
| --- | --- | --- | --- | --- |
| **JWT** | djangorestframework-simplejwt | 5.5.x | Access token 15min + refresh token httpOnly (NFR14). Standard DRF, extensible vers OAuth2 en Phase 2 | API, frontend, sécurité |
| **2FA** | django-otp + django-two-factor-auth | Dernières stables | TOTP (Google Authenticator, Authy). Léger, ciblé sur le besoin MVP. django-allauth ajouté en Phase 2 pour LDAP/SSO | Auth, utilisateurs |
| **Audit trail signé** | Chaîne de hachage (hash chain) | Custom (SHA-256) | Chaque entrée d'audit contient le hash de l'entrée précédente. Toute altération casse la chaîne → détection immédiate. Satisfait NF Z42-013. Horodatage qualifié (RFC 3161) ajouté en Phase 2/eIDAS | Conformité, audit, tous les composants |

**Détail de l'audit trail signé :**

```text
Entry N:
  action: "document.sealed"
  timestamp: "2026-03-17T14:32:00Z"
  user_id: 42
  document_id: "uuid-xxx"
  data_hash: SHA-256(action + timestamp + user_id + document_id + details)
  previous_hash: SHA-256(Entry N-1)
  chain_hash: SHA-256(data_hash + previous_hash)
```

Vérification d'intégrité : recalculer la chaîne depuis l'entrée 1. Si un `chain_hash` ne correspond pas → altération détectée. Vérification automatisée quotidienne (NFR48).

### API & Communication Patterns

| Décision | Choix | Version | Rationale | Affecte |
| --- | --- | --- | --- | --- |
| **Temps réel** | Django Channels + Redis channel layer | Channels 4.x | WebSocket bidirectionnel pour progression uploads, résultats IA temps réel, notifications. Redis déjà dans la stack | Frontend, workers, notifications |
| **Versioning API** | URL path versioning (`/api/v1/`) | — | Standard DRF, cohérent avec Mayan, explicite pour les intégrateurs | API, intégration |
| **Reverse proxy** | Nginx | Dernière stable | TLS 1.3 termination, static files, rate limiting, WebSocket proxy. Cohérent avec la stack Docker Mayan | Infrastructure, sécurité |
| **Gestion d'erreurs** | RFC 7807 (Problem Details for HTTP APIs) | — | Format standard JSON pour les erreurs. Custom exception handler DRF. Clair pour les intégrateurs | API, frontend |
| **Upload résumable** | Protocole tus (tus-js-client + tusd) | tus 1.0.0 | Reprise automatique après interruption (FR6, NFR28). Supporte les fichiers volumineux. Standard open source (Cloudflare, Vimeo) | Capture, frontend, stockage |

**Détail du flux tus :**

```text
Frontend (tus-js-client) → tusd (service Docker) → igar-temp (MinIO)
                                                         ↓
                                                   Pipeline OCR/IA (Celery)
                                                         ↓
                                                   igar-vault (MinIO + Object Lock)
```

tusd écrit dans le bucket `igar-temp` de MinIO. Après traitement OCR/IA et validation utilisateur, le document est transféré dans `igar-vault` avec scellement WORM.

### Frontend Architecture

| Décision | Choix | Version | Rationale | Affecte |
| --- | --- | --- | --- | --- |
| **Internationalisation** | react-i18next | Dernière stable | Intégré dès le MVP pour éviter un refactoring coûteux. Lazy loading des langues. Compatible Ant Design (ConfigProvider locale) | Frontend, tous les composants UI |
| **State Management** | TanStack Query v5 (server) + Zustand (client) | TQ 5.90.x, Zustand 4.x | Séparation claire server/client state. TQ gère cache, refetch, loading. Zustand gère UI state léger (~1KB) | Frontend |
| **Upload UI** | tus-js-client + composant custom DropZoneOverlay | tus-js-client 4.x | Intégration avec le protocole tus backend. Progression temps réel via WebSocket | Frontend, capture |

### Infrastructure & Deployment

| Décision | Choix | Version | Rationale | Affecte |
| --- | --- | --- | --- | --- |
| **CI/CD** | GitHub Actions | — | Repo hébergé sur GitHub. Workflows pour tests, build, lint, sécurité | DevOps, qualité |
| **Métriques** | Prometheus + Grafana | Dernières stables | Standard monitoring Docker. Métriques applicatives, alerting, dashboards. Healthcheck `/health` (NFR44) | Infrastructure, ops |
| **Logs** | Logs JSON structurés → Elasticsearch (déjà présent) | — | Réutilise Elasticsearch. Logs centralisés, requêtables, horodatés (NFR43) | Infrastructure, debug |
| **Error tracking** | Sentry self-hosted | 26.x | Error tracking Python + React. Self-hosted pour conformité on-premise. Zéro dépendance cloud | Debug, qualité |
| **Conversion documents** | Gotenberg | 8.x (Docker) | Service Docker avec API REST pour conversion Office → PDF. Utilise LibreOffice + Chromium sous le capot. S'intègre dans l'architecture conteneurisée | Visualiseur, workers |

### Decision Impact Analysis

**Séquence d'implémentation recommandée :**

1. **Infrastructure de base** — Docker Compose avec PostgreSQL, Redis, MinIO, Elasticsearch, Nginx
2. **Fork Mayan + Frontend Vite** — Initialisation des deux fondations
3. **Auth (JWT + 2FA)** — Sécurité dès le début
4. **Pipeline d'upload (tus)** — Fondation de la capture
5. **Pipeline OCR/IA (Celery workers)** — Intelligence documentaire
6. **Coffre-fort WORM (MinIO Object Lock + SSE-C)** — Archivage à valeur probante
7. **Recherche Elasticsearch** — Full-text avec indexation OCR
8. **Visualiseur + Gotenberg** — Consultation multi-format + filigrane
9. **Audit trail signé** — Chaîne de hachage + vérification
10. **Cycle de vie + conformité** — Automate de conservation, certificats
11. **Monitoring (Prometheus + Grafana + Sentry)** — Observabilité

**Dépendances inter-composants :**

| Composant | Dépend de |
| --- | --- |
| Pipeline OCR/IA | Redis, Celery, MinIO (igar-temp), Elasticsearch |
| Coffre-fort WORM | MinIO (Object Lock), PostgreSQL (clés SSE-C) |
| Recherche | Elasticsearch, Pipeline OCR (contenu indexé) |
| Visualiseur | Gotenberg (conversion Office), MinIO (lecture), auth (filigrane) |
| Audit trail | PostgreSQL, auth (identité utilisateur) |
| Temps réel | Django Channels, Redis (channel layer) |
| Upload résumable | tusd, MinIO (igar-temp), frontend (tus-js-client) |

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**25 points de conflit potentiels identifiés** où des agents IA pourraient faire des choix divergents, regroupés en 5 catégories.

### Naming Patterns

**Database Naming Conventions (PostgreSQL / Django ORM) :**

| Élément | Convention | Exemple | Anti-pattern |
| --- | --- | --- | --- |
| Tables | snake_case, pluriel, préfixé par app Django | `igar_vault_documents` | `Documents`, `document`, `IgarVaultDocument` |
| Colonnes | snake_case | `created_at`, `document_type` | `createdAt`, `DocumentType` |
| Clés étrangères | `<table_singulier>_id` | `user_id`, `document_id` | `fk_user`, `userId` |
| Index | `idx_<table>_<colonnes>` | `idx_documents_created_at` | `documents_created_at_index` |
| Contraintes | `ck_<table>_<description>` | `ck_documents_status_valid` | `check_1` |
| UUID | Champ `uuid` de type UUID v4, distinct du PK auto-increment | `uuid = models.UUIDField(default=uuid4)` | Utiliser l'UUID comme PK Django |

**API Naming Conventions (DRF / REST) :**

| Élément | Convention | Exemple | Anti-pattern |
| --- | --- | --- | --- |
| Endpoints | snake_case, pluriel | `/api/v1/documents/`, `/api/v1/audit_logs/` | `/api/v1/Document/`, `/api/v1/auditLogs/` |
| Paramètres URL | snake_case | `?document_type=facture&created_after=2026-01-01` | `?documentType=facture` |
| Champs JSON (réponse) | snake_case | `{"document_id": "...", "created_at": "..."}` | `{"documentId": "...", "createdAt": "..."}` |
| Actions custom | verbe en snake_case | `POST /api/v1/documents/{id}/seal/` | `POST /api/v1/documents/{id}/sealDocument/` |
| Headers custom | `X-Igar-<Nom>` | `X-Igar-Request-Id` | `x-request-id`, `Igar_Request_Id` |

**Code Naming Conventions — Backend (Python/Django) :**

| Élément | Convention | Exemple | Anti-pattern |
| --- | --- | --- | --- |
| Modules | snake_case | `document_vault.py`, `ocr_pipeline.py` | `documentVault.py`, `OCRPipeline.py` |
| Classes | PascalCase | `DocumentSerializer`, `SealingService` | `document_serializer`, `sealing_service` |
| Fonctions / méthodes | snake_case | `seal_document()`, `verify_integrity()` | `sealDocument()`, `VerifyIntegrity()` |
| Constantes | UPPER_SNAKE_CASE | `MAX_UPLOAD_SIZE`, `WORM_COMPLIANCE_MODE` | `maxUploadSize`, `WormComplianceMode` |
| Apps Django | snake_case, courte | `vault`, `intelligence`, `capture`, `compliance` | `IgarVault`, `document_intelligence_module` |
| Celery tasks | `<app>.<action>` | `intelligence.classify_document` | `classifyDocument`, `task_classify` |

**Code Naming Conventions — Frontend (React/TypeScript) :**

| Élément | Convention | Exemple | Anti-pattern |
| --- | --- | --- | --- |
| Composants | PascalCase fichier + export | `ConfidenceBadge.tsx`, `DocumentViewer.tsx` | `confidence-badge.tsx`, `confidenceBadge.tsx` |
| Hooks | camelCase, préfixe `use` | `useDocuments.ts`, `useSearchResults.ts` | `UseDocuments.ts`, `documents-hook.ts` |
| Stores Zustand | camelCase, suffixe `Store` | `authStore.ts`, `uiStore.ts` | `AuthStore.ts`, `auth-store.ts` |
| TanStack Query keys | tableau hiérarchique | `['documents', { type, page }]` | `'documents-list'`, `'getDocuments'` |
| Types/Interfaces | PascalCase, préfixe selon usage | `Document`, `SealCertificate`, `ApiResponse<T>` | `IDocument`, `DocumentInterface` |
| Constantes | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_UPLOAD_FILES` | `apiBaseUrl`, `maxUploadFiles` |
| Pages (routes) | PascalCase | `DocumentsPage.tsx`, `ImportPage.tsx` | `documents.tsx`, `documents-page.tsx` |
| CSS/classes | kebab-case (si CSS modules) | `confidence-badge`, `seal-status` | `confidenceBadge`, `ConfidenceBadge` |

### Structure Patterns

**Backend — Organisation des apps Django (dans le fork Mayan) :**

```text
igar-backend/
├── mayan/                          # Code Mayan EDMS (fork, modifications minimales)
│   └── apps/
│       ├── documents/              # App Mayan — étendue pour Igar
│       ├── ocr/                    # App Mayan — réutilisée
│       └── ...
├── igar/                           # Code spécifique Igar
│   ├── apps/
│   │   ├── vault/                  # Coffre-fort WORM, scellement, SSE-C
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── services.py         # Logique métier (seal_document, verify_integrity)
│   │   │   ├── tasks.py            # Celery tasks
│   │   │   ├── tests/
│   │   │   │   ├── test_models.py
│   │   │   │   ├── test_services.py
│   │   │   │   └── test_api.py
│   │   │   └── factories.py        # Factory Boy
│   │   ├── intelligence/           # IA classification, extraction métadonnées
│   │   ├── capture/                # Upload tus, IMAP, ingestion
│   │   ├── compliance/             # Cycle de vie, audit trail, certificats
│   │   ├── viewer/                 # Filigrane, conversion Gotenberg
│   │   └── licensing/              # Système de licences
│   ├── core/                       # Utilitaires partagés, base models, mixins
│   │   ├── models.py               # BaseModel avec uuid, created_at, updated_at
│   │   ├── exceptions.py           # Exceptions métier Igar
│   │   ├── permissions.py          # Permissions custom
│   │   └── audit.py                # Mixin audit trail
│   └── settings/
│       ├── base.py
│       ├── development.py
│       ├── production.py
│       └── test.py
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   └── services/
│       ├── nginx/
│       ├── tusd/
│       └── gotenberg/
├── tests/                          # Tests d'intégration cross-apps
├── conftest.py                     # Fixtures pytest globales
└── pyproject.toml
```

**Règle clé :** Chaque app Django Igar suit la structure `models → serializers → services → views → tasks → tests`. La logique métier vit dans `services.py`, jamais dans les views ou serializers.

**Frontend — Organisation des modules :**

```text
igar-frontend/
├── src/
│   ├── api/
│   │   ├── client.ts               # Axios/fetch configuré (base URL, JWT interceptor)
│   │   ├── hooks/
│   │   │   ├── useDocuments.ts      # TanStack Query hooks pour documents
│   │   │   ├── useSearch.ts
│   │   │   ├── useVault.ts
│   │   │   └── useCompliance.ts
│   │   └── types.ts                 # Types API (réponses snake_case)
│   ├── components/
│   │   ├── common/                  # Composants réutilisables génériques
│   │   │   ├── ConfidenceBadge.tsx
│   │   │   ├── SealBadge.tsx
│   │   │   └── LoadingSkeleton.tsx
│   │   ├── documents/               # Composants liés aux documents
│   │   │   ├── DocumentTable.tsx
│   │   │   ├── DocumentViewer.tsx
│   │   │   └── ClassificationResult.tsx
│   │   ├── capture/                 # Composants d'import
│   │   │   ├── DropZoneOverlay.tsx
│   │   │   └── ImportProgressList.tsx
│   │   └── compliance/              # Composants conformité
│   │       └── ComplianceDashboard.tsx
│   ├── layouts/
│   │   └── AppLayout.tsx            # ProLayout configuré
│   ├── pages/
│   │   ├── DocumentsPage.tsx
│   │   ├── ImportPage.tsx
│   │   ├── CompliancePage.tsx
│   │   ├── AdminPage.tsx
│   │   └── LoginPage.tsx
│   ├── stores/
│   │   ├── authStore.ts             # Zustand — auth, user, tokens
│   │   ├── uiStore.ts              # Zustand — sidebar, theme, preferences
│   │   └── importStore.ts          # Zustand — état d'import en cours
│   ├── hooks/
│   │   ├── useWebSocket.ts          # Hook WebSocket Django Channels
│   │   └── useKeyboardShortcuts.ts
│   ├── utils/
│   │   ├── format.ts                # Formatage dates, tailles, durées
│   │   ├── crypto.ts                # Vérification SHA-256 côté client
│   │   └── permissions.ts           # Helpers RBAC frontend
│   ├── types/
│   │   ├── document.ts
│   │   ├── user.ts
│   │   └── compliance.ts
│   ├── theme/
│   │   └── oceanDeep.ts             # Design tokens "Océan Profond"
│   ├── i18n/
│   │   ├── index.ts                 # Config react-i18next
│   │   └── locales/
│   │       ├── fr.json
│   │       └── en.json
│   ├── router.tsx                   # React Router v6 config
│   └── App.tsx
├── tests/
│   ├── unit/                        # Vitest + RTL, miroir de src/
│   │   ├── components/
│   │   └── hooks/
│   └── e2e/                         # Playwright
│       ├── journeys/
│       │   ├── fatima-capture.spec.ts
│       │   ├── philippe-search.spec.ts
│       │   ├── amina-viewer.spec.ts
│       │   ├── thomas-admin.spec.ts
│       │   └── sarah-api.spec.ts
│       └── fixtures/
└── public/
```

**Règle clé :** Tests unitaires dans `tests/unit/` en miroir de `src/`. Tests E2E organisés par journey utilisateur. Composants organisés par domaine fonctionnel, pas par type.

### Format Patterns

**API Response Formats :**

**Réponse succès (liste paginée) :**

```json
{
  "count": 1247,
  "next": "/api/v1/documents/?page=2",
  "previous": null,
  "results": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "label": "Contrat_Dupont_2023.pdf",
      "document_type": "contrat",
      "created_at": "2026-03-17T14:32:00Z",
      "seal_status": "sealed",
      "confidence_score": 0.97
    }
  ]
}
```

**Réponse succès (objet unique) :**

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "label": "Contrat_Dupont_2023.pdf",
  "document_type": "contrat",
  "metadata": {
    "date": "2023-06-15",
    "amount": 15000.00,
    "entities": ["Dupont SA", "Martin SARL"]
  },
  "seal": {
    "status": "sealed",
    "sha256": "a1b2c3d4...",
    "sealed_at": "2026-03-17T14:35:00Z",
    "retention_until": "2031-03-17"
  }
}
```

**Réponse erreur (RFC 7807) :**

```json
{
  "type": "https://igar.local/errors/document-protected",
  "title": "Document protégé",
  "status": 403,
  "detail": "Ce document est scellé en mode Compliance. Conservation jusqu'au 15/03/2031.",
  "instance": "/api/v1/documents/550e8400.../delete/"
}
```

**Conventions de format :**

| Élément | Format | Exemple |
| --- | --- | --- |
| Dates/heures | ISO 8601 UTC | `2026-03-17T14:32:00Z` |
| Dates seules | ISO 8601 | `2026-03-17` |
| UUIDs | UUID v4 string | `550e8400-e29b-41d4-a716-446655440000` |
| Booléens | `true` / `false` | `"is_sealed": true` |
| Null | `null` explicite | `"deleted_at": null` |
| Montants | Nombre décimal | `15000.00` (pas de string) |
| Tailles fichiers | Entier en bytes | `1048576` (pas `"1 Mo"`) |
| Pagination | DRF standard | `count`, `next`, `previous`, `results` |
| Codes HTTP | Standard REST | 200, 201, 204, 400, 401, 403, 404, 409, 422, 500 |

### Communication Patterns

**WebSocket Events (Django Channels) :**

| Événement | Format | Payload |
| --- | --- | --- |
| Progression upload | `upload.progress` | `{"document_id": "...", "progress": 0.65, "status": "uploading"}` |
| Résultat IA | `classification.result` | `{"document_id": "...", "type": "facture", "confidence": 0.97, "metadata": {...}}` |
| Scellement | `seal.completed` | `{"document_id": "...", "sha256": "...", "sealed_at": "..."}` |
| Notification | `notification.new` | `{"type": "retention_expiry", "message": "...", "document_id": "..."}` |

**Convention :** `<domaine>.<action>` en snake_case. Payload toujours en snake_case JSON.

**Celery Task Events :**

| Task | Naming | Queue |
| --- | --- | --- |
| OCR | `capture.process_ocr` | `ocr` |
| Classification IA | `intelligence.classify_document` | `ai` |
| Extraction métadonnées | `intelligence.extract_metadata` | `ai` |
| Vérification intégrité | `compliance.verify_integrity` | `compliance` |
| Notification | `compliance.send_notification` | `default` |

**Convention :** `<app_django>.<verbe_action>`. Queues séparées par type de charge (CPU-bound OCR/IA vs I/O-bound compliance).

**State Management Frontend :**

```typescript
// TanStack Query — Server state
// Clés hiérarchiques pour l'invalidation ciblée
const queryKeys = {
  documents: {
    all: ['documents'] as const,
    lists: () => [...queryKeys.documents.all, 'list'] as const,
    list: (filters: DocumentFilters) => [...queryKeys.documents.lists(), filters] as const,
    details: () => [...queryKeys.documents.all, 'detail'] as const,
    detail: (uuid: string) => [...queryKeys.documents.details(), uuid] as const,
  },
  search: {
    all: ['search'] as const,
    results: (query: string, filters: SearchFilters) => [...queryKeys.search.all, query, filters] as const,
  },
};

// Zustand — Client state (immutable updates via Immer intégré)
// Un store par domaine, jamais de mega-store
interface UiStore {
  sidebarCollapsed: boolean;
  activeTab: 'documents' | 'import' | 'compliance';
  toggleSidebar: () => void;
  setActiveTab: (tab: UiStore['activeTab']) => void;
}
```

### Process Patterns

**Error Handling — Backend :**

```python
# Exceptions métier Igar (dans igar/core/exceptions.py)
class IgarException(Exception):
    """Base exception pour toutes les erreurs métier Igar."""
    status_code = 500
    error_type = "internal_error"

class DocumentProtectedError(IgarException):
    status_code = 403
    error_type = "document_protected"

class IntegrityViolationError(IgarException):
    status_code = 409
    error_type = "integrity_violation"

class ClassificationFailedError(IgarException):
    status_code = 422
    error_type = "classification_failed"

# Custom exception handler DRF → RFC 7807
def igar_exception_handler(exc, context):
    # Convertit IgarException → RFC 7807 JSON
    ...
```

**Règle :** Toute erreur métier est une sous-classe de `IgarException`. Le handler DRF les convertit en RFC 7807. Les erreurs techniques (500) sont loguées dans Sentry, les erreurs métier (4xx) sont retournées au client avec un message humain.

**Error Handling — Frontend :**

```typescript
// Error boundary global dans App.tsx
// Erreurs TanStack Query gérées par composant via onError
// Erreurs réseau → banner persistant "Connexion interrompue"
// Erreurs 4xx → toast avec message de l'API (RFC 7807 detail)
// Erreurs 5xx → toast générique + log Sentry
```

**Loading States — Frontend :**

| Situation | Pattern | Composant Ant Design |
| --- | --- | --- |
| Chargement de page | Skeleton (structure de la page) | `Skeleton` |
| Recherche en cours | Skeleton des résultats | `Skeleton` + `Spin` |
| Action en cours (bouton) | Spinner dans le bouton | `Button loading={true}` |
| Upload | Progress bar par fichier + globale | `Progress` |
| Pipeline IA | Progress bar + compteur + résultats progressifs | `Progress` + `List` |

**Convention :** Utiliser `isLoading` (premier chargement) et `isFetching` (rechargement en arrière-plan) de TanStack Query. Skeleton si > 300ms, estimation de temps si > 2s.

**Logging — Backend :**

```python
import structlog

logger = structlog.get_logger(__name__)

# Format structuré obligatoire
logger.info("document_sealed",
    document_uuid="550e8400...",
    user_id=42,
    seal_sha256="a1b2c3...",
    retention_days=1825
)

# Niveaux :
# DEBUG — Détails de traitement (OCR, IA, SSE-C)
# INFO — Actions métier (scellement, destruction, connexion)
# WARNING — Anomalies récupérables (OCR faible confiance, retry)
# ERROR — Erreurs métier (classification échouée, intégrité violée)
# CRITICAL — Erreurs système (MinIO down, DB unreachable)
```

**Convention :** `structlog` pour les logs JSON structurés. Chaque log a un `event` (verbe snake_case), un `user_id` si applicable, et les données contextuelles.

### Enforcement Guidelines

**Tous les agents IA DOIVENT :**

1. Utiliser snake_case pour toute API, base de données, et code Python
2. Utiliser PascalCase pour les composants React et camelCase pour les variables/fonctions TypeScript
3. Placer la logique métier dans `services.py` (backend) ou des hooks custom (frontend), jamais dans les views/composants directement
4. Écrire les tests dans `tests/` (pas co-localisés) en miroir de la structure source
5. Utiliser les exceptions `IgarException` pour les erreurs métier, jamais de `raise Exception("...")`
6. Formater les réponses API selon RFC 7807 pour les erreurs, DRF standard pour les succès
7. Utiliser les query keys hiérarchiques TanStack Query pour permettre l'invalidation ciblée
8. Logger avec `structlog` en format structuré, jamais de `print()` ou `console.log()` en production
9. Documenter chaque endpoint API dans le schema OpenAPI via les serializers DRF
10. Préfixer les apps Django Igar dans `igar/apps/`, ne pas modifier les apps Mayan dans `mayan/apps/` sauf nécessité absolue

**Pattern Enforcement :**

- **ESLint + Prettier** (frontend) — Formatage et conventions automatiques
- **Ruff** (backend) — Linter Python rapide, remplace flake8/black/isort
- **Pre-commit hooks** — Vérification automatique avant chaque commit
- **CI GitHub Actions** — Lint + tests + type check sur chaque PR

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
igar/                                    # Racine monorepo
├── README.md
├── LICENSE
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci-backend.yml               # Lint + tests Python
│       ├── ci-frontend.yml              # Lint + tests + build React
│       ├── e2e.yml                      # Playwright E2E
│       └── security.yml                 # Audit dépendances + SAST
│
├── backend/                             # Fork Mayan EDMS 4.11
│   ├── mayan/                           # Code Mayan EDMS (fork, modifications minimales)
│   │   └── apps/
│   │       ├── documents/               # App Mayan — étendue pour Igar
│   │       ├── ocr/                     # App Mayan — réutilisée telle quelle
│   │       ├── file_metadata/           # App Mayan — réutilisée
│   │       ├── search/                  # App Mayan — étendue (Elasticsearch)
│   │       ├── permissions/             # App Mayan — réutilisée
│   │       └── rest_api/               # App Mayan — étendue
│   ├── igar/                            # Code spécifique Igar
│   │   ├── __init__.py
│   │   ├── apps/
│   │   │   ├── vault/                   # Coffre-fort WORM, scellement, SSE-C
│   │   │   │   ├── __init__.py
│   │   │   │   ├── apps.py
│   │   │   │   ├── models.py            # SealedDocument, SealCertificate, WormPolicy
│   │   │   │   ├── serializers.py       # API serializers DRF
│   │   │   │   ├── views.py             # ViewSets DRF
│   │   │   │   ├── services.py          # seal_document(), verify_integrity(), generate_certificate()
│   │   │   │   ├── tasks.py             # Celery: periodic_integrity_check
│   │   │   │   ├── urls.py
│   │   │   │   ├── admin.py
│   │   │   │   ├── factories.py         # Factory Boy
│   │   │   │   └── tests/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── test_models.py
│   │   │   │       ├── test_services.py
│   │   │   │       └── test_api.py
│   │   │   ├── intelligence/            # IA classification, extraction métadonnées
│   │   │   │   ├── __init__.py
│   │   │   │   ├── apps.py
│   │   │   │   ├── models.py            # ClassificationResult, ExtractionRule
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   ├── services.py          # classify_document(), extract_metadata()
│   │   │   │   ├── tasks.py             # Celery: classify_document, extract_metadata
│   │   │   │   ├── urls.py
│   │   │   │   ├── factories.py
│   │   │   │   └── tests/
│   │   │   │       ├── test_models.py
│   │   │   │       ├── test_services.py
│   │   │   │       └── test_api.py
│   │   │   ├── capture/                 # Upload tus, IMAP, ingestion multi-canal
│   │   │   │   ├── __init__.py
│   │   │   │   ├── apps.py
│   │   │   │   ├── models.py            # ImportSession, ImportSource
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   ├── services.py          # process_upload(), poll_imap(), start_pipeline()
│   │   │   │   ├── tasks.py             # Celery: process_ocr, poll_imap_sources
│   │   │   │   ├── urls.py
│   │   │   │   ├── factories.py
│   │   │   │   └── tests/
│   │   │   │       ├── test_models.py
│   │   │   │       ├── test_services.py
│   │   │   │       └── test_api.py
│   │   │   ├── compliance/              # Cycle de vie, audit trail, certificats, RGPD
│   │   │   │   ├── __init__.py
│   │   │   │   ├── apps.py
│   │   │   │   ├── models.py            # AuditEntry, RetentionPolicy, DestructionCertificate
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   ├── services.py          # append_audit(), verify_chain(), schedule_destruction()
│   │   │   │   ├── tasks.py             # Celery: verify_integrity, send_notification
│   │   │   │   ├── urls.py
│   │   │   │   ├── factories.py
│   │   │   │   └── tests/
│   │   │   │       ├── test_models.py
│   │   │   │       ├── test_services.py
│   │   │   │       └── test_api.py
│   │   │   ├── viewer/                  # Filigrane serveur, conversion Gotenberg
│   │   │   │   ├── __init__.py
│   │   │   │   ├── apps.py
│   │   │   │   ├── models.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   ├── services.py          # render_watermark(), convert_to_pdf()
│   │   │   │   ├── urls.py
│   │   │   │   └── tests/
│   │   │   │       └── test_services.py
│   │   │   └── licensing/               # Système de licences hardware-bound
│   │   │       ├── __init__.py
│   │   │       ├── apps.py
│   │   │       ├── models.py            # License, LicenseFeature
│   │   │       ├── serializers.py
│   │   │       ├── views.py
│   │   │       ├── services.py          # validate_license(), check_features()
│   │   │       ├── middleware.py         # LicenseCheckMiddleware
│   │   │       ├── urls.py
│   │   │       └── tests/
│   │   │           ├── test_services.py
│   │   │           └── test_middleware.py
│   │   ├── core/                        # Utilitaires partagés, base models, mixins
│   │   │   ├── __init__.py
│   │   │   ├── models.py               # BaseModel (uuid, created_at, updated_at)
│   │   │   ├── exceptions.py           # IgarException, DocumentProtectedError, etc.
│   │   │   ├── permissions.py          # Permissions custom Igar
│   │   │   ├── audit.py                # Mixin audit trail, hash chain utils
│   │   │   ├── pagination.py           # Pagination DRF custom
│   │   │   ├── exception_handler.py    # RFC 7807 handler DRF
│   │   │   └── storage.py              # Abstraction MinIO/S3 avec SSE-C
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Settings communs
│   │   │   ├── development.py          # DEBUG=True, CORS permissif
│   │   │   ├── production.py           # TLS, CORS strict, SSE-C
│   │   │   └── test.py                 # SQLite/in-memory, mocks MinIO
│   │   ├── urls.py                     # URL config racine /api/v1/
│   │   ├── wsgi.py
│   │   ├── asgi.py                     # Django Channels (WebSocket)
│   │   └── routing.py                  # WebSocket routing (Channels)
│   ├── docker/
│   │   ├── Dockerfile                  # Image backend Python
│   │   ├── Dockerfile.worker           # Image worker OCR/IA
│   │   └── entrypoint.sh
│   ├── tests/                          # Tests d'intégration cross-apps
│   │   ├── conftest.py                 # Fixtures pytest globales
│   │   ├── test_pipeline_integration.py # Test pipeline complet upload→OCR→IA→seal
│   │   └── test_audit_chain.py         # Test intégrité chaîne audit
│   ├── conftest.py                     # Configuration pytest racine
│   ├── pyproject.toml                  # Ruff, pytest, dependencies
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   ├── production.txt
│   │   └── test.txt
│   └── manage.py
│
├── frontend/                            # SPA React découplée
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts               # Axios configuré (base URL, JWT interceptor, refresh)
│   │   │   ├── hooks/
│   │   │   │   ├── useDocuments.ts      # TanStack Query hooks documents
│   │   │   │   ├── useSearch.ts         # TanStack Query hooks recherche
│   │   │   │   ├── useVault.ts          # TanStack Query hooks coffre-fort
│   │   │   │   ├── useCompliance.ts     # TanStack Query hooks conformité
│   │   │   │   ├── useAuth.ts           # TanStack Query hooks auth (login, refresh, 2FA)
│   │   │   │   └── useAdmin.ts          # TanStack Query hooks admin (users, roles)
│   │   │   ├── queryKeys.ts             # Clés TanStack Query hiérarchiques centralisées
│   │   │   └── types.ts                 # Types API (réponses snake_case)
│   │   ├── components/
│   │   │   ├── common/                  # Composants réutilisables génériques
│   │   │   │   ├── ConfidenceBadge.tsx
│   │   │   │   ├── SealBadge.tsx
│   │   │   │   ├── LoadingSkeleton.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   ├── documents/               # Composants liés aux documents
│   │   │   │   ├── DocumentTable.tsx     # ProTable documents
│   │   │   │   ├── DocumentViewer.tsx    # Visualiseur multi-format
│   │   │   │   └── ClassificationResult.tsx
│   │   │   ├── capture/                 # Composants d'import
│   │   │   │   ├── DropZoneOverlay.tsx   # Drag & drop + tus upload
│   │   │   │   └── ImportProgressList.tsx # Progression par fichier
│   │   │   └── compliance/              # Composants conformité
│   │   │       └── ComplianceDashboard.tsx
│   │   ├── layouts/
│   │   │   └── AppLayout.tsx            # ProLayout (sidebar, header, breadcrumb)
│   │   ├── pages/
│   │   │   ├── DocumentsPage.tsx        # Liste documents + filtres
│   │   │   ├── ImportPage.tsx           # Import multi-canal
│   │   │   ├── CompliancePage.tsx       # Dashboard conformité NF Z42-013
│   │   │   ├── AdminPage.tsx            # Gestion utilisateurs, rôles, paramètres
│   │   │   ├── SearchPage.tsx           # Recherche full-text avec surlignage
│   │   │   └── LoginPage.tsx            # Connexion + 2FA
│   │   ├── stores/
│   │   │   ├── authStore.ts             # Zustand — auth, user, tokens
│   │   │   ├── uiStore.ts              # Zustand — sidebar, theme, preferences
│   │   │   └── importStore.ts          # Zustand — état d'import en cours
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts          # Hook WebSocket Django Channels
│   │   │   └── useKeyboardShortcuts.ts  # Raccourcis clavier
│   │   ├── utils/
│   │   │   ├── format.ts                # Formatage dates, tailles, durées
│   │   │   ├── crypto.ts                # Vérification SHA-256 côté client
│   │   │   └── permissions.ts           # Helpers RBAC frontend
│   │   ├── types/
│   │   │   ├── document.ts              # Types Document, Metadata, SealStatus
│   │   │   ├── user.ts                  # Types User, Role, Permission
│   │   │   └── compliance.ts            # Types AuditEntry, RetentionPolicy
│   │   ├── theme/
│   │   │   └── oceanDeep.ts             # Design tokens "Océan Profond"
│   │   ├── i18n/
│   │   │   ├── index.ts                 # Config react-i18next
│   │   │   └── locales/
│   │   │       ├── fr.json              # Français (langue par défaut)
│   │   │       └── en.json              # Anglais
│   │   ├── router.tsx                   # React Router v6 config
│   │   ├── App.tsx                      # App root (providers, error boundary)
│   │   ├── main.tsx                     # Entry point Vite
│   │   └── vite-env.d.ts
│   ├── tests/
│   │   ├── unit/                        # Vitest + RTL (miroir de src/)
│   │   │   ├── components/
│   │   │   │   ├── ConfidenceBadge.test.tsx
│   │   │   │   ├── DocumentViewer.test.tsx
│   │   │   │   └── SealBadge.test.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useDocuments.test.ts
│   │   │   │   └── useWebSocket.test.ts
│   │   │   └── stores/
│   │   │       └── authStore.test.ts
│   │   └── e2e/                         # Playwright
│   │       ├── journeys/
│   │       │   ├── fatima-capture.spec.ts     # Journey Fatima : import → OCR → classif
│   │       │   ├── philippe-search.spec.ts    # Journey Philippe : recherche full-text
│   │       │   ├── amina-viewer.spec.ts       # Journey Amina : consultation + filigrane
│   │       │   ├── thomas-admin.spec.ts       # Journey Thomas : admin + audit
│   │       │   └── sarah-api.spec.ts          # Journey Sarah : API intégration
│   │       ├── fixtures/
│   │       │   └── test-documents/            # PDFs, images, Office pour tests
│   │       └── playwright.config.ts
│   ├── public/
│   │   └── favicon.svg
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── .eslintrc.cjs
│   ├── .prettierrc
│   └── .env.example                     # VITE_API_URL, VITE_WS_URL
│
├── infrastructure/                      # Configuration d'infrastructure
│   ├── docker-compose.yml               # Stack complète production
│   ├── docker-compose.dev.yml           # Override développement (volumes, hot-reload)
│   ├── docker-compose.test.yml          # Override tests (services légers)
│   ├── .env.example                     # Variables d'environnement template
│   ├── nginx/
│   │   ├── nginx.conf                   # Config Nginx (TLS, reverse proxy, rate limiting)
│   │   └── conf.d/
│   │       └── igar.conf                # Server block Igar (API, frontend, WS, tus)
│   ├── tusd/
│   │   └── tusd.conf                    # Config tusd (hooks, storage MinIO)
│   ├── gotenberg/
│   │   └── gotenberg.yml                # Config Gotenberg (timeouts, formats)
│   ├── minio/
│   │   └── init-buckets.sh              # Création igar-temp + igar-vault avec Object Lock
│   ├── elasticsearch/
│   │   └── elasticsearch.yml            # Config Elasticsearch (mémoire, index)
│   ├── prometheus/
│   │   └── prometheus.yml               # Config scraping + alertes
│   ├── grafana/
│   │   └── dashboards/
│   │       └── igar-overview.json       # Dashboard Igar prêt à l'emploi
│   ├── sentry/
│   │   └── sentry.conf.py              # Config Sentry self-hosted
│   └── scripts/
│       ├── setup-dev.sh                 # Script d'installation développeur
│       ├── backup-db.sh                 # Backup PostgreSQL
│       └── verify-integrity.sh          # Vérification intégrité chaîne audit
│
└── docs/                                # Documentation projet
    ├── api/                             # Documentation API (générée OpenAPI)
    ├── deployment/                      # Guides de déploiement
    └── compliance/                      # Documentation conformité NF Z42-013
```

### Architectural Boundaries

**Routing Nginx (point d'entrée unique) :**

| Route | Destination | Description |
| --- | --- | --- |
| `/` | Frontend (SPA) | Fichiers statiques React build |
| `/api/v1/` | Backend Django (Gunicorn) | API REST DRF |
| `/ws/` | Backend Django (Daphne/Uvicorn) | WebSocket Django Channels |
| `/uploads/` | tusd (service Docker) | Upload résumable tus |
| `/health` | Backend Django | Healthcheck (NFR44) |

**Séparation des services Docker :**

| Service | Port interne | Rôle | Communication |
| --- | --- | --- | --- |
| `nginx` | 80/443 | Reverse proxy, TLS termination | → tous les services |
| `backend` | 8000 | API Django (Gunicorn) | → PostgreSQL, Redis, MinIO, Elasticsearch |
| `backend-ws` | 8001 | WebSocket Django (Daphne) | → Redis (channel layer) |
| `worker-ocr` | — | Celery worker queue `ocr` | → Redis, MinIO, Elasticsearch |
| `worker-ai` | — | Celery worker queue `ai` | → Redis, MinIO, PostgreSQL |
| `worker-default` | — | Celery worker queue `default`, `compliance` | → Redis, PostgreSQL |
| `celery-beat` | — | Planificateur tâches périodiques | → Redis |
| `tusd` | 8080 | Upload résumable | → MinIO (igar-temp) |
| `gotenberg` | 3000 | Conversion Office → PDF | API REST interne |
| `postgresql` | 5432 | Base de données principale | TDE activé |
| `redis` | 6379 | Cache, broker Celery, channel layer WS | — |
| `minio` | 9000 | Stockage objet S3 | Object Lock (igar-vault) |
| `elasticsearch` | 9200 | Indexation full-text | — |
| `prometheus` | 9090 | Collecte métriques | Scrape tous les services |
| `grafana` | 3001 | Dashboards monitoring | → Prometheus |
| `sentry` | 9500 | Error tracking | — |

### Data Boundaries

| Donnée | Stockage | Raison |
| --- | --- | --- |
| Métadonnées documents | PostgreSQL | Requêtes relationnelles, FK, transactions ACID |
| Contenu indexé OCR | Elasticsearch | Recherche full-text performante |
| Fichiers originaux (archivés) | MinIO `igar-vault` | WORM Object Lock, SSE-C AES-256 |
| Fichiers temporaires (pipeline) | MinIO `igar-temp` | Traitement transitoire, TTL 24h |
| Clés SSE-C | PostgreSQL (TDE) | Séparation clés/données, chiffrement au repos |
| Sessions JWT | Redis | Tokens éphémères, invalidation rapide |
| Cache API | Redis | TTL court, invalidation via TanStack Query |
| Audit trail | PostgreSQL | Chaîne de hachage, requêtes chronologiques |
| Logs applicatifs | Elasticsearch | Recherche, rétention configurable |
| Métriques | Prometheus TSDB | Séries temporelles, alerting |
| État UI (client) | Zustand (mémoire) | Local au navigateur, pas de persistence serveur |
| État serveur (cache client) | TanStack Query (mémoire) | Cache intelligent avec invalidation automatique |

### Requirements to Structure Mapping

**FR Categories → Directories :**

| Domaine FR | Backend (igar/apps/) | Frontend (src/) | Infrastructure |
| --- | --- | --- | --- |
| Capture & Ingestion (FR1-FR6) | `capture/` | `components/capture/`, `pages/ImportPage.tsx` | `tusd/` |
| Intelligence & Classification (FR7-FR11) | `intelligence/` | `components/documents/ClassificationResult.tsx` | worker-ai |
| Visualisation & Consultation (FR12-FR19) | `viewer/` | `components/documents/DocumentViewer.tsx` | `gotenberg/` |
| Archivage & Immuabilité (FR20-FR28) | `vault/` | `components/common/SealBadge.tsx` | `minio/` (Object Lock) |
| Recherche & Découverte (FR29-FR33) | Mayan `search/` étendu | `pages/SearchPage.tsx`, `api/hooks/useSearch.ts` | `elasticsearch/` |
| Cycle de Vie & Conformité (FR34-FR40) | `compliance/` | `components/compliance/`, `pages/CompliancePage.tsx` | worker-default |
| Gestion Utilisateurs (FR41-FR46) | Mayan `permissions/` + `igar/core/` | `pages/AdminPage.tsx`, `stores/authStore.ts` | — |
| API & Intégration (FR52-FR57) | Tous les `urls.py` + `serializers.py` | — | `nginx/` (rate limiting) |

**Cross-Cutting Concerns → Locations :**

| Préoccupation | Backend | Frontend | Infrastructure |
| --- | --- | --- | --- |
| Sécurité & Chiffrement | `core/storage.py`, `settings/production.py` | `api/client.ts` (JWT interceptor) | `nginx/` (TLS 1.3, CSP) |
| Audit Trail Immuable | `core/audit.py`, `compliance/models.py` | — | PostgreSQL (TDE) |
| Temps Réel (WebSocket) | `routing.py`, `asgi.py` | `hooks/useWebSocket.ts` | Redis (channel layer) |
| Internationalisation | DRF (messages d'erreur) | `i18n/`, ConfigProvider locale | — |
| Monitoring | structlog, `/health` endpoint | Sentry SDK React | `prometheus/`, `grafana/` |
| RGPD | `compliance/services.py` | — | — |

### Data Flow Diagram

**Pipeline principal : Upload → OCR → Classification → Scellement**

```text
┌─────────────────┐     tus protocol      ┌──────────┐     S3 PUT     ┌─────────────────┐
│  Frontend SPA   │ ──────────────────────→│   tusd   │ ─────────────→│ MinIO igar-temp  │
│  (tus-js-client)│                        └──────────┘               └────────┬────────┘
└────────┬────────┘                                                            │
         │                                                                     │ hook notification
         │ WebSocket                                                           ▼
         │ (progression)                                              ┌─────────────────┐
         │                                                            │  Celery Worker   │
         │←─────── Django Channels ←──── Redis ←─────────────────────│    (queue: ocr)  │
         │         (ws/progress)          (pub/sub)                   │  process_ocr()   │
         │                                                            └────────┬────────┘
         │                                                                     │
         │                                                                     │ texte OCR
         │                                                                     ▼
         │                                                            ┌─────────────────┐
         │                                                            │  Celery Worker   │
         │←─────── Django Channels ←──── Redis ←─────────────────────│    (queue: ai)   │
         │         (classification.result)                            │  classify_doc()  │
         │                                                            └────────┬────────┘
         │                                                                     │
         │  POST /api/v1/documents/{id}/seal/                                  │ résultat IA
         │─────────────────────────────────────→┌──────────────┐               │
         │                                      │  Django API   │←─────────────┘
         │                                      │  vault/       │
         │                                      │  services.py  │
         │                                      │  seal_doc()   │
         │                                      └──────┬───────┘
         │                                             │
         │                                             │ S3 PUT + Object Lock + SSE-C
         │                                             ▼
         │                                      ┌─────────────────┐
         │                                      │ MinIO igar-vault │
         │←── seal.completed (WebSocket) ───────│  (WORM locked)  │
         │                                      └─────────────────┘
         │
         │                                      ┌─────────────────┐
         │                                      │  PostgreSQL     │
         │                                      │  - métadonnées  │
         │                                      │  - clé SSE-C    │
         │                                      │  - audit entry  │
         │                                      │  (hash chain)   │
         │                                      └─────────────────┘
         │
         │                                      ┌─────────────────┐
         │                                      │  Elasticsearch  │
         │                                      │  - contenu OCR  │
         │                                      │  - métadonnées  │
         │                                      │  indexées       │
         │                                      └─────────────────┘
```

### Development Workflow Integration

**Commandes de développement local :**

```bash
# Démarrage stack complète (développement)
cd infrastructure/
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Backend uniquement (hot-reload via volume mount)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up backend worker-ocr worker-ai

# Frontend (hors Docker, HMR Vite)
cd frontend/
npm run dev          # → http://localhost:5173 (proxy API vers Docker)

# Tests backend
cd backend/
pytest                              # Tous les tests
pytest igar/apps/vault/tests/       # Tests d'une app
pytest -x --ff                      # Arrêt au 1er échec, failed-first

# Tests frontend
cd frontend/
npm run test                        # Vitest watch mode
npm run test:e2e                    # Playwright headless
npm run test:e2e -- --ui            # Playwright UI mode

# Lint
cd backend/ && ruff check . && ruff format --check .
cd frontend/ && npm run lint && npm run format:check
```

**Variables d'environnement (`.env.example`) :**

```env
# PostgreSQL
POSTGRES_DB=igar
POSTGRES_USER=igar
POSTGRES_PASSWORD=<secret>

# MinIO
MINIO_ROOT_USER=igar-admin
MINIO_ROOT_PASSWORD=<secret>

# Redis
REDIS_URL=redis://redis:6379/0

# Django
DJANGO_SETTINGS_MODULE=igar.settings.development
SECRET_KEY=<secret>
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend
VITE_API_URL=http://localhost/api/v1
VITE_WS_URL=ws://localhost/ws

# Sentry
SENTRY_DSN=<sentry-self-hosted-url>
```

## Architecture Validation Results

### Coherence Validation

#### Decision Compatibility

Toutes les décisions technologiques fonctionnent ensemble sans conflit :

- **Backend stack** : Django 5.2 + DRF + Celery + Redis + PostgreSQL + Elasticsearch — stack Mayan 4.11 éprouvée, versions compatibles entre elles
- **Frontend stack** : React 18+ + Ant Design v6 + TanStack Query v5 + Zustand + Vite 8 — écosystème React 2026 cohérent
- **Communication** : tus (upload) + Django Channels/Redis (WebSocket) + DRF (REST) — trois canaux distincts sans chevauchement
- **Stockage** : MinIO (fichiers) + PostgreSQL (métadonnées + clés) + Elasticsearch (index) + Redis (cache) — chaque store a un rôle clair
- **Observabilité** : structlog → Elasticsearch (logs) + Prometheus → Grafana (métriques) + Sentry (erreurs) — pipeline complet sans redondance
- **Aucune contradiction détectée** entre les décisions architecturales

#### Pattern Consistency

- **snake_case uniforme** sur toute la chaîne : DB → API JSON → WebSocket events → Celery task names → URL params
- **PascalCase** pour composants React et classes Python, **camelCase** pour variables/fonctions TypeScript — séparation nette par langage
- **RFC 7807** pour toutes les erreurs API, **DRF standard** pour les réponses succès — format prévisible pour les intégrateurs
- **TanStack Query** (server state) vs **Zustand** (client state) — frontière claire, aucun chevauchement
- **structlog** backend avec format JSON structuré → indexable dans Elasticsearch — cohérent bout en bout

#### Structure Alignment

- La structure monorepo `backend/` + `frontend/` + `infrastructure/` reflète les trois domaines techniques
- Chaque app Django Igar suit le pattern uniforme `models → serializers → services → views → tasks → tests`
- Les tests E2E Playwright sont organisés par les 5 journeys utilisateur du PRD (Fatima, Philippe, Amina, Thomas, Sarah)
- Le routing Nginx mappe correctement chaque chemin vers le service correspondant (`/api/v1/` → Django, `/ws/` → Channels, `/uploads/` → tusd)

### Requirements Coverage Validation

#### Functional Requirements Coverage (57 FRs)

| Domaine | FRs | Support architectural | Statut |
| --- | --- | --- | --- |
| Capture & Ingestion | FR1-FR6 | `capture/` + tusd + MinIO igar-temp + Celery workers | Couvert |
| Intelligence & Classification | FR7-FR11 | `intelligence/` + workers Celery (queue ai) + Elasticsearch | Couvert |
| Visualisation & Consultation | FR12-FR19 | `viewer/` + Gotenberg + filigrane serveur + streaming | Couvert |
| Archivage & Immuabilité | FR20-FR28 | `vault/` + MinIO Object Lock + SSE-C AES-256 + hash chain | Couvert |
| Recherche & Découverte | FR29-FR33 | Elasticsearch + Mayan search étendu + surlignage | Couvert |
| Cycle de Vie & Conformité | FR34-FR40 | `compliance/` + Celery periodic tasks + certificats | Couvert |
| Gestion Utilisateurs & Sécurité | FR41-FR46 | simplejwt + django-otp + RBAC Mayan étendu | Couvert |
| API & Intégration | FR52-FR57 | DRF + OpenAPI 3.0 + URL versioning /api/v1/ | Couvert |

**Résultat : 57/57 FRs couverts architecturalement.**

#### Non-Functional Requirements Coverage (50 NFRs)

| Catégorie | NFRs | Support architectural | Statut |
| --- | --- | --- | --- |
| Performance | NFR1-9 | Vite 8 (FCP <1,5s), Elasticsearch (<2s), workers parallèles, SSE-C <5% overhead | Couvert |
| Sécurité | NFR10-20 | AES-256 SSE-C, TLS 1.3 Nginx, JWT 15min, 2FA TOTP, CSP, workers sandboxés Docker | Couvert |
| Scalabilité | NFR21-25 | Workers Celery horizontaux, MinIO distribué, Elasticsearch shards | Couvert |
| Fiabilité | NFR26-30 | tus resumable upload, hash chain daily verification, Docker health checks | Couvert |
| Accessibilité | NFR31-35 | eslint-plugin-jsx-a11y, axe-core, Ant Design a11y natif, Lighthouse CI | Couvert |
| Intégration | NFR36-40 | DRF + OpenAPI 3.0, IMAP polling Celery, API <500ms | Couvert |
| Maintenabilité | NFR41-45 | Docker Compose deploy, structlog JSON, `/health` endpoint, Prometheus | Couvert |
| Conformité | NFR46-50 | Hash chain audit signé, WORM Object Lock, certificats destruction, RGPD suppression logique | Couvert |

**Résultat : 50/50 NFRs couverts architecturalement.**

### Implementation Readiness Validation

#### Decision Completeness

- Toutes les décisions critiques sont documentées avec versions spécifiques (Django 5.2, Ant Design v6, TanStack Query v5, Redis 7.x, etc.)
- Les décisions différées sont clairement marquées Post-MVP : LDAP/SSO (Phase 2), eIDAS (Phase 2), Kubernetes (Phase 2), SaaS (Phase 3)
- Les patterns d'implémentation couvrent 25 points de conflit potentiels avec exemples de code
- Les conventions d'enforcement sont listées avec les outils automatisés (Ruff, ESLint, pre-commit, CI)

#### Structure Completeness

- Arborescence complète avec fichiers nommés pour backend (apps Django) et frontend (composants, hooks, stores, pages)
- Infrastructure Docker complète avec tous les services et leur configuration
- Mapping FR → répertoire explicite pour chaque domaine fonctionnel
- Mapping cross-cutting concerns → fichiers spécifiques

#### Pattern Completeness

- Naming conventions couvrent : DB, API, backend Python, frontend TypeScript (avec anti-patterns)
- Format patterns : réponses succès (liste paginée, objet unique), erreurs RFC 7807, conventions de format (dates, UUIDs, etc.)
- Communication patterns : WebSocket events, Celery tasks, state management frontend (avec code TypeScript)
- Process patterns : error handling (backend exceptions + frontend), loading states, logging structuré

### Gap Analysis Results

#### Gaps critiques

Aucun gap critique détecté. Toutes les exigences fonctionnelles et non-fonctionnelles ont un support architectural documenté.

#### Gaps importants (non bloquants, à traiter dans les stories)

1. **Stratégie d'extension Mayan** — Le processus exact pour étendre les apps Mayan existantes (`documents/`, `search/`) sera détaillé dans les stories d'implémentation concernées
2. **Schema Elasticsearch** — Les mappings d'index (champs, analyseurs, tokenizers français) seront définis lors de l'implémentation de la recherche (FR29-FR33)
3. **Configuration MinIO Object Lock** — Le mode exact (Compliance vs Governance) et les durées de rétention par défaut seront définis dans les stories du coffre-fort (FR20-FR28)

#### Gaps "nice-to-have" (post-MVP ou documentation complémentaire)

- Diagramme d'entités-relations (ERD) — utile pour visualiser les relations, mais les models.py servent de référence
- Spécification OpenAPI draft — sera générée automatiquement par DRF à partir des serializers
- Playbook de disaster recovery — documentation opérationnelle post-MVP

### Architecture Completeness Checklist

#### Requirements Analysis

- [x] Contexte projet analysé en profondeur (57 FRs, 50 NFRs, 5 personas)
- [x] Échelle et complexité évaluées (Élevé/Enterprise, 10-12 composants)
- [x] Contraintes techniques identifiées (fork Mayan, MinIO WORM, SSE-C, on-premise)
- [x] Préoccupations transversales cartographiées (8 cross-cutting concerns)

#### Architectural Decisions

- [x] Décisions critiques documentées avec versions (15+ décisions technologiques)
- [x] Stack technologique entièrement spécifiée (backend + frontend + infra)
- [x] Patterns d'intégration définis (REST, WebSocket, tus, Celery)
- [x] Considérations de performance adressées (FCP, recherche, OCR, SSE-C)

#### Implementation Patterns

- [x] Conventions de nommage établies (DB, API, Python, TypeScript)
- [x] Patterns de structure définis (apps Django, modules React)
- [x] Patterns de communication spécifiés (WebSocket events, Celery tasks, state management)
- [x] Patterns de processus documentés (error handling, loading states, logging)

#### Project Structure

- [x] Structure de répertoires complète définie (backend + frontend + infrastructure)
- [x] Limites des composants établies (services Docker, routing Nginx)
- [x] Points d'intégration cartographiés (API boundaries, data boundaries)
- [x] Mapping exigences → structure complété (FR → directories, cross-cutting → files)

### Architecture Readiness Assessment

**Statut global : PRÊT POUR L'IMPLÉMENTATION**

**Niveau de confiance : Élevé**

**Forces clés :**

- Fondation solide via le fork Mayan EDMS 4.11 (60-70% infrastructure GED réutilisée)
- Séparation nette backend API / frontend SPA (indépendance de déploiement et développement)
- Conformité NF Z42-013 intégrée dès la conception (WORM, hash chain, certificats)
- Stack technologique 2026 avec versions stables et compatibles
- Patterns d'implémentation détaillés avec exemples de code pour guider les agents IA
- Séquence d'implémentation ordonnée avec dépendances inter-composants explicites

**Axes d'amélioration futurs :**

- ERD formel pour visualiser les relations entre modèles
- Tests de charge (k6/Locust) pour valider les NFRs de performance
- Documentation de migration Mayan (guide pour synchroniser les mises à jour upstream)
- Hardening guide sécurité pour le déploiement production

### Implementation Handoff

#### Guidelines pour les agents IA

1. Suivre **toutes les décisions architecturales** exactement comme documentées — ne pas substituer de technologies alternatives
2. Utiliser les **patterns d'implémentation** de manière cohérente sur tous les composants
3. Respecter la **structure projet** et les **limites des composants** — ne pas créer de fichiers hors de l'arborescence définie
4. Consulter ce document pour **toute question architecturale** avant de prendre une décision
5. Appliquer les **10 règles d'enforcement** listées dans la section Implementation Patterns
6. Placer la logique métier dans `services.py` (backend) ou hooks custom (frontend), **jamais dans les views/composants**
7. Utiliser les exceptions `IgarException` pour les erreurs métier, **jamais** `raise Exception("...")`

#### Première priorité d'implémentation

```bash
# 1. Initialiser le fork Mayan EDMS
git clone https://gitlab.com/mayan-edms/mayan-edms.git backend
cd backend && git checkout v4.11
git remote rename origin mayan-upstream

# 2. Initialiser le frontend React
npm create vite@latest frontend -- --template react-swc-ts
cd frontend && npm install antd @ant-design/pro-components @ant-design/icons
npm install @tanstack/react-query zustand react-router-dom

# 3. Configurer l'infrastructure Docker
# Créer infrastructure/docker-compose.yml avec tous les services
```
