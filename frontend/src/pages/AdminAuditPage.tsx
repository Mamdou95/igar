import { useEffect, useState } from 'react'
import {
  Card,
  Table,
  Typography,
  message,
  Tag,
  Button,
  Modal,
  Descriptions,
  Empty,
  Select,
  Row,
  Col,
} from 'antd'
import { useTranslation } from 'react-i18next'
import { EyeOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { listAuditLogs, type AuditLogEntry } from '../api/admin'

export function AdminAuditPage() {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState<AuditLogEntry[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 25, total: 0 })
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [filters, setFilters] = useState({
    action: undefined as string | undefined,
    resource_type: undefined as string | undefined,
  })

  const loadLogs = async (page = 1) => {
    setLoading(true)
    try {
      const data = await listAuditLogs(page, pagination.pageSize, filters.action, filters.resource_type)
      setLogs(data.results)
      setPagination({ ...pagination, current: page, total: data.count })
    } catch {
      message.error(t('pages.admin_audit.loadLogsFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadLogs()
    // Reload when filters change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters])

  const handleViewDetails = (log: AuditLogEntry) => {
    setSelectedLog(log)
    setIsDetailOpen(true)
  }

  const actionOptions = [
    { label: 'User Created', value: 'user.created' },
    { label: 'User Modified', value: 'user.modified' },
    { label: 'User Deactivated', value: 'user.deactivated' },
    { label: 'Password Reset', value: 'user.password_reset' },
    { label: '2FA Reset', value: 'user.2fa_reset' },
    { label: 'Role Created', value: 'role.created' },
    { label: 'Role Modified', value: 'role.modified' },
    { label: 'Document Access Denied', value: 'document.access_denied' },
  ]

  const resourceTypeOptions = [
    { label: 'User', value: 'user' },
    { label: 'Role', value: 'role' },
    { label: 'Document', value: 'document' },
  ]

  const getActionColor = (action: string) => {
    if (action.includes('created')) return 'green'
    if (action.includes('modified')) return 'blue'
    if (action.includes('deleted')) return 'red'
    if (action.includes('access_denied')) return 'orange'
    return 'default'
  }

  const columns = [
    {
      title: t('pages.admin_audit.columns.timestamp'),
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('DD/MM/YYYY HH:mm:ss'),
      width: 180,
    },
    {
      title: t('pages.admin_audit.columns.action'),
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => <Tag color={getActionColor(action)}>{action}</Tag>,
      width: 180,
    },
    {
      title: t('pages.admin_audit.columns.resourceType'),
      dataIndex: 'resource_type',
      key: 'resource_type',
      width: 120,
    },
    {
      title: t('pages.admin_audit.columns.resourceId'),
      dataIndex: 'resource_id',
      key: 'resource_id',
      width: 100,
    },
    {
      title: t('pages.admin_audit.columns.user'),
      key: 'user',
      render: (_: unknown, record: AuditLogEntry) => record.user?.username || '–',
      width: 150,
    },
    {
      title: t('pages.admin_audit.columns.ipAddress'),
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 130,
    },
    {
      title: t('pages.admin_audit.columns.actions'),
      key: 'actions',
      render: (_: unknown, record: AuditLogEntry) => (
        <Button
          type="text"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record)}
        >
          {t('pages.admin_audit.details')}
        </Button>
      ),
      width: 100,
    },
  ]

  return (
    <Card className="admin-surface">
      <div style={{ marginBottom: 24 }}>
        <Typography.Title level={2}>{t('pages.admin_audit.title')}</Typography.Title>
        <Typography.Paragraph>{t('pages.admin_audit.description')}</Typography.Paragraph>
      </div>

      <Card className="admin-surface" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Select
              placeholder={t('pages.admin_audit.filterByAction')}
              allowClear
              style={{ width: '100%' }}
              options={actionOptions}
              value={filters.action}
              onChange={(value) => setFilters({ ...filters, action: value })}
            />
          </Col>
          <Col span={8}>
            <Select
              placeholder={t('pages.admin_audit.filterByResourceType')}
              allowClear
              style={{ width: '100%' }}
              options={resourceTypeOptions}
              value={filters.resource_type}
              onChange={(value) => setFilters({ ...filters, resource_type: value })}
            />
          </Col>
        </Row>
      </Card>

      <Table<AuditLogEntry>
        rowKey="id"
        loading={loading}
        dataSource={logs}
        columns={columns}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showQuickJumper: true,
          onChange: (page) => {
            loadLogs(page)
          },
        }}
        scroll={{ x: 1200 }}
      />

      <Modal
        title={t('pages.admin_audit.entryDetails')}
        open={isDetailOpen}
        onCancel={() => setIsDetailOpen(false)}
        footer={[
          <Button key="close" onClick={() => setIsDetailOpen(false)}>
            {t('pages.common.close')}
          </Button>,
        ]}
        width={700}
      >
        {selectedLog ? (
          <div>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label={t('pages.admin_audit.action')}>
                <Tag color={getActionColor(selectedLog.action)}>{selectedLog.action}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label={t('pages.admin_audit.resourceType')}>
                {selectedLog.resource_type}
              </Descriptions.Item>
              <Descriptions.Item label={t('pages.admin_audit.resourceId')}>
                {selectedLog.resource_id}
              </Descriptions.Item>
              <Descriptions.Item label={t('pages.admin_audit.user')}>
                {selectedLog.user?.username || '–'}
              </Descriptions.Item>
              <Descriptions.Item label={t('pages.admin_audit.ipAddress')}>
                {selectedLog.ip_address}
              </Descriptions.Item>
              <Descriptions.Item label={t('pages.admin_audit.timestamp')}>
                {dayjs(selectedLog.created_at).format('DD/MM/YYYY HH:mm:ss')}
              </Descriptions.Item>
              {selectedLog.reason && (
                <Descriptions.Item label={t('pages.admin_audit.reason')}>
                  {selectedLog.reason}
                </Descriptions.Item>
              )}
            </Descriptions>

            <Typography.Title level={4} style={{ marginTop: 24 }}>
              {t('pages.admin_audit.changes')}
            </Typography.Title>

            <div style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px' }}>
              {Object.keys(selectedLog.old_values || {}).length > 0 ? (
                <div>
                  <Typography.Text strong>{t('pages.admin_audit.oldValues')}:</Typography.Text>
                  <pre style={{ fontSize: '12px', marginTop: '8px' }}>
                    {JSON.stringify(selectedLog.old_values, null, 2)}
                  </pre>
                </div>
              ) : null}

              {Object.keys(selectedLog.new_values || {}).length > 0 ? (
                <div style={{ marginTop: '12px' }}>
                  <Typography.Text strong>{t('pages.admin_audit.newValues')}:</Typography.Text>
                  <pre style={{ fontSize: '12px', marginTop: '8px' }}>
                    {JSON.stringify(selectedLog.new_values, null, 2)}
                  </pre>
                </div>
              ) : null}

              {Object.keys(selectedLog.old_values || {}).length === 0 &&
                Object.keys(selectedLog.new_values || {}).length === 0 && (
                  <Empty description={t('pages.admin_audit.noChanges')} />
                )}
            </div>
          </div>
        ) : null}
      </Modal>
    </Card>
  )
}
