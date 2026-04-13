import { beforeEach, describe, expect, it, vi } from 'vitest'

const uploadCtorSpy = vi.fn()

vi.mock('tus-js-client', () => {
  const start = vi.fn()
  class Upload {
    start = start
    constructor(_file: File, _config: unknown) {
      uploadCtorSpy(_file, _config)
    }
  }
  return {
    Upload,
    __esModule: true,
  }
})

import { startTusUpload } from './capture'

describe('startTusUpload', () => {
  beforeEach(() => {
    uploadCtorSpy.mockClear()
  })

  it('creates and starts a tus upload with metadata', () => {
    const file = new File(['hello'], 'hello.pdf', { type: 'application/pdf' })
    const callbacks = {
      onProgress: vi.fn(),
      onSuccess: vi.fn(),
      onError: vi.fn(),
    }

    startTusUpload(file, callbacks)

    expect(uploadCtorSpy).toHaveBeenCalledTimes(1)
    const [, config] = uploadCtorSpy.mock.calls[0]
    const typedConfig = config as {
      metadata?: { filename?: string; filetype?: string; local_file_id?: string; storage_key?: string }
      retryDelays?: number[]
    }
    expect(typedConfig.metadata?.filename).toBe('hello.pdf')
    expect(typedConfig.metadata?.filetype).toBe('application/pdf')
    expect(typedConfig.metadata?.storage_key).toContain('capture/')
    expect(typedConfig.retryDelays).toEqual([0, 1000, 3000, 5000, 10000, 20000])
  })

  it('wires explicit resuming and resumed callbacks', () => {
    const file = new File(['hello'], 'hello.pdf', { type: 'application/pdf' })
    const callbacks = {
      onProgress: vi.fn(),
      onSuccess: vi.fn(),
      onError: vi.fn(),
      onResuming: vi.fn(),
      onResumed: vi.fn(),
    }

    startTusUpload(file, callbacks, { localFileId: 'local-1' })

    const [, config] = uploadCtorSpy.mock.calls[0]
    const typedConfig = config as {
      metadata?: { local_file_id?: string }
      onShouldRetry?: (error: Error, retryAttempt: number, options: { retryDelays?: number[] }) => boolean
      onProgress?: (uploadedBytes: number, totalBytes: number) => void
    }

    expect(typedConfig.metadata?.local_file_id).toBe('local-1')

    const shouldRetry = typedConfig.onShouldRetry?.(new Error('network'), 1, { retryDelays: [0, 1000, 3000] })
    expect(shouldRetry).toBe(true)
    expect(callbacks.onResuming).toHaveBeenCalledWith(2, 1000)

    typedConfig.onProgress?.(100, 200)
    expect(callbacks.onResumed).toHaveBeenCalledTimes(1)
    expect(callbacks.onProgress).toHaveBeenCalledWith(100, 200)
  })
})
