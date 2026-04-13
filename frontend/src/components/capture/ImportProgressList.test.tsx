import { describe, it, expect, beforeEach, vi } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import { message } from 'antd'
import { ImportProgressList } from './ImportProgressList'
import { useCaptureStore } from '../../stores/captureStore'

// Mock React i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, params?: { uploaded?: number; total?: number }) => {
      if (key === 'pages.import.globalProgress') {
        return `${params?.uploaded ?? 0}/${params?.total ?? 0} uploades`
      }
      if (key === 'pages.import.reconnecting') return 'Reconnexion en cours...'
      if (key === 'pages.import.disconnected') return 'Connexion interrompue'
      if (key === 'pages.import.disconnectedDescription') return 'Les uploads reprendront automatiquement.'
      if (key === 'pages.import.resumedMessage') return 'Upload repris - aucun fichier perdu'
      return key
    },
  }),
}))

describe('ImportProgressList - Task 2', () => {
  beforeEach(() => {
    useCaptureStore.getState().resetBatch()
    vi.restoreAllMocks()
  })

  describe('2.1: Barre globale + barres par fichier', () => {
    it('should render global progress bar with file count', () => {
      const { queueFiles, updateFileProgress } = useCaptureStore.getState()
      queueFiles([
        { id: '1', name: 'file1.pdf' },
        { id: '2', name: 'file2.pdf' },
        { id: '3', name: 'file3.pdf' },
      ])
      updateFileProgress('1', 100)
      updateFileProgress('2', 50)

      render(<ImportProgressList />)

      expect(screen.getByText('1/3 uploades')).toBeInTheDocument()
    })

    it('should render progress bar for each file', () => {
      const { queueFiles } = useCaptureStore.getState()
      queueFiles([
        { id: '1', name: 'file1.pdf' },
        { id: '2', name: 'file2.pdf' },
      ])

      render(<ImportProgressList />)

      expect(screen.getByText(/file1.pdf/i)).toBeInTheDocument()
      expect(screen.getByText(/file2.pdf/i)).toBeInTheDocument()
    })

    it('should update progress bars in real-time', async () => {
      const { queueFiles, updateFileProgress } = useCaptureStore.getState()
      queueFiles([{ id: '1', name: 'file1.pdf' }])

      const { rerender } = render(<ImportProgressList />)

      act(() => {
        updateFileProgress('1', 50)
      })
      rerender(<ImportProgressList />)

      expect(screen.getAllByText('50%').length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('2.2: Banner reconnexion persistante', () => {
    it('should display disconnected banner when not connected', () => {
      useCaptureStore.getState().queueFiles([{ id: '1', name: 'file1.pdf' }])
      useCaptureStore.getState().setConnectionStatus(false)

      render(<ImportProgressList />)

      expect(screen.getByText('Connexion interrompue')).toBeInTheDocument()
    })

    it('should not display reconnection banner when connected', () => {
      useCaptureStore.getState().queueFiles([{ id: '1', name: 'file1.pdf' }])

      render(<ImportProgressList />)

      expect(screen.queryByText('Connexion interrompue')).not.toBeInTheDocument()
    })

    it('should show "reconnecting" state when reconnecting', () => {
      useCaptureStore.getState().queueFiles([{ id: '1', name: 'file1.pdf' }])
      useCaptureStore.getState().setConnectionStatus(false)
      useCaptureStore.getState().setReconnecting(true)

      render(<ImportProgressList />)

      expect(screen.getByText('Reconnexion en cours...')).toBeInTheDocument()
    })
  })

  describe('2.3: Toast reprise a la reconnexion', () => {
    it('should trigger resume toast when reconnected', () => {
      const successSpy = vi.spyOn(message, 'success').mockImplementation(() => undefined)
      const { queueFiles, setConnectionStatus, setReconnecting } = useCaptureStore.getState()
      queueFiles([{ id: '1', name: 'file1.pdf' }])

      act(() => {
        setConnectionStatus(false)
        setReconnecting(true)
      })

      const { rerender } = render(<ImportProgressList />)

      act(() => {
        setReconnecting(false)
        setConnectionStatus(true)
      })
      rerender(<ImportProgressList />)

      expect(successSpy).toHaveBeenCalledWith('Upload repris - aucun fichier perdu')
    })

    it('should not show resume toast on initial render', () => {
      const successSpy = vi.spyOn(message, 'success').mockImplementation(() => undefined)
      useCaptureStore.getState().queueFiles([{ id: '1', name: 'file1.pdf' }])

      render(<ImportProgressList />)

      expect(successSpy).not.toHaveBeenCalled()
    })
  })

  describe('Non-blocking navigation support', () => {
    it('should persist state when component unmounts and remounts', () => {
      const { queueFiles, updateFileProgress } = useCaptureStore.getState()
      queueFiles([{ id: '1', name: 'file1.pdf' }])
      updateFileProgress('1', 60)

      const mounted = render(<ImportProgressList />)
      expect(screen.getByText(/file1.pdf/i)).toBeInTheDocument()

      mounted.unmount()

      render(<ImportProgressList />)
      expect(screen.getByText(/file1.pdf/i)).toBeInTheDocument()
    })

    it('should keep progress after route-like remount', () => {
      const { queueFiles, updateFileProgress } = useCaptureStore.getState()
      queueFiles([{ id: '1', name: 'file1.pdf' }])
      updateFileProgress('1', 60)

      const mounted = render(<ImportProgressList />)
      expect(screen.getAllByText('60%').length).toBeGreaterThanOrEqual(1)

      mounted.unmount()

      render(<ImportProgressList />)
      expect(screen.getAllByText('60%').length).toBeGreaterThanOrEqual(1)
    })
  })
})
