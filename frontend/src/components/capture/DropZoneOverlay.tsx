import { InboxOutlined } from '@ant-design/icons'
import { Button, Typography } from 'antd'
import './capture.css'

type DropZoneOverlayProps = {
  visible: boolean
  activeDrag: boolean
  onBrowse: () => void
}

export function DropZoneOverlay({ visible, activeDrag, onBrowse }: DropZoneOverlayProps) {
  if (!visible) {
    return null
  }

  return (
    <div className={`capture-overlay ${activeDrag ? 'capture-overlay-active' : ''}`} data-testid="dropzone-overlay">
      <div className="capture-overlay-card">
        <InboxOutlined className="capture-overlay-icon" />
        <Typography.Title level={3}>Deposez vos documents ici</Typography.Title>
        <Typography.Paragraph>
          Jusqu'a 500 fichiers - PDF, Office, Images, Emails, Audio, Video, ZIP
        </Typography.Paragraph>
        <Button type="primary" onClick={onBrowse} aria-label="Importer des documents">
          Importer
        </Button>
      </div>
    </div>
  )
}
