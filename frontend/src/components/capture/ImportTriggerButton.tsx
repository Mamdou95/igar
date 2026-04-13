import { UploadOutlined } from '@ant-design/icons'
import { Button } from 'antd'
import { useRef } from 'react'

type ImportTriggerButtonProps = {
  onFilesSelected: (files: File[]) => void
}

export function ImportTriggerButton({ onFilesSelected }: ImportTriggerButtonProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)

  const openPicker = () => {
    inputRef.current?.click()
  }

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        multiple
        hidden
        aria-label="Selection des fichiers a importer"
        onChange={(event) => {
          const files = Array.from(event.target.files ?? [])
          if (files.length > 0) {
            onFilesSelected(files)
          }
        }}
        // @ts-expect-error webkitdirectory is browser-specific and not yet in TS DOM typings.
        webkitdirectory=""
        directory=""
      />
      <Button icon={<UploadOutlined />} type="primary" onClick={openPicker}>
        Importer
      </Button>
    </>
  )
}
