import { Form, Modal, Select } from 'antd'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import type { DocumentAccessGroup, Group } from '../../api/admin'

interface AccessGroupsModalProps {
  open: boolean
  loading: boolean
  editingRole: Group | null
  accessGroups: DocumentAccessGroup[]
  onCancel: () => void
  onSubmit: (groupIds: number[]) => Promise<void>
}

export function AccessGroupsModal({
  open,
  loading,
  editingRole,
  accessGroups,
  onCancel,
  onSubmit,
}: AccessGroupsModalProps) {
  const { t } = useTranslation()
  const [form] = Form.useForm()

  useEffect(() => {
    form.setFieldsValue({
      allowed_document_groups: editingRole?.allowed_document_groups ?? [],
    })
  }, [editingRole, form, open])

  return (
    <Modal
      title={t('pages.admin_roles.accessGroupsTitle')}
      open={open}
      onOk={() => form.submit()}
      onCancel={onCancel}
      confirmLoading={loading}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={(values: { allowed_document_groups: number[] }) =>
          onSubmit(values.allowed_document_groups ?? [])
        }
      >
        <Form.Item label={t('pages.admin_roles.accessGroups')} name="allowed_document_groups">
          <Select
            mode="multiple"
            allowClear
            options={accessGroups.map((group) => ({
              label: group.name,
              value: group.id,
            }))}
            aria-label={t('pages.admin_roles.accessGroups')}
            placeholder={t('pages.admin_roles.accessGroupsPlaceholder')}
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}
