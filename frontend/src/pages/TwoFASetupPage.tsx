import { useEffect, useState } from 'react'
import { Alert, Card, Flex, Skeleton, Typography } from 'antd'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { confirmTwoFactor, setupTwoFactor } from '../api/auth'
import { useAuthStore } from '../stores/authStore'
import { TwoFAVerifyForm } from '../components/TwoFAVerifyForm'

export function TwoFASetupPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const challengeToken = useAuthStore((state) => state.twoFactor.challengeToken)
  const setSession = useAuthStore((state) => state.setSession)
  const [loading, setLoading] = useState(false)
  const [loadingSetup, setLoadingSetup] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [qrCode, setQrCode] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadSetup() {
      if (!challengeToken) {
        navigate('/login', { replace: true })
        return
      }

      setLoadingSetup(true)
      setErrorMessage(null)

      try {
        const data = await setupTwoFactor(challengeToken)
        if (active) {
          setQrCode(data.qr_code)
        }
      } catch (error: unknown) {
        if (active) {
          const fallbackMessage = t('pages.login.errorGeneric')
          if (typeof error === 'object' && error !== null && 'response' in error) {
            const maybeResponse = (error as { response?: { data?: { detail?: string } } }).response
            setErrorMessage(maybeResponse?.data?.detail ?? fallbackMessage)
          } else {
            setErrorMessage(fallbackMessage)
          }
        }
      } finally {
        if (active) {
          setLoadingSetup(false)
        }
      }
    }

    void loadSetup()

    return () => {
      active = false
    }
  }, [challengeToken, navigate, t])

  const handleConfirm = async (otpCode: string) => {
    if (!challengeToken) {
      navigate('/login', { replace: true })
      return
    }

    setLoading(true)
    setErrorMessage(null)

    try {
      const payload = await confirmTwoFactor(challengeToken, otpCode)
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
        <Typography.Title level={3}>{t('pages.login.twoFactorSetupTitle')}</Typography.Title>
        <Typography.Paragraph>{t('pages.login.twoFactorSetupDescription')}</Typography.Paragraph>

        {loadingSetup ? <Skeleton active paragraph={{ rows: 4 }} /> : null}
        {!loadingSetup && qrCode ? (
          <Flex justify="center" style={{ marginBottom: 16 }}>
            <img src={qrCode} alt={t('pages.login.twoFactorQrAlt')} width={220} height={220} />
          </Flex>
        ) : null}

        {errorMessage && !loading ? <Alert style={{ marginBottom: 12 }} type="error" message={errorMessage} showIcon /> : null}

        <TwoFAVerifyForm
          loading={loading}
          errorMessage={loading ? null : errorMessage}
          submitLabel={t('pages.login.twoFactorConfirm')}
          onSubmit={handleConfirm}
        />
      </Card>
    </Flex>
  )
}
