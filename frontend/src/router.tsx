import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppLayout } from './layouts/AppLayout'
import { AdminPage } from './pages/AdminPage'
import { AdminAuditPage } from './pages/AdminAuditPage'
import { AdminRolesPage } from './pages/AdminRolesPage'
import { AdminUsersPage } from './pages/AdminUsersPage'
import { ConformitePage } from './pages/ConformitePage'
import { DocumentsPage } from './pages/DocumentsPage'
import { ImportPage } from './pages/ImportPage'
import { LoginPage } from './pages/LoginPage'
import { E2EImportHarnessPage } from './pages/E2EImportHarnessPage'
import { TwoFAInitPage } from './pages/TwoFAInitPage'
import { TwoFASetupPage } from './pages/TwoFASetupPage'
import { TwoFAVerifyPage } from './pages/TwoFAVerifyPage'
import { AdminPermissionGuard } from './components/AdminPermissionGuard'
import { RequireAuth, PublicOnly } from './components/RouteGuards'

const e2eRoutes = import.meta.env.VITE_E2E === '1'
  ? [{ path: '/e2e/import', element: <E2EImportHarnessPage /> }]
  : []

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RequireAuth />,
    children: [
      {
        path: '/',
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="/documents" replace /> },
          { path: 'documents', element: <DocumentsPage /> },
          { path: 'import', element: <ImportPage /> },
          { path: 'conformite', element: <ConformitePage /> },
          { path: 'admin', element: <AdminPage /> },
          {
            path: 'admin',
            element: <AdminPermissionGuard />,
            children: [
              { path: 'users', element: <AdminUsersPage /> },
              { path: 'roles', element: <AdminRolesPage /> },
              { path: 'audit', element: <AdminAuditPage /> },
            ],
          },
        ],
      },
    ],
  },
  {
    element: <PublicOnly />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/login/2fa', element: <TwoFAInitPage /> },
      { path: '/login/2fa/setup', element: <TwoFASetupPage /> },
      { path: '/login/2fa/verify', element: <TwoFAVerifyPage /> },
    ],
  },
  ...e2eRoutes,
])
