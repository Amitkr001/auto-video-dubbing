import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Download,
  ArrowLeft,
  CheckCircle2,
  Upload,
  Play,
  Loader2,
} from 'lucide-react'
import { getJobStatus, getDownloadUrl, getPreviewUrl, JobStatus } from '../api/client'

function PreviewPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!jobId) return
    const fetchStatus = async () => {
      try {
        const data = await getJobStatus(jobId)
        setStatus(data)
      } catch {
        // handle error
      } finally {
        setLoading(false)
      }
    }
    fetchStatus()
  }, [jobId])

  if (loading) {
    return (
      <div className="pt-24 pb-16 px-4 min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    )
  }

  if (!status || status.status !== 'completed') {
    return (
      <div className="pt-24 pb-16 px-4 min-h-screen">
        <div className="max-w-2xl mx-auto text-center">
          <div className="glass-card p-12">
            <Loader2 className="w-12 h-12 text-indigo-400 mx-auto mb-4 animate-spin" />
            <h2 className="text-2xl font-bold mb-2">Video Not Ready</h2>
            <p className="text-gray-400 mb-6">
              {status?.status === 'failed'
                ? `Processing failed: ${status.error}`
                : 'The video is still being processed.'}
            </p>
            {status?.status === 'failed' ? (
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl gradient-bg text-white font-medium"
              >
                <Upload className="w-4 h-4" />
                Try Again
              </Link>
            ) : (
              <Link
                to={`/progress/${jobId}`}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl gradient-bg text-white font-medium"
              >
                View Progress
              </Link>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="pt-24 pb-16 px-4 min-h-screen">
      <div className="max-w-4xl mx-auto">
        {/* Success Banner */}
        <div className="glass-card p-6 mb-6 border-green-500/20">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-8 h-8 text-green-400" />
            <div>
              <h2 className="text-xl font-bold">Dubbing Complete!</h2>
              <p className="text-gray-400 text-sm">
                Your video has been successfully dubbed. Preview and download below.
              </p>
            </div>
          </div>
        </div>

        {/* Video Player */}
        <div className="glass-card overflow-hidden mb-6">
          <div className="relative bg-black rounded-t-2xl">
            <video
              src={getPreviewUrl(jobId!)}
              controls
              className="w-full max-h-[500px]"
              poster=""
            >
              Your browser does not support the video tag.
            </video>
          </div>
          <div className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Play className="w-4 h-4 text-indigo-400" />
              <span className="text-sm text-gray-400">Dubbed Video Preview</span>
            </div>
            <span className="text-xs text-gray-600">
              Job: {jobId?.slice(0, 8)}...
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4">
          <a
            href={getDownloadUrl(jobId!)}
            download
            className="flex-1 py-4 rounded-xl gradient-bg text-white font-semibold text-center hover:opacity-90 transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-5 h-5" />
            Download Dubbed Video
          </a>
          <Link
            to="/upload"
            className="flex-1 py-4 rounded-xl glass text-white font-semibold text-center hover:bg-white/10 transition-all flex items-center justify-center gap-2"
          >
            <Upload className="w-5 h-5" />
            Dub Another Video
          </Link>
        </div>

        {/* Back */}
        <div className="mt-8 text-center">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-gray-500 hover:text-white transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}

export default PreviewPage
