import { useEffect, useState } from 'react'
import {
  Button,
  Card,
  Input,
  Space,
  Table,
  Tag,
  Typography,
  message,
  Popconfirm,
  Select,
} from 'antd'
import { useTranslation } from 'react-i18next'
import {
  DownloadOutlined,
  EditOutlined,
  LockOutlined,
  ReloadOutlined,
  UserAddOutlined,
} from '@ant-design/icons'
import {
  listUsers,
  getUser,
  createUser,
  updateUser,
  deactivateUser,
  resetUserPassword,
  resetUserTwoFactor,
  listRoles,
  type User,
  type UserCreate,
  type UserUpdate,
  type Group,
} from '../api/admin'
import { UserEditModal } from '../components/admin/UserEditModal'

export function AdminUsersPage() {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Group[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 25, total: 0 })
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [searchText, setSearchText] = useState('')
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>(undefined)
  const [groupFilter, setGroupFilter] = useState<number | undefined>(undefined)

  const loadRoles = async () => {
    try {
      const data = await listRoles()
      setRoles(data.results)
    } catch {
      message.error(t('pages.admin_users.loadRolesFailed'))
    }
  }

  const loadUsers = async (page = 1, pageSize = pagination.pageSize) => {
    setLoading(true)
    try {
      const data = await listUsers({
        page,
        limit: pageSize,
        search: searchText || undefined,
        groupId: groupFilter,
        isActive: statusFilter,
      })
      setUsers(data.results)
      setPagination({ ...pagination, current: page, pageSize, total: data.count })
    } catch {
      message.error(t('pages.admin_users.loadUsersFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadRoles()
    void loadUsers()
    // Load initial data once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    void loadUsers(1)
    // Reload table when filters change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, groupFilter])

  const handleCreateUser = () => {
    setEditingUser(null)
    setIsModalOpen(true)
  }

  const handleEditUser = async (user: User) => {
    try {
      const fullUser = await getUser(user.id)
      setEditingUser(fullUser)
      setIsModalOpen(true)
    } catch {
      message.error(t('pages.admin_users.loadUserFailed'))
    }
  }

  const handleSaveUser = async (values: UserCreate | UserUpdate) => {
    setLoading(true)
    try {
      if (editingUser) {
        await updateUser(editingUser.id, values as UserUpdate)
        message.success(t('pages.admin_users.userUpdatedSuccess'))
      } else {
        if (!('password' in values)) {
          message.error(t('pages.admin_users.passwordRequired'))
          setLoading(false)
          return
        }
        await createUser(values as UserCreate)
        message.success(t('pages.admin_users.userCreatedSuccess'))
      }
      setIsModalOpen(false)
      await loadUsers(pagination.current)
    } catch {
      message.error(t('pages.admin_users.saveUserFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleDeactivateUser = async (user: User) => {
    setLoading(true)
    try {
      await deactivateUser(user.id)
      message.success(t('pages.admin_users.userDeactivatedSuccess'))
      await loadUsers(pagination.current)
    } catch {
      message.error(t('pages.admin_users.deactivateUserFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (user: User) => {
    setLoading(true)
    try {
      await resetUserPassword(user.id)
      message.success(t('pages.admin_users.passwordResetSuccess'))
      await loadUsers(pagination.current)
    } catch {
      message.error(t('pages.admin_users.passwordResetFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleReset2FA = async (user: User) => {
    setLoading(true)
    try {
      await resetUserTwoFactor(user.id)
      message.success(t('pages.admin_users.twoFactorResetSuccess'))
      await loadUsers(pagination.current)
    } catch {
      message.error(t('pages.admin_users.twoFactorResetFailed'))
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: t('pages.admin_users.columns.username'),
      dataIndex: 'username',
      key: 'username',
      width: 150,
    },
    {
      title: t('pages.admin_users.columns.email'),
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: t('pages.admin_users.columns.name'),
      key: 'name',
      render: (_: unknown, record: User) => `${record.first_name} ${record.last_name}`.trim() || '–',
      width: 200,
    },
    {
      title: t('pages.admin_users.columns.roles'),
      key: 'groups',
      render: (_: unknown, record: User) => (
        <span>
          {record.groups.length > 0
            ? record.groups.map((groupId: number) => {
                const group = roles.find((r) => r.id === groupId)
                return group ? <Tag key={groupId}>{group.name}</Tag> : null
              })
            : '–'}
        </span>
      ),
      width: 200,
    },
    {
      title: t('pages.admin_users.columns.status'),
      key: 'is_active',
      render: (_: unknown, record: User) =>
        record.is_active ? (
          <Tag color="green">{t('pages.admin_users.active')}</Tag>
        ) : (
          <Tag color="red">{t('pages.admin_users.inactive')}</Tag>
        ),
      width: 100,
    },
    {
      title: t('pages.admin_users.columns.actions'),
      key: 'actions',
      render: (_: unknown, record: User) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            disabled={record.is_readonly}
            onClick={() => handleEditUser(record)}
          >
            {t('pages.admin_users.edit')}
          </Button>
          {record.is_active && !record.is_readonly && (
            <Popconfirm
              title={t('pages.admin_users.deactivateTitle')}
              description={t('pages.admin_users.deactivateConfirm')}
              onConfirm={() => handleDeactivateUser(record)}
              okText={t('pages.admin_users.deactivate')}
              cancelText={t('pages.common.cancel')}
            >
              <Button type="text" size="small" danger>
                {t('pages.admin_users.deactivate')}
              </Button>
            </Popconfirm>
          )}
          <Popconfirm
            title={t('pages.admin_users.resetPasswordTitle')}
            description={t('pages.admin_users.resetPasswordConfirm')}
            onConfirm={() => handleResetPassword(record)}
            okText={t('pages.admin_users.reset')}
            cancelText={t('pages.common.cancel')}
          >
            <Button type="text" size="small" icon={<LockOutlined />}>
              {t('pages.admin_users.resetPassword')}
            </Button>
          </Popconfirm>
          <Button
            type="text"
            size="small"
            onClick={() => handleReset2FA(record)}
          >
            {t('pages.admin_users.reset2FA')}
          </Button>
        </Space>
      ),
      width: 350,
    },
  ]

  return (
    <main aria-label={t('pages.admin_users.title')}>
      <Card className="admin-surface">
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <div>
            <Typography.Title level={2}>{t('pages.admin_users.title')}</Typography.Title>
            <Typography.Paragraph>{t('pages.admin_users.description')}</Typography.Paragraph>
          </div>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={() => void loadUsers(pagination.current)}>
              {t('pages.admin_users.refresh')}
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => {
                const headers = ['username', 'email', 'first_name', 'last_name', 'is_active']
                const rows = users.map((user) =>
                  [
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.is_active ? 'true' : 'false',
                  ].join(','),
                )
                const csvContent = [headers.join(','), ...rows].join('\n')
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
                const url = URL.createObjectURL(blob)
                const link = document.createElement('a')
                link.href = url
                link.download = 'admin-users.csv'
                link.click()
                URL.revokeObjectURL(url)
              }}
            >
              {t('pages.admin_users.export')}
            </Button>
            <Button type="primary" icon={<UserAddOutlined />} onClick={handleCreateUser}>
              {t('pages.admin_users.createUser')}
            </Button>
          </Space>
        </div>

        <div style={{ marginBottom: 16, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <Input.Search
            aria-label={t('pages.admin_users.searchPlaceholder')}
            placeholder={t('pages.admin_users.searchPlaceholder')}
            onSearch={(value) => {
              setSearchText(value)
              void loadUsers(1)
            }}
            allowClear
            style={{ width: 300 }}
          />
          <Select
            aria-label={t('pages.admin_users.filterByStatus')}
            allowClear
            placeholder={t('pages.admin_users.filterByStatus')}
            style={{ width: 220 }}
            value={statusFilter}
            onChange={(value) => setStatusFilter(value)}
            options={[
              { label: t('pages.admin_users.active'), value: true },
              { label: t('pages.admin_users.inactive'), value: false },
            ]}
          />
          <Select
            aria-label={t('pages.admin_users.filterByGroup')}
            allowClear
            placeholder={t('pages.admin_users.filterByGroup')}
            style={{ width: 260 }}
            value={groupFilter}
            onChange={(value) => setGroupFilter(value)}
            options={roles.map((role) => ({ label: role.name, value: role.id }))}
          />
        </div>

        <Table<User>
          rowKey="id"
          loading={loading}
          dataSource={users}
          columns={columns}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            onChange: (page, pageSize) => {
              void loadUsers(page, pageSize)
            },
          }}
          scroll={{ x: 1200 }}
        />

        <UserEditModal
          open={isModalOpen}
          loading={loading}
          roles={roles}
          editingUser={editingUser}
          onCancel={() => setIsModalOpen(false)}
          onSubmit={handleSaveUser}
        />
      </Card>
    </main>
  )
}
