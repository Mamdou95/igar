import { useEffect, useState } from 'react'
import { Flex, Spin } from 'antd'
import { RouterProvider } from 'react-router-dom'
import { apiClient } from './api/client'
import { router } from './router'
import { useAuthStore } from './stores/authStore'

function App() {
  const setSession = useAuthStore((state) => state.setSession)
  const [isBootstrapped, setIsBootstrapped] = useState(false)

  useEffect(() => {
    let active = true

    async function bootstrapSession() {
      try {
        await apiClient.get('/auth/csrf/')
        const response = await apiClient.post('/auth/refresh/')
        const accessToken = response.data?.access as string | undefined
        const user = response.data?.user as { id: number; username: string } | undefined

        if (accessToken && user) {
          setSession(accessToken, user)
        }
      } catch {
        // Anonymous sessions are expected until login succeeds.
      } finally {
        if (active) {
          setIsBootstrapped(true)
        }
      }
    }

    void bootstrapSession()

    return () => {
      active = false
    }
  }, [setSession])

  if (!isBootstrapped) {
    return (
      <Flex align="center" justify="center" style={{ minHeight: '100vh' }}>
        <Spin size="large" />
      </Flex>
    )
  }

  return <RouterProvider router={router} />
}

export default App
