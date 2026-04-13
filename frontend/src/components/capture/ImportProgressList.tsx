import { Alert, List, Progress, Space, Tag, Typography, message } from 'antd'
import { useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { useCaptureStore } from '../../stores/captureStore'

export function ImportProgressList() {
  const { t } = useTranslation()
  const files = useCaptureStore((state) => state.files)
  const isConnected = useCaptureStore((state) => state.isConnected)
  const isReconnecting = useCaptureStore((state) => state.isReconnecting)

  const prevConnectionState = useRef<boolean>(true)

  // Show resume toast when reconnected
  useEffect(() => {
    const wasDisconnected = !prevConnectionState.current
    const hasFiles = files.length > 0

    if (wasDisconnected && isConnected && hasFiles) {
      message.success(t('pages.import.resumedMessage'))
    }

    prevConnectionState.current = isConnected
  }, [files.length, isConnected, t])

  const totalFiles = files.length
  const uploadedCount = files.filter((file) => file.status === 'uploaded').length
  const progressPercent =
    totalFiles === 0
      ? 0
      : Math.round(files.reduce((sum, file) => sum + Math.max(0, Math.min(100, file.progress)), 0) / totalFiles)

  return (
    <Space orientation="vertical" size={16} style={{ width: '100%' }}>
      {/* Global Progress Bar */}
      <div>
        <Typography.Text strong>
          {t('pages.import.globalProgress', { uploaded: uploadedCount, total: totalFiles })}
        </Typography.Text>
        <Progress percent={progressPercent} />
      </div>

      {/* Reconnection Banner */}
      {!isConnected && (
        <Alert
          type="warning"
          showIcon
          title={isReconnecting ? t('pages.import.reconnecting') : t('pages.import.disconnected')}
          description={t('pages.import.disconnectedDescription')}
        />
      )}

      {/* Per-File Progress List */}
      <List
        bordered
        dataSource={files}
        renderItem={(file) => (
          <List.Item>
            <div style={{ width: '100%' }}>
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <Typography.Text>{file.name}</Typography.Text>
                <Tag
                  color={
                    file.status === 'uploaded'
                      ? 'green'
                      : file.status === 'failed'
                        ? 'red'
                        : file.status === 'resuming'
                          ? 'orange'
                          : 'blue'
                  }
                >
                  {file.status}
                </Tag>
              </Space>
              <Progress percent={file.progress} size="small" />
              {file.error && <Typography.Text type="danger">{file.error}</Typography.Text>}
            </div>
          </List.Item>
        )}
      />
    </Space>
  )
}
