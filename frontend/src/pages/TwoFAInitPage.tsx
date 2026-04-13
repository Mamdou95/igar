import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export function TwoFAInitPage() {
  const nextAction = useAuthStore((state) => state.twoFactor.nextAction)

  if (nextAction === 'setup') {
    return <Navigate to="/login/2fa/setup" replace />
  }

  if (nextAction === 'verify') {
    return <Navigate to="/login/2fa/verify" replace />
  }

  return <Navigate to="/login" replace />
}
