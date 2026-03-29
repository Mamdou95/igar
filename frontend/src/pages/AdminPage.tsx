import { Card, Typography } from 'antd'
import { useTranslation } from 'react-i18next'

export function AdminPage() {
  const { t } = useTranslation()

  return (
    <Card>
      <Typography.Title level={2}>{t('pages.admin.title')}</Typography.Title>
      <Typography.Paragraph>{t('pages.admin.description')}</Typography.Paragraph>
    </Card>
  )
}
