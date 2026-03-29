# Story 1.3: Interface Utilisateur de Base et Theme Igar

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developpeur**,
I want **initialiser le frontend SPA React avec Vite 8, TypeScript, Ant Design v6, le theme "Ocean Profond", le routing et l'internationalisation**,
so that **l'interface utilisateur dispose d'une base coherente et thematisee prete pour le developpement des composants**.

## Acceptance Criteria

1. **Given** le projet frontend initialise avec `create-vite react-swc-ts` **When** je lance `npm run dev` **Then** l'application demarre avec HMR sur `localhost:5173`
2. **And** Ant Design v6 + Pro Components sont installes et fonctionnels
3. **And** le theme "Ocean Profond" est configure via ConfigProvider (Primary #1B3A5C, Accent #10B981, Background #F8FAFC, etc.)
4. **And** la police Inter est chargee avec la grille 8px et la densite compacte (`size="small"`)
5. **And** ProLayout est configure avec sidebar (220px repliable vers 64px), header fixe (56px) avec barre de recherche placeholder, et zone de contenu fluide
6. **And** React Router v6 est configure avec les routes de base (Login, Documents, Import, Conformite, Admin)
7. **And** react-i18next est configure avec les fichiers `fr.json` et `en.json` (labels de base)
8. **And** Zustand stores sont initialises (`authStore`, `uiStore`)
9. **And** TanStack Query est configure avec le `QueryClientProvider`
10. **And** le client API (Axios) est configure avec le base URL et l'intercepteur JWT
11. **And** ESLint + Prettier + `eslint-plugin-jsx-a11y` sont configures
12. **And** Vitest + React Testing Library sont configures et un test basique passe
13. **And** `npm run build` produit un build de production sans erreur

## Tasks / Subtasks

- [x] Task 1: Initialiser le projet frontend (AC: #1)
  - [x] 1.1 Creer `frontend/` avec Vite React SWC TypeScript
  - [x] 1.2 Verifier execution de `npm run dev` avec HMR sur port 5173
  - [x] 1.3 Ajouter `.env.example` frontend (`VITE_API_URL`, `VITE_WS_URL`)

- [x] Task 2: Installer et configurer la stack UI (AC: #2, #3, #4)
  - [x] 2.1 Installer `antd`, `@ant-design/pro-components`, `@ant-design/icons`
  - [x] 2.2 Configurer `ConfigProvider` avec theme "Ocean Profond" (tokens principaux)
  - [x] 2.3 Charger la police Inter et appliquer grille 8px + densite compacte (`size="small"`)
  - [x] 2.4 Ajouter un layout de base responsive desktop-first

- [x] Task 3: Mettre en place la structure applicative (AC: #5, #6)
  - [x] 3.1 Configurer `ProLayout` (sidebar 220px/64px, header fixe 56px)
  - [x] 3.2 Configurer `React Router v6` avec routes: Login, Documents, Import, Conformite, Admin
  - [x] 3.3 Creer les pages placeholder correspondantes

- [x] Task 4: Configurer data/access layer frontend (AC: #7, #8, #9, #10)
  - [x] 4.1 Initialiser `react-i18next` avec `fr.json` et `en.json`
  - [x] 4.2 Initialiser Zustand (`authStore`, `uiStore`)
  - [x] 4.3 Initialiser TanStack Query (`QueryClient`, provider global)
  - [x] 4.4 Configurer client Axios (`baseURL`, interceptor JWT/refresh)

- [x] Task 5: Configurer qualite et tests (AC: #11, #12, #13)
  - [x] 5.1 Configurer ESLint + Prettier + `eslint-plugin-jsx-a11y`
  - [x] 5.2 Configurer Vitest + React Testing Library
  - [x] 5.3 Ecrire un smoke test d'interface (render App)
  - [x] 5.4 Valider `npm run build` sans erreur

- [x] Task 6: Validation finale story (AC: #1-#13)
  - [x] 6.1 Verifier `npm run dev` (HMR)
  - [x] 6.2 Verifier rendu theme et layout de base
  - [x] 6.3 Verifier routing base et i18n
  - [x] 6.4 Verifier tests et lint
  - [x] 6.5 Verifier build production

## Dev Notes

### Story Foundation

- Story source: `_bmad-output/planning-artifacts/epics.md` (section Story 1.3)
- Epic: **Epic 1 - Acces Securise & Gestion des Permissions**
- Business intent: etablir un socle frontend solide, thematise et maintenable avant les features d'auth, capture et administration

### Technical Requirements (Developer Guardrails)

1. **Frontend stack mandatee**
- Vite 8 + React (template `react-swc-ts`) + TypeScript strict.
- Ant Design v6 + Pro Components obligatoires pour coherence enterprise.

2. **Theme and visual baseline**
- Theme "Ocean Profond" via `ConfigProvider` avec tokens design centralises.
- Couleurs minimales a respecter: Primary `#1B3A5C`, Accent `#10B981`, Background `#F8FAFC`.
- Densite compacte (`size="small"`) et grille 8px.

3. **Layout and navigation**
- `ProLayout` impose comme shell applicatif de base.
- Routes de base obligatoires: Login, Documents, Import, Conformite, Admin.
- App desktop-first, comportement tablette acceptable, mobile non prioritaire (post-MVP).

4. **Data and state patterns**
- TanStack Query v5 pour server state.
- Zustand pour client state (stores separes par domaine, pas de mega-store).
- Axios centralise avec interceptor JWT (prepare Story 1.4).

5. **Naming and structure conventions**
- Composants React: PascalCase (`DocumentsPage.tsx`, `AppLayout.tsx`).
- Hooks/stores/utils: camelCase (`useAuth.ts`, `authStore.ts`).
- Structure recommandee a suivre: `src/api`, `src/components`, `src/layouts`, `src/pages`, `src/stores`, `src/i18n`, `src/theme`.

### Architecture Compliance

- Respecter la separation monorepo definie: `backend/`, `frontend/`, `infrastructure/`.
- Ne pas melanger logique metier backend dans le frontend; tout passe par API REST et WebSocket.
- S'aligner avec les conventions de l'architecture pour les formats d'erreur (RFC 7807 cote API), i18n et accessibilite.

### Library and Framework Requirements

- `react`, `react-dom`, `react-router-dom` (v6)
- `antd`, `@ant-design/pro-components`, `@ant-design/icons`
- `@tanstack/react-query`
- `zustand`
- `axios`
- `react-i18next`, `i18next`
- Dev quality: `eslint`, `prettier`, `eslint-plugin-jsx-a11y`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`

### File Structure Requirements

Cible minimale:

- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/DocumentsPage.tsx`
- `frontend/src/pages/ImportPage.tsx`
- `frontend/src/pages/ConformitePage.tsx`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/router.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/stores/authStore.ts`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/i18n/index.ts`
- `frontend/src/i18n/locales/fr.json`
- `frontend/src/i18n/locales/en.json`
- `frontend/src/theme/oceanDeep.ts`

### Testing Requirements

- Ajouter au moins un test de smoke UI (render root App) avec Vitest + RTL.
- Verifier que les routes de base sont montables sans crash.
- Integrer verification accessibilite lint (`eslint-plugin-jsx-a11y`) des le socle.
- Build production obligatoire (`npm run build`) avant cloture de story.

### Previous Story Intelligence (1.2)

- L'infrastructure Docker/Nginx preparee en Story 1.2 contient un routage frontend; cette story doit s'aligner sur le point d'entree attendu (`/`), et garder `localhost:5173` pour le mode dev.
- Les decisions backend et infra sont deja posees; eviter toute divergence de conventions (naming, env vars, separation des responsabilites).
- Le socle backend est deja en place; cette story ne doit pas modifier les apps backend.

### Git Intelligence Summary

- Aucun depot git detecte a la racine workspace pendant l'execution; intelligence git derivee des artefacts existants.
- Le dernier commit de reference documente dans les artefacts implementation est: `ce4d77f` (initialisation socle backend sur fork Mayan).

### Latest Tech Information

- Cette execution ne dispose pas d'acces web direct. Les choix versions sont donc alignes sur les documents projet deja valides (epics + architecture + UX).
- En cas de divergence future de versions npm, prioriser la compatibilite avec les decisions d'architecture documentees avant upgrade.

### Project Context Reference

- Aucun fichier `project-context.md` detecte dans le workspace.
- Context utilise: `epics.md`, `architecture.md`, `ux-design-specification.md`, plus les stories d'implementation existantes.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Platform Strategy]
- [Source: _bmad-output/implementation-artifacts/1-2-deploiement-operationnel-de-la-plateforme-igar.md]

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- Workflow: `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- Engine: `_bmad/core/tasks/workflow.xml`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story auto-selected from first backlog item in sprint status: `1-3-interface-utilisateur-de-base-et-theme-igar`.
- Story status set to `ready-for-dev`.
- Frontend Vite TypeScript initialise dans `frontend/` et execute en mode dev sur `localhost:5173` (HMR valide).
- Stack UI configuree: Ant Design v6, Pro Components, theme Ocean Profond, police Inter, layout de base responsive desktop-first.
- Structure applicative livree: ProLayout, routes React Router v6 (Login, Documents, Import, Conformite, Admin), pages placeholder.
- Data/access layer configure: react-i18next (fr/en), stores Zustand (auth/ui), TanStack Query provider, client Axios avec intercepteur JWT.
- Qualite et tests valides: ESLint + jsx-a11y + Prettier configures, Vitest + RTL operationnels, smoke test passant, build production passant.

### File List

- `_bmad-output/implementation-artifacts/1-3-interface-utilisateur-de-base-et-theme-igar.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `frontend/.env.example`
- `frontend/.prettierrc.json`
- `frontend/eslint.config.js`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/tsconfig.app.json`
- `frontend/vite.config.ts`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/i18n/index.ts`
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/fr.json`
- `frontend/src/index.css`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/main.tsx`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/pages/ConformitePage.tsx`
- `frontend/src/pages/DocumentsPage.tsx`
- `frontend/src/pages/ImportPage.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/router.tsx`
- `frontend/src/stores/authStore.ts`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/test/setup.ts`
- `frontend/src/theme/oceanDeep.ts`

## Change Log

- 2026-03-27: Implementation complete de la Story 1.3 (socle frontend, theme, routing, i18n, state, data layer, qualite, tests, build).
