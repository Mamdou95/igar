import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export function RequireAuth() {
  const location = useLocation()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}

export function PublicOnly() {
  const location = useLocation()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const twoFactorRequired = useAuthStore((state) => state.twoFactor.required)

  if (isAuthenticated) {
    return <Navigate to="/documents" replace />
  }

  if (twoFactorRequired && !location.pathname.startsWith('/login/2fa')) {
    return <Navigate to="/login/2fa" replace />
  }

  return <Outlet />
}
