import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useUploadProgressSocket } from './useUploadProgressSocket'
import { useCaptureStore } from '../stores/captureStore'

class MockWebSocket {
  static instances: MockWebSocket[] = []
  readonly url: string

  onopen: (() => void) | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onclose: (() => void) | null = null
  onerror: (() => void) | null = null

  constructor(url: string) {
    this.url = url
    MockWebSocket.instances.push(this)
  }

  close() {
    this.onclose?.()
  }

  emitOpen() {
    this.onopen?.()
  }

  emitMessage(payload: unknown) {
    this.onmessage?.({ data: JSON.stringify(payload) } as MessageEvent<string>)
  }
}

describe('useUploadProgressSocket', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    MockWebSocket.instances = []
    vi.stubGlobal('WebSocket', MockWebSocket as unknown as typeof WebSocket)
    useCaptureStore.getState().resetBatch()
  })

  it('maps upload.progress messages to the capture store', () => {
    useCaptureStore.getState().queueFiles([{ id: 'file-1', name: 'file1.pdf' }])

    const hook = renderHook(() => useUploadProgressSocket({ enabled: true }))

    expect(MockWebSocket.instances.length).toBe(1)

    act(() => {
      MockWebSocket.instances[0].emitOpen()
      MockWebSocket.instances[0].emitMessage({
        event: 'upload.progress',
        event_id: 'evt-1',
        payload: {
          local_file_id: 'file-1',
          progress: 40,
          status: 'uploading',
        },
      })
    })

    expect(useCaptureStore.getState().files[0].progress).toBe(40)
    expect(useCaptureStore.getState().files[0].status).toBe('uploading')

    hook.unmount()
  })

  it('deduplicates websocket messages using event_id', () => {
    useCaptureStore.getState().queueFiles([{ id: 'file-1', name: 'file1.pdf' }])

    const hook = renderHook(() => useUploadProgressSocket({ enabled: true }))

    act(() => {
      MockWebSocket.instances[0].emitOpen()
      MockWebSocket.instances[0].emitMessage({
        event: 'upload.progress',
        event_id: 'evt-1',
        payload: {
          local_file_id: 'file-1',
          progress: 20,
          status: 'uploading',
        },
      })
      MockWebSocket.instances[0].emitMessage({
        event: 'upload.progress',
        event_id: 'evt-1',
        payload: {
          local_file_id: 'file-1',
          progress: 80,
          status: 'uploading',
        },
      })
    })

    expect(useCaptureStore.getState().files[0].progress).toBe(20)

    hook.unmount()
  })

  it('sets reconnecting state when socket closes unexpectedly', () => {
    const hook = renderHook(() => useUploadProgressSocket({ enabled: true }))

    act(() => {
      MockWebSocket.instances[0].emitOpen()
      MockWebSocket.instances[0].close()
    })

    expect(useCaptureStore.getState().isConnected).toBe(false)
    expect(useCaptureStore.getState().isReconnecting).toBe(true)

    act(() => {
      vi.runOnlyPendingTimers()
    })

    expect(MockWebSocket.instances.length).toBeGreaterThanOrEqual(2)

    hook.unmount()
  })
})
