import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import UploadPage from './pages/UploadPage'
import ProgressPage from './pages/ProgressPage'
import PreviewPage from './pages/PreviewPage'
import Navbar from './components/Navbar'

function App() {
  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/progress/:jobId" element={<ProgressPage />} />
        <Route path="/preview/:jobId" element={<PreviewPage />} />
      </Routes>
    </div>
  )
}

export default App
