import { describe, beforeEach, it, expect } from 'vitest'
import { useCaptureStore } from './captureStore'

describe('capture store - Task 1.1 extensions', () => {
  beforeEach(() => {
    const { resetBatch } = useCaptureStore.getState()
    resetBatch()
  })

  describe('batch state (total, progress, connection)', () => {
    it('should calculate total files in batch', () => {
        const { queueFiles, getTotalFiles } = useCaptureStore.getState()
        queueFiles([
        { id: '1', name: 'file1.pdf' },
        { id: '2', name: 'file2.pdf' },
      ])
        expect(getTotalFiles()).toBe(2)
    })

    it('should calculate uploaded files count', () => {
        const { queueFiles, markUploaded, getUploadedFiles } = useCaptureStore.getState()
        queueFiles([
        { id: '1', name: 'file1.pdf' },
        { id: '2', name: 'file2.pdf' },
      ])
        markUploaded('1')
        expect(getUploadedFiles()).toBe(1)
    })

    it('should calculate progress percentage', () => {
        const { queueFiles, markUploaded, getProgressPercentage } = useCaptureStore.getState()
        queueFiles([
        { id: '1', name: 'file1.pdf' },
        { id: '2', name: 'file2.pdf' },
      ])
        markUploaded('1')
        expect(getProgressPercentage()).toBe(50)
    })

    it('should include partial file progress in global percentage', () => {
      const { queueFiles, updateFileProgress, getProgressPercentage } = useCaptureStore.getState()
      queueFiles([
        { id: '1', name: 'file1.pdf' },
        { id: '2', name: 'file2.pdf' },
      ])

      updateFileProgress('1', 50)

      expect(getProgressPercentage()).toBe(25)
    })

    it('should track connection status', () => {
        const { setConnectionStatus } = useCaptureStore.getState()
        expect(useCaptureStore.getState().isConnected).toBe(true)
        setConnectionStatus(false)
        expect(useCaptureStore.getState().isConnected).toBe(false)
        useCaptureStore.getState().setConnectionStatus(true)
        expect(useCaptureStore.getState().isConnected).toBe(true)
    })

    it('should track reconnecting status independently', () => {
        const { setReconnecting } = useCaptureStore.getState()
        expect(useCaptureStore.getState().isReconnecting).toBe(false)
        setReconnecting(true)
        expect(useCaptureStore.getState().isReconnecting).toBe(true)
        useCaptureStore.getState().setReconnecting(false)
        expect(useCaptureStore.getState().isReconnecting).toBe(false)
    })
  })

  describe('file status extensions for reprise (Task 1.2)', () => {
    it('should support resuming status', () => {
        const { queueFiles, markResuming } = useCaptureStore.getState()
        queueFiles([{ id: '1', name: 'file1.pdf' }])
        markResuming('1')
        const file = useCaptureStore.getState().files[0]
      expect(file.status).toMatch(/resuming|uploading/) // resuming or uploading after resume
    })

    it('should not lose progress when marking resumed', () => {
        const { queueFiles, updateFileProgress, markResuming } = useCaptureStore.getState()
        queueFiles([{ id: '1', name: 'file1.pdf' }])
        updateFileProgress('1', 50)
        markResuming('1')
        const file = useCaptureStore.getState().files[0]
      expect(file.progress).toBe(50) // progress preserved
    })
  })

  describe('session persistence (Task 1.3)', () => {
    it('should persist batch across component remount', () => {
      const { queueFiles, updateFileProgress } = useCaptureStore.getState()
      queueFiles([{ id: '1', name: 'file1.pdf' }])
      updateFileProgress('1', 60)

      // Simulate component remount
      const store2 = useCaptureStore.getState()
      expect(store2.files).toHaveLength(1)
      expect(store2.files[0].progress).toBe(60)
    })

    it('should reset batch only when explicitly called', () => {
        const { queueFiles, setConnectionStatus } = useCaptureStore.getState()
        queueFiles([{ id: '1', name: 'file1.pdf' }])
        setConnectionStatus(false)
      
      // Navigation should NOT reset
        expect(useCaptureStore.getState().files).toHaveLength(1)
        expect(useCaptureStore.getState().isConnected).toBe(false)
      
      // Only explicit reset should clear
        useCaptureStore.getState().resetBatch()
        expect(useCaptureStore.getState().files).toHaveLength(0)
        expect(useCaptureStore.getState().isConnected).toBe(true) // Also reset on batch reset
    })
  })

  describe('websocket progress event mapping (Task 3.2)', () => {
    it('should map a progress event to a file by local_file_id', () => {
      const { queueFiles, applyProgressEvent } = useCaptureStore.getState()
      queueFiles([{ id: 'local-1', name: 'file1.pdf' }])

      applyProgressEvent({
        local_file_id: 'local-1',
        progress: 0.42,
        status: 'uploading',
      })

      const file = useCaptureStore.getState().files[0]
      expect(file.progress).toBe(42)
      expect(file.status).toBe('uploading')
    })

    it('should map a completed event by filename when id is absent', () => {
      const { queueFiles, applyProgressEvent } = useCaptureStore.getState()
      queueFiles([{ id: 'local-1', name: 'file1.pdf' }])

      applyProgressEvent({
        filename: 'file1.pdf',
        progress: 1,
        status: 'uploaded',
      })

      const file = useCaptureStore.getState().files[0]
      expect(file.progress).toBe(100)
      expect(file.status).toBe('uploaded')
    })
  })
})
