---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/prd-validation-report.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
---

# Igar - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Igar, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

#### Capture & Ingestion de Documents

- **FR1:** L'utilisateur peut deposer jusqu'a 500 documents par lot via glisser-deposer dans l'interface
- **FR2:** L'utilisateur peut importer des documents via un selecteur de fichiers (fichier unique ou dossier complet)
- **FR3:** Le systeme ingere automatiquement les documents recus par email via un connecteur IMAP
- **FR4:** Un systeme externe peut soumettre un document avec ses metadonnees via l'API REST d'ingestion
- **FR5:** L'utilisateur peut suivre la progression de l'ingestion en temps reel (statut par document)
- **FR6:** Le systeme reprend automatiquement les uploads interrompus par une perte de connexion

#### Intelligence & Classification Automatique

- **FR7:** Le systeme extrait le texte de documents PDF et images via OCR
- **FR8:** Le systeme classifie automatiquement un document par type parmi les categories configurees (facture, contrat, courrier, deliberation, arrete, ordonnance, compte-rendu, bon de commande, bulletin de paie, document d'identite)
- **FR9:** Le systeme extrait automatiquement les metadonnees cles d'un document (date, montant, entites nommees, numero de reference)
- **FR10:** L'utilisateur peut valider ou corriger les metadonnees pre-remplies par l'IA en un clic
- **FR11:** L'utilisateur peut assigner manuellement un type et des metadonnees si la classification automatique echoue

#### Visualisation & Consultation

- **FR12:** L'utilisateur peut consulter un document PDF directement dans le visualiseur integre
- **FR13:** L'utilisateur peut consulter des documents Office (Word, Excel, PowerPoint) dans le visualiseur integre
- **FR14:** L'utilisateur peut consulter des images (JPEG, PNG, TIFF) dans le visualiseur integre
- **FR15:** L'utilisateur peut lire des fichiers audio directement dans le visualiseur integre
- **FR16:** L'utilisateur peut lire des fichiers video directement dans le visualiseur integre
- **FR17:** L'utilisateur peut consulter le contenu d'une archive (ZIP, RAR) dans le visualiseur integre
- **FR18:** Le systeme affiche un filigrane dynamique (nom d'utilisateur + horodatage) lors de chaque consultation
- **FR19:** Le filigrane est rendu cote serveur et ne peut pas etre desactive cote client

#### Archivage & Immuabilite (SAE)

- **FR20:** Le systeme scelle un document dans le coffre-fort WORM apres validation utilisateur
- **FR21:** Le systeme genere une empreinte SHA-256 unique pour chaque document scelle
- **FR22:** Le systeme applique automatiquement une duree de conservation (Object Lock Retention) selon le plan de classement
- **FR23:** Le systeme interdit toute suppression ou modification d'un document scelle avant l'expiration de sa duree de conservation
- **FR24:** Le systeme chiffre chaque document avec une cle AES-256 unique (SSE-C) avant stockage
- **FR25:** Le systeme stocke chaque document sous un nom UUID sans lien avec le nom original
- **FR26:** Le systeme genere un certificat de scellement pour chaque document archive (horodatage + empreinte + metadonnees)
- **FR27:** L'utilisateur peut verifier l'integrite d'un document archive a tout moment
- **FR28:** Le systeme effectue des verifications d'integrite periodiques automatisees sur l'ensemble des documents archives

#### Recherche & Decouverte

- **FR29:** L'utilisateur peut rechercher des documents par mots-cles dans le contenu full-text (y compris le texte OCR)
- **FR30:** L'utilisateur peut filtrer les resultats de recherche par metadonnees (type, date, auteur, service)
- **FR31:** Le systeme surligne les termes recherches dans le visualiseur integre
- **FR32:** L'utilisateur peut parcourir les documents via le plan de classement (arborescence hierarchique)
- **FR33:** L'utilisateur peut combiner recherche full-text et filtres par metadonnees

#### Cycle de Vie & Conformite

- **FR34:** L'administrateur peut configurer un plan de classement avec des durees de conservation par type de document
- **FR35:** Le systeme notifie les responsables conformite lorsqu'un document approche de sa date d'expiration (90j, 30j, 7j)
- **FR36:** Le responsable conformite peut decider de detruire, prolonger ou reporter la conservation d'un document arrive a echeance
- **FR37:** La destruction d'un document necessite la double validation de deux personnes distinctes
- **FR38:** Le systeme genere un certificat de destruction signe pour chaque document detruit (empreinte originale, dates, validateurs, motif)
- **FR39:** Le certificat de destruction est lui-meme scelle et archive dans le coffre-fort
- **FR40:** Le systeme applique une suppression logique avec masquage des donnees personnelles en cas de demande RGPD sur un document a valeur probante

#### Gestion des Utilisateurs & Securite

- **FR41:** L'administrateur peut creer, modifier et desactiver des comptes utilisateurs
- **FR42:** L'administrateur peut definir des roles et permissions (RBAC) par groupe d'utilisateurs
- **FR43:** L'administrateur peut restreindre l'acces a des espaces documentaires specifiques par role
- **FR44:** Le systeme impose l'authentification a deux facteurs (2FA) pour tous les utilisateurs
- **FR45:** Le systeme journalise toutes les actions utilisateur dans un audit trail immuable (depot, consultation, recherche, tentative de suppression, modification de droits)
- **FR46:** L'utilisateur ne peut jamais acceder a un document hors de son perimetre autorise, y compris via la recherche full-text

#### Administration & Configuration

- **FR47:** L'administrateur peut configurer les canaux de capture (email IMAP, API REST)
- **FR48:** L'administrateur peut gerer le plan de classement (creer, modifier, desactiver des categories et durees de conservation)
- **FR49:** L'administrateur peut consulter un tableau de bord affichant les indicateurs cles (volume de documents, espace de stockage, disponibilite, alertes de securite)
- **FR50:** L'administrateur peut consulter les logs d'audit trail et les exporter
- **FR51:** L'administrateur peut configurer les parametres de securite (politique de mots de passe, 2FA, sessions)

#### API & Integration

- **FR52:** Un systeme externe peut deposer un document avec metadonnees via l'API REST
- **FR53:** Un systeme externe peut rechercher des documents via l'API REST
- **FR54:** Un systeme externe peut recuperer un document et ses metadonnees via l'API REST
- **FR55:** Un systeme externe peut verifier l'integrite d'un document via l'API REST
- **FR56:** Un systeme externe peut obtenir le certificat de scellement d'un document via l'API REST
- **FR57:** L'API REST retourne l'empreinte SHA-256 et le statut de scellement pour chaque document

### NonFunctional Requirements

#### Performance

- **NFR1:** Les actions utilisateur courantes (navigation, ouverture de vue) s'executent en moins de 1,5 seconde (First Contentful Paint)
- **NFR2:** L'interface est interactive en moins de 3 secondes (Time to Interactive)
- **NFR3:** Une recherche full-text sur un corpus de 100 000 documents retourne des resultats en moins de 2 secondes
- **NFR4:** L'acceptation d'un lot de 50 fichiers en drag & drop s'effectue en moins de 5 secondes
- **NFR5:** Le visualiseur affiche la premiere page d'un PDF de 50 pages en moins de 2 secondes
- **NFR6:** Le visualiseur demarre la lecture d'une video 1080p en moins de 3 secondes
- **NFR7:** Le traitement OCR/IA d'un document unitaire s'effectue en moins de 5 secondes
- **NFR8:** L'indexation d'un document dans Elasticsearch est disponible en recherche en moins de 30 secondes apres depot
- **NFR9:** Le surcout de chiffrement/dechiffrement SSE-C est inferieur a 5% sur les operations de lecture/ecriture

#### Securite

- **NFR10:** Toutes les donnees au repos sont chiffrees en AES-256 via SSE-C (une cle unique par document)
- **NFR11:** Toutes les communications sont chiffrees en transit via TLS 1.3
- **NFR12:** Les cles de chiffrement sont stockees dans un systeme de base de donnees distinct du stockage objet, verifie par audit de separation des responsabilites
- **NFR13:** L'authentification 2FA est obligatoire pour tous les comptes utilisateurs sans exception
- **NFR14:** Les tokens JWT expirent apres 15 minutes (access token) avec refresh token httpOnly
- **NFR15:** Une politique CSP stricte est appliquee, validee par un score A+ sur Mozilla Observatory et zero directive unsafe-inline ou unsafe-eval en production
- **NFR16:** Une protection anti-CSRF est active sur 100% des operations de mutation, verifie par scan automatise retournant zero finding CSRF
- **NFR17:** Les workers OCR/IA s'executent dans des conteneurs isoles avec ressources limitees (CPU, memoire, timeout)
- **NFR18:** Zero faille de securite critique (CVSS >= 9.0) non corrigee sous 48 heures
- **NFR19:** Zero faille de securite elevee (CVSS >= 7.0) non corrigee sous 7 jours
- **NFR20:** Les noms de fichiers stockes (UUID) ne permettent aucune correlation avec le contenu ou le nom original du document

#### Scalabilite

- **NFR21:** Le systeme supporte 100 utilisateurs simultanes au MVP sans degradation de performance
- **NFR22:** Le systeme supporte 500 utilisateurs simultanes en cible 24 mois
- **NFR23:** Le systeme gere 100 000 documents par instance au MVP, 1 million en cible 24 mois
- **NFR24:** L'architecture de conteneurisation permet le scaling horizontal des workers OCR/IA independamment du backend
- **NFR25:** L'ajout de workers Celery supplementaires augmente lineairement la capacite de traitement OCR/IA

#### Fiabilite & Disponibilite

- **NFR26:** Disponibilite cible de 99,5% au MVP, 99,9% en cible 12 mois
- **NFR27:** Aucune perte de donnees en cas de panne d'un composant unique
- **NFR28:** Les uploads interrompus sont repris automatiquement a la reconnexion sans perte de donnees
- **NFR29:** La verification d'integrite periodique detecte toute corruption silencieuse de donnees dans un delai maximum de 24 heures
- **NFR30:** En cas de panne MinIO, le systeme bascule en mode degrade (lecture seule depuis replica) plutot qu'en indisponibilite totale

#### Accessibilite

- **NFR31:** L'interface respecte le niveau AA des WCAG 2.1 / RGAA pour les clients du secteur public
- **NFR32:** Toute la navigation est accessible au clavier sans souris
- **NFR33:** L'interface est compatible avec les lecteurs d'ecran (ARIA landmarks, labels, live regions), verifie par test avec NVDA/VoiceOver
- **NFR34:** Les contrastes de couleurs respectent un ratio minimum de 4,5:1
- **NFR35:** Les textes alternatifs sont fournis pour tous les elements visuels non decoratifs

#### Integration

- **NFR36:** L'API REST respecte les conventions RESTful et retourne des reponses JSON structurees avec codes HTTP standard
- **NFR37:** L'API REST est documentee au format OpenAPI 3.0 (Swagger) et maintenue a jour
- **NFR38:** Le temps de reponse moyen de l'API est inferieur a 500ms pour les operations de lecture
- **NFR39:** L'API supporte la pagination, le filtrage et le tri sur toutes les ressources listees
- **NFR40:** Le connecteur IMAP verifie les nouveaux emails au minimum toutes les 5 minutes

#### Maintenabilite & Operabilite

- **NFR41:** Le deploiement d'une nouvelle instance via Docker Compose s'effectue en moins de 30 minutes
- **NFR42:** Les mises a jour de version sont appliquees sans perte de donnees et avec un downtime maximum de 15 minutes
- **NFR43:** Les logs applicatifs sont structures (JSON), horodates et centralisables
- **NFR44:** Le systeme expose des metriques de sante (healthcheck) pour chaque composant avec un endpoint /health
- **NFR45:** La documentation d'installation et de configuration est fournie pour Linux et Windows Server

#### Conformite

- **NFR46:** Le systeme est conforme a la norme NF Z42-013 pour l'archivage electronique a valeur probante
- **NFR47:** Le systeme est conforme au RGPD (droit d'acces, droit a l'effacement avec exception legale, registre des traitements, notification de violation sous 72h)
- **NFR48:** L'audit trail est immuable, horodate et signe cryptographiquement, verifie par un test d'integrite automatise quotidien
- **NFR49:** Toutes les operations de destruction sont documentees par un certificat de destruction scelle
- **NFR50:** Le systeme produit les preuves necessaires pour un audit de conformite NF Z42-013, avec un rapport d'audit generable a la demande

### Additional Requirements

#### Exigences issues de l'Architecture

- **Starter Template Backend** : Fork Mayan EDMS 4.11 (Python/Django 5.2) — fournit 60-70% de l'infrastructure GED (OCR, Elasticsearch, Celery, RBAC, API REST). Impacte Epic 1 Story 1
- **Starter Template Frontend** : create-vite react-swc-ts + Ant Design v6 + Pro Components + TanStack Query v5 + Zustand + React Router v6. Impacte Epic 1
- **Infrastructure Docker Compose** : PostgreSQL (TDE), Redis 7.x, MinIO (Object Lock), Elasticsearch, Nginx, tusd, Gotenberg, Celery workers (queues: ocr, ai, default, compliance), Django Channels (WebSocket), Prometheus, Grafana, Sentry self-hosted
- **Upload resumable** : Protocole tus (tus-js-client + tusd) pour reprise automatique apres interruption (FR6, NFR28)
- **Conversion documents** : Gotenberg 8.x (Docker) pour conversion Office -> PDF via LibreOffice + Chromium
- **Temps reel** : Django Channels + Redis channel layer pour WebSocket (progression uploads, resultats IA, notifications)
- **Authentification** : djangorestframework-simplejwt 5.5.x (access 15min + refresh httpOnly) + django-otp + django-two-factor-auth (TOTP)
- **Audit trail signe** : Chaine de hachage SHA-256 — chaque entree contient le hash de l'entree precedente. Verification automatisee quotidienne
- **Erreurs API** : Format RFC 7807 (Problem Details for HTTP APIs) via custom exception handler DRF
- **Monitoring** : Prometheus + Grafana (metriques), structlog (logs JSON structures), Sentry self-hosted (error tracking)
- **Internationalisation** : react-i18next integre des le MVP, lazy loading des langues, compatible Ant Design ConfigProvider locale
- **Reverse proxy** : Nginx — TLS 1.3 termination, static files, rate limiting, WebSocket proxy
- **Versioning API** : URL path versioning /api/v1/
- **Validation donnees** : DRF Serializers + Pydantic 2.x pour structures metier critiques (certificats, politiques WORM, audit)
- **Cache** : Django cache framework + Redis backend (metadonnees chaudes, sessions, resultats recherche)
- **Protection code** : Cython (coeur SAE/WORM, IA, licence) + PyArmor (Django views, modules Mayan)
- **Testing Backend** : pytest + pytest-django + Factory Boy + pytest-xdist + Coverage.py
- **Testing Frontend** : Vitest + React Testing Library + Playwright + axe-core/jest-axe + Lighthouse CI + eslint-plugin-jsx-a11y
- **Linting** : Ruff (backend), ESLint + Prettier (frontend), pre-commit hooks
- **CI/CD** : GitHub Actions (lint, tests, build, securite)
- **Structure monorepo** : backend/ + frontend/ + infrastructure/ + docs/

#### Exigences issues du UX Design

- **Direction design choisie** : Hybrid Flow — table principale + panel contextuel droit (320px retractable) + tabs navigation + toggle table/cartes + sidebar gauche (220px) + header fixe avec recherche omniprésente
- **Theme "Ocean Profond"** : Design tokens via ConfigProvider Ant Design — Primary #1B3A5C, Accent #10B981, Warning #F59E0B, Error #EF4444, Background #F8FAFC
- **Typographie** : Inter, grille 8px, densite compacte (size="small")
- **7 composants custom obligatoires** : ConfidenceBadge, DocumentViewer, ClassificationResult, DropZoneOverlay, ImportProgressList, SealBadge, ComplianceDashboard
- **Responsive** : Desktop-first (min 1280px), tablette paysage (>=768px) en secondaire, mobile post-MVP
- **Raccourcis clavier** : Ctrl+K (recherche), Escape (fermer), fleches (naviguer), Ctrl+I (import), Ctrl+Entree (plein ecran)
- **Loading states** : Skeleton si >300ms, estimation temps si >2s, optimistic UI
- **Feedback patterns** : Toast succes (3s), notification operation (5s), banner erreur reseau (persistant), badge compteur sur tab
- **Empty states** : Messages humanises avec action proposee pour chaque situation vide
- **Accessibilite WCAG 2.1 AA** : Contraste 4.5:1, focus visible (#4A90D9, 2px), cibles 44x44px, couleur + icone + texte, skip links, aria-live regions
- **Pattern button** : Max 1 primaire par zone, primaire a droite, size="small" par defaut
- **Pattern modale** : Max 1 modale a la fois, jamais modale sur modale, Escape = fermer
- **Pattern notification** : Max 3 simultanees, plus anciennes disparaissent automatiquement
- **Pattern formulaire** : Champs IA visuellement distingues (fond teinte bleu), validation inline temps reel, labels au-dessus

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 2 | Drag & drop 500 documents par lot |
| FR2 | Epic 2 | Import via selecteur fichiers/dossiers |
| FR3 | Epic 2 | Ingestion email IMAP |
| FR4 | Epic 2 | Soumission via API REST ingestion |
| FR5 | Epic 2 | Progression ingestion temps reel |
| FR6 | Epic 2 | Reprise uploads interrompus (tus) |
| FR7 | Epic 2 | OCR sur PDF et images |
| FR8 | Epic 2 | Classification IA par type |
| FR9 | Epic 2 | Extraction metadonnees automatique |
| FR10 | Epic 2 | Validation/correction metadonnees 1 clic |
| FR11 | Epic 2 | Assignation manuelle type/metadonnees |
| FR12 | Epic 4 | Visualiseur PDF integre |
| FR13 | Epic 4 | Visualiseur Office integre |
| FR14 | Epic 4 | Visualiseur images integre |
| FR15 | Epic 4 | Lecteur audio integre |
| FR16 | Epic 4 | Lecteur video integre |
| FR17 | Epic 4 | Visualiseur archives ZIP/RAR |
| FR18 | Epic 4 | Filigrane dynamique consultation |
| FR19 | Epic 4 | Filigrane rendu cote serveur |
| FR20 | Epic 3 | Scellement WORM apres validation |
| FR21 | Epic 3 | Empreinte SHA-256 par document |
| FR22 | Epic 3 | Duree conservation Object Lock |
| FR23 | Epic 3 | Interdiction suppression/modification |
| FR24 | Epic 3 | Chiffrement AES-256 SSE-C |
| FR25 | Epic 3 | Stockage UUID anonymise |
| FR26 | Epic 3 | Certificat de scellement |
| FR27 | Epic 3 | Verification integrite a la demande |
| FR28 | Epic 3 | Verification integrite periodique |
| FR29 | Epic 4 | Recherche full-text + contenu OCR |
| FR30 | Epic 4 | Filtres par metadonnees |
| FR31 | Epic 4 | Surlignage termes recherches |
| FR32 | Epic 4 | Navigation plan de classement |
| FR33 | Epic 4 | Recherche combinee full-text + filtres |
| FR34 | Epic 5 | Plan de classement configurable |
| FR35 | Epic 5 | Notifications echeance (90j/30j/7j) |
| FR36 | Epic 5 | Decision destruction/prolongation/report |
| FR37 | Epic 5 | Double validation destruction |
| FR38 | Epic 5 | Certificat de destruction signe |
| FR39 | Epic 5 | Certificat destruction scelle dans coffre |
| FR40 | Epic 5 | Suppression logique RGPD |
| FR41 | Epic 1 | Gestion comptes utilisateurs |
| FR42 | Epic 1 | RBAC par groupe |
| FR43 | Epic 1 | Restriction acces espaces documentaires |
| FR44 | Epic 1 | 2FA obligatoire |
| FR45 | Epic 5 | Audit trail immuable |
| FR46 | Epic 1 | Cloisonnement recherche full-text |
| FR47 | Epic 5 | Configuration canaux capture |
| FR48 | Epic 5 | Gestion plan de classement |
| FR49 | Epic 5 | Tableau de bord indicateurs |
| FR50 | Epic 5 | Consultation/export audit trail |
| FR51 | Epic 5 | Configuration securite |
| FR52 | Epic 6 | API depot document + metadonnees |
| FR53 | Epic 6 | API recherche documents |
| FR54 | Epic 6 | API recuperation document |
| FR55 | Epic 6 | API verification integrite |
| FR56 | Epic 6 | API certificat scellement |
| FR57 | Epic 6 | API empreinte SHA-256 + statut |

**Couverture : 57/57 FRs mappes.**

## Epic List

### Epic 1: Acces Securise & Gestion des Permissions

Les utilisateurs peuvent se connecter de maniere securisee (2FA), acceder a leur espace documentaire selon leur role, et l'administrateur peut gerer les comptes et permissions. Inclut l'initialisation du fork Mayan EDMS 4.11, la creation du frontend React/Ant Design, l'infrastructure Docker Compose complete, l'authentification JWT + 2FA, le RBAC et le cloisonnement.

**FRs couverts:** FR41, FR42, FR43, FR44, FR46

### Epic 2: Capture Intelligente & Classification IA

Les utilisateurs peuvent importer des documents (drag & drop, fichiers, dossiers, email IMAP, API) et l'IA les classifie automatiquement avec extraction de metadonnees. L'utilisateur valide ou corrige en 1 clic. C'est le "magic moment" d'Igar — le journey de Fatima. Inclut le protocole tus (uploads resumables), les workers OCR/IA Celery, le WebSocket pour la progression temps reel, et les composants UX DropZoneOverlay, ImportProgressList, ClassificationResult, ConfidenceBadge.

**FRs couverts:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10, FR11

### Epic 3: Coffre-Fort Numerique & Archivage a Valeur Probante

Les documents valides sont scelles dans un coffre-fort WORM inviolable avec chiffrement, empreinte cryptographique et certificat de scellement. L'utilisateur peut verifier l'integrite a tout moment. Personne ne peut supprimer ou modifier un document scelle. Coeur du SAE — le journey de Philippe. Inclut MinIO Object Lock, SSE-C AES-256, noms UUID, certificats de scellement, verification d'integrite periodique. Composant UX SealBadge.

**FRs couverts:** FR20, FR21, FR22, FR23, FR24, FR25, FR26, FR27, FR28

### Epic 4: Recherche Instantanee & Consultation Securisee

Les utilisateurs trouvent n'importe quel document en < 2 secondes via recherche full-text avec surlignage, naviguent dans le plan de classement, et consultent tous les formats (PDF, Office, images, audio, video, ZIP) directement dans le visualiseur integre avec filigrane dynamique. Le hub de navigation d'Igar — journeys de Philippe et Amina. Inclut Elasticsearch, Gotenberg, visualiseur universel avec filigrane serveur. Composant UX DocumentViewer. Direction design Hybrid Flow.

**FRs couverts:** FR12, FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR29, FR30, FR31, FR32, FR33

### Epic 5: Cycle de Vie, Conformite & Administration

L'administrateur configure le plan de classement avec durees de conservation, recoit les alertes d'echeance, gere la destruction reglementaire (double validation + certificat), consulte l'audit trail complet et le tableau de bord de conformite. Le systeme gere les demandes RGPD. Le journey de Thomas. Inclut l'automate de conservation, audit trail signe (chaine de hachage), notifications proactives, certificats de destruction scelles, suppression logique RGPD. Composant UX ComplianceDashboard.

**FRs couverts:** FR34, FR35, FR36, FR37, FR38, FR39, FR40, FR45, FR47, FR48, FR49, FR50, FR51

### Epic 6: API REST & Integration Externe

Un systeme externe (ERP, CRM, integrateur) peut deposer, rechercher, recuperer des documents et verifier leur integrite via une API REST documentee OpenAPI 3.0, avec empreinte SHA-256 et certificats de scellement. Le journey de Sarah (developpeuse/integratrice, persona definie dans le PRD — Journey 5). S'appuie sur toutes les fonctionnalites construites dans les epics precedents.

**FRs couverts:** FR52, FR53, FR54, FR55, FR56, FR57

## Epic 1: Acces Securise & Gestion des Permissions

Les utilisateurs peuvent se connecter de maniere securisee (2FA), acceder a leur espace documentaire selon leur role, et l'administrateur peut gerer les comptes et permissions. Inclut l'initialisation du fork Mayan EDMS 4.11, la creation du frontend React/Ant Design, l'infrastructure Docker Compose complete.

### Story 1.1: Mise en Place du Socle Backend pour les Services Documentaires

As a **developpeur**,
I want **initialiser le fork Mayan EDMS 4.11 avec la structure du projet Igar (dossiers igar/apps/, igar/core/, igar/settings/), le fichier pyproject.toml et les dependances**,
So that **le backend dispose d'une base fonctionnelle reutilisant 60-70% de l'infrastructure GED de Mayan**.

**Acceptance Criteria:**

**Given** un environnement de developpement vierge
**When** je clone le fork Mayan EDMS 4.11 et j'applique la structure Igar
**Then** le projet backend demarre avec `manage.py runserver` sans erreur
**And** la structure `igar/apps/`, `igar/core/`, `igar/settings/` est creee conformement a l'architecture
**And** les settings `development.py`, `production.py`, `test.py` sont configures
**And** `pyproject.toml` contient les dependances (Ruff, pytest, pytest-django, Factory Boy, structlog, Pydantic)
**And** la commande `ruff check .` s'execute sans erreur

### Story 1.2: Deploiement Operationnel de la Plateforme Igar

As a **administrateur IT (Thomas)**,
I want **deployer l'ensemble de la stack Igar via Docker Compose en moins de 30 minutes**,
So that **l'infrastructure complete est operationnelle avec tous les services necessaires**.

**Acceptance Criteria:**

**Given** un serveur Linux avec Docker installe
**When** je lance `docker compose up -d` depuis le dossier infrastructure/
**Then** tous les services demarrent : backend (Gunicorn), PostgreSQL (TDE), Redis 7.x, MinIO (avec Object Lock active), Elasticsearch, Nginx (TLS), tusd, Gotenberg, Celery workers (queues ocr, ai, default, compliance), Celery Beat, Django Channels (Daphne)
**And** le endpoint `/health` retourne un statut agrege de tous les composants en moins de 500ms
**And** Nginx route correctement `/` vers frontend, `/api/v1/` vers Django, `/ws/` vers Channels, `/uploads/` vers tusd
**And** le script `init-buckets.sh` cree les buckets MinIO (igar-temp, igar-vault avec Object Lock, igar-thumbnails)
**And** un `docker-compose.dev.yml` override est disponible pour le developpement (volumes, hot-reload)
**And** un fichier `.env.example` documente toutes les variables d'environnement

### Story 1.3: Interface Utilisateur de Base et Theme Igar

As a **developpeur**,
I want **initialiser le frontend SPA React avec Vite 8, TypeScript, Ant Design v6, le theme "Ocean Profond", le routing et l'internationalisation**,
So that **l'interface utilisateur dispose d'une base coherente et thematisee prete pour le developpement des composants**.

**Acceptance Criteria:**

**Given** le projet frontend initialise avec `create-vite react-swc-ts`
**When** je lance `npm run dev`
**Then** l'application demarre avec HMR sur `localhost:5173`
**And** Ant Design v6 + Pro Components sont installes et fonctionnels
**And** le theme "Ocean Profond" est configure via ConfigProvider (Primary #1B3A5C, Accent #10B981, Background #F8FAFC, etc.)
**And** la police Inter est chargee avec la grille 8px et la densite compacte (size="small")
**And** ProLayout est configure avec sidebar (220px repliable vers 64px), header fixe (56px) avec barre de recherche placeholder, et zone de contenu fluide
**And** React Router v6 est configure avec les routes de base (Login, Documents, Import, Conformite, Admin)
**And** react-i18next est configure avec les fichiers fr.json et en.json (labels de base)
**And** Zustand stores sont initialises (authStore, uiStore)
**And** TanStack Query est configure avec le QueryClientProvider
**And** le client API (Axios) est configure avec le base URL et l'intercepteur JWT
**And** ESLint + Prettier + eslint-plugin-jsx-a11y sont configures
**And** Vitest + React Testing Library sont configures et un test basique passe
**And** `npm run build` produit un build de production sans erreur

### Story 1.4: Authentification JWT & Interface de Connexion

As a **utilisateur**,
I want **me connecter a Igar avec mon identifiant et mot de passe via une page de connexion securisee**,
So that **j'accede a mon espace documentaire de maniere authentifiee et protegee**.

**Acceptance Criteria:**

**Given** un utilisateur avec un compte existant dans le systeme
**When** il saisit ses identifiants sur la page de connexion (LoginPage)
**Then** le systeme verifie les identifiants via l'API `/api/v1/auth/login/`
**And** en cas de succes, un access token JWT (15 min TTL) et un refresh token (httpOnly cookie) sont emis (NFR14)
**And** l'utilisateur est redirige vers la vue Documents
**And** en cas d'echec, un message d'erreur humain est affiche (RFC 7807) sans reveler si c'est l'identifiant ou le mot de passe qui est incorrect
**And** le refresh token renouvelle automatiquement l'access token expire via l'intercepteur Axios
**And** la deconnexion invalide les tokens et redirige vers la page de connexion
**And** la page de connexion respecte le theme "Ocean Profond" et est accessible au clavier (WCAG 2.1 AA)
**And** toutes les communications sont en TLS 1.3 (NFR11)
**And** une protection anti-CSRF est active (NFR16)

### Story 1.5: Authentification a Deux Facteurs (2FA)

As a **utilisateur**,
I want **configurer et utiliser l'authentification a deux facteurs (TOTP) pour securiser mon acces**,
So that **mon compte est protege meme si mon mot de passe est compromis** (FR44).

**Acceptance Criteria:**

**Given** un utilisateur authentifie par mot de passe
**When** le 2FA n'est pas encore configure
**Then** l'utilisateur est redirige vers l'ecran de configuration 2FA (affichage QR code TOTP compatible Google Authenticator / Authy)
**And** apres scan du QR code et saisie du code de verification, le 2FA est active
**And** lors des connexions suivantes, apres le mot de passe, un ecran demande le code TOTP
**And** le code TOTP est verifie cote serveur (django-otp)
**And** le 2FA est obligatoire pour TOUS les comptes sans exception (NFR13)
**And** l'administrateur peut reinitialiser le 2FA d'un utilisateur en cas de perte de l'appareil
**And** les tentatives de connexion echouees sont journalisees
**And** l'interface 2FA est accessible au clavier et compatible lecteurs d'ecran

### Story 1.6: Gestion des Utilisateurs, Roles et Cloisonnement

As a **administrateur (Thomas)**,
I want **creer des utilisateurs, definir des roles avec permissions, et restreindre l'acces aux espaces documentaires par role**,
So that **chaque utilisateur n'accede qu'aux documents de son perimetre autorise** (FR41, FR42, FR43, FR46).

**Acceptance Criteria:**

**Given** un administrateur connecte avec le role administrateur
**When** il accede a la page d'administration des utilisateurs
**Then** il peut creer, modifier et desactiver des comptes utilisateurs (FR41)
**And** il peut creer des roles (ex : Direction, Comptabilite, RH, Production) avec des permissions granulaires (FR42)
**And** il peut associer des utilisateurs a des groupes/roles
**And** il peut restreindre l'acces a des espaces documentaires specifiques par role (FR43)
**And** un utilisateur ne peut jamais acceder a un document hors de son perimetre autorise, y compris via la recherche full-text (FR46)
**And** les modifications de droits sont journalisees dans l'audit trail
**And** l'interface d'administration utilise ProTable et ProForm (Ant Design)
**And** la page respecte le theme "Ocean Profond" et les principes d'accessibilite WCAG 2.1 AA

## Epic 2: Capture Intelligente & Classification IA

Les utilisateurs peuvent importer des documents (drag & drop, fichiers, dossiers, email IMAP, API) et l'IA les classifie automatiquement avec extraction de metadonnees. L'utilisateur valide ou corrige en 1 clic. C'est le "magic moment" d'Igar — le journey de Fatima.

### Story 2.1: Upload de Documents par Drag & Drop et Selecteur de Fichiers

As a **utilisateur (Fatima)**,
I want **deposer des documents par glisser-deposer (jusqu'a 500 fichiers) ou via un selecteur de fichiers/dossiers sur l'interface**,
So that **je peux importer rapidement tous mes documents sans friction** (FR1, FR2).

**Acceptance Criteria:**

**Given** un utilisateur authentifie sur la vue Documents
**When** il glisse des fichiers sur la fenetre
**Then** le composant DropZoneOverlay apparait en plein ecran (fond semi-transparent, icone animee, texte "Deposez vos documents ici")
**And** au relachement, les fichiers sont acceptes en moins de 5 secondes pour un lot de 50 (NFR4)
**And** l'upload demarre via le protocole tus (resumable)
**And** le tab "Import en cours" s'active avec un badge compteur
**And** un bouton "Importer" est disponible en alternative pour le clavier/accessibilite
**And** le selecteur de fichiers accepte fichiers individuels et dossiers complets (FR2)
**And** les formats acceptes incluent : PDF, Office (docx/xlsx/pptx), images (jpg/png/tiff), emails (.eml/.msg), audio, video, ZIP
**And** l'overlay disparait avec fade-out si l'utilisateur sort de la zone sans deposer
**And** l'overlay est accessible : le bouton "Importer" est toujours focusable au clavier

### Story 2.2: Upload Resumable et Progression Temps Reel

As a **utilisateur (Fatima)**,
I want **suivre la progression de l'upload en temps reel et que les uploads interrompus reprennent automatiquement**,
So that **je ne perds jamais de fichiers meme en cas de coupure reseau** (FR5, FR6).

**Acceptance Criteria:**

**Given** un lot de fichiers en cours d'upload
**When** l'upload est en cours
**Then** le composant ImportProgressList affiche une barre de progression globale ("12/50 uploades") et une barre par fichier
**And** la progression est mise a jour en temps reel via WebSocket (Django Channels)
**And** si la connexion est interrompue, l'upload reprend automatiquement au point d'arret via le protocole tus (NFR28)
**And** un message "Connexion interrompue — reconnexion en cours..." s'affiche en banner persistant
**And** apres reconnexion, un toast confirme la reprise "Upload repris — aucun fichier perdu"
**And** les fichiers uploades sont stockes dans le bucket MinIO `igar-temp` (TTL 24h)
**And** l'utilisateur peut continuer a naviguer dans l'application pendant l'upload (non-bloquant)

### Story 2.3: Pipeline OCR — Extraction de Texte

As a **utilisateur (Fatima)**,
I want **que le systeme extraie automatiquement le texte des documents PDF et images via OCR**,
So that **le contenu devient recherchable et analysable par l'IA** (FR7).

**Acceptance Criteria:**

**Given** un document PDF ou image uploade dans `igar-temp`
**When** le pipeline de traitement est declenche
**Then** un worker Celery (queue `ocr`) execute l'OCR via Tesseract 5
**And** le texte extrait est stocke en metadonnee associee au document
**And** le traitement OCR d'un document unitaire s'effectue en moins de 5 secondes (NFR7)
**And** la progression est envoyee via WebSocket (evenement `upload.progress`)
**And** les workers OCR s'executent dans des conteneurs isoles avec ressources limitees (NFR17)
**And** en cas d'echec OCR (document illisible, image trop basse resolution), le document est marque "OCR echoue" et continue dans le pipeline avec metadonnees vides
**And** les logs structures (structlog) tracent chaque traitement OCR avec document_uuid, duree, et statut

### Story 2.4: Classification IA et Extraction de Metadonnees

As a **utilisateur (Fatima)**,
I want **que l'IA classifie automatiquement chaque document par type et pre-remplisse les metadonnees (date, montant, entites)**,
So that **90% de mes documents sont classes sans intervention manuelle** (FR8, FR9).

**Acceptance Criteria:**

**Given** un document dont le texte a ete extrait par OCR
**When** le worker IA (queue `ai`) traite le document
**Then** le systeme classifie le document parmi les types configures : facture, contrat, courrier, deliberation, arrete, ordonnance, compte-rendu, bon de commande, bulletin de paie, document d'identite (FR8)
**And** le systeme extrait les metadonnees cles : date, montant, entites nommees, numero de reference (FR9)
**And** un score de confiance est attribue (0-100%)
**And** le resultat est envoye au frontend via WebSocket (evenement `classification.result` avec type, confidence, metadonnees)
**And** le document apparait dans l'ImportProgressList avec un ClassificationResult et un ConfidenceBadge
**And** les badges de confiance suivent les seuils : vert (>=85%), orange (50-84%), rouge (<50%)
**And** le traitement complet (OCR + IA) d'un document s'effectue en moins de 5 secondes (NFR7)
**And** en cas d'echec de classification, le document est marque "Non reconnu" avec badge rouge

### Story 2.5: Validation et Correction des Metadonnees par l'Utilisateur

As a **utilisateur (Fatima)**,
I want **valider ou corriger les metadonnees pre-remplies par l'IA en un clic**,
So that **je controle la qualite du classement tout en profitant de l'automatisation** (FR10, FR11).

**Acceptance Criteria:**

**Given** un document classifie par l'IA avec ses metadonnees pre-remplies
**When** le niveau de confiance est eleve (>=85%)
**Then** le document est auto-valide avec badge vert, aucune action requise

**Given** un document avec confiance moyenne (50-84%)
**When** l'utilisateur voit le ClassificationResult avec 2 suggestions alternatives
**Then** il peut cliquer sur la bonne suggestion pour corriger en 1 clic (FR10)
**And** le badge se met a jour instantanement

**Given** un document avec confiance basse (<50%) ou "Non reconnu"
**When** l'utilisateur voit le ClassificationResult avec un selecteur de type
**Then** il peut assigner manuellement un type et remplir les metadonnees (FR11)

**And** les champs pre-remplis par l'IA sont visuellement distingues (fond legerement teinte bleu, label "IA")
**And** les metadonnees sont affichees au survol et editables au clic
**And** un compteur global resume le statut : "47/50 classes automatiquement (94%)"
**And** les corrections utilisateur sont enregistrees pour le document

### Story 2.6: Validation en Masse et Lancement du Scellement

As a **utilisateur (Fatima)**,
I want **valider et archiver un lot complet de documents en une seule action**,
So that **le processus de classement se conclut rapidement et les documents sont prets pour le scellement** (les documents passent au statut "En attente de scellement" dans la base de donnees — le scellement effectif sera implemente dans Epic 3).

**Acceptance Criteria:**

**Given** un lot de documents entierement traite (tous les OCR/IA termines)
**When** l'utilisateur consulte l'ImportProgressList avec le resume final
**Then** un toast "Import termine — 50 documents classes" apparait
**And** un bouton "Valider et archiver" est affiche
**And** l'utilisateur peut choisir "Valider tout" (scellement en masse) ou "Valider haute confiance, reviser les moyennes"
**And** apres validation, les documents passent au statut "En attente de scellement" (le scellement effectif est traite par Epic 3)
**And** les documents valides apparaissent dans le tab "Documents" avec un badge "En attente de scellement"
**And** le badge compteur du tab "Import en cours" disparait quand le lot est completement traite

### Story 2.7: Ingestion Automatique par Email (IMAP)

As a **administrateur (Thomas)**,
I want **configurer un connecteur email IMAP pour que les documents recus par email soient automatiquement ingeres dans Igar**,
So that **les courriers electroniques sont captures sans intervention manuelle** (FR3).

**Acceptance Criteria:**

**Given** un administrateur connecte
**When** il configure une source IMAP (serveur, port, identifiants, dossier a surveiller) via l'interface d'administration
**Then** un worker Celery (queue `default`) verifie les nouveaux emails selon la frequence configuree (minimum toutes les 5 minutes, NFR40)
**And** les pieces jointes des emails sont extraites et ingerees dans le pipeline OCR/IA
**And** les metadonnees de l'email (expediteur, objet, date) sont associees aux documents
**And** les emails deja traites ne sont pas re-traites (marquage lu ou deplacement)
**And** les documents ingeres apparaissent dans la liste des documents avec la source "Email IMAP"
**And** en cas d'erreur de connexion IMAP, une alerte est generee et journalisee
**And** l'administrateur peut activer/desactiver un connecteur IMAP sans redemarrage

## Epic 3: Coffre-Fort Numerique & Archivage a Valeur Probante

Les documents valides sont scelles dans un coffre-fort WORM inviolable avec chiffrement, empreinte cryptographique et certificat de scellement. L'utilisateur peut verifier l'integrite a tout moment. Personne ne peut supprimer ou modifier un document scelle. Coeur du SAE — le journey de Philippe.

### Story 3.1: Abstraction de Stockage MinIO et Chiffrement SSE-C

As a **developpeur**,
I want **une couche d'abstraction S3 avec chiffrement SSE-C AES-256 par document et nommage UUID**,
So that **chaque document stocke est chiffre avec sa propre cle et illisible sans Igar** (FR24, FR25).

**Acceptance Criteria:**

**Given** un document valide pret a etre stocke
**When** le service de stockage est appele
**Then** une cle AES-256 unique est generee pour ce document
**And** la cle est stockee dans PostgreSQL (TDE) liee a l'UUID du document
**And** le document est envoye a MinIO via `PutObject` avec le header SSE-C contenant la cle
**And** le nom du fichier dans MinIO est un UUID v4 sans lien avec le nom original (FR25, NFR20)
**And** la lecture du document requiert la cle SSE-C via le header a chaque requete
**And** sans la cle (acces direct au disque MinIO), le fichier est un blob binaire illisible
**And** le surcout de chiffrement/dechiffrement est inferieur a 5% (NFR9)
**And** les operations de stockage sont tracees via structlog

### Story 3.2: Scellement WORM et Object Lock

As a **utilisateur (Philippe)**,
I want **que mes documents soient scelles dans un coffre-fort WORM apres validation, avec impossibilite de suppression ou modification**,
So that **mes documents ont une valeur probante juridique incontestable** (FR20, FR22, FR23).

**Acceptance Criteria:**

**Given** un document valide par l'utilisateur (statut "En attente de scellement" depuis Epic 2)
**When** le service de scellement est declenche
**Then** le document est transfere de `igar-temp` vers `igar-vault` avec Object Lock en mode Compliance
**And** la duree de retention Object Lock est appliquee selon le type de document dans le plan de classement (FR22)
**And** toute tentative de suppression ou modification avant l'expiration est rejetee par MinIO avec un message explicatif (FR23)
**And** le scellement peut etre declenche en masse (lot de documents)
**And** la progression du scellement en masse est communiquee via WebSocket (evenement `seal.completed`)
**And** le badge du document passe de "En attente" a "Scelle" (composant SealBadge vert avec icone cadenas)
**And** le scellement est journalise dans l'audit trail

### Story 3.3: Empreinte SHA-256 et Certificat de Scellement

As a **utilisateur (Philippe)**,
I want **que chaque document scelle possede une empreinte SHA-256 et un certificat de scellement verifiable**,
So that **je peux prouver l'integrite et l'authenticite de mes documents** (FR21, FR26).

**Acceptance Criteria:**

**Given** un document en cours de scellement
**When** le service de scellement genere le certificat
**Then** une empreinte SHA-256 est calculee sur le contenu original du document (FR21)
**And** l'empreinte est stockee en base PostgreSQL associee au document
**And** un certificat de scellement est genere contenant : identifiant unique du certificat, UUID du document, empreinte SHA-256, date et heure de scellement (horodatage), metadonnees du document, identite de l'utilisateur validateur (FR26)
**And** le certificat est lui-meme stocke dans `igar-vault` (scelle)
**And** le certificat est telechargeable en PDF depuis le composant SealBadge (popover au clic)
**And** le popover SealBadge affiche : empreinte SHA-256 (tronquee), date de scellement, duree de conservation

### Story 3.4: Verification d'Integrite a la Demande

As a **utilisateur (Philippe)**,
I want **verifier l'integrite d'un document archive a tout moment**,
So that **je peux confirmer qu'un document n'a pas ete altere depuis son scellement** (FR27).

**Acceptance Criteria:**

**Given** un document scelle dans le coffre-fort
**When** l'utilisateur clique sur "Verifier l'integrite" depuis le SealBadge ou le panel contextuel
**Then** le systeme recalcule l'empreinte SHA-256 du document stocke dans MinIO
**And** compare l'empreinte recalculee avec l'empreinte stockee en base
**And** si les empreintes correspondent : affiche "Document integre — identique depuis le [date scellement]" avec icone verte
**And** si les empreintes ne correspondent pas : affiche une alerte rouge "ALERTE — Integrite compromise" et journalise l'anomalie immediatement
**And** la verification est journalisee dans l'audit trail (identite, horodatage, resultat)
**And** le temps de verification est raisonnable (<3 secondes pour un document de 50Mo)

### Story 3.5: Verification d'Integrite Periodique Automatisee

As a **administrateur (Thomas)**,
I want **que le systeme verifie periodiquement l'integrite de tous les documents archives**,
So that **toute corruption silencieuse est detectee automatiquement en moins de 24 heures** (FR28, NFR29).

**Acceptance Criteria:**

**Given** des documents scelles dans le coffre-fort `igar-vault`
**When** la tache Celery periodique de verification d'integrite s'execute (planifiee via Celery Beat)
**Then** le systeme recalcule l'empreinte SHA-256 de chaque document et la compare avec l'empreinte stockee
**And** toute anomalie detectee declenche une alerte immediate (notification, log CRITICAL, email si configure)
**And** l'ensemble du corpus est verifie dans un delai maximum de 24 heures (NFR29)
**And** la verification est executee par le worker Celery (queue `compliance`)
**And** les resultats sont journalises : nombre de documents verifies, duree, anomalies detectees
**And** un resume de la derniere verification est visible dans le futur tableau de bord conformite (Epic 5)

### Story 3.6: Protection Contre la Suppression et Message Explicatif

As a **utilisateur (Philippe)**,
I want **que toute tentative de suppression d'un document scelle soit bloquee avec un message explicatif clair**,
So that **je comprends pourquoi le document est protege et jusqu'a quand** (FR23).

**Acceptance Criteria:**

**Given** un document scelle en mode Compliance WORM
**When** un utilisateur tente de supprimer le document (via l'interface ou l'API)
**Then** la suppression est refusee
**And** un message explicatif humain est affiche : "Document protege — conservation jusqu'au [date]. Raison : [politique de conservation]." (pas de jargon technique)
**And** l'erreur API suit le format RFC 7807 avec type "document-protected", status 403
**And** la tentative de suppression est journalisee dans l'audit trail (identite, document, horodatage)
**And** le message est affiche dans un composant Result d'Ant Design (pas un blocage sec)
**And** meme un administrateur ne peut pas supprimer un document en mode Compliance avant expiration

## Epic 4: Recherche Instantanee & Consultation Securisee

Les utilisateurs trouvent n'importe quel document en < 2 secondes via recherche full-text avec surlignage, naviguent dans le plan de classement, et consultent tous les formats (PDF, Office, images, audio, video, ZIP) directement dans le visualiseur integre avec filigrane dynamique. Le hub de navigation d'Igar — journeys de Philippe et Amina.

### Story 4.1: Indexation Full-Text dans Elasticsearch

As a **utilisateur (Fatima)**,
I want **que le contenu de mes documents (y compris le texte OCR) soit indexe automatiquement pour la recherche**,
So that **je peux retrouver n'importe quel document par son contenu en quelques secondes** (FR29).

**Acceptance Criteria:**

**Given** un document dont le texte a ete extrait par OCR et qui est scelle dans le coffre-fort
**When** le pipeline d'indexation s'execute
**Then** le contenu textuel et les metadonnees sont indexes dans Elasticsearch
**And** le document est disponible en recherche en moins de 30 secondes apres le depot (NFR8)
**And** l'index Elasticsearch utilise des analyseurs adaptes au francais (tokenizer, stemming, stopwords)
**And** les metadonnees indexees incluent : type de document, date, entites, auteur, service, source d'import
**And** le cloisonnement est respecte : seuls les documents du perimetre autorise de l'utilisateur sont retournes (FR46)
**And** l'indexation est journalisee via structlog

### Story 4.2: Recherche Full-Text et Filtres Combines

As a **utilisateur (Philippe)**,
I want **rechercher des documents par mots-cles dans le contenu full-text et filtrer par metadonnees**,
So that **je retrouve le bon document parmi 100 000+ en moins de 2 secondes** (FR29, FR30, FR33).

**Acceptance Criteria:**

**Given** un utilisateur authentifie sur n'importe quelle vue
**When** il clique sur la barre de recherche (header fixe) ou utilise Ctrl+K
**Then** le focus est immediat sur la barre de recherche avec suggestions recentes affichees
**And** l'autocompletion affiche jusqu'a 5 suggestions en temps reel pendant la frappe
**And** en appuyant Entree, la recherche full-text retourne des resultats en moins de 2 secondes sur 100K+ documents (NFR3)
**And** les resultats affichent des extraits contextuels avec les termes recherches surlignes
**And** un panneau de filtres lateral permet de filtrer par : Type documentaire, Periode (date), Statut (scelle/en attente), Classification (plan de classement)
**And** les filtres sont combinables avec la recherche full-text (FR33)
**And** les filtres actifs sont affiches en Tags sous la barre de recherche, supprimables en 1 clic
**And** un compteur de resultats est mis a jour en temps reel lors du filtrage
**And** un bouton "Reinitialiser les filtres" apparait des qu'un filtre est actif
**And** la recherche est tolerante aux fautes de frappe (fuzzy search)

### Story 4.3: Navigation par Plan de Classement

As a **utilisateur (Fatima)**,
I want **parcourir les documents via le plan de classement hierarchique dans la sidebar**,
So that **je peux naviguer dans l'arborescence documentaire de maniere structuree** (FR32).

**Acceptance Criteria:**

**Given** un utilisateur authentifie sur la vue Documents
**When** il interagit avec la sidebar gauche
**Then** le plan de classement est affiche en arborescence hierarchique via le composant Tree/DirectoryTree d'Ant Design
**And** chaque noeud affiche un compteur de documents
**And** le clic sur un noeud filtre la table de documents pour n'afficher que les documents de cette categorie
**And** le breadcrumb se met a jour automatiquement pour refleter la position dans l'arborescence
**And** la sidebar est repliable (220px vers 64px avec icones seules)
**And** la navigation dans l'arbre est accessible au clavier (fleches haut/bas, gauche/droite pour expand/collapse)
**And** la table principale (ProTable) affiche les documents avec colonnes : Nom, Type, Date, Statut scellement, Confiance IA

### Story 4.4: Visualiseur PDF et Images Integre

As a **utilisateur (Philippe)**,
I want **consulter des documents PDF et images directement dans le visualiseur integre sans telechargement**,
So that **je peux acceder instantanement au contenu de mes documents** (FR12, FR14).

**Acceptance Criteria:**

**Given** un document PDF ou image (JPEG, PNG, TIFF) dans la liste des documents
**When** l'utilisateur clique sur le document (panel contextuel) ou double-clique (plein ecran)
**Then** le composant DocumentViewer affiche le document directement dans l'interface
**And** la premiere page d'un PDF de 50 pages s'affiche en moins de 2 secondes (NFR5)
**And** une toolbar propose : zoom (+/-), pagination (precedent/suivant avec compteur), rotation, telechargement
**And** la navigation est accessible au clavier (fleches pour pages, +/- pour zoom)
**And** en mode panel contextuel (Drawer 320px), le document s'affiche a cote de la liste
**And** en mode plein ecran (Modal), le document occupe tout l'ecran avec overlay sombre
**And** le composant affiche un skeleton avec barre de progression pendant le chargement

### Story 4.5: Visualiseur Office, Audio, Video et Archives

As a **utilisateur (Amina)**,
I want **consulter des documents Office, ecouter des fichiers audio, lire des videos et explorer des archives ZIP directement dans Igar**,
So that **je n'ai jamais besoin de quitter l'application ou d'installer un logiciel tiers** (FR13, FR15, FR16, FR17).

**Acceptance Criteria:**

**Given** un document Office (Word, Excel, PowerPoint)
**When** l'utilisateur l'ouvre dans le DocumentViewer
**Then** le document est converti en PDF cote serveur via Gotenberg et affiche dans le visualiseur PDF (FR13)

**Given** un fichier audio (MP3, WAV, OGG)
**When** l'utilisateur l'ouvre dans le DocumentViewer
**Then** un lecteur audio HTML5 integre permet la lecture, pause, avance/recul, controle de volume (FR15)

**Given** un fichier video (MP4, WebM)
**When** l'utilisateur l'ouvre dans le DocumentViewer
**Then** un lecteur video HTML5 integre demarre la lecture en moins de 3 secondes en 1080p (FR16, NFR6)
**And** le lecteur propose : play/pause, avance/recul, plein ecran, controle de volume

**Given** une archive (ZIP, RAR)
**When** l'utilisateur l'ouvre dans le DocumentViewer
**Then** le contenu de l'archive est liste (noms de fichiers, tailles) dans une vue arborescente (FR17)

**And** pour tous les formats, le composant affiche un message "Format non supporte" si le rendu echoue, avec option de telechargement controle

### Story 4.6: Filigrane Dynamique Cote Serveur

As a **utilisateur (Philippe)**,
I want **que chaque consultation de document affiche un filigrane dynamique (mon nom + horodatage) rendu cote serveur**,
So that **chaque consultation est tracee visuellement et les fuites sont dissuadees** (FR18, FR19).

**Acceptance Criteria:**

**Given** un utilisateur consultant un document dans le DocumentViewer
**When** le document est rendu
**Then** un filigrane semi-transparent est superpose contenant : nom complet de l'utilisateur + date et heure de consultation (FR18)
**And** le filigrane est rendu cote serveur (pas cote client) et ne peut pas etre desactive par l'utilisateur (FR19)
**And** le filigrane est visible mais non intrusif (ne gene pas la lecture)
**And** le filigrane s'applique sur tous les formats rendus (PDF, images, Office converti, video en overlay)
**And** si l'utilisateur telecharge le document, le filigrane est inclus dans le fichier telecharge
**And** la consultation filigranee est journalisee dans l'audit trail (identite, document, horodatage)

### Story 4.7: Surlignage des Termes de Recherche dans le Visualiseur

As a **utilisateur (Philippe)**,
I want **que les termes recherches soient surlignes dans le visualiseur integre avec navigation entre occurrences**,
So that **je localise immediatement l'information pertinente dans un document long** (FR31).

**Acceptance Criteria:**

**Given** un utilisateur ayant effectue une recherche full-text
**When** il ouvre un resultat de recherche dans le DocumentViewer
**Then** les termes recherches sont surlignes en jaune dans le document rendu (FR31)
**And** un compteur d'occurrences est affiche ("3/12 occurrences")
**And** des boutons "Occurrence suivante" / "Occurrence precedente" permettent de naviguer entre les surlignages
**And** la premiere occurrence est automatiquement scrollee en vue
**And** le surlignage fonctionne sur les documents PDF et les documents Office convertis
**And** la navigation entre occurrences est accessible au clavier

## Epic 5: Cycle de Vie, Conformite & Administration

L'administrateur configure le plan de classement avec durees de conservation, recoit les alertes d'echeance, gere la destruction reglementaire (double validation + certificat), consulte l'audit trail complet et le tableau de bord de conformite. Le systeme gere les demandes RGPD. Le journey de Thomas.

### Story 5.1: Audit Trail Immuable et Signe Cryptographiquement

As a **administrateur (Thomas)**,
I want **que toutes les actions utilisateur soient journalisees dans un audit trail immuable signe par chaine de hachage**,
So that **chaque action est tracable et toute alteration des logs est detectable** (FR45, NFR48).

**Acceptance Criteria:**

**Given** un utilisateur effectuant une action dans Igar (depot, consultation, recherche, tentative de suppression, modification de droits)
**When** l'action est executee
**Then** une entree d'audit est creee contenant : action, horodatage, identite utilisateur, document concerne (si applicable), details
**And** chaque entree contient un `data_hash` SHA-256 calcule sur ses propres donnees
**And** chaque entree contient le `previous_hash` de l'entree precedente
**And** un `chain_hash` SHA-256 est calcule sur `data_hash + previous_hash`, formant une chaine de hachage
**And** toute alteration d'une entree casse la chaine et est detectable
**And** une tache Celery periodique (quotidienne via Celery Beat) verifie l'integrite de la chaine complete (NFR48)
**And** en cas d'anomalie detectee, une alerte CRITICAL est declenchee immediatement
**And** l'audit trail est stocke dans PostgreSQL et les entrees ne peuvent pas etre modifiees ou supprimees

### Story 5.2: Configuration du Plan de Classement

As a **administrateur (Thomas)**,
I want **configurer un plan de classement hierarchique avec des durees de conservation par type de document**,
So that **l'archivage est organise selon les obligations reglementaires de chaque client** (FR34, FR48).

**Acceptance Criteria:**

**Given** un administrateur connecte sur la page Administration
**When** il accede a la section "Plan de classement"
**Then** il peut creer une arborescence hierarchique de categories (ex : Comptabilite > Factures > Fournisseurs)
**And** il peut associer une duree de conservation a chaque categorie (5 ans factures, 10 ans comptabilite, 30 ans actes notaries, illimitee pour certains actes)
**And** il peut creer, modifier et desactiver des categories (FR48)
**And** il peut configurer les types de documents avec leurs metadonnees attendues par type
**And** la modification d'une duree de conservation ne s'applique qu'aux nouveaux documents (pas retroactif sur les documents deja scelles)
**And** l'interface utilise un wizard StepsForm d'Ant Design pour la configuration complexe
**And** les modifications sont journalisees dans l'audit trail

### Story 5.3: Notifications d'Echeance de Conservation

As a **responsable conformite**,
I want **etre notifie automatiquement lorsqu'un document approche de sa date d'expiration de conservation**,
So that **je peux anticiper les decisions de destruction ou prolongation** (FR35).

**Acceptance Criteria:**

**Given** un document scelle dont la duree de conservation approche de son expiration
**When** le document atteint les seuils de 90 jours, 30 jours et 7 jours avant expiration
**Then** une notification est envoyee au responsable conformite a chaque seuil (FR35)
**And** la notification est affichee via le systeme de notification Ant Design (notification en haut a droite, 5s)
**And** un badge compteur apparait sur le tab "Conformite" indiquant le nombre de documents a echeance
**And** la notification contient : nom du document, type, date d'expiration, duree restante, action requise
**And** les notifications sont generees par une tache Celery periodique (queue `compliance`)
**And** les notifications sont envoyees via WebSocket en temps reel pour les utilisateurs connectes
**And** les notifications sont journalisees dans l'audit trail

### Story 5.4: Processus de Destruction Reglementaire avec Double Validation

As a **responsable conformite**,
I want **gerer la destruction d'un document arrive a echeance avec double validation obligatoire et certificat de destruction**,
So that **la destruction est conforme a la reglementation et juridiquement tracable** (FR36, FR37, FR38, FR39).

**Acceptance Criteria:**

**Given** un document dont la duree de conservation est arrivee a echeance
**When** le responsable conformite consulte la liste des documents a echeance
**Then** il peut choisir parmi 3 options : Detruire / Prolonger / Reporter (FR36)

**Given** l'option "Detruire" est selectionnee par un premier validateur
**When** la demande de destruction est soumise
**Then** un second validateur distinct doit approuver la destruction (FR37)
**And** la destruction ne peut pas etre auto-validee (les 2 validateurs doivent etre differents)

**Given** les deux validations sont obtenues
**When** la destruction est executee
**Then** un certificat de destruction est genere contenant : identifiant unique, empreinte SHA-256 originale, dates de scellement et destruction, identites des 2 validateurs, motif de destruction (FR38)
**And** le certificat de destruction est lui-meme scelle et archive dans `igar-vault` (FR39)
**And** le document original est supprime de MinIO et son index est purge d'Elasticsearch
**And** l'operation complete est journalisee dans l'audit trail

**Given** l'option "Prolonger" est selectionnee
**When** la prolongation est confirmee
**Then** la duree de conservation est etendue et un nouveau scellement Object Lock est applique

**Given** l'option "Reporter" est selectionne
**When** le report est confirme
**Then** un rappel est programme dans 30 jours

### Story 5.5: Suppression Logique RGPD

As a **administrateur (Thomas)**,
I want **appliquer une suppression logique avec masquage des donnees personnelles en cas de demande RGPD sur un document a valeur probante**,
So that **le droit a l'effacement est respecte tout en conservant l'enveloppe d'archivage** (FR40, NFR47).

**Acceptance Criteria:**

**Given** une demande RGPD de droit a l'effacement pour un document scelle a valeur probante
**When** l'administrateur initie la procedure de suppression logique RGPD
**Then** les donnees personnelles du document sont masquees (nom, adresse, identifiants personnels rendus illisibles)
**And** l'enveloppe d'archivage est conservee (empreinte SHA-256, certificat de scellement, metadonnees non personnelles, horodatage)
**And** une mention "Donnees personnelles effacees — demande RGPD du [date]" est ajoutee aux metadonnees
**And** le document reste visible dans le coffre-fort avec le badge "RGPD — Donnees masquees"
**And** l'empreinte SHA-256 originale reste verifiable (le document masque est un nouveau document avec sa propre empreinte)
**And** l'operation est journalisee dans l'audit trail avec la reference de la demande RGPD
**And** un certificat de traitement RGPD est genere et archive

### Story 5.6: Configuration des Canaux de Capture et Parametres de Securite

As a **administrateur (Thomas)**,
I want **configurer les canaux de capture (IMAP, API REST) et les parametres de securite (politique de mots de passe, 2FA, sessions)**,
So that **le systeme est adapte aux besoins specifiques de mon organisation** (FR47, FR51).

**Acceptance Criteria:**

**Given** un administrateur connecte sur la page Administration
**When** il accede a la section "Canaux de capture"
**Then** il peut configurer les connecteurs email IMAP (serveur, port, identifiants, frequence de polling) (FR47)
**And** il peut activer/desactiver chaque canal de capture
**And** il peut consulter l'etat des connecteurs (actif, en erreur, derniere synchronisation)

**When** il accede a la section "Securite"
**Then** il peut configurer la politique de mots de passe (longueur minimale, complexite, expiration) (FR51)
**And** il peut configurer les parametres de session (duree d'inactivite, sessions simultanees)
**And** il peut voir les sessions actives et forcer la deconnexion d'un utilisateur
**And** les modifications de configuration sont journalisees dans l'audit trail

### Story 5.7: Tableau de Bord de Conformite

As a **administrateur (Thomas)**,
I want **consulter un tableau de bord de conformite affichant les indicateurs cles du systeme**,
So that **je verifie en un coup d'oeil que tout est conforme et que le systeme fonctionne correctement** (FR49).

**Acceptance Criteria:**

**Given** un administrateur connecte
**When** il clique sur le tab "Conformite"
**Then** le composant ComplianceDashboard (style 1Password Watchtower) affiche 4 indicateurs principaux :
- **Integrite** : pourcentage de documents integres (derniere verification periodique)
- **Stockage** : espace utilise / espace total avec pourcentage
- **Retention** : nombre de documents arrivant a echeance ce mois
- **Securite** : nombre d'alertes actives, date du dernier audit

**And** les indicateurs utilisent des couleurs semantiques : vert (sain), orange (a surveiller), rouge (alerte)
**And** une section "Alertes" liste les actions requises (documents a echeance, anomalies d'integrite)
**And** une section "Activite recente" affiche les 50 dernieres actions du journal d'audit
**And** un bouton "Generer rapport d'audit" produit un rapport PDF couvrant les exigences NF Z42-013 (NFR50)
**And** le dashboard affiche "Tout est conforme — aucune action requise" si aucune alerte n'est active
**And** le tableau de bord utilise les composants Statistic, Card et List d'Ant Design

### Story 5.8: Consultation et Export de l'Audit Trail

As a **administrateur (Thomas)**,
I want **consulter les logs d'audit trail avec filtres et les exporter**,
So that **je peux repondre aux demandes d'audit et analyser l'activite du systeme** (FR50).

**Acceptance Criteria:**

**Given** un administrateur connecte sur la page Conformite
**When** il accede a la section "Journal d'audit"
**Then** les entrees d'audit sont affichees dans un ProTable avec colonnes : Date/Heure, Utilisateur, Action, Document, Details
**And** le tableau est filtrable par : periode, utilisateur, type d'action, document
**And** le tableau est triable par date (plus recent en premier par defaut)
**And** la pagination permet de parcourir l'historique complet
**And** un bouton "Exporter" permet de telecharger les entrees filtrees en CSV ou JSON (FR50)
**And** l'export inclut les hash de chaine pour permettre la verification d'integrite externe
**And** l'acces a l'audit trail est reserve aux administrateurs
**And** la consultation de l'audit trail est elle-meme journalisee

## Epic 6: API REST & Integration Externe

Un systeme externe (ERP, CRM, integrateur) peut deposer, rechercher, recuperer des documents et verifier leur integrite via une API REST documentee OpenAPI 3.0, avec empreinte SHA-256 et certificats de scellement. Le journey de Sarah (developpeuse/integratrice, persona definie dans le PRD — Journey 5). S'appuie sur toutes les fonctionnalites construites dans les epics precedents.

### Story 6.1: Documentation OpenAPI 3.0 et Versioning API

As a **developpeuse/integratrice (Sarah)**,
I want **acceder a une documentation OpenAPI 3.0 interactive et versionee de l'API REST Igar**,
So that **je peux decouvrir les endpoints, tester les appels et integrer l'API dans mon systeme externe rapidement**.

**Acceptance Criteria:**

**Given** l'API REST Igar est deployee
**When** Sarah accede a l'endpoint `/api/v1/docs/`
**Then** une documentation OpenAPI 3.0 interactive (Swagger UI ou ReDoc) est affichee
**And** tous les endpoints sont documentes avec leurs parametres, types de reponse et codes d'erreur
**And** l'authentification JWT est documentee avec un exemple de flux (obtenir token, utiliser token)
**And** le versioning est gere via le prefixe URL `/api/v1/` (NFR39)
**And** les schemas de requete et reponse sont definis avec des exemples concrets
**And** un endpoint `/api/v1/health/` retourne le statut du systeme (HTTP 200 si operationnel)
**And** la documentation est generee automatiquement depuis les serialiseurs DRF via `drf-spectacular`

### Story 6.2: API de Depot de Document avec Metadonnees

As a **developpeuse/integratrice (Sarah)**,
I want **soumettre un document avec ses metadonnees via l'API REST**,
So that **mon ERP peut automatiser le versement de documents dans le coffre-fort Igar** (FR52).

**Acceptance Criteria:**

**Given** Sarah est authentifiee via JWT et possede le role `api_contributor`
**When** elle envoie une requete `POST /api/v1/documents/` avec le fichier en multipart/form-data et les metadonnees en JSON (type, titre, date, tags, plan de classement)
**Then** le document est accepte et un identifiant unique est retourne (HTTP 201)
**And** le document entre dans le pipeline d'ingestion (OCR → classification IA → scellement) de maniere asynchrone
**And** la reponse inclut un `task_id` permettant de suivre la progression du traitement
**And** un endpoint `GET /api/v1/documents/{id}/status/` retourne l'etat du traitement (pending, processing, sealed, error)
**And** si les metadonnees obligatoires sont manquantes, une erreur HTTP 422 avec detail des champs est retournee
**And** le temps de reponse de l'acceptation est < 500ms (NFR36)
**And** le rate limiting est applique (NFR38) et une erreur HTTP 429 est retournee si la limite est depassee

### Story 6.3: API de Recherche de Documents

As a **developpeuse/integratrice (Sarah)**,
I want **rechercher des documents via l'API REST avec filtres et pagination**,
So that **mon systeme externe peut retrouver les documents archives dans Igar** (FR53).

**Acceptance Criteria:**

**Given** Sarah est authentifiee via JWT
**When** elle envoie une requete `GET /api/v1/documents/?q=facture&type=facture&date_from=2025-01-01&date_to=2025-12-31`
**Then** les resultats sont retournes en JSON avec pagination (NFR37)
**And** chaque resultat contient : id, titre, type, date, empreinte SHA-256, statut de scellement, date de scellement
**And** les filtres disponibles sont : recherche full-text (`q`), type de document, plage de dates, tags, plan de classement, statut de scellement
**And** la pagination utilise `page` et `page_size` (max 100 par page) avec les metadonnees `total_count`, `page`, `total_pages`
**And** les resultats sont triables par date, titre ou pertinence via le parametre `ordering`
**And** seuls les documents accessibles selon le role et le cloisonnement de Sarah sont retournes
**And** le temps de reponse est < 500ms pour les requetes paginees (NFR36)

### Story 6.4: API de Recuperation de Document et Metadonnees

As a **developpeuse/integratrice (Sarah)**,
I want **recuperer un document specifique avec ses metadonnees completes via l'API REST**,
So that **mon systeme externe peut telecharger et exploiter les documents archives** (FR54, FR57).

**Acceptance Criteria:**

**Given** Sarah est authentifiee via JWT
**When** elle envoie une requete `GET /api/v1/documents/{id}/`
**Then** les metadonnees completes du document sont retournees en JSON : id, titre, type, date, tags, plan de classement, empreinte SHA-256, statut de scellement, date de scellement, taille du fichier, type MIME (FR57)

**When** elle envoie une requete `GET /api/v1/documents/{id}/download/`
**Then** le fichier original est retourne en streaming avec les headers Content-Type et Content-Disposition corrects (FR54)
**And** un filigrane dynamique est applique sur le document telecharge (coherent avec Story 4.6)

**Given** un document inexistant ou non accessible
**When** Sarah tente d'y acceder
**Then** une erreur HTTP 404 est retournee (sans reveler l'existence du document pour un autre tenant)
**And** l'acces est journalise dans l'audit trail

### Story 6.5: API de Verification d'Integrite

As a **developpeuse/integratrice (Sarah)**,
I want **verifier l'integrite d'un document archive via l'API REST**,
So that **mon systeme externe peut confirmer qu'un document n'a pas ete altere depuis son scellement** (FR55).

**Acceptance Criteria:**

**Given** Sarah est authentifiee via JWT
**When** elle envoie une requete `GET /api/v1/documents/{id}/integrity/`
**Then** la reponse JSON contient : `status` (intact/corrupted/pending), `original_hash` (SHA-256), `current_hash` (SHA-256 recalcule), `verified_at` (horodatage de la verification), `sealed_at` (date de scellement)
**And** si le document est intact, `status` = "intact" et `original_hash` === `current_hash`
**And** si le document est corrompu, `status` = "corrupted" et une alerte est declenchee automatiquement
**And** si le document n'est pas encore scelle, `status` = "pending" avec un message explicatif
**And** la verification recalcule le SHA-256 a la demande (verification a la volee, coherent avec Story 3.4)
**And** l'operation de verification est journalisee dans l'audit trail

### Story 6.6: API de Certificat de Scellement

As a **developpeuse/integratrice (Sarah)**,
I want **obtenir le certificat de scellement d'un document via l'API REST**,
So that **mon systeme externe peut conserver une preuve de l'archivage a valeur probante** (FR56).

**Acceptance Criteria:**

**Given** Sarah est authentifiee via JWT et le document est scelle
**When** elle envoie une requete `GET /api/v1/documents/{id}/certificate/`
**Then** le certificat de scellement est retourne en JSON contenant : identifiant unique du certificat, empreinte SHA-256 du document, date et heure de scellement, algorithme de hachage utilise, reference Object Lock (bucket, cle, version), duree de retention configuree

**When** elle envoie une requete `GET /api/v1/documents/{id}/certificate/?format=pdf`
**Then** le certificat est retourne en format PDF (genere via Gotenberg) avec mise en page officielle

**Given** le document n'est pas encore scelle
**When** Sarah demande le certificat
**Then** une erreur HTTP 409 (Conflict) est retournee avec le message "Document not yet sealed"
**And** l'acces au certificat est journalise dans l'audit trail
**And** le certificat PDF inclut un QR code pointant vers l'URL de verification d'integrite
