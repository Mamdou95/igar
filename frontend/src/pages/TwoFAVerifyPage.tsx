import { useState } from 'react'
import { Card, Flex, Typography } from 'antd'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { verifyTwoFactor } from '../api/auth'
import { useAuthStore } from '../stores/authStore'
import { TwoFAVerifyForm } from '../components/TwoFAVerifyForm'

export function TwoFAVerifyPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const challengeToken = useAuthStore((state) => state.twoFactor.challengeToken)
  const setSession = useAuthStore((state) => state.setSession)
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const onSubmit = async (otpCode: string) => {
    if (!challengeToken) {
      navigate('/login', { replace: true })
      return
    }

    setLoading(true)
    setErrorMessage(null)

    try {
      const payload = await verifyTwoFactor(challengeToken, otpCode)
      setSession(payload.access, payload.user)
      navigate('/documents', { replace: true })
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
    <Flex vertical justify="center" align="center" style={{ minHeight: '100vh', padding: 24, background: '#f8fafc' }}>
      <Card style={{ width: '100%', maxWidth: 420 }}>
        <Typography.Title level={3}>{t('pages.login.twoFactorVerifyTitle')}</Typography.Title>
        <Typography.Paragraph>{t('pages.login.twoFactorVerifyDescription')}</Typography.Paragraph>
        <TwoFAVerifyForm
          loading={loading}
          errorMessage={errorMessage}
          submitLabel={t('pages.login.twoFactorVerify')}
          onSubmit={onSubmit}
        />
      </Card>
    </Flex>
  )
}
