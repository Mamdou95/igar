---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
inputDocuments: []
workflowType: 'prd'
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 0
  projectDocs: 0
classification:
  projectName: Igar
  projectType: web_app
  projectTypeDetail: Logiciel on-premise/hybride commercialisé par licence
  domain: legaltech/govtech
  domainDetail: GED/SAE réglementée
  complexity: high
  projectContext: greenfield
  targets: Administrations publiques, PME/GE, Secteurs Médical (HDS) et Juridique
  mvp: Capture intelligente (OCR/IA), coffre-fort numérique immuable, cycle de vie documentaire, recherche full-text, API REST, conformité native
  compliance: NF Z42-013, RGPD, HDS, valeur probatoire
  availability: 99.9%
  security: AES-256, 2FA
  date: '2026-03-14'
---

# Product Requirements Document - Igar

**Author:** Masy
**Date:** 2026-03-13

## Executive Summary

**Igar** est une plateforme de Gestion Électronique de Documents (GED) et de Système d'Archivage Électronique (SAE) hybride, commercialisée par licence, destinée aux administrations publiques, PME/grandes entreprises, ainsi qu'aux secteurs médical (HDS) et juridique.

Ces organisations subissent une fragmentation documentaire critique : documents dispersés entre emails, scanners, répertoires réseau et applications métier ; classement manuel chronophage et source d'erreurs ; archivage non conforme exposant à des risques juridiques ; et recherche documentaire inefficace dans des volumes croissants de contenus multi-formats.

Igar résout ce problème en unifiant capture, intelligence, conservation et accès dans une plateforme unique qui combine la fluidité d'une GED collaborative moderne et la rigueur juridique d'un SAE à valeur probatoire — sans que l'utilisateur ne perçoive la complexité sous-jacente.

### Ce qui rend Igar spécial

Igar repose sur **5 piliers fondamentaux** :

- **Capture Multi-Canal** — Scanner, email, drag & drop, API REST, imports en masse : un seul point d'entrée quel que soit la source du document.
- **Intelligence IA** — OCR et classification automatique qui comprennent le contenu du document (type, métadonnées, entités) et réalisent 90% du travail de classement sans intervention humaine.
- **Multi-Format avec Visualiseur Universel** — Documents, audio, vidéo, archives ZIP et tout type de fichier, consultables directement dans l'interface sans logiciel tiers.
- **Immuabilité WORM** — Coffre-fort numérique à valeur probatoire avec scellement cryptographique (AES-256), protection contre la suppression accidentelle ou malveillante, et conformité native NF Z42-013.
- **Recherche Full-Text Instantanée** — Moteur de recherche "Google-like" qui fouille dans le contenu même des documents et restitue les résultats en moins de 2 secondes avec surlignage contextuel.

Le bonus confiance : une **visionneuse sécurisée** avec filigrane dynamique (nom de l'utilisateur + horodatage) pour une traçabilité totale des consultations et une dissuasion des fuites.

L'insight fondamental : là où les concurrents séparent GED et SAE ou sacrifient la simplicité pour la conformité, Igar prouve qu'on peut offrir la fluidité du drag & drop ET la rigueur du scellement WORM dans une seule expérience utilisateur.

## Project Classification

| Critère | Valeur |
|---------|--------|
| **Type de projet** | Web App — Logiciel on-premise/hybride commercialisé par licence |
| **Domaine** | Legaltech / Govtech (GED/SAE réglementée) |
| **Complexité** | Élevée — NF Z42-013, RGPD, HDS, valeur probatoire, AES-256, 2FA |
| **Contexte** | Greenfield |
| **Disponibilité cible** | 99,9% |
| **Cibles** | Administrations publiques, PME/GE, Secteurs Médical (HDS) et Juridique |

Les critères de succès ci-dessous découlent directement de cette classification et de la vision des 5 piliers.

## Success Criteria

### User Success

- **Classement automatique en < 5 secondes** — Un document déposé (scan, email, upload) est analysé par l'IA et ses métadonnées (type, date, entités, mots-clés) sont pré-remplies avec un taux de précision ≥ 90%. L'utilisateur valide ou corrige en un clic.
- **Recherche instantanée < 2 secondes** — Sur un corpus de 100 000+ documents, une recherche full-text retourne des résultats pertinents avec surlignage contextuel en moins de 2 secondes.
- **Zéro application tierce** — L'utilisateur consulte tous les formats (PDF, Office, images, audio, vidéo, ZIP) directement dans le visualiseur intégré sans jamais quitter Igar.
- **Confiance totale** — L'utilisateur constate qu'un document scellé ne peut être ni modifié, ni supprimé, ni même consulté sans traçabilité (filigrane dynamique). Le sentiment : "mes documents sont en sécurité".
- **Adoption en < 2 heures** — Un collaborateur non technique est opérationnel après une formation de 2 heures maximum grâce à une interface intuitive.

### Business Success

- **Premier client en production** — Déploiement pilote chez un client cible dans les 12 mois suivant le début du développement.
- **3 à 5 licences vendues en année 1** — Premiers contrats signés dans au moins 2 secteurs cibles différents (ex : administration + santé, ou juridique + PME).
- **Taux de rétention ≥ 95%** — Les clients renouvellent leur licence après la première année, signe que la plateforme est devenue indispensable.
- **Volume géré** — Au moins un client gérant 50 000+ documents dans Igar en production à la fin de l'année 1.
- **Certification de conformité** — Obtention d'une attestation de conformité NF Z42-013 dans les 18 mois.

### Technical Success

- **Disponibilité 99,9%** — Soit moins de 8h45 d'indisponibilité par an, hors maintenance planifiée.
- **Sécurité renforcée** — Chiffrement AES-256 au repos et en transit, authentification 2FA obligatoire, zéro faille critique non corrigée sous 48h.
- **Intégrité cryptographique** — Chaque document archivé possède une empreinte SHA-256 vérifiable. Toute altération est détectée automatiquement.
- **Scalabilité** — La plateforme supporte 1 million de documents et 500 utilisateurs simultanés sans dégradation de performance.
- **Conformité native** — NF Z42-013 (archivage), RGPD (données personnelles), HDS (données de santé) intégrées dès la conception, pas en surcouche.
- **API REST documentée** — Couverture fonctionnelle ≥ 90% via API pour intégration avec les systèmes métier (ERP, CRM, messagerie).

### Measurable Outcomes

| Indicateur | Cible MVP | Cible 12 mois | Cible 24 mois |
| --- | --- | --- | --- |
| Temps de classement IA | < 5s | < 3s | < 2s |
| Précision OCR/classification | ≥ 85% | ≥ 90% | ≥ 95% |
| Temps de recherche full-text | < 3s | < 2s | < 1s |
| Formats supportés par le visualiseur | 10+ | 20+ | 30+ |
| Documents gérés par instance | 100K | 500K | 1M+ |
| Utilisateurs simultanés | 100 | 300 | 500+ |
| Disponibilité | 99,5% | 99,9% | 99,9% |

## Product Scope

Le périmètre d'Igar se découpe en trois phases. Cette section résume la vision ; le détail complet des features MVP, des exclusions explicites et du phasage se trouve dans la section [Project Scoping & Phased Development](#project-scoping--phased-development).

### MVP — Minimum Viable Product

**Objectif :** Prouver la valeur des 5 piliers sur un périmètre contrôlé.

- **Capture** — Drag & drop, import fichier/dossier, connecteur email IMAP, API REST d'ingestion
- **Intelligence IA** — OCR sur PDF/images, extraction de métadonnées, classification automatique par type
- **Stockage multi-format** — Tous types de fichiers avec visualiseur intégré (PDF, images, Office, audio, vidéo)
- **Coffre-fort SAE** — Scellement WORM, empreinte SHA-256, horodatage, journalisation, politique de conservation/destruction
- **Recherche** — Full-text avec indexation du contenu OCR, filtres par métadonnées, surlignage contextuel
- **Sécurité** — AES-256, 2FA, RBAC, audit trail complet
- **Visionneuse sécurisée** — Filigrane dynamique, consultation sans téléchargement
- **Administration** — Gestion utilisateurs, plan de classement configurable, tableau de bord de conformité
- **Conformité** — NF Z42-013 et RGPD natifs

### Growth (Post-MVP)

Capture avancée (scanner réseau, hot folder, mobile), IA apprentissage continu, workflows de validation, connecteurs métier (ERP, CRM, signature électronique), LDAP/AD/SSO, conformité HDS et eIDAS, reporting avancé. Voir détails en section [Post-MVP Features](#post-mvp-features).

### Vision (Future)

IA générative et chatbot documentaire, blockchain pour ancrage de preuves, collaboration temps réel, marketplace de connecteurs, mode SaaS optionnel, archivage intelligent. Voir détails en section [Post-MVP Features](#post-mvp-features).

Les user journeys ci-dessous illustrent comment ces capabilities se traduisent en valeur concrète pour chaque profil cible.

## User Journeys

### Journey 1 : Fatima, Assistante Administrative — "Le scan qui se classe tout seul"

**Persona :** Fatima, 34 ans, assistante administrative dans une mairie de 15 000 habitants. Elle gère 200+ documents par jour : courriers entrants, délibérations, factures, arrêtés. Actuellement, elle renomme chaque fichier à la main, le range dans une arborescence de 6 niveaux de dossiers, et prie pour ne rien perdre.

**Scène d'ouverture :** Lundi matin, 8h30. Fatima arrive devant une pile de 50 courriers scannés la veille par le service courrier. Les fichiers s'appellent `scan_001.pdf` à `scan_050.pdf`. Elle soupire — c'est parti pour 2 heures de classement manuel.

**Action montante :** Avec Igar, Fatima sélectionne les 50 fichiers et les dépose d'un seul geste dans la zone de capture. En quelques secondes, l'IA analyse chaque document : facture EDF identifiée avec montant et date, courrier du préfet classé en "correspondance institutionnelle", délibération du conseil municipal indexée par date et numéro. Les métadonnées apparaissent, pré-remplies.

**Climax :** Fatima parcourt la liste : 47 documents sur 50 sont parfaitement classés. Elle corrige 3 cas ambigus en un clic chacun. **Temps total : 4 minutes au lieu de 2 heures.**

**Résolution :** Fatima utilise le temps gagné pour se concentrer sur ses missions à valeur ajoutée. Elle sait que chaque document est archivé conformément aux règles de conservation de la mairie, et qu'elle pourra le retrouver instantanément si un administré en fait la demande.

**Capabilities révélées :** Capture par lot, OCR/IA multi-types, classification automatique, correction rapide, plan de classement configurable.

### Journey 2 : Maître Dubois, Avocat — "La preuve intouchable"

**Persona :** Philippe Dubois, 52 ans, avocat associé dans un cabinet de 12 personnes spécialisé en droit des affaires. Il gère des contrats sensibles et des pièces à conviction. Son cauchemar : qu'un document soit altéré, supprimé, ou que sa date d'archivage soit contestée devant un tribunal.

**Scène d'ouverture :** Un client l'appelle en urgence : un litige commercial éclate et il faut produire un contrat signé il y a 3 ans. Dans l'ancien système, Philippe aurait passé 45 minutes à fouiller les dossiers réseau, sans certitude que la version trouvée est l'originale.

**Action montante :** Philippe ouvre Igar et tape le nom du client dans la barre de recherche. En 1,5 seconde, le contrat apparaît avec surlignage du nom. Il l'ouvre dans la visionneuse sécurisée — son nom et l'heure s'affichent en filigrane. Il vérifie l'empreinte cryptographique : le document est intègre, identique au byte près depuis son archivage.

**Climax :** Philippe tente de supprimer le document pour démontrer la robustesse à son client. **Message rouge : "Suppression interdite — document scellé WORM, conservation jusqu'au 15/03/2029."** Le client comprend instantanément : ses preuves sont juridiquement intouchables.

**Résolution :** Le contrat est produit au tribunal avec son certificat d'intégrité horodaté. L'adversaire ne peut pas contester l'authenticité. Philippe recommande Igar à 3 confrères dans la semaine.

**Capabilities révélées :** Recherche full-text instantanée, visionneuse sécurisée avec filigrane, scellement WORM, empreinte SHA-256, certificat d'intégrité, politique de conservation.

### Journey 3 : Dr. Amina Khelif, Médecin — "Le dossier patient, partout, en sécurité"

**Persona :** Amina, 41 ans, médecin dans une clinique privée de 80 lits. Elle manipule quotidiennement des comptes-rendus, imageries, résultats de laboratoire, ordonnances — des données de santé ultra-sensibles soumises au RGPD et aux exigences HDS.

**Scène d'ouverture :** Un patient arrive en urgence. Amina a besoin de son historique complet : le compte-rendu opératoire d'il y a 6 mois, les dernières analyses sanguines, et la lettre du spécialiste. Auparavant, elle devait appeler 3 services différents et attendre des fax.

**Action montante :** Amina ouvre Igar, cherche le nom du patient. Tous les documents apparaissent chronologiquement : PDF du compte-rendu, image DICOM de la radio, résultat de labo en PDF. Elle les consulte tous dans le visualiseur intégré — pas besoin d'ouvrir un logiciel DICOM séparé.

**Climax :** Elle accède au dossier complet en 10 secondes. Son nom et l'horodatage apparaissent en filigrane — chaque consultation est tracée pour la conformité RGPD. Le patient est pris en charge immédiatement avec toutes les informations nécessaires.

**Résolution :** La clinique passe un audit HDS sans remarque. Chaque accès aux données de santé est journalisé, chaque document est intègre et sa durée de conservation respecte les obligations légales (20 ans pour les dossiers médicaux).

**Capabilities révélées :** Visualiseur multi-format (y compris images médicales), traçabilité des accès RGPD, conformité HDS, recherche par patient, audit trail complet, durées de conservation spécifiques.

### Journey 4 : Thomas, Administrateur IT — "Le contrôle total sans la complexité"

**Persona :** Thomas, 29 ans, administrateur système dans une PME industrielle de 300 salariés. Il doit déployer Igar, configurer les droits, intégrer avec l'ERP existant, et s'assurer que tout tourne sans interruption. Il n'est pas archiviste — il veut que ça marche, point.

**Scène d'ouverture :** La direction a validé l'achat d'Igar. Thomas reçoit le package d'installation. Son inquiétude : combien de temps avant que ce soit opérationnel ? La dernière GED a pris 3 mois à configurer.

**Action montante :** Thomas suit l'assistant d'installation : serveur, base de données, stockage. En 2 heures, l'instance est en ligne. Il configure le plan de classement via l'interface d'administration, crée les groupes d'utilisateurs (Direction, Comptabilité, RH, Production), et définit les permissions RBAC. Il active le 2FA pour tous les comptes.

**Climax :** Thomas connecte Igar à l'ERP via l'API REST. Les bons de commande générés par l'ERP sont automatiquement ingérés et classés dans Igar. Il configure un hot folder pour le scanner réseau du service courrier. **Tout est opérationnel en une journée.**

**Résolution :** Thomas consulte le tableau de bord : disponibilité 99,9%, espace de stockage, nombre de documents, alertes de sécurité. Il reçoit une notification quand un lot de documents arrive à sa date de destruction programmée — il valide ou reporte. Igar lui simplifie la vie au lieu de la compliquer.

**Capabilities révélées :** Installation simplifiée, interface d'administration, RBAC, 2FA, API REST, connecteur ERP, hot folder, tableau de bord, notifications, gestion du cycle de vie.

### Journey 5 : Sarah, Développeuse Intégratrice — "L'API qui fait le travail"

**Persona :** Sarah, 31 ans, développeuse chez un intégrateur partenaire. Son client veut connecter son CRM à Igar pour archiver automatiquement les contrats clients signés électroniquement.

**Scène d'ouverture :** Sarah ouvre la documentation API d'Igar. Elle cherche comment ingérer un document avec ses métadonnées et le sceller automatiquement dans le coffre-fort.

**Action montante :** L'API REST est claire, documentée avec des exemples. Sarah fait son premier appel en 15 minutes : `POST /api/v1/documents` avec le fichier et les métadonnées en JSON. Le document est ingéré, analysé par l'IA, et scellé. Elle reçoit en retour l'empreinte SHA-256 et le certificat d'archivage.

**Climax :** Sarah développe le connecteur CRM→Igar en 2 jours. À chaque signature de contrat dans le CRM, le document est automatiquement archivé dans Igar avec la bonne classification. Elle implémente un webhook pour notifier le CRM quand un document approche de sa date d'expiration.

**Résolution :** Le client est autonome. Les contrats sont archivés sans intervention humaine, conformément à la réglementation. Sarah propose le même connecteur à 5 autres clients de l'intégrateur.

**Capabilities révélées :** API REST documentée, ingestion programmatique, métadonnées JSON, scellement automatique, webhooks, certificat d'archivage via API.

### Journey Requirements Summary

| Capability | Fatima (Admin) | Philippe (Avocat) | Amina (Médecin) | Thomas (IT) | Sarah (Dev) |
| --- | --- | --- | --- | --- | --- |
| Capture par lot / drag & drop | ✅ | | | | |
| OCR/IA classification | ✅ | | | | |
| Recherche full-text | ✅ | ✅ | ✅ | | |
| Visionneuse multi-format | | ✅ | ✅ | | |
| Filigrane dynamique | | ✅ | ✅ | | |
| Scellement WORM | | ✅ | | | |
| Empreinte SHA-256 | | ✅ | | | ✅ |
| Politique de conservation | | ✅ | ✅ | ✅ | |
| Audit trail / traçabilité | | | ✅ | ✅ | |
| RBAC / 2FA | | | | ✅ | |
| Tableau de bord admin | | | | ✅ | |
| API REST | | | | ✅ | ✅ |
| Webhooks | | | | | ✅ |
| Hot folder / connecteurs | | | | ✅ | |
| Conformité RGPD/HDS | | | ✅ | | |

Les exigences ci-dessus opèrent dans un cadre réglementaire strict détaillé dans la section suivante.

## Domain-Specific Requirements

### Compliance & Réglementaire

#### Archivage à valeur probante

- **NF Z42-013 (AFNOR)** — Norme française pour l'archivage électronique à valeur probante. Igar doit garantir l'intégrité, la pérennité, la traçabilité et la confidentialité des documents archivés. Exigences : empreinte cryptographique, horodatage, journalisation, stockage WORM (Write Once Read Many).
- **eIDAS (UE)** — Règlement européen sur l'identification électronique et les services de confiance. Impact sur la signature électronique qualifiée et l'horodatage qualifié intégrés au processus d'archivage (Growth feature).
- **ISO 14641** — Norme internationale pour la conception et l'exploitation d'un SAE. Référence complémentaire à NF Z42-013 pour les clients internationaux.

#### Protection des données

- **RGPD (UE)** — Droit d'accès, droit à l'effacement (avec exception pour obligations légales d'archivage), registre des traitements, minimisation des données, notification de violation sous 72h. Impact direct : le droit à l'effacement doit coexister avec l'immuabilité WORM — nécessite une politique de "suppression logique" avec masquage des données personnelles tout en conservant l'enveloppe d'archivage.
- **HDS (Hébergement de Données de Santé)** — Certification obligatoire pour tout hébergeur de données de santé en France. Impact : les clients du secteur médical exigeront que l'infrastructure Igar (ou leur infrastructure on-premise) soit certifiée HDS. La documentation d'installation doit guider les exigences HDS.

#### Secteur public

- **RGS (Référentiel Général de Sécurité)** — Exigences de sécurité pour les SI des administrations françaises. Niveaux de sécurité à respecter pour les certificats, le chiffrement et l'authentification.
- **RGAA (Référentiel Général d'Amélioration de l'Accessibilité)** — Accessibilité numérique obligatoire pour les services publics. L'interface d'Igar doit atteindre le niveau AA des WCAG 2.1 pour les clients du secteur public.
- **Habilitations et clearance** — Les opérateurs et administrateurs ayant accès aux données archivées ou aux clés de chiffrement doivent disposer d'un niveau d'habilitation défini par le client (ex : habilitation Confidentiel Défense pour certains ministères). Igar doit supporter la restriction d'accès aux fonctions d'administration par niveau d'habilitation configurable.
- **Contraintes marchés publics** — Les déploiements en administration publique sont soumis au Code de la commande publique. Igar doit fournir : documentation technique complète pour les CCTP, grille tarifaire compatible avec les formats de marchés publics, et réversibilité contractuelle garantie (export SEDA).
- **Transparence et open data** — Pour les administrations soumises à la Loi pour une République Numérique, Igar doit permettre l'export sélectif de documents publics dans des formats ouverts (CSV, JSON, PDF/A) pour publication en open data, tout en garantissant le cloisonnement des documents non communicables.

#### Secteur juridique

- **Secret professionnel** — Les documents d'avocats bénéficient du secret professionnel. Igar doit garantir l'étanchéité totale entre les espaces de stockage des différents clients/dossiers.
- **Conservation légale** — Durées de conservation spécifiques par type de document : 5 ans (factures), 10 ans (documents comptables), 30 ans (actes notariés), durée illimitée (certains actes d'état civil). Le plan de classement doit intégrer ces durées nativement.
- **Production judiciaire** — Igar doit permettre l'export de documents archivés avec leur certificat d'intégrité (empreinte SHA-256, horodatage, chaîne de traçabilité) dans un format recevable en justice. L'export inclut un dossier de preuve complet (document original, métadonnées, historique de consultation, certificat de scellement) exploitable par les juridictions sans nécessiter l'accès à Igar.

### Contraintes Techniques

#### Sécurité

- **Chiffrement** — AES-256 au repos, TLS 1.3 en transit. Les clés de chiffrement doivent être gérées séparément des données (séparation des responsabilités).
- **Authentification** — 2FA obligatoire. Support LDAP/Active Directory pour l'intégration dans les SI d'entreprise. SSO via SAML 2.0 / OpenID Connect pour les grandes organisations.
- **Audit trail** — Journalisation exhaustive et immuable de toutes les actions : dépôt, consultation, recherche, tentative de suppression, modification de droits. Les logs doivent être horodatés et signés cryptographiquement.
- **Cloisonnement** — Isolation stricte des espaces documentaires entre services/entités. Un utilisateur ne doit jamais accéder à un document hors de son périmètre autorisé, même par recherche full-text.

#### Pérennité et intégrité

- **Formats pérennes** — Conversion automatique vers des formats d'archivage pérennes (PDF/A pour les documents, TIFF pour les images) tout en conservant le format original. Double stockage : format natif + format pérenne.
- **Vérification d'intégrité** — Contrôle périodique automatisé des empreintes SHA-256 de tous les documents archivés. Alerte en cas d'anomalie détectée.
- **Migration** — Stratégie de migration des données en cas de changement de version ou de technologie de stockage, sans rupture de la chaîne de confiance.

#### Performance

- **Indexation** — Le moteur de recherche full-text doit indexer en temps réel (latence < 30s entre dépôt et disponibilité en recherche).
- **Stockage** — Architecture de stockage hiérarchique : stockage rapide (SSD) pour les documents récents, stockage froid pour les archives anciennes, avec accès transparent pour l'utilisateur.

### Exigences d'Intégration

- **LDAP / Active Directory** — Synchronisation des utilisateurs et groupes pour les déploiements on-premise en entreprise.
- **Protocoles de capture** — SMTP/IMAP (emails), TWAIN/WIA (scanners), WebDAV (dossiers réseau), API REST (applications métier).
- **Connecteurs métier** — ERP (SAP, Sage, Cegid), CRM (Salesforce, Dynamics), logiciels métier sectoriels (logiciels médicaux via HL7/FHIR pour le secteur santé).
- **Signature électronique** — Intégration avec les prestataires de signature qualifiée (DocuSign, Yousign, Universign) pour le scellement après signature.
- **Export et réversibilité** — Export complet des données dans un format ouvert et documenté (SEDA pour le secteur public) pour garantir la réversibilité en cas de changement de solution.

### Risques et Mitigations

| Risque | Impact | Mitigation |
| --- | --- | --- |
| Conflit RGPD / immuabilité WORM | Un citoyen demande l'effacement d'un document archivé à valeur probante | Suppression logique : masquage des données personnelles, conservation de l'enveloppe d'archivage avec mention de l'effacement |
| Corruption silencieuse des données | Perte d'intégrité non détectée sur le stockage | Vérification périodique automatisée des empreintes + réplication sur stockage séparé |
| Obsolescence des formats | Documents illisibles après 10-20 ans | Conversion systématique en formats pérennes (PDF/A, TIFF) + conservation du format natif |
| Non-conformité réglementaire | Rejet lors d'un audit, sanctions financières | Tests de conformité intégrés, checklist d'audit automatisée, veille réglementaire |
| Fuite de données sensibles | Atteinte à la confidentialité, sanctions RGPD | Filigrane dynamique, chiffrement bout en bout, cloisonnement strict, journalisation des accès |
| Dépendance technologique (vendor lock-in) | Client bloqué sans possibilité de migration | Format d'export ouvert (SEDA), API documentée, réversibilité contractuelle garantie |

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. Convergence GED/SAE transparente**
L'innovation principale d'Igar réside dans la fusion de deux univers traditionnellement séparés : la Gestion Électronique de Documents (fluidité, collaboration, accès rapide) et le Système d'Archivage Électronique (rigueur juridique, immuabilité, conformité). L'utilisateur interagit avec une interface unique — le scellement à valeur probante est automatique et invisible. Aucune solution du marché ne propose cette convergence avec ce niveau de transparence.

**2. Intelligence artificielle comme pilier, pas comme option**
Dans les GED classiques, l'IA est un module optionnel ajouté en surcouche. Dans Igar, l'OCR et la classification automatique sont le moteur central de la capture. Le produit est conçu autour de l'IA — elle n'est pas greffée après coup. Cela permet un taux de classement automatique de 90%+ dès le dépôt.

**3. Visualiseur universel sécurisé avec filigrane dynamique**
La combinaison d'un visualiseur capable d'afficher tous les formats (document, audio, vidéo, archive) avec un système de filigrane dynamique traçant chaque consultation est unique. Cela transforme la consultation de document en acte juridiquement tracé, sans friction pour l'utilisateur.

**4. Réconciliation RGPD / Immuabilité WORM**
Le conflit entre le droit à l'effacement (RGPD) et l'immuabilité des archives (NF Z42-013) est un problème ouvert dans l'industrie. L'approche d'Igar — suppression logique avec masquage des données personnelles tout en conservant l'enveloppe d'archivage — propose une solution juridiquement défendable et techniquement élégante.

### Market Context & Competitive Landscape

| Solution | GED | SAE | IA native | Visualiseur universel | Licence on-premise |
| --- | --- | --- | --- | --- | --- |
| Alfresco | ✅ | ❌ | ❌ | Partiel | ✅ |
| M-Files | ✅ | Partiel | Partiel | Partiel | ✅ |
| Docuware | ✅ | ❌ | Partiel | Partiel | ✅/SaaS |
| Spark Archives | ❌ | ✅ | ❌ | ❌ | ✅ |
| Everteam | Partiel | ✅ | ❌ | ❌ | ✅ |
| **Igar** | **✅** | **✅** | **✅** | **✅** | **✅** |

Aucun concurrent ne coche toutes les cases simultanément. C'est le positionnement différenciant d'Igar.

### Validation Approach

- **Preuve de concept IA** — Valider le taux de classification automatique ≥ 85% sur un corpus de 1 000 documents réels multi-types avant le MVP.
- **Test d'immuabilité** — Audit de pénétration ciblé sur le coffre-fort WORM pour valider l'impossibilité de modification/suppression.
- **Prototype visualiseur** — Tester la couverture des 10 formats les plus courants avec filigrane dynamique sur navigateur web standard.
- **Validation juridique RGPD/WORM** — Consulter un expert juridique pour confirmer la conformité de l'approche "suppression logique" au regard du RGPD et de la NF Z42-013.

### Innovation Risk Mitigation

| Innovation | Risque | Fallback |
| --- | --- | --- |
| IA classification native | Précision insuffisante sur certains types de documents | Classification semi-automatique avec suggestions IA + validation manuelle obligatoire |
| Convergence GED/SAE | Complexité technique du scellement transparent | Scellement explicite en 1 clic si le scellement automatique pose problème |
| Visualiseur universel | Certains formats propriétaires non supportés | Téléchargement contrôlé avec filigrane sur le fichier exporté |
| Réconciliation RGPD/WORM | Rejet de l'approche par un régulateur | Processus de destruction physique avec approbation d'un officier de conformité et journalisation renforcée |

## Web App Specific Requirements

Les décisions techniques ci-dessous concrétisent les exigences fonctionnelles et non-fonctionnelles dans le contexte d'une application web on-premise.

### Project-Type Overview

Igar est une application web professionnelle de type **SPA** construite sur un **fork de Mayan EDMS** (Python/Django), avec **MinIO (S3-compatible) et Object Lock** comme socle de stockage immuable. L'application est déployée on-premise (Windows Server / Linux) ou en mode hybride, et commercialisée par licence.

### Technical Architecture Considerations

#### Décisions techniques fondamentales

| Décision | Choix | Justification |
| --- | --- | --- |
| **Moteur GED** | Fork Mayan EDMS (Python/Django) | Flexibilité IA native (écosystème Python), customisation illimitée, OCR distribué, communauté active |
| **Stockage** | MinIO (S3-compatible) + Object Lock | Immuabilité WORM matérielle, compatible on-premise ET cloud, API S3 standard |
| **Sécurité stockage** | SSE-C AES-256, noms fichiers UUID, isolation processus | Protection contre accès non autorisé au stockage physique, anonymisation des fichiers sur disque |
| **Conformité cycle de vie** | Automate avec validation humaine + certificats de destruction | Traçabilité complète du cycle de vie, preuve juridique de destruction conforme |

#### Stack technique complète

| Couche | Technologie | Rôle |
| --- | --- | --- |
| **Backend** | Python / Django (fork Mayan EDMS) | Moteur GED, API REST, logique métier |
| **Frontend** | SPA moderne (React ou Vue.js) | UX refaite, visualiseur universel, drag & drop |
| **Stockage objets** | MinIO (S3-compatible) | Stockage documents + Object Lock WORM |
| **Chiffrement** | SSE-C AES-256 (clé par document) | Chiffrement au repos, fichiers illisibles sans Igar |
| **OCR** | Tesseract 5 (distribué via Celery) | Extraction texte multi-format |
| **IA / Classification** | Ollama / Hugging Face / spaCy | Classification auto, extraction métadonnées |
| **Recherche** | Elasticsearch | Full-text < 2s sur 100K+ documents |
| **File d'attente** | Redis + Celery | Workers OCR/IA, notifications temps réel |
| **Base de données** | PostgreSQL (TDE) | Métadonnées, clés de chiffrement, audit trail |
| **Temps réel** | Django Channels (WebSocket) | Notifications, progression uploads |
| **Déploiement** | Docker Compose / Kubernetes | Installation simplifiée, scaling horizontal |

### Socle Mayan EDMS — Réutilisé vs Développé

#### Réutilisé de Mayan

- Stockage et versionnement documentaire
- OCR distribué (Tesseract via Celery workers)
- Recherche Elasticsearch intégrée
- API REST fonctionnelle
- RBAC (rôles et permissions)
- Gestion des métadonnées et tags
- Workflows et automatisations
- Audit trail basique

#### Développé from scratch pour Igar

- Coffre-fort WORM / SAE via MinIO Object Lock
- IA de classification avancée (Ollama/HF)
- Frontend SPA complet (Tailwind, dark mode)
- Visualiseur universel sécurisé (PDF, Office, audio, vidéo, ZIP)
- Capture multi-canal (email IMAP, hot folder, API étendue)
- Sécurité renforcée (2FA, LDAP/AD, SSO SAML/OIDC)
- Réconciliation RGPD/WORM (suppression logique)
- Plan de classement réglementaire + automate cycle de vie
- Protection code hybride (Cython + PyArmor)
- Système de licences (binding hardware)

### Stockage — MinIO + Object Lock + SSE-C

#### Architecture de stockage

```text
┌──────────────────────────────────────────────┐
│                    IGAR                       │
│           Storage Abstraction Layer           │
│    (S3 API — identique on-premise et cloud)   │
├──────────────────────────────────────────────┤
│              MinIO Server                     │
│  ┌─────────────────────────────────────────┐ │
│  │  Bucket: igar-vault (versionné + lock)  │ │
│  │  ├── Object Lock: Compliance Mode       │ │
│  │  ├── Retention: selon plan classement   │ │
│  │  ├── SSE-C: AES-256 (clé par document)  │ │
│  │  └── Noms fichiers: UUID v4             │ │
│  ├─────────────────────────────────────────┤ │
│  │  Bucket: igar-temp (uploads en cours)   │ │
│  │  └── TTL: 24h, pas de lock             │ │
│  ├─────────────────────────────────────────┤ │
│  │  Bucket: igar-thumbnails (previews)     │ │
│  │  └── Cache, régénérable                │ │
│  └─────────────────────────────────────────┘ │
├──────────────────────────────────────────────┤
│  Disques : SSD/HDD local, NAS, ou Cloud S3   │
└──────────────────────────────────────────────┘
```

#### Object Lock — Modes d'immuabilité

| Mode | Comportement | Cas d'usage |
| --- | --- | --- |
| **Compliance** | Personne — pas même root — ne peut supprimer/modifier avant expiration | Documents à valeur probante (contrats, archives légales) |
| **Governance** | Utilisateurs privilégiés peuvent lever le verrou | Documents courants avec possibilité de correction |

#### Chiffrement SSE-C — Défense en profondeur

```text
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    IGAR     │         │    MinIO    │         │  Disque     │
│  (Django)   │         │  (S3 API)   │         │  physique   │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ Stocke la   │──clé──▶│ Chiffre     │──blob──▶│ Fichier     │
│ clé AES-256 │ à chaque│ avec la clé │ chiffré │ ILLISIBLE   │
│ dans        │ requête │ reçue       │         │ sans clé    │
│ PostgreSQL  │         │             │         │             │
│ (TDE)       │◀─data──│ Déchiffre   │◀─blob──│             │
│             │         │ à la volée  │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
```

- Chaque document possède sa propre clé AES-256 générée par Igar
- Les clés sont stockées dans PostgreSQL (chiffré TDE), liées à l'UUID du document
- MinIO chiffre/déchiffre à la volée via les headers S3 SSE-C
- **Sans Igar, les fichiers sur disque sont des blobs binaires illisibles**

#### 4 couches de protection stockage

| Couche | Protection | Attaquant bloqué |
| --- | --- | --- |
| **1. Nom UUID** | Pas de lien fichier ↔ document | Impossible d'identifier les documents |
| **2. SSE-C AES-256** | Fichier chiffré avec clé unique par document | Impossible de lire le contenu sur disque |
| **3. Clés dans PostgreSQL TDE** | Clés protégées par chiffrement DB | Impossible de récupérer les clés |
| **4. Object Lock Compliance** | Impossible de supprimer/modifier | Même root ne peut pas altérer |

#### Flux de scellement

1. Document déposé → stocké dans `igar-temp`
2. OCR/IA exécuté → métadonnées extraites
3. Utilisateur valide → clé AES-256 unique générée
4. `PutObject` dans `igar-vault` avec UUID + header SSE-C
5. `PutObjectRetention` appliqué selon la durée du plan de classement
6. Empreinte SHA-256 calculée et stockée en base PostgreSQL
7. Certificat de scellement généré (horodatage + empreinte + métadonnées)

### Sécurité — Défense en profondeur

#### Isolation des processus

- **Conteneurs Docker séparés** — Chaque service tourne dans son propre conteneur isolé
- **Réseau interne Docker** — Communication via réseau privé non exposé
- **Principe du moindre privilège** — Chaque conteneur n'accède qu'aux ressources nécessaires
- **Workers OCR/IA sandboxés** — Traitements de documents potentiellement malveillants dans des workers isolés avec ressources limitées (CPU, mémoire, timeout)

#### Sécurité frontend

- **CSP stricte**, **JWT** refresh token (httpOnly, 15 min TTL), **anti-CSRF**
- **Filigrane côté serveur** — Rendu serveur, impossible à désactiver côté client

### Conformité — Automate de cycle de vie

#### Cycle de vie documentaire

```text
Dépôt → Scellement → Conservation → Révision → Destruction/Prolongation
  │         │            │              │              │
  ▼         ▼            ▼              ▼              ▼
igar-temp  Object Lock  Vérification   Notification   Certificat
           Compliance   intégrité      humaine        destruction
           + SSE-C      périodique     obligatoire     signé
           + SHA-256
```

#### Automate de conservation

- **Politiques configurables** — Durée par type de document (5 ans factures, 10 ans comptabilité, 30 ans actes)
- **Alertes proactives** — Notification 90j / 30j / 7j avant expiration
- **Aucune destruction automatique** — L'automate propose, l'humain dispose

#### Validation humaine obligatoire

- Workflow de révision déclenché automatiquement à l'approche de l'expiration
- 3 options : **Détruire** / **Prolonger** / **Reporter**
- **Double validation** — Destruction nécessite l'approbation de 2 personnes distinctes
- Chaque décision journalisée (identité, horodatage, justification)

#### Certificats de destruction

- Identifiant unique, empreinte SHA-256 originale, dates, identités des validateurs, motif
- Le certificat est lui-même **scellé et archivé** dans `igar-vault`
- Destruction effective : suppression objet MinIO + purge index + conservation certificat

### Browser Matrix

| Navigateur | Version minimale | Priorité |
| --- | --- | --- |
| Google Chrome | 2 dernières versions stables | Principale |
| Mozilla Firefox | 2 dernières versions stables | Principale |
| Microsoft Edge (Chromium) | 2 dernières versions stables | Principale |
| Safari | 2 dernières versions stables | Secondaire |

### SEO Strategy

**Exclusion explicite :** Igar est une application web professionnelle B2B déployée on-premise, accessible uniquement après authentification. Aucune page publique n'est indexable par les moteurs de recherche. Le SEO n'est pas applicable à ce type de produit. Le site vitrine commercial (hors périmètre PRD) fera l'objet d'une stratégie SEO séparée.

### Responsive Design

- **Desktop-first** — Optimisé ≥ 1280px, cible 1920x1080
- **Tablette** — Support adaptatif ≥ 768px paysage
- **Mobile** — Post-MVP

### Performance Targets

| Métrique | Cible |
| --- | --- |
| First Contentful Paint | < 1,5s |
| Time to Interactive | < 3s |
| Recherche full-text (100K docs) | < 2s |
| Upload 50 fichiers (acceptation) | < 5s |
| Rendu visionneuse PDF 50p | < 2s |
| Rendu visionneuse vidéo 1080p | < 3s |
| Traitement OCR/IA (1 doc) | < 5s |

### Compatibilité OS (déploiement client)

| OS | Support | Notes |
| --- | --- | --- |
| **Linux** (Ubuntu, Debian, RHEL) | ✅ Recommandé | Docker natif, performance optimale |
| **Windows Server** 2019/2022 | ✅ Supporté | Docker Desktop / WSL2, installeur MSI prévu |

### Protection du code — Approche hybride Cython + PyArmor

| Couche | Protection | Justification |
| --- | --- | --- |
| **Cœur SAE/WORM** (scellement, empreintes, cycle de vie) | **Cython** (compilé en .so/.pyd) | Propriété intellectuelle critique — protection maximale + gain de performance |
| **IA/Classification** (modèles, pipeline) | **Cython** | Algorithmes propriétaires + performance critique |
| **API REST / Django views** | **PyArmor** | Compatible Django sans modification |
| **Modules Mayan étendus** | **PyArmor** | Introspection Django préservée |
| **Système de licence** | **Cython** (compilé) | Vérification hardware ID, expiration — inviolable |

```text
┌────────────────────────────────────────┐
│            IGAR distribué               │
├────────────────────────────────────────┤
│  Cython (.so/.pyd)     PyArmor (.py)   │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ SAE/WORM     │    │ Django views  │  │
│  │ Crypto/Hash  │    │ URL routing   │  │
│  │ IA Pipeline  │    │ Templates     │  │
│  │ Licence check│    │ Mayan modules │  │
│  │ Cycle de vie │    │ Admin config  │  │
│  └──────────────┘    └──────────────┘  │
│    Binaire natif      Bytecode chiffré  │
│    (impossible à      (protection       │
│     décompiler)        raisonnable)     │
└────────────────────────────────────────┘
```

## Project Scoping & Phased Development

Cette section détaille le phasage introduit dans [Product Scope](#product-scope) avec les arbitrages précis pour chaque phase.

### MVP Strategy & Philosophy

**Approche MVP choisie : MVP de résolution de problème (Problem-Solving MVP)**

L'objectif n'est pas de livrer toutes les fonctionnalités, mais de prouver que les **5 piliers** fonctionnent ensemble sur un périmètre contrôlé. Le MVP doit permettre à un client pilote de dire : "Mes documents sont capturés intelligemment, protégés juridiquement, et retrouvés instantanément."

**Ressources estimées :**
- Équipe cœur : 2-3 développeurs full-stack Python/Django + 1 développeur frontend SPA
- Compétences critiques : sécurité/cryptographie, IA/NLP, DevOps Docker/MinIO
- Durée estimée MVP : 9-12 mois

### MVP Feature Set (Phase 1)

**Parcours utilisateur supportés au MVP :**

| Journey | Supporté MVP | Justification |
| --- | --- | --- |
| Fatima (Assistante admin) | ✅ Complet | Parcours principal — prouve la capture IA |
| Philippe (Avocat) | ✅ Complet | Prouve l'immuabilité WORM et la valeur probante |
| Amina (Médecin) | ⚠️ Partiel | Visualiseur OK, conformité HDS reportée post-MVP |
| Thomas (Admin IT) | ✅ Essentiel | Déploiement Docker, RBAC, tableau de bord basique |
| Sarah (Développeuse) | ⚠️ Partiel | API REST fonctionnelle, webhooks post-MVP |

**Must-Have MVP (sans ça, le produit échoue) :**

| Capability | Pilier | Justification |
| --- | --- | --- |
| Drag & drop + import fichier/dossier | Capture | Point d'entrée principal |
| Connecteur email IMAP | Capture | Canal de capture #2 le plus demandé |
| API REST d'ingestion basique | Capture | Intégration minimale pour les intégrateurs |
| OCR Tesseract sur PDF/images | Intelligence | Sans ça, pas de classification automatique |
| Classification IA par type de document | Intelligence | Le "moment wow" — 90% du classement auto |
| Extraction métadonnées (date, entités) | Intelligence | Pré-remplissage automatique |
| Visualiseur PDF, images, Office | Multi-Format | Formats les plus courants (80% des cas) |
| Visualiseur audio/vidéo basique | Multi-Format | Différenciateur clé vs concurrents |
| Filigrane dynamique côté serveur | Multi-Format | Traçabilité des consultations |
| MinIO + Object Lock Compliance | Immuabilité | Cœur du SAE — valeur probante |
| SSE-C AES-256 par document | Immuabilité | Fichiers illisibles sans Igar |
| Empreinte SHA-256 + certificat scellement | Immuabilité | Preuve d'intégrité |
| Elasticsearch full-text | Vitesse | Recherche < 2s avec surlignage |
| Indexation contenu OCR | Vitesse | Rechercher dans le contenu, pas juste les titres |
| RBAC + 2FA | Sécurité | Minimum viable pour les entreprises |
| Plan de classement configurable | Conformité | Durées de conservation par type |
| Automate cycle de vie + validation humaine | Conformité | Destruction contrôlée + certificats |
| Certificats de destruction | Conformité | Preuve juridique |
| Audit trail complet | Conformité | NF Z42-013 exige la journalisation |
| Docker Compose (Linux) | Déploiement | Installation simplifiée |
| Interface d'administration basique | Admin | Gestion utilisateurs, configuration |

**Explicitement hors MVP :**

| Feature | Raison du report | Phase cible |
| --- | --- | --- |
| Connecteur scanner TWAIN/WIA | Import PDF manuel suffisant | Phase 2 |
| Hot folder (dossier surveillé) | Import manuel suffisant | Phase 2 |
| Application mobile / PWA | Desktop-first | Phase 2 |
| IA avancée (apprentissage sur corrections) | IA basique suffit pour prouver la valeur | Phase 2 |
| Détection de doublons | Nice-to-have | Phase 2 |
| Workflows de validation | Circuits d'approbation manuels au départ | Phase 2 |
| Connecteurs ERP/CRM | API REST suffit | Phase 2 |
| LDAP/AD, SSO SAML/OIDC | 2FA + gestion locale suffisent | Phase 2 |
| Conformité HDS | Nécessite certification hébergeur | Phase 2 |
| eIDAS (signature qualifiée) | Post-MVP | Phase 2 |
| Webhooks | API polling suffisant | Phase 2 |
| Multi-site / réplication | Un seul site au MVP | Phase 3 |
| Windows Server (installeur MSI) | Linux Docker prioritaire | Phase 2 |
| Reporting avancé / dashboards | Tableau de bord basique suffisant | Phase 2 |
| IA générative / chatbot documentaire | Innovation future | Phase 3 |
| Blockchain (ancrage preuves) | Innovation future | Phase 3 |
| Collaboration temps réel | Innovation future | Phase 3 |
| Marketplace de connecteurs | Nécessite écosystème établi | Phase 3 |
| Mode SaaS optionnel | Focus on-premise d'abord | Phase 3 |

### Post-MVP Features

**Phase 2 — Growth (mois 12-18) :**

- Capture avancée : hot folder, scanner TWAIN, capture mobile
- IA avancée : apprentissage continu, détection doublons, suggestions prédictives
- Workflows de validation configurables + notifications
- Connecteurs métier : ERP (SAP, Sage), CRM, signature électronique (Yousign, DocuSign)
- LDAP/Active Directory, SSO SAML/OIDC
- Windows Server (installeur MSI)
- Conformité HDS (documentation + guide certification hébergeur)
- Webhooks + API étendue
- Reporting et tableaux de bord personnalisables
- Formats supplémentaires dans le visualiseur (10 → 20+)

**Phase 3 — Expansion (mois 18-30) :**

- IA générative : résumé automatique, extraction de clauses, chatbot documentaire
- Multi-site avec réplication et synchronisation
- eIDAS : signatures qualifiées et horodatage qualifié
- Blockchain : ancrage des preuves d'archivage
- Collaboration temps réel : annotation, co-édition
- Marketplace de connecteurs certifiés
- Mode SaaS optionnel (cloud souverain)
- Archivage intelligent (recommandations IA de conservation)

### Risk Mitigation Strategy

**Risques techniques :**

| Risque | Probabilité | Impact | Mitigation |
| --- | --- | --- | --- |
| Précision IA < 85% sur documents réels | Moyenne | Élevé | POC IA sur corpus 1000 docs avant MVP complet. Fallback : classification semi-auto |
| Performance Elasticsearch < 2s sur gros volumes | Faible | Moyen | Architecture indexation optimisée. Benchmark à 100K docs avant livraison |
| Complexité intégration MinIO Object Lock + SSE-C | Moyenne | Élevé | Prototype coffre-fort WORM en sprint 1. Fallback : WORM applicatif |
| Visualiseur universel — formats exotiques | Faible | Faible | MVP limité aux 10 formats courants. Téléchargement contrôlé en fallback |

**Risques marché :**

| Risque | Mitigation |
| --- | --- |
| Marché GED/SAE très concurrentiel | Positionnement unique (5 piliers). Client pilote dans secteur de niche |
| Cycle de vente long (administrations) | Cibler d'abord PME/cabinets. Administrations en Phase 2 |
| Conformité NF Z42-013 non certifiée | Expert conformité dès le MVP. Documentation d'audit préparée |

**Risques ressources :**

| Risque | Mitigation |
| --- | --- |
| Équipe réduite (< 3 devs) | Priorisation stricte Must-Have. Fork Mayan accélère le démarrage |
| Perte d'un développeur clé | Documentation technique continue. Pas de bus factor = 1 |
| Budget limité | Stack 100% open source (Mayan, MinIO, Tesseract, Elasticsearch) |

Les exigences fonctionnelles ci-dessous formalisent les capabilities identifiées dans les user journeys et le scoping MVP.

## Functional Requirements

### Capture & Ingestion de Documents

- **FR1:** L'utilisateur peut déposer jusqu'à 500 documents par lot via glisser-déposer dans l'interface
- **FR2:** L'utilisateur peut importer des documents via un sélecteur de fichiers (fichier unique ou dossier complet)
- **FR3:** Le système ingère automatiquement les documents reçus par email via un connecteur IMAP
- **FR4:** Un système externe peut soumettre un document avec ses métadonnées via l'API REST d'ingestion
- **FR5:** L'utilisateur peut suivre la progression de l'ingestion en temps réel (statut par document)
- **FR6:** Le système reprend automatiquement les uploads interrompus par une perte de connexion

### Intelligence & Classification Automatique

- **FR7:** Le système extrait le texte de documents PDF et images via OCR
- **FR8:** Le système classifie automatiquement un document par type parmi les catégories configurées (facture, contrat, courrier, délibération, arrêté, ordonnance, compte-rendu, bon de commande, bulletin de paie, document d'identité)
- **FR9:** Le système extrait automatiquement les métadonnées clés d'un document (date, montant, entités nommées, numéro de référence)
- **FR10:** L'utilisateur peut valider ou corriger les métadonnées pré-remplies par l'IA en un clic
- **FR11:** L'utilisateur peut assigner manuellement un type et des métadonnées si la classification automatique échoue

### Visualisation & Consultation

- **FR12:** L'utilisateur peut consulter un document PDF directement dans le visualiseur intégré
- **FR13:** L'utilisateur peut consulter des documents Office (Word, Excel, PowerPoint) dans le visualiseur intégré
- **FR14:** L'utilisateur peut consulter des images (JPEG, PNG, TIFF) dans le visualiseur intégré
- **FR15:** L'utilisateur peut lire des fichiers audio directement dans le visualiseur intégré
- **FR16:** L'utilisateur peut lire des fichiers vidéo directement dans le visualiseur intégré
- **FR17:** L'utilisateur peut consulter le contenu d'une archive (ZIP, RAR) dans le visualiseur intégré
- **FR18:** Le système affiche un filigrane dynamique (nom d'utilisateur + horodatage) lors de chaque consultation
- **FR19:** Le filigrane est rendu côté serveur et ne peut pas être désactivé côté client

### Archivage & Immuabilité (SAE)

- **FR20:** Le système scelle un document dans le coffre-fort WORM après validation utilisateur
- **FR21:** Le système génère une empreinte SHA-256 unique pour chaque document scellé
- **FR22:** Le système applique automatiquement une durée de conservation (Object Lock Retention) selon le plan de classement
- **FR23:** Le système interdit toute suppression ou modification d'un document scellé avant l'expiration de sa durée de conservation
- **FR24:** Le système chiffre chaque document avec une clé AES-256 unique (SSE-C) avant stockage
- **FR25:** Le système stocke chaque document sous un nom UUID sans lien avec le nom original
- **FR26:** Le système génère un certificat de scellement pour chaque document archivé (horodatage + empreinte + métadonnées)
- **FR27:** L'utilisateur peut vérifier l'intégrité d'un document archivé à tout moment
- **FR28:** Le système effectue des vérifications d'intégrité périodiques automatisées sur l'ensemble des documents archivés

### Recherche & Découverte

- **FR29:** L'utilisateur peut rechercher des documents par mots-clés dans le contenu full-text (y compris le texte OCR)
- **FR30:** L'utilisateur peut filtrer les résultats de recherche par métadonnées (type, date, auteur, service)
- **FR31:** Le système surligne les termes recherchés dans le visualiseur intégré
- **FR32:** L'utilisateur peut parcourir les documents via le plan de classement (arborescence hiérarchique)
- **FR33:** L'utilisateur peut combiner recherche full-text et filtres par métadonnées

### Cycle de Vie & Conformité

- **FR34:** L'administrateur peut configurer un plan de classement avec des durées de conservation par type de document
- **FR35:** Le système notifie les responsables conformité lorsqu'un document approche de sa date d'expiration (90j, 30j, 7j)
- **FR36:** Le responsable conformité peut décider de détruire, prolonger ou reporter la conservation d'un document arrivé à échéance
- **FR37:** La destruction d'un document nécessite la double validation de deux personnes distinctes
- **FR38:** Le système génère un certificat de destruction signé pour chaque document détruit (empreinte originale, dates, validateurs, motif)
- **FR39:** Le certificat de destruction est lui-même scellé et archivé dans le coffre-fort
- **FR40:** Le système applique une suppression logique avec masquage des données personnelles en cas de demande RGPD sur un document à valeur probante

### Gestion des Utilisateurs & Sécurité

- **FR41:** L'administrateur peut créer, modifier et désactiver des comptes utilisateurs
- **FR42:** L'administrateur peut définir des rôles et permissions (RBAC) par groupe d'utilisateurs
- **FR43:** L'administrateur peut restreindre l'accès à des espaces documentaires spécifiques par rôle
- **FR44:** Le système impose l'authentification à deux facteurs (2FA) pour tous les utilisateurs
- **FR45:** Le système journalise toutes les actions utilisateur dans un audit trail immuable (dépôt, consultation, recherche, tentative de suppression, modification de droits)
- **FR46:** L'utilisateur ne peut jamais accéder à un document hors de son périmètre autorisé, y compris via la recherche full-text

### Administration & Configuration

- **FR47:** L'administrateur peut configurer les canaux de capture (email IMAP, API REST)
- **FR48:** L'administrateur peut gérer le plan de classement (créer, modifier, désactiver des catégories et durées de conservation)
- **FR49:** L'administrateur peut consulter un tableau de bord affichant les indicateurs clés (volume de documents, espace de stockage, disponibilité, alertes de sécurité)
- **FR50:** L'administrateur peut consulter les logs d'audit trail et les exporter
- **FR51:** L'administrateur peut configurer les paramètres de sécurité (politique de mots de passe, 2FA, sessions)

### API & Intégration

- **FR52:** Un système externe peut déposer un document avec métadonnées via l'API REST
- **FR53:** Un système externe peut rechercher des documents via l'API REST
- **FR54:** Un système externe peut récupérer un document et ses métadonnées via l'API REST
- **FR55:** Un système externe peut vérifier l'intégrité d'un document via l'API REST
- **FR56:** Un système externe peut obtenir le certificat de scellement d'un document via l'API REST
- **FR57:** L'API REST retourne l'empreinte SHA-256 et le statut de scellement pour chaque document

Les exigences non-fonctionnelles ci-dessous définissent les attributs de qualité mesurables qui encadrent l'implémentation des FRs.

## Non-Functional Requirements

### Performance

- **NFR1:** Les actions utilisateur courantes (navigation, ouverture de vue) s'exécutent en moins de 1,5 seconde (First Contentful Paint)
- **NFR2:** L'interface est interactive en moins de 3 secondes (Time to Interactive)
- **NFR3:** Une recherche full-text sur un corpus de 100 000 documents retourne des résultats en moins de 2 secondes
- **NFR4:** L'acceptation d'un lot de 50 fichiers en drag & drop s'effectue en moins de 5 secondes
- **NFR5:** Le visualiseur affiche la première page d'un PDF de 50 pages en moins de 2 secondes
- **NFR6:** Le visualiseur démarre la lecture d'une vidéo 1080p en moins de 3 secondes
- **NFR7:** Le traitement OCR/IA d'un document unitaire s'effectue en moins de 5 secondes
- **NFR8:** L'indexation d'un document dans Elasticsearch est disponible en recherche en moins de 30 secondes après dépôt
- **NFR9:** Le surcoût de chiffrement/déchiffrement SSE-C est inférieur à 5% sur les opérations de lecture/écriture

### Security

- **NFR10:** Toutes les données au repos sont chiffrées en AES-256 via SSE-C (une clé unique par document)
- **NFR11:** Toutes les communications sont chiffrées en transit via TLS 1.3
- **NFR12:** Les clés de chiffrement sont stockées dans un système de base de données distinct du stockage objet, vérifié par audit de séparation des responsabilités (aucune clé présente sur le système de fichiers du stockage)
- **NFR13:** L'authentification 2FA est obligatoire pour tous les comptes utilisateurs sans exception
- **NFR14:** Les tokens JWT expirent après 15 minutes (access token) avec refresh token httpOnly
- **NFR15:** Une politique CSP stricte est appliquée, validée par un score A+ sur Mozilla Observatory (ou outil équivalent) et zéro directive `unsafe-inline` ou `unsafe-eval` en production
- **NFR16:** Une protection anti-CSRF est active sur 100% des opérations de mutation, vérifié par scan automatisé (OWASP ZAP ou équivalent) retournant zéro finding CSRF
- **NFR17:** Les workers OCR/IA s'exécutent dans des conteneurs isolés avec ressources limitées (CPU, mémoire, timeout) pour contenir les documents malveillants
- **NFR18:** Zéro faille de sécurité critique (CVSS ≥ 9.0) non corrigée sous 48 heures
- **NFR19:** Zéro faille de sécurité élevée (CVSS ≥ 7.0) non corrigée sous 7 jours
- **NFR20:** Les noms de fichiers stockés (UUID) ne permettent aucune corrélation avec le contenu ou le nom original du document

### Scalability

- **NFR21:** Le système supporte 100 utilisateurs simultanés au MVP sans dégradation de performance
- **NFR22:** Le système supporte 500 utilisateurs simultanés en cible 24 mois
- **NFR23:** Le système gère 100 000 documents par instance au MVP, 1 million en cible 24 mois
- **NFR24:** L'architecture de conteneurisation permet le scaling horizontal des workers OCR/IA indépendamment du backend, mesuré par une augmentation linéaire du débit de traitement (±10%) à chaque ajout de worker
- **NFR25:** L'ajout de workers Celery supplémentaires augmente linéairement la capacité de traitement OCR/IA

### Reliability & Availability

- **NFR26:** Disponibilité cible de 99,5% au MVP (soit < 44h d'indisponibilité par an), 99,9% en cible 12 mois
- **NFR27:** Aucune perte de données en cas de panne d'un composant unique (conteneur, disque, service)
- **NFR28:** Les uploads interrompus sont repris automatiquement à la reconnexion sans perte de données
- **NFR29:** La vérification d'intégrité périodique détecte toute corruption silencieuse de données dans un délai maximum de 24 heures
- **NFR30:** En cas de panne MinIO, le système bascule en mode dégradé (lecture seule depuis réplica) plutôt qu'en indisponibilité totale

### Accessibility

- **NFR31:** L'interface respecte le niveau AA des WCAG 2.1 / RGAA pour les clients du secteur public
- **NFR32:** Toute la navigation est accessible au clavier sans souris
- **NFR33:** L'interface est compatible avec les lecteurs d'écran (ARIA landmarks, labels, live regions), vérifié par test avec NVDA/VoiceOver sur les 5 parcours utilisateur principaux avec zéro blocage fonctionnel
- **NFR34:** Les contrastes de couleurs respectent un ratio minimum de 4,5:1
- **NFR35:** Les textes alternatifs sont fournis pour tous les éléments visuels non décoratifs

### Integration

- **NFR36:** L'API REST respecte les conventions RESTful et retourne des réponses JSON structurées avec codes HTTP standard
- **NFR37:** L'API REST est documentée au format OpenAPI 3.0 (Swagger) et maintenue à jour
- **NFR38:** Le temps de réponse moyen de l'API est inférieur à 500ms pour les opérations de lecture
- **NFR39:** L'API supporte la pagination, le filtrage et le tri sur toutes les ressources listées
- **NFR40:** Le connecteur IMAP vérifie les nouveaux emails au minimum toutes les 5 minutes

### Maintainability & Operability

- **NFR41:** Le déploiement d'une nouvelle instance via l'outil d'orchestration de conteneurs s'effectue en moins de 30 minutes par un administrateur système, mesuré depuis le téléchargement du package jusqu'à la première connexion réussie
- **NFR42:** Les mises à jour de version sont appliquées sans perte de données et avec un downtime maximum de 15 minutes
- **NFR43:** Les logs applicatifs sont structurés (JSON), horodatés et centralisables
- **NFR44:** Le système expose des métriques de santé (healthcheck) pour chaque composant (API, stockage objet, moteur de recherche, base de données, workers), avec un endpoint `/health` retournant un statut agrégé en moins de 500ms
- **NFR45:** La documentation d'installation et de configuration est fournie pour Linux et Windows Server

### Compliance

- **NFR46:** Le système est conforme à la norme NF Z42-013 pour l'archivage électronique à valeur probante
- **NFR47:** Le système est conforme au RGPD (droit d'accès, droit à l'effacement avec exception légale, registre des traitements, notification de violation sous 72h)
- **NFR48:** L'audit trail est immuable, horodaté et signé cryptographiquement — vérifié par un test d'intégrité automatisé quotidien (vérification des signatures chaînées) avec alerte immédiate en cas d'anomalie
- **NFR49:** Toutes les opérations de destruction sont documentées par un certificat de destruction scellé
- **NFR50:** Le système produit les preuves nécessaires pour un audit de conformité NF Z42-013 (journaux, empreintes, certificats), avec un rapport d'audit générable à la demande couvrant 100% des exigences NF Z42-013 applicables
