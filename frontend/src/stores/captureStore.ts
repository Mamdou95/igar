import { create } from 'zustand'

export type CaptureFileStatus = 'queued' | 'uploading' | 'uploaded' | 'failed' | 'resuming'

export type CaptureFileItem = {
  id: string
  name: string
  progress: number
  status: CaptureFileStatus
  error?: string
}

export type CaptureProgressEvent = {
  event_id?: string
  local_file_id?: string
  upload_id?: string
  filename?: string
  progress?: number
  status?: 'queued' | 'uploading' | 'uploaded' | 'failed' | 'resuming'
  error?: string
}

type CaptureState = {
  overlayVisible: boolean
  activeDrag: boolean
  files: CaptureFileItem[]
  isConnected: boolean
  isReconnecting: boolean
  setOverlayVisible: (visible: boolean) => void
  setActiveDrag: (active: boolean) => void
  queueFiles: (files: Array<{ id: string; name: string }>) => void
  updateFileProgress: (id: string, progress: number) => void
  markUploaded: (id: string) => void
  markFailed: (id: string, error: string) => void
  markResuming: (id: string) => void
  setConnectionStatus: (connected: boolean) => void
  setReconnecting: (reconnecting: boolean) => void
  applyProgressEvent: (event: CaptureProgressEvent) => void
  getTotalFiles: () => number
  getUploadedFiles: () => number
  getProgressPercentage: () => number
  resetBatch: () => void
}

export const useCaptureStore = create<CaptureState>((set, get) => ({
  overlayVisible: false,
  activeDrag: false,
  files: [],
  isConnected: true,
  isReconnecting: false,
  setOverlayVisible: (overlayVisible) => set({ overlayVisible }),
  setActiveDrag: (activeDrag) => set({ activeDrag }),
  setConnectionStatus: (isConnected) => set({ isConnected }),
  setReconnecting: (isReconnecting) => set({ isReconnecting }),
  applyProgressEvent: (event) =>
    set((state) => {
      const explicitId = event.local_file_id ?? event.upload_id
      const status = event.status
      const progressPercent =
        typeof event.progress === 'number'
          ? Math.round(Math.max(0, Math.min(100, event.progress <= 1 ? event.progress * 100 : event.progress)))
          : undefined

      const targetIndex = state.files.findIndex((file) => {
        if (explicitId && file.id === explicitId) {
          return true
        }

        if (event.filename && file.name === event.filename && (file.status === 'queued' || file.status === 'uploading' || file.status === 'resuming')) {
          return true
        }

        return false
      })

      if (targetIndex < 0) {
        return state
      }

      const currentFile = state.files[targetIndex]
      const nextStatus = status ?? (progressPercent === 100 ? 'uploaded' : currentFile.status)

      const updatedFile: CaptureFileItem = {
        ...currentFile,
        status: nextStatus,
        progress:
          typeof progressPercent === 'number'
            ? progressPercent
            : nextStatus === 'uploaded'
              ? 100
              : currentFile.progress,
        error: nextStatus === 'failed' ? (event.error ?? currentFile.error) : undefined,
      }

      const nextFiles = [...state.files]
      nextFiles[targetIndex] = updatedFile

      return {
        files: nextFiles,
      }
    }),
  queueFiles: (files) =>
    set((state) => ({
      files: [
        ...state.files,
        ...files.map((file) => ({
          id: file.id,
          name: file.name,
          progress: 0,
          status: 'queued' as const,
        })),
      ],
    })),
  updateFileProgress: (id, progress) =>
    set((state) => ({
      files: state.files.map((file) =>
        file.id === id
          ? {
              ...file,
              status: progress >= 100 ? 'uploaded' : 'uploading',
              progress,
            }
          : file,
      ),
    })),
  markUploaded: (id) =>
    set((state) => ({
      files: state.files.map((file) =>
        file.id === id ? { ...file, status: 'uploaded', progress: 100 } : file,
      ),
    })),
  markFailed: (id, error) =>
    set((state) => ({
      files: state.files.map((file) =>
        file.id === id ? { ...file, status: 'failed', error } : file,
      ),
    })),
  markResuming: (id) =>
    set((state) => ({
      files: state.files.map((file) =>
        file.id === id ? { ...file, status: 'resuming', error: undefined } : file,
      ),
    })),
  getTotalFiles: () => get().files.length,
  getUploadedFiles: () => get().files.filter((f) => f.status === 'uploaded').length,
  getProgressPercentage: () => {
    const state = get()
    if (state.getTotalFiles() === 0) return 0
    const totalProgress = state.files.reduce((sum, file) => {
      const normalizedProgress = Math.max(0, Math.min(100, file.progress))
      return sum + normalizedProgress
    }, 0)

    return Math.round(totalProgress / state.getTotalFiles())
  },
  resetBatch: () =>
    set({
      files: [],
      overlayVisible: false,
      activeDrag: false,
      isConnected: true,
      isReconnecting: false,
    }),
}))
