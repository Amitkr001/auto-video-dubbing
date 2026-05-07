import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE,
})

export interface UploadResponse {
  file_id: string
  filename: string
  size: number
  path: string
}

export interface DubResponse {
  job_id: string
  status: string
}

export interface JobStatus {
  job_id: string
  status: string
  progress: number
  current_stage: string
  error: string | null
  output_video: string | null
  total_segments: number
  processed_segments: number
}

export interface LanguagesResponse {
  languages: Record<string, string>
}

export async function uploadVideo(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<UploadResponse>('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function startDubbing(
  fileId: string,
  targetLanguage: string,
  sourceLanguage: string = 'auto'
): Promise<DubResponse> {
  const { data } = await api.post<DubResponse>(`/api/dub/${fileId}`, {
    target_language: targetLanguage,
    source_language: sourceLanguage,
  })
  return data
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const { data } = await api.get<JobStatus>(`/api/status/${jobId}`)
  return data
}

export async function getLanguages(): Promise<LanguagesResponse> {
  const { data } = await api.get<LanguagesResponse>('/api/languages')
  return data
}

export function getDownloadUrl(jobId: string): string {
  return `${API_BASE}/api/download/${jobId}`
}

export function getPreviewUrl(jobId: string): string {
  return `${API_BASE}/api/preview/${jobId}`
}

export function getWebSocketUrl(jobId: string): string {
  const wsBase = API_BASE
    ? API_BASE.replace(/^http/, 'ws')
    : `ws://${window.location.host}`
  return `${wsBase}/ws/progress/${jobId}`
}
