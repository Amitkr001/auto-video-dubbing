import { useState, useEffect, useRef, useCallback } from 'react'
import { JobStatus, getWebSocketUrl } from '../api/client'

interface UseWebSocketReturn {
  status: JobStatus | null
  connected: boolean
  error: string | null
}

export function useWebSocket(jobId: string | undefined): UseWebSocketReturn {
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>()

  const connect = useCallback(() => {
    if (!jobId) return

    const ws = new WebSocket(getWebSocketUrl(jobId))
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      setError(null)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as JobStatus
        setStatus(data)
        if (data.status === 'completed' || data.status === 'failed') {
          ws.close()
        }
      } catch {
        console.error('Failed to parse WebSocket message')
      }
    }

    ws.onerror = () => {
      setError('WebSocket connection error')
      setConnected(false)
    }

    ws.onclose = () => {
      setConnected(false)
      if (status?.status !== 'completed' && status?.status !== 'failed') {
        reconnectTimer.current = setTimeout(connect, 3000)
      }
    }
  }, [jobId, status?.status])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current)
      }
    }
  }, [jobId])

  return { status, connected, error }
}
