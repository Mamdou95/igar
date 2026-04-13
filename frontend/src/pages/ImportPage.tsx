import { Card, Space, Typography, message } from 'antd'
import { useMemo, useRef } from 'react'
import type { DragEvent } from 'react'
import { useTranslation } from 'react-i18next'
import { startTusUpload } from '../api/capture'
import { DropZoneOverlay } from '../components/capture/DropZoneOverlay'
import { ImportProgressList } from '../components/capture/ImportProgressList'
import { ImportTriggerButton } from '../components/capture/ImportTriggerButton'
import { useUploadProgressSocket } from '../hooks/useUploadProgressSocket'
import { useCaptureStore } from '../stores/captureStore'

export function ImportPage() {
  const { t } = useTranslation()
  const overlayVisible = useCaptureStore((state) => state.overlayVisible)
  const activeDrag = useCaptureStore((state) => state.activeDrag)
  const files = useCaptureStore((state) => state.files)
  const setOverlayVisible = useCaptureStore((state) => state.setOverlayVisible)
  const setActiveDrag = useCaptureStore((state) => state.setActiveDrag)
  const queueFiles = useCaptureStore((state) => state.queueFiles)
  const updateFileProgress = useCaptureStore((state) => state.updateFileProgress)
  const markUploaded = useCaptureStore((state) => state.markUploaded)
  const markFailed = useCaptureStore((state) => state.markFailed)
  const markResuming = useCaptureStore((state) => state.markResuming)
  const setReconnecting = useCaptureStore((state) => state.setReconnecting)
  const setConnectionStatus = useCaptureStore((state) => state.setConnectionStatus)
  const dragDepth = useRef(0)

  const pendingCount = useMemo(
    () => files.filter((file) => file.status === 'queued' || file.status === 'uploading').length,
    [files],
  )

  useUploadProgressSocket({ enabled: pendingCount > 0 })

  const launchUpload = (selectedFiles: File[]) => {
    const batchItems = selectedFiles.map((file, index) => ({
      id: `${Date.now()}-${index}-${file.name}`,
      file,
    }))

    queueFiles(batchItems.map((item) => ({ id: item.id, name: item.file.name })))

    batchItems.forEach(({ file, id: fileId }) => {
      updateFileProgress(fileId, 0)
      startTusUpload(file, {
        onProgress: (uploadedBytes, totalBytes) => {
          const progress = Math.round((uploadedBytes / totalBytes) * 100)
          updateFileProgress(fileId, progress)
        },
        onResuming: () => {
          setConnectionStatus(false)
          setReconnecting(true)
          markResuming(fileId)
        },
        onResumed: () => {
          setConnectionStatus(true)
          setReconnecting(false)
        },
        onSuccess: () => {
          setConnectionStatus(true)
          setReconnecting(false)
          markUploaded(fileId)
        },
        onError: (error) => {
          setConnectionStatus(false)
          markFailed(fileId, error.message)
          message.error(`${file.name} - ${t('pages.import.uploadFailed')}`)
        },
      }, { localFileId: fileId })
    })

    setOverlayVisible(false)
    setActiveDrag(false)
    dragDepth.current = 0
  }

  const onDragEnter = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    dragDepth.current += 1
    setOverlayVisible(true)
    setActiveDrag(true)
  }

  const onDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setActiveDrag(true)
  }

  const onDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    dragDepth.current -= 1
    if (dragDepth.current <= 0) {
      setActiveDrag(false)
      setOverlayVisible(false)
      dragDepth.current = 0
    }
  }

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const droppedFiles = Array.from(event.dataTransfer.files ?? [])
    if (droppedFiles.length > 0) {
      launchUpload(droppedFiles)
    }
  }

  return (
    <div
      data-testid="import-drop-area"
      onDragEnter={onDragEnter}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <DropZoneOverlay visible={overlayVisible} activeDrag={activeDrag} onBrowse={() => setOverlayVisible(false)} />
      <Card>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Typography.Title level={2}>{t('pages.import.title')}</Typography.Title>
          <Typography.Paragraph>{t('pages.import.description')}</Typography.Paragraph>
          <ImportTriggerButton onFilesSelected={launchUpload} />
          <Typography.Text type="secondary">
            {t('pages.import.inProgress', { count: pendingCount })}
          </Typography.Text>
          <ImportProgressList />
        </Space>
      </Card>
    </div>
  )
}
