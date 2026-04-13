import { useEffect, useState } from 'react'
import { Button, Card, Modal, Space, Table, Tag, Typography, message } from 'antd'
import { useTranslation } from 'react-i18next'
import { disableTwoFactor, listTwoFactorUsers } from '../api/auth'

type TwoFactorUser = {
  id: number
  username: string
  is_active: boolean
  is_staff: boolean
  has_2fa: boolean
  last_2fa_reset_at: string | null
  two_factor_reset_history: string[]
}

export function AdminPage() {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [users, setUsers] = useState<TwoFactorUser[]>([])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const payload = await listTwoFactorUsers()
      setUsers(payload.results)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadUsers()
  }, [])

  const onReset = (record: TwoFactorUser) => {
    Modal.confirm({
      title: t('pages.admin.twoFactorResetTitle'),
      content: t('pages.admin.twoFactorResetConfirm'),
      okText: t('pages.admin.twoFactorResetAction'),
      cancelText: t('pages.admin.twoFactorResetCancel'),
      onOk: async () => {
        await disableTwoFactor(record.id)
        message.success(t('pages.admin.twoFactorResetSuccess'))
        await loadUsers()
      },
    })
  }

  return (
    <Card>
      <Typography.Title level={2}>{t('pages.admin.title')}</Typography.Title>
      <Typography.Paragraph>{t('pages.admin.description')}</Typography.Paragraph>
      <Table<TwoFactorUser>
        rowKey="id"
        loading={loading}
        dataSource={users}
        pagination={false}
        columns={[
          { title: t('pages.admin.columns.username'), dataIndex: 'username', key: 'username' },
          {
            title: t('pages.admin.columns.twoFactorStatus'),
            key: 'has_2fa',
            render: (_, record) =>
              record.has_2fa ? <Tag color="green">{t('pages.admin.twoFactorEnabled')}</Tag> : <Tag>{t('pages.admin.twoFactorDisabled')}</Tag>,
          },
          {
            title: t('pages.admin.columns.lastReset'),
            key: 'last_2fa_reset_at',
            render: (_, record) => record.last_2fa_reset_at ?? '—',
          },
          {
            title: t('pages.admin.columns.resetHistory'),
            key: 'two_factor_reset_history',
            render: (_, record) => record.two_factor_reset_history.join(' · ') || '—',
          },
          {
            title: t('pages.admin.columns.actions'),
            key: 'actions',
            render: (_, record) => (
              <Space>
                <Button size="small" onClick={() => onReset(record)}>
                  {t('pages.admin.twoFactorResetAction')}
                </Button>
              </Space>
            ),
          },
        ]}
      />
    </Card>
  )
}
