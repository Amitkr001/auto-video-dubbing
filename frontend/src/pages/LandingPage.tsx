import { Link } from 'react-router-dom'
import {
  Upload,
  Languages,
  Mic,
  Music,
  MonitorPlay,
  Zap,
  ArrowRight,
  CheckCircle2,
  Waves,
  Users,
} from 'lucide-react'

const features = [
  {
    icon: Users,
    title: 'Speaker Detection',
    description: 'Identifies who spoke when using advanced speaker diarization with pyannote.audio.',
  },
  {
    icon: Mic,
    title: 'Gender-Matched Voices',
    description: 'Male voice for male speakers, female voice for female speakers using Coqui TTS.',
  },
  {
    icon: MonitorPlay,
    title: 'Lip Sync Correction',
    description: 'Wav2Lip ensures mouth movements match the dubbed audio perfectly.',
  },
  {
    icon: Music,
    title: 'Background Preserved',
    description: 'Demucs separates vocals from music. Background audio stays untouched.',
  },
  {
    icon: Waves,
    title: 'Perfect Timing',
    description: 'Every segment is time-aligned — no language overlap, no gaps.',
  },
  {
    icon: Zap,
    title: 'No Quality Loss',
    description: 'Video stream is copied without re-encoding. Zero quality degradation.',
  },
]

const pipelineSteps = [
  'Extract audio from video',
  'Separate vocals & background',
  'Detect speakers & timestamps',
  'Transcribe each segment',
  'Translate per segment',
  'Generate gender-matched voice',
  'Apply lip sync correction',
  'Merge & rebuild final video',
]

function LandingPage() {
  return (
    <div className="relative overflow-hidden">
      {/* Hero */}
      <section className="relative pt-32 pb-20 px-4">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-gray-300">100% Open Source AI Pipeline</span>
          </div>

          <h1 className="text-5xl sm:text-7xl font-bold leading-tight mb-6">
            <span className="gradient-text">Auto Video Dubbing</span>
            <br />
            <span className="text-white">Powered by AI</span>
          </h1>

          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Upload any video. Choose a language. Get a perfectly dubbed version with
            speaker detection, gender-matched voices, lip sync, and preserved background audio.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/upload"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl gradient-bg text-white font-semibold text-lg hover:opacity-90 transition-all shadow-lg shadow-indigo-600/25"
            >
              <Upload className="w-5 h-5" />
              Start Dubbing
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <span className="gradient-text">Production-Grade</span> Dubbing
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Every aspect of the dubbing pipeline is handled with precision.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="glass-card p-6 hover:border-indigo-500/30 transition-all group"
              >
                <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline Steps */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <span className="gradient-text">8-Stage</span> AI Pipeline
            </h2>
            <p className="text-gray-400 text-lg">
              Each stage is processed per-speaker-segment for maximum precision.
            </p>
          </div>

          <div className="glass-card p-8">
            <div className="space-y-4">
              {pipelineSteps.map((step, index) => (
                <div key={step} className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full gradient-bg flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold">{index + 1}</span>
                  </div>
                  <div className="flex-1 h-px bg-gradient-to-r from-white/20 to-transparent" />
                  <span className="text-gray-300 text-sm sm:text-base font-medium">
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            <span className="gradient-text">Open Source</span> Stack
          </h2>
          <p className="text-gray-400 text-lg mb-12">
            Built entirely with free and open-source tools.
          </p>

          <div className="flex flex-wrap justify-center gap-3">
            {[
              'FFmpeg', 'Demucs', 'pyannote.audio', 'Whisper',
              'M2M100', 'Coqui TTS', 'Wav2Lip', 'FastAPI',
              'Redis', 'React', 'Docker',
            ].map((tech) => (
              <span
                key={tech}
                className="px-4 py-2 rounded-lg glass text-sm text-gray-300 hover:text-white transition-colors"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <div className="glass-card p-12">
            <Languages className="w-12 h-12 text-indigo-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4">Ready to Dub?</h2>
            <p className="text-gray-400 mb-8">
              Upload your video and choose a target language to get started.
            </p>
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl gradient-bg text-white font-semibold hover:opacity-90 transition-all"
            >
              Upload Video
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-white/10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg gradient-bg flex items-center justify-center">
              <Languages className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold gradient-text">DubSync</span>
          </div>
          <p className="text-sm text-gray-500">Open Source Auto Video Dubbing</p>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
