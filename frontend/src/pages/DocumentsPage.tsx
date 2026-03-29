import { Card, Typography } from 'antd'
import { useTranslation } from 'react-i18next'

export function DocumentsPage() {
  const { t } = useTranslation()

  return (
    <Card>
      <Typography.Title level={2}>{t('pages.documents.title')}</Typography.Title>
      <Typography.Paragraph>{t('pages.documents.description')}</Typography.Paragraph>
    </Card>
  )
}
