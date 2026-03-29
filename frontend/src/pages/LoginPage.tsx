import { useState } from 'react'
import { Alert, Button, Card, Flex, Form, Input, Typography } from 'antd'
import { useTranslation } from 'react-i18next'
import { useLocation, useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client'
import { useAuthStore } from '../stores/authStore'

type LoginFormValues = {
  username: string
  password: string
}

export function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const setSession = useAuthStore((state) => state.setSession)
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const onFinish = async (values: LoginFormValues) => {
    setLoading(true)
    setErrorMessage(null)

    try {
      await apiClient.get('/auth/csrf/')
      const response = await apiClient.post('/auth/login/', values)

      const accessToken = response.data?.access as string
      const user = response.data?.user as { id: number; username: string }

      setSession(accessToken, user)

      const redirectPath = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname
      navigate(redirectPath ?? '/documents', { replace: true })
    } catch (error: unknown) {
      const fallbackMessage = t('pages.login.errorGeneric')

      if (typeof error === 'object' && error !== null && 'response' in error) {
        const maybeResponse = (error as { response?: { data?: { detail?: string } } }).response
        setErrorMessage(maybeResponse?.data?.detail ?? fallbackMessage)
      } else {
        setErrorMessage(fallbackMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Flex
      vertical
      justify="center"
      align="center"
      style={{ minHeight: '100vh', padding: 24, background: '#f8fafc' }}
    >
      <Card style={{ width: '100%', maxWidth: 380 }}>
        <Typography.Title level={3}>{t('pages.login.title')}</Typography.Title>
        <Form<LoginFormValues> layout="vertical" onFinish={onFinish} requiredMark={false}>
          <Form.Item
            label={t('pages.login.username')}
            name="username"
            rules={[{ required: true, message: t('pages.login.usernameRequired') }]}
          >
            <Input autoComplete="username" placeholder={t('pages.login.username')} />
          </Form.Item>

          <Form.Item
            label={t('pages.login.password')}
            name="password"
            rules={[{ required: true, message: t('pages.login.passwordRequired') }]}
          >
            <Input.Password autoComplete="current-password" placeholder={t('pages.login.password')} />
          </Form.Item>

          <Flex vertical gap={12}>
            {errorMessage ? <Alert type="error" message={errorMessage} showIcon /> : null}
            <Button htmlType="submit" type="primary" loading={loading}>
              {t('pages.login.submit')}
            </Button>
          </Flex>
        </Form>
      </Card>
    </Flex>
  )
}
