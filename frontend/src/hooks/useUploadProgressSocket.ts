import { useEffect, useMemo, useRef } from 'react'
import { useCaptureStore, type CaptureProgressEvent } from '../stores/captureStore'

type UploadSocketMessage = {
  event?: string
  event_id?: string
  payload?: CaptureProgressEvent
} & CaptureProgressEvent

type UseUploadProgressSocketOptions = {
  enabled?: boolean
}

const RECONNECT_BASE_DELAY_MS = 1000
const RECONNECT_MAX_DELAY_MS = 10000
const DEDUP_TTL_MS = 30_000

function toWebSocketUrl(): string {
  const configuredUrl = import.meta.env.VITE_UPLOAD_PROGRESS_WS_URL
  if (configuredUrl) {
    return configuredUrl
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/ws/uploads/progress/`
}

export function useUploadProgressSocket(options: UseUploadProgressSocketOptions = {}) {
  const enabled = options.enabled ?? true
  const applyProgressEvent = useCaptureStore((state) => state.applyProgressEvent)
  const setConnectionStatus = useCaptureStore((state) => state.setConnectionStatus)
  const setReconnecting = useCaptureStore((state) => state.setReconnecting)

  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const socketRef = useRef<WebSocket | null>(null)
  const dedupMapRef = useRef<Map<string, number>>(new Map())

  const wsUrl = useMemo(() => toWebSocketUrl(), [])

  useEffect(() => {
    if (!enabled) {
      if (socketRef.current) {
        socketRef.current.close()
        socketRef.current = null
      }
      if (reconnectTimeoutRef.current !== null) {
        window.clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      setConnectionStatus(true)
      setReconnecting(false)
      reconnectAttemptsRef.current = 0
      return
    }

    let unmounted = false

    const cleanupDedupMap = () => {
      const now = Date.now()
      dedupMapRef.current.forEach((timestamp, key) => {
        if (now - timestamp > DEDUP_TTL_MS) {
          dedupMapRef.current.delete(key)
        }
      })
    }

    const rememberEventId = (eventId: string): boolean => {
      cleanupDedupMap()
      if (dedupMapRef.current.has(eventId)) {
        return false
      }
      dedupMapRef.current.set(eventId, Date.now())
      return true
    }

    const scheduleReconnect = () => {
      if (unmounted) {
        return
      }

      setReconnecting(true)
      const attempt = reconnectAttemptsRef.current
      const delay = Math.min(RECONNECT_BASE_DELAY_MS * Math.pow(2, attempt), RECONNECT_MAX_DELAY_MS)

      if (reconnectTimeoutRef.current !== null) {
        window.clearTimeout(reconnectTimeoutRef.current)
      }

      reconnectTimeoutRef.current = window.setTimeout(() => {
        reconnectAttemptsRef.current += 1
        connect()
      }, delay)
    }

    const onSocketMessage = (event: MessageEvent<string>) => {
      let parsed: UploadSocketMessage
      try {
        parsed = JSON.parse(event.data) as UploadSocketMessage
      } catch {
        return
      }

      const payload = parsed.payload ?? parsed
      const eventType = parsed.event

      if (eventType && eventType !== 'upload.progress') {
        return
      }

      const eventId = parsed.event_id ?? payload.event_id
      if (eventId && !rememberEventId(eventId)) {
        return
      }

      applyProgressEvent(payload)
    }

    const connect = () => {
      if (unmounted) {
        return
      }

      if (socketRef.current) {
        socketRef.current.close()
      }

      try {
        const socket = new WebSocket(wsUrl)
        socketRef.current = socket

        socket.onopen = () => {
          if (unmounted) {
            return
          }
          reconnectAttemptsRef.current = 0
          setConnectionStatus(true)
          setReconnecting(false)
        }

        socket.onmessage = onSocketMessage

        socket.onclose = () => {
          if (unmounted) {
            return
          }
          setConnectionStatus(false)
          scheduleReconnect()
        }

        socket.onerror = () => {
          if (unmounted) {
            return
          }
          setConnectionStatus(false)
        }
      } catch {
        setConnectionStatus(false)
        scheduleReconnect()
      }
    }

    connect()

    return () => {
      unmounted = true
      if (reconnectTimeoutRef.current !== null) {
        window.clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (socketRef.current) {
        socketRef.current.close()
        socketRef.current = null
      }
    }
  }, [applyProgressEvent, enabled, setConnectionStatus, setReconnecting, wsUrl])
}
