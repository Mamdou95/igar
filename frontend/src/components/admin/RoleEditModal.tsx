import { Form, Input, Modal, Tree } from 'antd'
import { useEffect, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import type { Group, Permission } from '../../api/admin'

interface RoleEditModalProps {
  open: boolean
  loading: boolean
  editingRole: Group | null
  permissions: Permission[]
  onCancel: () => void
  onSubmit: (values: { name: string; permissions: number[] }) => Promise<void>
}

export function RoleEditModal({
  open,
  loading,
  editingRole,
  permissions,
  onCancel,
  onSubmit,
}: RoleEditModalProps) {
  const { t } = useTranslation()
  const [form] = Form.useForm()
  const selectedPermissions = Form.useWatch('permissions', form) as number[] | undefined

  useEffect(() => {
    form.setFieldsValue({
      name: editingRole?.name ?? '',
      permissions: editingRole?.permissions ?? [],
    })
  }, [editingRole, form, open])

  const groupedTreeData = useMemo(() => {
    const byApp = permissions.reduce<Record<string, Permission[]>>((acc, permission) => {
      const app = permission.app ?? 'core'
      if (!acc[app]) {
        acc[app] = []
      }
      acc[app].push(permission)
      return acc
    }, {})

    return Object.entries(byApp).map(([app, appPermissions]) => ({
      title: app,
      key: `app-${app}`,
      selectable: false,
      children: appPermissions.map((permission) => ({
        title: permission.name,
        key: permission.id,
      })),
    }))
  }, [permissions])

  return (
    <Modal
      title={editingRole ? t('pages.admin_roles.editRole') : t('pages.admin_roles.createRole')}
      open={open}
      onOk={() => form.submit()}
      onCancel={onCancel}
      confirmLoading={loading}
      width={700}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{ name: editingRole?.name ?? '' }}
        onFinish={(values) => onSubmit({ ...values, permissions: values.permissions ?? [] })}
      >
        <Form.Item
          label={t('pages.admin_roles.name')}
          name="name"
          rules={[{ required: true, message: t('pages.admin_roles.nameRequired') }]}
        >
          <Input aria-label={t('pages.admin_roles.name')} />
        </Form.Item>

        <Form.Item
          label={t('pages.admin_roles.permissions')}
          name="permissions"
          required
          validateStatus={(selectedPermissions?.length ?? 0) === 0 ? 'error' : undefined}
          help={(selectedPermissions?.length ?? 0) === 0 ? t('pages.admin_roles.permissionsRequired') : undefined}
        >
          <Tree
            checkable
            defaultExpandAll
            checkedKeys={selectedPermissions ?? []}
            treeData={groupedTreeData}
            onCheck={(checked) => {
              const checkedKeys = Array.isArray(checked) ? checked : checked.checked
              const numericKeys = checkedKeys.filter(
                (key): key is number => typeof key === 'number',
              )
              form.setFieldsValue({ permissions: numericKeys })
            }}
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}