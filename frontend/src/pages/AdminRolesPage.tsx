import { useEffect, useState } from 'react'
import {
  Button,
  Card,
  Popconfirm,
  Space,
  Table,
  Typography,
  message,
} from 'antd'
import { useTranslation } from 'react-i18next'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import {
  listRoles,
  createRole,
  updateRole,
  deleteRole,
  listPermissions,
  listDocumentAccessGroups,
  type Group,
  type DocumentAccessGroup,
  type Permission,
} from '../api/admin'
import { RoleEditModal } from '../components/admin/RoleEditModal'
import { AccessGroupsModal } from '../components/admin/AccessGroupsModal'

export function AdminRolesPage() {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [roles, setRoles] = useState<Group[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [accessGroups, setAccessGroups] = useState<DocumentAccessGroup[]>([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 25, total: 0 })
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isAccessModalOpen, setIsAccessModalOpen] = useState(false)
  const [editingRole, setEditingRole] = useState<Group | null>(null)

  const loadPermissions = async () => {
    try {
      const data = await listPermissions()
      setPermissions(data)
    } catch {
      message.error(t('pages.admin_roles.loadPermissionsFailed'))
    }
  }

  const loadRoles = async (page = 1) => {
    setLoading(true)
    try {
      const data = await listRoles(page, pagination.pageSize)
      setRoles(data.results)
      setPagination({ ...pagination, current: page, total: data.count })
    } catch {
      message.error(t('pages.admin_roles.loadRolesFailed'))
    } finally {
      setLoading(false)
    }
  }

  const loadAccessGroups = async () => {
    try {
      const data = await listDocumentAccessGroups()
      setAccessGroups(data.results)
    } catch {
      message.error(t('pages.admin_roles.loadAccessGroupsFailed'))
    }
  }

  useEffect(() => {
    void loadPermissions()
    void loadAccessGroups()
    void loadRoles()
    // Load initial data once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleCreateRole = () => {
    setEditingRole(null)
    setIsModalOpen(true)
  }

  const handleEditRole = (role: Group) => {
    setEditingRole(role)
    setIsModalOpen(true)
  }

  const handleEditAccessGroups = (role: Group) => {
    setEditingRole(role)
    setIsAccessModalOpen(true)
  }

  const handleSaveRole = async (values: { name: string; permissions: number[] }) => {
    if (!values.permissions.length) {
      message.error(t('pages.admin_roles.permissionsRequired'))
      return
    }

    setLoading(true)
    try {
      if (editingRole) {
        await updateRole(editingRole.id, {
          name: values.name,
          permissions: values.permissions,
        })
        message.success(t('pages.admin_roles.roleUpdatedSuccess'))
      } else {
        await createRole({
          name: values.name,
          permissions: values.permissions,
        })
        message.success(t('pages.admin_roles.roleCreatedSuccess'))
      }
      setIsModalOpen(false)
      await loadRoles(pagination.current)
    } catch {
      message.error(t('pages.admin_roles.saveRoleFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteRole = async (role: Group) => {
    setLoading(true)
    try {
      await deleteRole(role.id)
      message.success(t('pages.admin_roles.roleDeletedSuccess'))
      await loadRoles(pagination.current)
    } catch {
      message.error(t('pages.admin_roles.deleteRoleFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleSaveAccessGroups = async (allowedDocumentGroups: number[]) => {
    if (!editingRole) {
      return
    }

    setLoading(true)
    try {
      await updateRole(editingRole.id, {
        allowed_document_groups: allowedDocumentGroups,
      })
      message.success(t('pages.admin_roles.accessGroupsUpdatedSuccess'))
      setIsAccessModalOpen(false)
      await loadRoles(pagination.current)
    } catch {
      message.error(t('pages.admin_roles.saveRoleFailed'))
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: t('pages.admin_roles.columns.name'),
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: t('pages.admin_roles.columns.permissionCount'),
      key: 'permissionCount',
      render: (_: unknown, record: Group) => record.permissions.length,
      width: 150,
    },
    {
      title: t('pages.admin_roles.columns.actions'),
      key: 'actions',
      render: (_: unknown, record: Group) => (
        <Space>
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditRole(record)}
          >
            {t('pages.admin_roles.edit')}
          </Button>
          <Button
            type="text"
            size="small"
            onClick={() => handleEditAccessGroups(record)}
          >
            {t('pages.admin_roles.accessGroups')}
          </Button>
          <Popconfirm
            title={t('pages.admin_roles.deleteRole')}
            description={t('pages.admin_roles.deleteRoleConfirm')}
            onConfirm={() => void handleDeleteRole(record)}
            okText={t('pages.common.delete')}
            cancelText={t('pages.common.cancel')}
          >
            <Button type="text" size="small" danger icon={<DeleteOutlined />}>
              {t('pages.admin_roles.deleteRole')}
            </Button>
          </Popconfirm>
        </Space>
      ),
      width: 200,
    },
  ]

  return (
    <main aria-label={t('pages.admin_roles.title')}>
      <Card className="admin-surface">
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <div>
            <Typography.Title level={2}>{t('pages.admin_roles.title')}</Typography.Title>
            <Typography.Paragraph>{t('pages.admin_roles.description')}</Typography.Paragraph>
          </div>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateRole}>
            {t('pages.admin_roles.createRole')}
          </Button>
        </div>

        <Table<Group>
          rowKey="id"
          loading={loading}
          dataSource={roles}
          columns={columns}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize })
              loadRoles(page)
            },
          }}
        />

        <RoleEditModal
          open={isModalOpen}
          loading={loading}
          editingRole={editingRole}
          permissions={permissions}
          onCancel={() => setIsModalOpen(false)}
          onSubmit={handleSaveRole}
        />

        <AccessGroupsModal
          open={isAccessModalOpen}
          loading={loading}
          editingRole={editingRole}
          accessGroups={accessGroups}
          onCancel={() => setIsAccessModalOpen(false)}
          onSubmit={handleSaveAccessGroups}
        />
      </Card>
    </main>
  )
}
