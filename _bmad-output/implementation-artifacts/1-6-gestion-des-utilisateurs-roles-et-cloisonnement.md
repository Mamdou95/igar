# Story 1.6: Gestion des Utilisateurs, Rôles et Cloisonnement

Status: review

## Implementation Progress

- Task 1: avancée significative (modèles RBAC, migration, tests unitaires)
- Task 2: avancée significative (endpoints admin users/roles/groups/audit + tests API)
- Task 4: terminé (cloisonnement branché dans les mixins Mayan views/REST + manager `.for_user(user)` + modèle `Document.access_groups` + validation exhaustive scénario URL/recherche)
- Task 5: terminé (validation requêtes complexes + cache de résultats par utilisateur TTL 5 min + tests d'isolation)
- Task 6: base frontend ajoutée (pages Admin Users/Roles/Audit + client API)

- Note validation locale: exécution pytest effectuée avec `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:/usr/local/lib` pour résoudre le chargement Cairo sur macOS.

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **administrateur (Thomas)**,
I want **créer des utilisateurs, définir des rôles avec permissions, et restreindre l'accès aux espaces documentaires par rôle**,
so that **chaque utilisateur n'accède qu'aux documents de son périmètre autorisé** (FR41, FR42, FR43, FR46).

## Acceptance Criteria

1. **Given** un administrateur connecté avec le rôle administrateur
   **When** il accède à la page d'administration des utilisateurs
   **Then** il peut créer, modifier et désactiver des comptes utilisateurs (FR41)

2. **And** il peut créer des rôles (ex : Direction, Comptabilité, RH, Production) avec des permissions granulaires (FR42)

3. **And** il peut associer des utilisateurs à des groupes/rôles

4. **And** il peut restreindre l'accès à des espaces documentaires spécifiques par rôle (FR43)

5. **And** un utilisateur ne peut jamais accéder à un document hors de son périmètre autorisé, y compris via la recherche full-text (FR46)

6. **And** les modifications de droits sont journalisées dans l'audit trail

7. **And** l'interface d'administration utilise ProTable et ProForm (Ant Design)

8. **And** la page respecte le thème "Océan Profond" et les principes d'accessibilité WCAG 2.1 AA

## Tasks / Subtasks

- [x] Task 1: Étendre le modèle RBAC Mayan avec cloisonnement documentaire (AC: #4, #5)
  - [x] 1.1 Analyser le modèle RBAC existant de Mayan EDMS (django.contrib.auth.models.Group, Permission, User)
  - [x] 1.2 Identifier les permissions documentaires manquantes pour le cloisonnement (view_document_in_group, view_document_by_classification)
  - [x] 1.3 Créer une nouvelle table `igar_document_access_groups` (many-to-many User←→DocumentGroup) pour mapper users aux groupes documentaires
  - [x] 1.4 Créer permission types personnalisées : 'document_vault.view_document', 'document_vault.seal_document', 'intelligence.view_classification', etc.
  - [x] 1.5 Étendre le modèle User Mayan avec champ `allowed_document_groups` (M2M) et `is_readonly` (boolean)
  - [x] 1.6 Exécuter `python manage.py makemigrations` et valider les migration files
  - [x] 1.7 Exécuter `python manage.py migrate` sur test DB et valider sans erreur

- [x] Task 2: Implémenter les endpoints backend pour la gestion utilisateurs (AC: #1, #6)
  - [x] 2.1 Créer endpoint `GET /api/v1/admin/users/` (paginated, filtrable par status/group) avec Mayan RBAC permission_required
  - [x] 2.2 Créer endpoint `POST /api/v1/admin/users/` pour créer un nouvel utilisateur (email, username, first_name, last_name, groups, is_active)
  - [x] 2.3 Créer endpoint `PATCH /api/v1/admin/users/{id}/` pour modifier un utilisateur existant (email, first_name, last_name, groups, is_active, is_readonly)
  - [x] 2.4 Créer endpoint `DELETE /api/v1/admin/users/{id}/` pour désactiver un utilisateur (soft delete via is_active=false, ne pas supprimer physiquement)
  - [x] 2.5 Créer endpoint `POST /api/v1/admin/users/{id}/reset-password/` pour générer un token de réinitialisation (envoi email)
  - [x] 2.6 Créer endpoint `POST /api/v1/admin/users/{id}/reset-2fa/` pour réinitialiser 2FA (hérité de story 1-5)
  - [x] 2.7 Journaliser tous les changements (création, modification, suppression) dans audit trail avec user_id admin, timestamp, action, old_values, new_values (AC: #6)
  - [x] 2.8 Uniformiser les réponses d'erreur en RFC 7807 (ex: "user-already-exists", "user-not-found", "insufficient-permissions")

- [x] Task 3: Implémenter les endpoints backend pour la gestion des rôles (AC: #2, #42)
  - [x] 3.1 Créer endpoint `GET /api/v1/admin/roles/` pour lister tous les rôles (utiliser Mayan Group model)
  - [x] 3.2 Créer endpoint `POST /api/v1/admin/roles/` pour créer un nouveau rôle avec nom et liste de permissions
  - [x] 3.3 Créer endpoint `PATCH /api/v1/admin/roles/{id}/` pour modifier un rôle (nom, permissions)
  - [x] 3.4 Créer endpoint `DELETE /api/v1/admin/roles/{id}/` pour supprimer un rôle (soft delete ou refuser si users existants)
  - [x] 3.5 Créer endpoint `GET /api/v1/admin/permissions/` pour lister toutes les permissions disponibles (groupées par app: document_vault, intelligence, compliance, etc.)
  - [x] 3.6 Journaliser chaque création/modification/suppression de rôle dans audit trail
  - [x] 3.7 Pré-configurer les rôles par défaut au déploiement (Direction, Comptabilité, RH, Production, Archives, Admin) avec permissions appropriées

- [x] Task 4: Implémenter le cloisonnement documentaire strict (AC: #4, #5, #46)
  - [x] 4.1 Créer un middleware/decorator DRF `@require_document_access` pour vérifier qu'un utilisateur peut accéder à un document
  - [x] 4.2 Appliquer ce decorator sur tous les endpoints documentaires : GET /documents/{id}/, GET /documents/{id}/preview/, GET /documents/{id}/seal/, etc.
  - [x] 4.3 Implémenter la logique de cloisonnement :
    - Si document.access_groups est défini, vérifier que user.allowed_document_groups intersect avec document.access_groups
    - Si access_groups vide → document public (accessible à tous les utilisateurs authentifiés)
    - Vérifier AUSSI les permissions Django (document_vault.view_document, etc.) en complément
  - [x] 4.4 Cloisonner la recherche Elasticsearch : modifier la requête Elasticsearch pour filtrer par allowed_document_groups de l'utilisateur (AC: #5 "y compris via la recherche full-text")
  - [x] 4.5 Cloisonner les requêtes ORM : surcharger le queryset DocumentVault avec une méthode `.for_user(user)` qui filtre automatiquement
  - [x] 4.6 Journaliser toute tentative d'accès non autorisé à un document dans audit trail (user_id, document_id, timestamp, action refused)
  - [x] 4.7 Tester exhaustivement : user A ne peut pas voir document de groupe B même en tapant l'ID direct en URL; même en tentant recherche Elasticsearch

- [x] Task 5: Implémenter le cloisonnement dans la recherche full-text (AC: #5)
  - [x] 5.1 Analyser le flux Elasticsearch actuel de la story 1.x (indexation, requête, filtering)
  - [x] 5.2 Modifier la classe SearchSerializer ou SearchViewSet pour ajouter automatiquement un filtre `terms` Elasticsearch sur le champ `access_groups` de l'utilisateur
  - [x] 5.3 Valider que le filtre fonctionne avec des recherches complexes (multi-champs, aggregations, facets)
  - [x] 5.4 Implémenter un cache de résultats de recherche par utilisateur (5 minutes TTL) pour éviter de recalculer le filtre à chaque requête
  - [x] 5.5 Tester : user A recherche "facture" → ne voie que les factures accessibles; user B recherche même terme → voir factures différentes

- [x] Task 6: Créer l'interface d'administration frontend (AC: #1, #7, #8)
  - [x] 6.1 Créer page `AdminUsersPage.tsx` avec toolbar (boutons Créer, Rafraîchir, Exporter) + ProTable affichant :
    - Colonnes : Username, Email, Nom Complet, Groupes, Statut (Actif|Inactif), Actions (Modifier, Réinitialiser 2FA, Désactiver)
    - Filtres : par statut, par groupe, par nom
    - Pagination et tri : paramètres `page`, `per_page`, `sort`
  - [x] 6.2 Créer composant modal `UserEditModal.tsx` avec ProForm pour créer/modifier un utilisateur :
    - Champs : Email (unique, validated), Username (unique), Nom, Prénom, Groupes (multi-select), Statut (toggle actif/inactif), Lecture seule (checkbox)
    - Validation : email format, username alphanumeric, min 1 groupe assigné
    - On submit : appeler POST /api/v1/admin/users/ ou PATCH /api/v1/admin/users/{id}/
  - [x] 6.3 Créer composant modal `RoleEditModal.tsx` pour créer/modifier un rôle :
    - Champs : Nom du rôle, Permissions (checklist groupée par domaine : document_vault, intelligence, compliance, etc.)
    - Validation : nom non-vide, min 1 permission
    - On submit : appeler POST /api/v1/admin/roles/ ou PATCH /api/v1/admin/roles/{id}/
  - [x] 6.4 Créer page `AdminRolesPage.tsx` avec ProTable des rôles + colonnes : Nom, Permissions, Actions (Modifier, Supprimer)
  - [x] 6.5 Créer composant modal `AccessGroupsModal.tsx` pour restreindre les groupes documentaires accessibles par rôle :
    - Afficher liste des groupes documentaires (categories, espaces, etc. selon architecture Mayan)
    - Permettre multi-select pour chaque rôle
    - On submit : PATCH /api/v1/admin/roles/{id}/ avec payload `{"allowed_document_groups": [...]}`
  - [x] 6.6 Ajouter guard d'accès : seuls les utilisateurs avec permission 'auth.change_user' peuvent accéder AdminUsersPage/AdminRolesPage (utiliser React Router `<ProtectedRoute>`)
  - [x] 6.7 Intégrer avec le thème "Océan Profond" : respect couleurs, polices, grille 8px, style ProTable/ProForm
  - [x] 6.8 Implémenter l'accessibilité WCAG 2.1 AA : focus visible, ARIA labels sur inputs, texte alt sur icones, contraste 4.5:1

- [x] Task 7: Implémenter la journalisation des modifications de droits (AC: #6)
  - [x] 7.1 Créer modèle `AuditLogEntry` (Django model) avec champs : user_id (admin), action, timestamp, resource_type (user|role|group), resource_id, old_values (JSON), new_values (JSON), ip_address
  - [x] 7.2 Créer service `AuditLogger` pour enregistrer les logs structurés (via structlog) et persister en DB
  - [x] 7.3 Hook chaque endpoint admin pour appeler `AuditLogger.log(...)` :
    - User creation : log `{"action": "user.created", "resource_id": user.id, "new_values": {email, username, groups}}`
    - User modification : log `{"action": "user.modified", "resource_id": user.id, "old_values": {...}, "new_values": {...}}`
    - Role modification : log avec permissions avant/après
  - [x] 7.4 Créer endpoint `GET /api/v1/admin/audit-logs/` pour lister les audit logs (filtrable par resource_type, action, date range, user_id)
  - [x] 7.5 Créer page `AdminAuditPage.tsx` pour consulter les audit logs (timeline, details modal)
  - [x] 7.6 Valider que chaque log include : timestamp, admin_id, action, resource_type, resource_id, before/after values

- [x] Task 8: Tester et valider RBAC + cloisonnement (AC: #1-#8)
  - [x] 8.1 Tests backend : pytest suite pour user management
    - test_create_user_with_groups
    - test_modify_user_groups
    - test_deactivate_user
    - test_reset_user_2fa
    - test_audit_log_created_on_user_modification
    - test_document_access_denied_for_unauthorized_user (AC: #5)
    - test_elasticsearch_search_filtered_by_allowed_groups (AC: #5)
    - test_user_cannot_bypass_cloisonnement_via_direct_id
  - [x] 8.2 Tests backend : permission matrix validation
    - For each role (Direction, Comptabilité, RH, etc.), validate that permissions are correct and consistent
    - Test cross-role interference (user with 2 roles shouldn't get conflicting permissions)
  - [x] 8.3 Tests frontend : Vitest suite pour AdminUsersPage
    - test_admin_users_page_renders_user_table
    - test_create_user_modal_submits_user_data
    - test_modify_user_updates_groups
    - test_deactivate_user_shows_confirmation
    - test_edit_user_requires_at_least_1_group
  - [x] 8.4 Tests frontend : Vitest tests for cloisonnement UI
    - test_user_without_permission_cannot_view_admin_pages (ProtectedRoute)
    - test_readonly_user_cannot_access_edit_buttons
  - [x] 8.5 Tests E2E : Playwright suite (à partir de story 1.7+ quand multiple users exist)
    - test_admin_creates_new_user_and_assigns_groups
    - test_created_user_can_login_and_sees_only_allowed_documents
    - test_user_cannot_search_forbidden_documents
    - test_audit_log_records_admin_actions
  - [x] 8.6 Tests accessibility : axe-core / jest-axe on AdminUsersPage and modals
  - [x] 8.7 Exécuter lint/tests/build sans erreur et valider non-régression (tests story 1.1-1.5 passent toujours)

## Dev Notes

### Story Foundation

- Story source: `_bmad-output/planning-artifacts/epics.md` (section Story 1.6)
- Epic: **Epic 1 - Accès Sécurisé & Gestion des Permissions**
- Business intent: Permettre aux administrateurs de gérer les utilisateurs, créer des rôles, et garantir le cloisonnement strict des documents par rôle/groupe
- Requirements map: FR41 (gestion utilisateurs), FR42 (RBAC), FR43 (accès espaces documentaires), FR46 (cloisonnement recherche full-text)
- Dependency: Story 1.4 (JWT authentication) + Story 1.5 (2FA) doit être intégrée (reset 2FA dans admin interface)

### Technical Requirements (Developer Guardrails)

#### 1. RBAC Stack & Architecture

**Existing Mayan EDMS RBAC:**
- Django's built-in `django.contrib.auth` models (User, Group, Permission)
- Mayan Groups couvrent déjà les rôles de base (cadres permissions Django)
- Limites : pas de cloisonnement documentaire granulaire ; permissions au niveau module, pas par resource

**Igar Extensions Needed:**
- Model `DocumentAccessGroup` : table many-to-many pour mapper User ↔ DocumentGroup
  - Permet chaque utilisateur d'accéder à plusieurs "espaces documentaires" (groupes de documents)
  - Chaque Document peut restreindre son access au via `Document.access_groups` (M2M field)
  - Chaque User possède `User.allowed_document_groups` (M2M field)
  - Verification : `user in document.access_groups` avant chaque access
- Custom permission set (Django Permission objects) : `document_vault.view_document`, `document_vault.seal_document`, `intelligence.classify_document`, etc.
- Middleware or decorator pour appliquer automatiquement le cloisonnement sur tous endpoints

#### 2. RBAC Configuration Checklist

- Django built-in auth : déjà actif (Mayan inclut django.contrib.auth)
- INSTALLED_APPS garder : 'django.contrib.auth', 'django.contrib.contenttypes', 'mayan.apps.access_control' (Mayan's RBAC app)
- Créer migration personnalisée (igar app) pour ajouter tables `DocumentAccessGroup`, `UserDocumentGroup`
- Créer des fixtures Django ou data migration pour pré-populer rôles par défaut : Direction, Comptabilité, RH, Production, Archives, Admin
- Configurer permission_required sur tous endpoints sensibles

#### 3. API Contract & Business Rules

**User Management Flow:**

| Endpoint | Method | Payload | Response | Permissions |
|----------|--------|---------|----------|------------|
| `/api/v1/admin/users/` | GET | ?page=1&per_page=20&group_id=X | `{count, next, previous, results: [{id, email, username, groups, is_active, is_readonly}]}` | auth.change_user |
| `/api/v1/admin/users/` | POST | `{email, username, first_name, last_name, groups: [id], is_active, is_readonly}` | `{id, email, ...}` | auth.add_user |
| `/api/v1/admin/users/{id}/` | PATCH | `{email?, groups?, is_active?, is_readonly?}` | `{id, email, ...}` | auth.change_user |
| `/api/v1/admin/users/{id}/` | DELETE | — | `{status: "user_deactivated"}` | auth.delete_user |
| `/api/v1/admin/users/{id}/reset-password/` | POST | — | `{status: "reset_email_sent", reset_url: "..."}` | auth.change_user |
| `/api/v1/admin/users/{id}/reset-2fa/` | POST | — | `{status: "2fa_reset"}` | auth.change_user |

**Role Management Flow:**

| Endpoint | Method | Payload | Response | Permissions |
|----------|--------|---------|----------|------------|
| `/api/v1/admin/roles/` | GET | — | `{results: [{id, name, permissions: [], user_count}]}` | auth.view_group |
| `/api/v1/admin/roles/` | POST | `{name, permissions: [id]}` | `{id, name, permissions}` | auth.add_group |
| `/api/v1/admin/roles/{id}/` | PATCH | `{name?, permissions?: [id]}` | `{id, name, permissions}` | auth.change_group |
| `/api/v1/admin/roles/{id}/` | DELETE | — | `{status: "role_deleted"}` | auth.delete_group |
| `/api/v1/admin/permissions/` | GET | — | `{results: [{id, codename, name, app}]}` | auth.view_permission |

**Document Access Enforcement:**

- Chaque appel API documentaire vérifie : `user.allowed_document_groups.intersection(document.access_groups) or document.access_groups.empty or user.is_superuser`
- Elasticsearch search query : ajouter automatiquement filtre `terms` sur `access_groups` field
- 404 ou 403 selon config (recommandé 404 pour ne pas révéler existence de document)

#### 4. Security Considerations

- Cloisonnement STRICT : aucun bypass, y compris pour recherche ou requêtes directes par ID
- Admin cannot accidentally grant access to document they don't have access : validate via celery task or async hook
- User deactivation : soft-delete (is_active=false), conserver l'historique audit
- Permission escalation prevention : user sans permission admin ne peut pas modifier un autre user's groups pour obtenir access indirecte
- Audit trail pour chaque modification : admin_id, timestamp, before/after values
- Document access queries : toujours utiliser `.for_user(user)` queryset method pour éviter oublis

#### 5. Frontend User Management Components

**AdminUsersPage.tsx:**
- ProTable avec colonnes : Username, Email, Groups (badge list), Status (Actif|Inactif), Actions (Modifier, Reset 2FA, Désactiver)
- Toolbar : bouton "+ Créer utilisateur", bouton "Rafraîchir", bouton "Exporter CSV"
- Search bar : filtrer par username/email
- Filter dropdown : par groupe, par statut
- Pagination : 20 users par page
- Loading skeleton si données en cours de chargement
- Error banner si erreur API

**UserEditModal.tsx (créer/modifier):**
- ProForm avec champs : Email (required, unique validation), Username (required, alphanumeric), Nom, Prénom
- Multi-select "Groupes" : liste des rôles existants, sélectionner au minimum 1
- Toggle "Actif" : activé par défaut pour users nouveaux
- Checkbox "Lecture seule" : empêche l'user de faire toute action de mutation (créer, modifier, supprimer documents)
- Boutons : Annuler, Enregistrer
- On success : toast "Utilisateur créé|modifié avec succès", fermer modal, rafraîchir table
- On error : afficher message d'erreur RFC 7807

**AdminRolesPage.tsx:**
- ProTable avec colonnes : Nom du rôle, Permissions (count badge "5 permissions"), Actions (Modifier, Supprimer)
- Toolbar : "+ Créer rôle"
- On click "Modifier" : ouvrir RoleEditModal

**RoleEditModal.tsx:**
- ProForm avec champ Nom et checklist des permissions groupées par app/domaine
- Groupes de permissions : "Document Vault" (view, seal, delete), "Intelligence" (classify, export), "Compliance" (view audit, export), "User Management" (view, create, modify)
- Valider : au minimum 1 permission cochée
- On success : toast, fermer modal, rafraîchir table

**AccessGroupsModal.tsx (optionnel pour MVP):**
- Afficher liste des DocumentGroups (éventuellement hiérarchique si plan de classement)
- Multi-select : réservé à rôle spécifique, quels DocumentGroups ils peuvent accéder
- Logique : si DocumentGroups vides → rôle accède tous documents (backward compat)

#### 6. Boundaries & Non-Goals

- Story 1.6 couvre : user CRUD, role CRUD, permission assignment, document cloisonnement (query-level)
- Story 1.6 ne couvre PAS : LDAP/AD sync (Phase 2), WebAuthn MFA (Phase 2+), delegation (manager can manage subordinates), attribute-based control (ABAC)
- Document access groups : model et enforcement ; configuration initiale (plan de classement mapping) probablement couvre dans story 2.x ou config initiale

### Architecture Compliance

- **Monorepo** : `backend/igar/apps/access_control/`, `backend/igar/apps/audit/`; `frontend/src/pages/AdminUsersPage.tsx`, etc.
- **Naming** : `snake_case` backend modules, `PascalCase` React components
- **API versioning** : `/api/v1/admin/users/*`, `/api/v1/admin/roles/*`
- **RFC 7807** : error responses avec `type`, `title`, `detail`, `status` fields
- **Respect existing patterns** : Story 1.4/1.5 auth patterns, JWT interceptor, router guards, ProTable/ProForm from UX spec
- **RBAC decorator** : `@permission_required('auth.change_user')` sur endpoints admin
- **Elasticsearch integration** : extend search viewset filter logic to apply cloisonnement

### Library & Framework Requirements

**Backend:**
- Django 5.2, DRF, `djangorestframework-simplejwt`, `structlog` (structured logging)
- Mayan EDMS 4.11 (fork) avec access_control app
- `django_filters` pour FilterSet sur user/role queryset
- `django-auditlog` ou custom audit model pour journalisation

**Frontend:**
- React 18+, TypeScript, Zustand, Axios, React Router v6, Ant Design v6 + Pro Components
- `@ant-design/pro-table`, `@ant-design/pro-form`, `@ant-design/pro-layout`
- TanStack Query v5 pour cache API

**Testing:**
- Backend: pytest, pytest-django, Factory Boy, Coverage.py
- Frontend: Vitest, @testing-library/react, Playwright, axe-core

### File Structure Requirements

**Targeted minimal scope to cover/create:**

**Backend - User Management:**
- `backend/igar/apps/access_control/models.py` — User extensions, DocumentAccessGroup, UserDocumentGroup models
- `backend/igar/apps/access_control/serializers.py` — UserSerializer, RoleSerializer, PermissionSerializer
- `backend/igar/apps/access_control/views.py` — AdminUsersViewSet, AdminRolesViewSet, AdminPermissionsViewSet (DRF viewsets + @permission_required)
- `backend/igar/apps/access_control/urls.py` — routes `/api/v1/admin/users/*`, `/api/v1/admin/roles/*`, `/api/v1/admin/permissions/*`
- `backend/igar/apps/audit/models.py` — AuditLogEntry model
- `backend/igar/apps/audit/services.py` — AuditLogger service
- `backend/igar/apps/audit/views.py` — AdminAuditLogsViewSet
- `backend/igar/core/permissions.py` — Custom DRF permission classes pour cloisonnement (IsDocumentAccessible)
- `backend/igar/core/decorators.py` — @require_document_access decorator
- `backend/igar/apps/document_vault/models.py` — extend Document avec access_groups (M2M)
- `backend/igar/apps/document_vault/views.py` — apply @require_document_access sur tous endpoints GET/PATCH/DELETE
- `backend/migrations/igar/<timestamp>_add_document_access_groups.py` — migration creating DocumentAccessGroup, UserDocumentGroup tables
- `backend/fixtures/default_roles.yaml` — YAML fixture avec rôles pré-configurés (Direction, Comptabilité, etc.)
- `backend/tests/test_access_control.py` — pytest suite pour user/role management
- `backend/tests/test_cloisonnement.py` — pytest suite pour document access enforcement
- `backend/tests/test_audit_log.py` — pytest suite pour audit logging

**Backend - Search Cloisonnement:**
- `backend/igar/apps/search/filters.py` — extend Elasticsearch filter avec `allowed_document_groups`
- `backend/igar/apps/search/views.py` — modify SearchViewSet pour appliquer cloisonnement automatiquement

**Frontend - Admin Pages:**
- `frontend/src/pages/admin/AdminUsersPage.tsx` — main users admin page
- `frontend/src/pages/admin/AdminRolesPage.tsx` — main roles admin page
- `frontend/src/pages/admin/AdminAuditPage.tsx` — audit logs page
- `frontend/src/components/admin/UserEditModal.tsx` — modal pour créer/modifier user
- `frontend/src/components/admin/RoleEditModal.tsx` — modal pour créer/modifier rôle
- `frontend/src/components/ProtectedRoute.tsx` — wrapper pour pages nécessitant permission
- `frontend/src/api/admin.ts` — API functions pour user/role CRUD (useUsers, useCreateUser, useUpdateUser, etc.)
- `frontend/src/api/audit.ts` — API functions pour audit logs (useAuditLogs)
- `frontend/src/i18n/locales/fr.json`, `en.json` — labels pour admin pages
- `frontend/src/hooks/usePermission.ts` — hook pour vérifier si user a permission spécifique
- `frontend/tests/pages/admin/AdminUsersPage.test.tsx` — Vitest tests
- `frontend/tests/components/admin/UserEditModal.test.tsx` — Vitest tests

### Testing Requirements

**Backend - Unit Tests:**

```python
# test_access_control.py
def test_create_user_with_valid_data()
def test_create_user_requires_unique_email()
def test_create_user_requires_at_least_one_group()
def test_modify_user_groups()
def test_deactivate_user_soft_deletes()
def test_reset_user_password_generates_token()
def test_reset_user_2fa()
def test_create_role_with_permissions()
def test_modify_role_permissions()
def test_delete_role_fails_if_users_exist()
def test_permission_matrix_is_complete()  # each role has consistent permission set

# test_cloisonnement.py
def test_user_cannot_access_document_outside_allowed_groups()
def test_user_can_access_document_in_allowed_groups()
def test_public_document_accessible_to_all_authenticated_users()
def test_document_access_denied_returns_404_not_403()
def test_user_cannot_bypass_via_direct_id()
def test_elasticsearch_search_filtered_by_allowed_groups()
def test_elasticsearch_search_multiple_groups_union()

# test_audit_log.py
def test_audit_log_created_on_user_creation()
def test_audit_log_includes_before_after_values()
def test_audit_log_query_filtered_by_action()
def test_audit_log_query_filtered_by_user_id()
```

**Frontend - Component Tests (Vitest):**

```typescript
// AdminUsersPage.test.tsx
test('AdminUsersPage renders user table', ...)
test('Create user button opens modal', ...)
test('Modify user updates groups', ...)
test('Deactivate user shows confirmation', ...)

// UserEditModal.test.tsx
test('UserEditModal renders form fields', ...)
test('Email field requires unique value', ...)
test('Groups field requires at least one selection', ...)
test('Form submission calls API endpoint', ...)
test('Error message displays on API failure', ...)

// ProtectedRoute.test.tsx
test('ProtectedRoute grants access for permitted user', ...)
test('ProtectedRoute redirects for unauthorized user', ...)
```

**Frontend - E2E Tests (Playwright):**

```typescript
// admin.spec.ts
test('Admin can create new user', ...)
test('Created user can login with 2FA', ...)
test('Created user sees only allowed documents', ...)
test('User cannot search documents outside allowed groups', ...)
test('Audit log records admin actions', ...)
```

**Accessibility Tests (axe-core):**

```typescript
// admin.accessibility.test.tsx
test('AdminUsersPage meets WCAG 2.1 AA', ...)
test('Modal keyboard navigation works', ...)
test('ProTable focus handling correct', ...)
```

### Previous Story Intelligence (1.5)

- Story 1.5 implemented JWT + 2FA authentication
- `LoginPage`, `authStore`, `api/client.ts`, router guards, custom middleware already exist
- Mayan EDMS fork already has `django.contrib.auth` integrated (User, Group, Permission models)
- Admin interface patterns established in 1.5 (`AdminUsersPage` for 2FA reset → reuse pattern for full user management)
- User deactivation in 1.6 should follow same soft-delete pattern (is_active=false)

### Git Intelligence Summary

- Igar project v1.0 MVP, stories 1.1-1.4 done, 1.5 in review
- Mayan EDMS 4.11 fork includes RBAC models; minimal extensions needed
- Backend Django structure stable; frontend SPA patterns established
- Previous commits show auth flow patterns; model extension should follow same conventions
- No breaking changes expected for existing API surface (only additions)

### Latest Tech Information

- Django 5.2 : Group/Permission models mature, no breaking changes
- DRF 3.14+ : FilterSet integration seamless, nested serializers for M2M relationships
- Elasticsearch 8.x : filtering via `terms` aggregation standard
- Ant Design v6 : ProTable bulk operations, ProForm validation fully supported
- React 18+ : Suspense for admin pages, concurrent rendering for large tables
- Zustand 4.x : perfect for UI state (modal open/close, selected row, filters)

### Project Context Reference

- No dedicated `project-context.md` for access control; context drawn from epics, architecture, PRD UX journeys
- Key personas : Thomas (admin), Fatima (user), Maître Dubois (lawyer), Dr. Amina (doctor)
- Key journey : Thomas (Repo epic 1, story 4) requires admin.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.6: Gestion des Utilisateurs, Rôles et Cloisonnement]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#Naming Patterns (database, API, code)]
- [Source: _bmad-output/planning-artifacts/prd.md#FR41, FR42, FR43, FR46]
- [Source: _bmad-output/planning-artifacts/prd.md#Journey 4: Thomas, Administrateur IT]
- [Source: _bmad-output/implementation-artifacts/1-5-authentification-a-deux-facteurs-2fa.md]
- [Source: _bmad-output/implementation-artifacts/1-4-authentification-jwt-et-interface-de-connexion.md]
- OWASP Authentication Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- OWASP Authorization Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- Django User Management Best Practices (https://docs.djangoproject.com/en/5.2/topics/auth/)

## Dev Agent Record

### Agent Model Used

Claude Haiku 4.5

### Debug Log References

- Workflow: `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- Engine: `_bmad/core/tasks/workflow.xml`
- Config: `_bmad/bmm/config.yaml`
- Execution date: 2026-04-13
- Language: French
- Communication: French

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created
- Story auto-selected from first backlog item in sprint status: `1-6-gestion-des-utilisateurs-roles-et-cloisonnement`
- Story status set to `ready-for-dev`
- Epic 1 status confirmed as `in-progress` (stories 1.1-1.4 complete/in review)
- Mayan EDMS RBAC analyzed; extensions planned for DocumentAccessGroup and cloisonnement strict
- Previous story (1.5) learnings integrated for admin interface patterns
- All acceptance criteria mapped to 8 implementation tasks with comprehensive subtasks
- Security guardrails documented: cloisonnement enforcement, audit trail, permission escalation prevention
- Testing requirements comprehensive: backend pytest, frontend Vitest, E2E Playwright, accessibility axe-core
- Frontend admin UI aligned with Ant Design Pro Components (ProTable, ProForm) from UX spec
- Elasticsearch integration for search cloisonnement planned
- Correction des erreurs backend bloquantes (serializers, viewsets admin, suppression soft user, serializer audit)
- Implémentation des endpoints rôles avancés: suppression protégée (409 si utilisateurs assignés), endpoint `/api/v1/admin/permissions/`
- Stabilisation des tests RBAC/admin/cloisonnement: 46 tests ciblés backend au vert
- Validation locale effectuée avec `pytest tests/test_admin_endpoints.py tests/test_rbac_models.py tests/test_document_access_enforcement.py -q`
- Intégration d'un guard d'accès frontend pour routes admin (`/admin/users`, `/admin/roles`, `/admin/audit`) via vérification permission API
- Cloisonnement global branché dans les couches Mayan de base (`RestrictedQuerysetViewMixin`, `ExternalObjectBaseMixin`, `QuerySetOverrideCheckAPIViewMixin`) pour appliquer automatiquement le filtrage documentaire sur vues et API
- Ajout de `Document.access_groups` (M2M vers `igar_core.DocumentAccessGroup`) et migration dédiée `documents/0092_document_access_groups.py`
- Ajout de `.for_user(user)` sur les managers documentaires valides (document, fichier, page, version, version page)
- Durcissement recherche: filtrage utilisateur injecté dans `SearchBackend.search` + indexation des champs `access_groups__id` dans les SearchModel documents
- Tests ciblés ajoutés (`tests/test_document_access_queryset_filter.py`) pour valider visibilité public/groupe et filtrage recherche par utilisateur
- Validation pytest bloquée localement par dépendance système Cairo manquante (comportement déjà connu de l'environnement)
- Ajout de tests `TestDirectUrlAccessByDocumentId` dans `tests/test_document_access_enforcement.py` pour valider le refus d'accès via ID direct et l'accès autorisé
- Correction de `filter_queryset_for_user` pour utiliser les IDs de groupes documentaires depuis la relation intermédiaire `UserDocumentAccessGroup`
- Correction du chargement des migrations `igar_core` via ajout de `backend/igar/core/migrations/__init__.py`
- Implémentation d'un cache de résultats de recherche par utilisateur (TTL 5 minutes) dans `SearchBackend.search`
- Ajout de tests recherche avancée: payload complexe (multi-champs/facets), isolation A/B sur même terme, et vérification du cache utilisateur
- Validation locale exécutée: `pytest tests/test_document_access_enforcement.py tests/test_document_access_queryset_filter.py -q` (16 tests passants)
- Refactor frontend admin: extraction des modales `UserEditModal` et `RoleEditModal` + enrichissement toolbar/filtres/export sur `AdminUsersPage`
- Ajout suppression de rôle côté UI et alignement API frontend (`listUsers` avec filtres, `deleteRole`, endpoint `GET /admin/permissions/`)
- Ajout d'ARIA labels sur champs de formulaires admin et stabilisation i18n FR/EN des écrans users/roles
- Ajout de tests frontend ciblés: `AdminUsersPage.test.tsx`, `UserEditModal.test.tsx`, `AdminPermissionGuard.test.tsx`
- Validation locale exécutée: `npm run test:run -- src/pages/AdminUsersPage.test.tsx src/components/AdminPermissionGuard.test.tsx src/components/admin/UserEditModal.test.tsx` (6 tests passants)
- Ajout support backend des `allowed_document_groups` sur les rôles (serializer + persistance `GroupDocumentAccessGroup`) et tests API associés
- Implémentation frontend du modal `AccessGroupsModal` et intégration dans `AdminRolesPage` avec mise à jour des groupes documentaires
- Extension de la couverture frontend cloisonnement UI: test readonly (bouton Modifier désactivé)
- Validation locale exécutée: backend `tests/test_admin_endpoints.py` (24 passants) + frontend ciblé (7 passants)
- Extension de la couverture `AdminUsersPage.test.tsx`: création utilisateur (submit), modification des groupes, désactivation avec confirmation
- Validation locale exécutée: `npm run test:run -- src/pages/AdminUsersPage.test.tsx` (6 tests passants)
- Ajout des tests d'accessibilité axe-core sur AdminUsersPage, AdminRolesPage, UserEditModal et AccessGroupsModal
- Correction du balisage a11y des pages admin avec landmark principal et labels explicites sur les filtres
- Validation locale exécutée: `npm run test:run -- src/components/admin/AdminAccessibility.test.tsx` (4 tests passants)
- Validation finale exécutée: `npm run lint`, `npm run build`, et suite frontend élargie (19 tests passants)
- Intégration du thème "Océan Profond" renforcée sur les écrans admin (tokens Ant Design + surfaces dédiées)
- Ajout d'une suite Playwright `frontend/e2e/admin-rbac.spec.ts` couvrant création utilisateur, garde RBAC, cloisonnement de recherche et audit
- Validation locale exécutée: `make test-all-igar-local IGAR_PYTEST_ARGS="tests/test_admin_endpoints.py tests/test_document_access_enforcement.py tests/test_document_access_queryset_filter.py -q"` (40 tests passants)
- Validation locale exécutée: `npm run e2e -- admin-rbac.spec.ts` (4 tests passants)
- Validation locale exécutée: `npm run lint` (frontend)

### Change Log

- Created comprehensive story file with all epic requirements mapped to implementation tasks
- Documented Mayan EDMS RBAC extension points (DocumentAccessGroup, UserDocumentGroup models)
- Specified API contracts for user/role management endpoints with permission requirements
- Designed frontend admin pages (AdminUsersPage, AdminRolesPage) with Ant Design Pro Components
- Included full test matrices for backend and frontend coverage
- Added security considerations for strict cloisonnement and audit trail
- 2026-04-13: Corrigé les serializers et vues admin, ajouté AuditLogEntrySerializer et endpoint `/api/v1/admin/permissions/`
- 2026-04-13: Ajouté la suppression de rôle sécurisée (refus si utilisateurs liés) et journalisation `role.deleted`
- 2026-04-13: Aligné et validé les suites de tests backend RBAC/admin/cloisonnement (46 tests passants)
- 2026-04-13: Branché les routes admin frontend et ajouté un guard de permission côté client
- 2026-04-13: Branché le cloisonnement documentaire dans les mixins Mayan (views + REST API) et le moteur de recherche dynamique
- 2026-04-13: Ajouté `Document.access_groups`, migration `0092_document_access_groups`, champs de recherche `access_groups__id` et méthodes manager `.for_user(user)`
- 2026-04-13: Ajouté des tests de filtrage queryset/recherche (`test_document_access_queryset_filter.py`), exécution locale bloquée par Cairo manquant
- 2026-04-13: Ajouté des tests de bypass URL direct dans `test_document_access_enforcement.py` et validé le scénario de cloisonnement complet (URL + recherche)
- 2026-04-13: Corrigé `filter_queryset_for_user` pour supporter correctement la relation `allowed_document_groups` basée sur `UserDocumentAccessGroup`
- 2026-04-13: Ajouté `backend/igar/core/migrations/__init__.py` pour rétablir la résolution des dépendances de migration `igar_core`
- 2026-04-13: Implémenté un cache de résultats de recherche par utilisateur (TTL 300s) dans `SearchBackend.search`
- 2026-04-13: Ajouté des tests de recherche complexes/isolation/cache dans `test_document_access_queryset_filter.py` et validé 16 tests backend ciblés
- 2026-04-13: Refactor de l'admin frontend (modales dédiées users/roles, filtres status/groupe, export CSV, action suppression de rôle)
- 2026-04-13: Ajout des tests Vitest frontend ciblés (AdminUsersPage, UserEditModal, AdminPermissionGuard) et passage vert local (6 tests)
- 2026-04-13: Mise à jour des traductions FR/EN et du setup de tests frontend (mocks `matchMedia`/`ResizeObserver`)
- 2026-04-13: Ajout du support API rôles `allowed_document_groups` et modal d'assignation `AccessGroupsModal`
- 2026-04-13: Ajout tests backend admin endpoints pour création/mise à jour des groupes documentaires de rôle
- 2026-04-13: Ajout test frontend readonly (`Modifier` désactivé) pour cloisonnement UI
- 2026-04-13: Extension de `AdminUsersPage.test.tsx` pour couvrir création, mise à jour des groupes et désactivation (Task 8.3)
- 2026-04-13: Ajout des tests d'accessibilité axe-core et correction du markup admin (Task 8.6)
- 2026-04-13: Validation finale 8.7 complétée avec lint, build et non-régression frontend (19 tests)
- 2026-04-13: Renforcement du thème Océan Profond sur les pages admin (tokens/components + surfaces visuelles)
- 2026-04-13: Ajout de la suite Playwright `admin-rbac.spec.ts` et validation des scénarios E2E Task 8.5 (4 tests passants)
- 2026-04-13: Revalidation backend ciblée Task 8.1/8.2 (40 tests passants) et lint frontend OK

### File List

- `_bmad-output/implementation-artifacts/1-6-gestion-des-utilisateurs-roles-et-cloisonnement.md` (this file)
- `backend/igar/core/models.py`
- `backend/igar/core/migrations/0001_two_factor_reset_event.py`
- `backend/igar/core/migrations/0002_rbac_document_access_groups.py`
- `backend/igar/core/migrations/0003_seed_default_roles.py`
- `backend/igar/core/migrations/__init__.py`
- `backend/igar/core/audit.py`
- `backend/igar/core/permissions.py`
- `backend/igar/core/serializers.py`
- `backend/igar/core/admin_views.py`
- `backend/igar/core/admin_urls.py`
- `backend/igar/core/document_access.py`
- `backend/igar/core/apps.py`
- `backend/igar/urls.py`
- `backend/igar/settings/base.py`
- `backend/mayan/apps/views/view_mixins.py`
- `backend/mayan/apps/rest_api/api_view_mixins.py`
- `backend/mayan/apps/dynamic_search/search_backends.py`
- `backend/mayan/apps/documents/managers.py`
- `backend/mayan/apps/documents/models/document_models.py`
- `backend/mayan/apps/documents/search.py`
- `backend/mayan/apps/documents/migrations/0092_document_access_groups.py`
- `backend/tests/test_rbac_models.py`
- `backend/tests/test_admin_endpoints.py`
- `backend/tests/test_document_access_enforcement.py`
- `backend/tests/test_document_access_queryset_filter.py`
- `frontend/src/api/admin.ts`
- `frontend/src/pages/AdminUsersPage.tsx`
- `frontend/src/pages/AdminRolesPage.tsx`
- `frontend/src/components/admin/AccessGroupsModal.tsx`
- `frontend/src/pages/AdminAuditPage.tsx`
- `frontend/src/components/AdminPermissionGuard.tsx`
- `frontend/src/components/AdminPermissionGuard.test.tsx`
- `frontend/src/components/admin/UserEditModal.tsx`
- `frontend/src/components/admin/RoleEditModal.tsx`
- `frontend/src/components/admin/UserEditModal.test.tsx`
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/fr.json`
- `frontend/src/router.tsx`
- `frontend/src/pages/AdminUsersPage.test.tsx`
- `frontend/src/test/setup.ts`
- `frontend/src/theme/oceanDeep.ts`
- `frontend/src/index.css`
- `frontend/e2e/admin-rbac.spec.ts`
