import { Card, Typography } from 'antd'
import { useTranslation } from 'react-i18next'

export function ImportPage() {
  const { t } = useTranslation()

  return (
    <Card>
      <Typography.Title level={2}>{t('pages.import.title')}</Typography.Title>
      <Typography.Paragraph>{t('pages.import.description')}</Typography.Paragraph>
    </Card>
  )
}
