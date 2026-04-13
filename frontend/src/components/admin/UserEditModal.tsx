import { Form, Input, Modal, Select, Switch } from 'antd'
import { useTranslation } from 'react-i18next'
import type { Group, User, UserCreate, UserUpdate } from '../../api/admin'

interface UserEditModalProps {
  open: boolean
  loading: boolean
  roles: Group[]
  editingUser: User | null
  onCancel: () => void
  onSubmit: (values: UserCreate | UserUpdate) => Promise<void>
}

export function UserEditModal({
  open,
  loading,
  roles,
  editingUser,
  onCancel,
  onSubmit,
}: UserEditModalProps) {
  const { t } = useTranslation()
  const [form] = Form.useForm()

  const isCreate = !editingUser

  return (
    <Modal
      title={isCreate ? t('pages.admin_users.createUser') : t('pages.admin_users.editUser')}
      open={open}
      onOk={() => form.submit()}
      onCancel={onCancel}
      confirmLoading={loading}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          username: editingUser?.username,
          email: editingUser?.email,
          first_name: editingUser?.first_name,
          last_name: editingUser?.last_name,
          groups: editingUser?.groups ?? [],
          is_active: editingUser?.is_active ?? true,
          is_readonly: editingUser?.is_readonly ?? false,
        }}
        onFinish={onSubmit}
      >
        <Form.Item
          label={t('pages.admin_users.username')}
          name="username"
          rules={[
            { required: true, message: t('pages.admin_users.usernameRequired') },
            {
              pattern: /^[a-zA-Z0-9._-]+$/,
              message: t('pages.admin_users.usernameAlphanumeric'),
            },
          ]}
        >
          <Input disabled={!isCreate} aria-label={t('pages.admin_users.username')} />
        </Form.Item>

        <Form.Item
          label={t('pages.admin_users.email')}
          name="email"
          rules={[
            { required: true, message: t('pages.admin_users.emailRequired') },
            { type: 'email', message: t('pages.admin_users.emailInvalid') },
          ]}
        >
          <Input type="email" aria-label={t('pages.admin_users.email')} />
        </Form.Item>

        {isCreate && (
          <Form.Item
            label={t('pages.admin_users.password')}
            name="password"
            rules={[{ required: true, message: t('pages.admin_users.passwordRequired') }]}
          >
            <Input.Password aria-label={t('pages.admin_users.password')} />
          </Form.Item>
        )}

        <Form.Item label={t('pages.admin_users.firstName')} name="first_name">
          <Input aria-label={t('pages.admin_users.firstName')} />
        </Form.Item>

        <Form.Item label={t('pages.admin_users.lastName')} name="last_name">
          <Input aria-label={t('pages.admin_users.lastName')} />
        </Form.Item>

        <Form.Item
          label={t('pages.admin_users.groups')}
          name="groups"
          rules={[
            { required: true, message: t('pages.admin_users.groupsRequired') },
            {
              validator: (_, value: number[]) => {
                if (Array.isArray(value) && value.length > 0) {
                  return Promise.resolve()
                }
                return Promise.reject(new Error(t('pages.admin_users.groupsRequired')))
              },
            },
          ]}
        >
          <Select
            mode="multiple"
            options={roles.map((role) => ({ label: role.name, value: role.id }))}
            aria-label={t('pages.admin_users.groups')}
          />
        </Form.Item>

        <Form.Item label={t('pages.admin_users.active')} name="is_active" valuePropName="checked">
          <Switch aria-label={t('pages.admin_users.active')} />
        </Form.Item>

        <Form.Item
          label={t('pages.admin_users.readOnly')}
          name="is_readonly"
          valuePropName="checked"
        >
          <Switch aria-label={t('pages.admin_users.readOnly')} />
        </Form.Item>
      </Form>
    </Modal>
  )
}