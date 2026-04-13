import { Alert, Button, Flex, Form, Input } from 'antd'
import { useTranslation } from 'react-i18next'

type TwoFAVerifyFormProps = {
  loading: boolean
  errorMessage: string | null
  submitLabel: string
  onSubmit: (otpCode: string) => Promise<void>
}

type OTPFormValues = {
  otpCode: string
}

export function TwoFAVerifyForm({ loading, errorMessage, submitLabel, onSubmit }: TwoFAVerifyFormProps) {
  const { t } = useTranslation()

  return (
    <Form<OTPFormValues>
      layout="vertical"
      requiredMark={false}
      onFinish={async (values) => {
        await onSubmit(values.otpCode)
      }}
    >
      <Form.Item
        label={t('pages.login.twoFactorCode')}
        name="otpCode"
        rules={[
          { required: true, message: t('pages.login.twoFactorCodeRequired') },
          { pattern: /^\d{6}$/, message: t('pages.login.twoFactorCodeInvalid') },
        ]}
      >
        <Input
          autoComplete="one-time-code"
          inputMode="numeric"
          maxLength={6}
          placeholder={t('pages.login.twoFactorCodePlaceholder')}
        />
      </Form.Item>

      <Flex vertical gap={12}>
        {errorMessage ? <Alert type="error" message={errorMessage} showIcon /> : null}
        <Button htmlType="submit" type="primary" loading={loading}>
          {submitLabel}
        </Button>
      </Flex>
    </Form>
  )
}
