import { useEffect, useState } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { Spin } from 'antd'
import { listPermissions } from '../api/admin'

export function AdminPermissionGuard() {
  const [checking, setChecking] = useState(true)
  const [allowed, setAllowed] = useState(false)

  useEffect(() => {
    let mounted = true

    const checkPermission = async () => {
      try {
        await listPermissions()
        if (mounted) {
          setAllowed(true)
        }
      } catch {
        if (mounted) {
          setAllowed(false)
        }
      } finally {
        if (mounted) {
          setChecking(false)
        }
      }
    }

    void checkPermission()

    return () => {
      mounted = false
    }
  }, [])

  if (checking) {
    return <Spin />
  }

  if (!allowed) {
    return <Navigate to="/documents" replace />
  }

  return <Outlet />
}
