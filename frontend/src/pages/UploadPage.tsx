import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload,
  FileVideo,
  Languages,
  ArrowRight,
  X,
  AlertCircle,
  Loader2,
} from 'lucide-react'
import { uploadVideo, startDubbing, getLanguages } from '../api/client'

function UploadPage() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null)
  const [languages, setLanguages] = useState<Record<string, string>>({})
  const [targetLanguage, setTargetLanguage] = useState('')
  const [sourceLanguage, setSourceLanguage] = useState('auto')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  useEffect(() => {
    getLanguages()
      .then((res) => {
        setLanguages(res.languages)
        const keys = Object.keys(res.languages)
        if (keys.length > 0 && !targetLanguage) {
          setTargetLanguage(keys[0])
        }
      })
      .catch(() => {
        setLanguages({
          en: 'English', es: 'Spanish', fr: 'French', de: 'German',
          hi: 'Hindi', ja: 'Japanese', ko: 'Korean', zh: 'Chinese',
          pt: 'Portuguese', ru: 'Russian', ar: 'Arabic', it: 'Italian',
        })
        setTargetLanguage('es')
      })
  }, [])

  const handleFile = useCallback((selectedFile: File) => {
    const validExtensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm']
    const ext = '.' + selectedFile.name.split('.').pop()?.toLowerCase()
    if (!validExtensions.includes(ext)) {
      setError('Unsupported format. Use MP4, MKV, AVI, MOV, or WebM.')
      return
    }
    if (selectedFile.size > 500 * 1024 * 1024) {
      setError('File too large. Maximum size is 500MB.')
      return
    }
    setFile(selectedFile)
    setError(null)
    setVideoPreviewUrl(URL.createObjectURL(selectedFile))
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragActive(false)
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile) handleFile(droppedFile)
    },
    [handleFile]
  )

  const handleSubmit = async () => {
    if (!file || !targetLanguage) return
    setUploading(true)
    setError(null)
    try {
      setUploadProgress(30)
      const uploadRes = await uploadVideo(file)
      setUploadProgress(70)
      const dubRes = await startDubbing(
        uploadRes.file_id,
        targetLanguage,
        sourceLanguage
      )
      setUploadProgress(100)
      navigate(`/progress/${dubRes.job_id}`)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Upload failed. Please try again.')
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const removeFile = () => {
    setFile(null)
    if (videoPreviewUrl) URL.revokeObjectURL(videoPreviewUrl)
    setVideoPreviewUrl(null)
  }

  return (
    <div className="pt-24 pb-16 px-4 min-h-screen">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-3">
            <span className="gradient-text">Upload Your Video</span>
          </h1>
          <p className="text-gray-400">
            Select a video file and choose the target language for dubbing.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {/* Drop Zone */}
        <div
          className={`glass-card p-8 mb-6 transition-all ${
            dragActive
              ? 'border-indigo-500 bg-indigo-500/10'
              : 'hover:border-white/20'
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          {!file ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center mx-auto mb-6">
                <Upload className="w-8 h-8 text-white" />
              </div>
              <p className="text-lg font-medium mb-2">
                Drag & drop your video here
              </p>
              <p className="text-gray-500 text-sm mb-6">
                or click to browse — MP4, MKV, AVI, MOV, WebM (max 500MB)
              </p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-6 py-3 rounded-xl gradient-bg text-white font-medium hover:opacity-90 transition-opacity"
              >
                Browse Files
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0]
                  if (f) handleFile(f)
                }}
              />
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <FileVideo className="w-8 h-8 text-indigo-400" />
                  <div>
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(file.size / (1024 * 1024)).toFixed(1)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={removeFile}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              {videoPreviewUrl && (
                <video
                  src={videoPreviewUrl}
                  controls
                  className="w-full rounded-xl max-h-80 bg-black"
                />
              )}
            </div>
          )}
        </div>

        {/* Language Selection */}
        <div className="glass-card p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Languages className="w-5 h-5 text-indigo-400" />
            <h3 className="font-semibold">Language Settings</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Source Language
              </label>
              <select
                value={sourceLanguage}
                onChange={(e) => setSourceLanguage(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-indigo-500 transition-colors"
              >
                <option value="auto">Auto Detect</option>
                {Object.entries(languages).map(([code, name]) => (
                  <option key={code} value={code}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Target Language
              </label>
              <select
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-indigo-500 transition-colors"
              >
                {Object.entries(languages).map(([code, name]) => (
                  <option key={code} value={code}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Upload Progress */}
        {uploading && (
          <div className="glass-card p-6 mb-6">
            <div className="flex items-center gap-3 mb-3">
              <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
              <span className="text-sm font-medium">Uploading & starting job...</span>
            </div>
            <div className="w-full h-2 rounded-full bg-white/10">
              <div
                className="h-full rounded-full gradient-bg transition-all duration-500"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!file || !targetLanguage || uploading}
          className="w-full py-4 rounded-xl gradient-bg text-white font-semibold text-lg hover:opacity-90 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              Start Dubbing
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>
    </div>
  )
}

export default UploadPage
