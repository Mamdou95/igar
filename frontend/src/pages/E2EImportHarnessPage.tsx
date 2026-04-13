import { Badge, Card, Space, Typography } from 'antd'
import { ImportPage } from './ImportPage'
import { useCaptureStore } from '../stores/captureStore'

export function E2EImportHarnessPage() {
  const importPendingCount = useCaptureStore(
    (state) => state.files.filter((file) => file.status === 'queued' || file.status === 'uploading').length,
  )

  return (
    <Space direction="vertical" style={{ width: '100%', padding: 24 }} size={16}>
      <Card>
        <Space align="center" size={12}>
          <Typography.Text strong>E2E Import Harness</Typography.Text>
          <Badge count={importPendingCount} data-testid="import-badge">
            <Typography.Text>Import en cours</Typography.Text>
          </Badge>
        </Space>
      </Card>

      <ImportPage />
    </Space>
  )
}
