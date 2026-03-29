import { Card, Typography } from 'antd'
import { useTranslation } from 'react-i18next'

export function ConformitePage() {
  const { t } = useTranslation()

  return (
    <Card>
      <Typography.Title level={2}>{t('pages.conformite.title')}</Typography.Title>
      <Typography.Paragraph>{t('pages.conformite.description')}</Typography.Paragraph>
    </Card>
  )
}
