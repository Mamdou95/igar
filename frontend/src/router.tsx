import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppLayout } from './layouts/AppLayout'
import { AdminPage } from './pages/AdminPage'
import { ConformitePage } from './pages/ConformitePage'
import { DocumentsPage } from './pages/DocumentsPage'
import { ImportPage } from './pages/ImportPage'
import { LoginPage } from './pages/LoginPage'
import { RequireAuth, PublicOnly } from './components/RouteGuards'

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
        ],
      },
    ],
  },
  {
    element: <PublicOnly />,
    children: [{ path: '/login', element: <LoginPage /> }],
  },
])
