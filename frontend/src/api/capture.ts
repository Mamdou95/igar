import { Upload } from 'tus-js-client'

const UPLOADS_URL = import.meta.env.VITE_UPLOADS_URL ?? 'http://localhost/uploads/'
const RESUME_RETRY_DELAYS_MS = [0, 1000, 3000, 5000, 10000, 20000]

function buildStorageKey(file: File): string {
  const sanitizedName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_')
  return `capture/${Date.now()}-${sanitizedName}`
}

export type CaptureUploadCallbacks = {
  onProgress: (uploadedBytes: number, totalBytes: number) => void
  onSuccess: () => void
  onError: (error: Error) => void
  onResuming?: (attempt: number, delayMs: number) => void
  onResumed?: () => void
}

export function startTusUpload(
  file: File,
  callbacks: CaptureUploadCallbacks,
  options: { localFileId?: string } = {},
) {
  let waitingForResume = false
  let lastUploadedBytes = 0

  const upload = new Upload(file, {
    endpoint: UPLOADS_URL,
    retryDelays: RESUME_RETRY_DELAYS_MS,
    metadata: {
      filename: file.name,
      filetype: file.type || 'application/octet-stream',
      ...(options.localFileId ? { local_file_id: options.localFileId } : {}),
      storage_key: buildStorageKey(file),
    },
    onError: (error) => callbacks.onError(error),
    onShouldRetry: (_error, retryAttempt, uploadOptions) => {
      const delayMs = uploadOptions.retryDelays?.[retryAttempt] ?? RESUME_RETRY_DELAYS_MS.at(-1) ?? 0
      waitingForResume = true
      callbacks.onResuming?.(retryAttempt + 1, delayMs)
      return true
    },
    onProgress: (uploadedBytes, totalBytes) => {
      if (waitingForResume && uploadedBytes > lastUploadedBytes) {
        waitingForResume = false
        callbacks.onResumed?.()
      }
      lastUploadedBytes = uploadedBytes
      callbacks.onProgress(uploadedBytes, totalBytes)
    },
    onSuccess: () => callbacks.onSuccess(),
  })

  upload.start()
  return upload
}
