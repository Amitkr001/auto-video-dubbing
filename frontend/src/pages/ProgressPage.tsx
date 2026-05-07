import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  FileAudio,
  SplitSquareVertical,
  Users,
  MessageSquare,
  Languages,
  Mic,
  MonitorPlay,
  Merge,
  CheckCircle2,
  Loader2,
  XCircle,
  AlertCircle,
} from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'
import { getJobStatus, JobStatus } from '../api/client'

const PIPELINE_STAGES = [
  { key: 'extracting', label: 'Extracting Audio', icon: FileAudio },
  { key: 'separating', label: 'Separating Vocals', icon: SplitSquareVertical },
  { key: 'diarizing', label: 'Detecting Speakers', icon: Users },
  { key: 'transcribing', label: 'Transcribing', icon: MessageSquare },
  { key: 'translating', label: 'Translating', icon: Languages },
  { key: 'generating_voice', label: 'Generating Voice', icon: Mic },
  { key: 'lip_syncing', label: 'Lip Sync', icon: MonitorPlay },
  { key: 'merging', label: 'Merging', icon: Merge },
]

function getStageIndex(status: string): number {
  const idx = PIPELINE_STAGES.findIndex((s) => s.key === status)
  if (status === 'completed') return PIPELINE_STAGES.length
  return idx >= 0 ? idx : -1
}

function ProgressPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const { status: wsStatus } = useWebSocket(jobId)
  const [pollStatus, setPollStatus] = useState<JobStatus | null>(null)

  const status = wsStatus || pollStatus

  useEffect(() => {
    if (!jobId) return
    const interval = setInterval(async () => {
      try {
        const data = await getJobStatus(jobId)
        setPollStatus(data)
        if (data.status === 'completed') {
          clearInterval(interval)
        }
      } catch {
        // WebSocket is primary, polling is fallback
      }
    }, 3000)
    return () => clearInterval(interval)
  }, [jobId])

  useEffect(() => {
    if (status?.status === 'completed') {
      const timer = setTimeout(() => navigate(`/preview/${jobId}`), 2000)
      return () => clearTimeout(timer)
    }
  }, [status?.status, jobId, navigate])

  const currentStageIndex = status ? getStageIndex(status.status) : -1
  const progress = status ? Math.round(status.progress * 100) : 0

  return (
    <div className="pt-24 pb-16 px-4 min-h-screen">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-3">
            <span className="gradient-text">Dubbing in Progress</span>
          </h1>
          <p className="text-gray-400">
            {status?.status === 'failed'
              ? 'An error occurred during processing.'
              : status?.status === 'completed'
              ? 'Your video has been dubbed successfully!'
              : 'Your video is being processed through the AI pipeline.'}
          </p>
        </div>

        {/* Error Display */}
        {status?.status === 'failed' && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-300">Pipeline Error</p>
              <p className="text-red-400/80 text-sm mt-1">{status.error}</p>
            </div>
          </div>
        )}

        {/* Overall Progress */}
        <div className="glass-card p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-300">
              {status?.current_stage || 'Initializing...'}
            </span>
            <span className="text-sm font-bold gradient-text">{progress}%</span>
          </div>
          <div className="w-full h-3 rounded-full bg-white/10 overflow-hidden">
            <div
              className="h-full rounded-full gradient-bg transition-all duration-700 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          {status && status.total_segments > 0 && (
            <p className="text-xs text-gray-500 mt-2">
              Segments: {status.processed_segments} / {status.total_segments}
            </p>
          )}
        </div>

        {/* Pipeline Stages */}
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-6">Pipeline Stages</h3>
          <div className="space-y-1">
            {PIPELINE_STAGES.map((stage, index) => {
              let stageStatus: 'pending' | 'active' | 'done' | 'error' = 'pending'
              if (status?.status === 'failed' && index === currentStageIndex) {
                stageStatus = 'error'
              } else if (index < currentStageIndex) {
                stageStatus = 'done'
              } else if (index === currentStageIndex) {
                stageStatus = 'active'
              }

              return (
                <div key={stage.key}>
                  <div
                    className={`flex items-center gap-4 p-3 rounded-xl transition-all ${
                      stageStatus === 'active'
                        ? 'bg-indigo-500/10 border border-indigo-500/20'
                        : stageStatus === 'error'
                        ? 'bg-red-500/10 border border-red-500/20'
                        : ''
                    }`}
                  >
                    {/* Status Icon */}
                    <div className="flex-shrink-0">
                      {stageStatus === 'done' ? (
                        <CheckCircle2 className="w-6 h-6 text-green-400" />
                      ) : stageStatus === 'active' ? (
                        <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
                      ) : stageStatus === 'error' ? (
                        <XCircle className="w-6 h-6 text-red-400" />
                      ) : (
                        <div className="w-6 h-6 rounded-full border-2 border-gray-700" />
                      )}
                    </div>

                    {/* Stage Icon */}
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                        stageStatus === 'done'
                          ? 'bg-green-500/20'
                          : stageStatus === 'active'
                          ? 'gradient-bg'
                          : stageStatus === 'error'
                          ? 'bg-red-500/20'
                          : 'bg-white/5'
                      }`}
                    >
                      <stage.icon
                        className={`w-5 h-5 ${
                          stageStatus === 'done'
                            ? 'text-green-400'
                            : stageStatus === 'active'
                            ? 'text-white'
                            : stageStatus === 'error'
                            ? 'text-red-400'
                            : 'text-gray-600'
                        }`}
                      />
                    </div>

                    {/* Label */}
                    <span
                      className={`font-medium ${
                        stageStatus === 'done'
                          ? 'text-green-400'
                          : stageStatus === 'active'
                          ? 'text-white'
                          : stageStatus === 'error'
                          ? 'text-red-400'
                          : 'text-gray-600'
                      }`}
                    >
                      {stage.label}
                    </span>
                  </div>

                  {/* Connector */}
                  {index < PIPELINE_STAGES.length - 1 && (
                    <div className="ml-7 h-1 border-l-2 border-dashed border-gray-800" />
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProgressPage
