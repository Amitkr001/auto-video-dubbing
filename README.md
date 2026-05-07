# Auto Video Dubbing

Production-grade Auto Video Dubbing Web Application powered by AI. Upload a video, select a target language, and get a perfectly dubbed video with speaker detection, gender-matched voices, preserved background audio, and proper timestamp alignment.

## Features

- **Speaker Diarization** - Detects who spoke when using pyannote.audio
- **Gender-Matched Voices** - Male voice for male speakers, female voice for female speakers
- **Background Preservation** - Music and ambient sounds are separated and preserved
- **Per-Segment Processing** - Each speaker segment is transcribed, translated, and voiced individually
- **Real-Time Progress** - WebSocket updates showing pipeline stage progression
- **20+ Languages** - Supports translation to 20+ target languages via M2M100
- **Lip Sync** - Optional Wav2Lip integration for mouth movement correction

## AI Pipeline (9 Stages)

```
1. Extract Audio (FFmpeg)
2. Separate Vocals & Background (Demucs)
3. Detect Speakers (pyannote.audio)
4. Transcribe Each Segment (Whisper)
5. Detect Gender & Translate (M2M100)
6. Generate Voice (Coqui TTS)
7. Lip Sync Correction (Wav2Lip)
8. Rebuild & Merge Audio
9. Replace Audio in Video (FFmpeg)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI + Uvicorn |
| Job Queue | Redis |
| Audio/Video | FFmpeg |
| Vocal Separation | Demucs |
| Speaker Diarization | pyannote.audio |
| Speech-to-Text | OpenAI Whisper |
| Translation | M2M100 (418M) |
| Text-to-Speech | Coqui TTS |
| Lip Sync | Wav2Lip |
| Frontend | React + TypeScript + Tailwind CSS |
| Containerization | Docker + Docker Compose |

---

## Installation Guide

- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Docker Installation (Any OS)](#docker-installation)

---

## Windows Installation

### Prerequisites

#### 1. Install Python 3.11

> **Important:** Use Python 3.11 specifically. Python 3.12+ has compatibility issues with some ML packages.

1. Download Python 3.11 from [python.org/downloads](https://www.python.org/downloads/release/python-31110/)
2. Run the installer
3. **Check "Add Python to PATH"** during installation
4. Verify:
   ```cmd
   python --version
   ```

#### 2. Install Node.js 18+

1. Download from [nodejs.org](https://nodejs.org/) (LTS recommended)
2. Run the installer
3. Verify:
   ```cmd
   node --version
   npm --version
   ```

#### 3. Install FFmpeg

1. Download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) (get the "essentials" build)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Search "Environment Variables" in Start Menu
   - Edit `Path` under System Variables
   - Add `C:\ffmpeg\bin`
4. Verify:
   ```cmd
   ffmpeg -version
   ```

#### 4. Install Redis

**Option A: Using Memurai (Recommended for Windows)**
1. Download from [memurai.com](https://www.memurai.com/get-memurai)
2. Install and it runs automatically as a Windows service

**Option B: Using WSL2**
```bash
wsl --install
# Inside WSL:
sudo apt update && sudo apt install redis-server
sudo service redis-server start
```

#### 5. Install NVIDIA CUDA (Optional - for GPU acceleration)

> Skip this if you don't have an NVIDIA GPU. The app works on CPU too (just slower).

1. Install [NVIDIA GPU Drivers](https://www.nvidia.com/drivers) (latest for your GPU)
2. Install [CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive)
3. Verify:
   ```cmd
   nvidia-smi
   ```

### Setup

#### Clone the Repository

```cmd
git clone https://github.com/Amitkr001/auto-video-dubbing.git
cd auto-video-dubbing
```

#### Backend Setup

```cmd
cd backend

:: Create virtual environment
python -m venv venv
venv\Scripts\activate

:: Install PyTorch (choose one):

:: WITH NVIDIA GPU (CUDA 11.8):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

:: WITHOUT GPU (CPU only):
pip install torch torchvision torchaudio

:: Install remaining dependencies
pip install -r requirements.txt
pip install "transformers>=4.40,<5"
```

#### Configure Environment

```cmd
:: Still in backend/ directory
copy .env.example .env
```

Edit `backend\.env` and set your HuggingFace token:
```
REDIS_URL=redis://localhost:6379/0
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
TEMP_DIR=./temp
WHISPER_MODEL=base
M2M100_MODEL=facebook/m2m100_418M
PYANNOTE_AUTH_TOKEN=your_huggingface_token_here
WAV2LIP_CHECKPOINT=./models/wav2lip.pth
COQUI_TTS_MODEL=tts_models/multilingual/multi-dataset/your_tts
MAX_UPLOAD_SIZE_MB=500
```

> **Get your HuggingFace token:** Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and create a token. Then accept the model agreements at:
> - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
> - [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)
> - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

#### Create Required Directories

```cmd
mkdir uploads outputs temp models
```

#### Frontend Setup

```cmd
cd ..\frontend
npm install
```

### Running the Application

Open **4 separate Command Prompt / Terminal windows**:

**Terminal 1 - Redis:**
```cmd
:: If using Memurai, it's already running as a service
:: If using WSL:
wsl -e redis-server
```

**Terminal 2 - Backend API:**
```cmd
cd auto-video-dubbing\backend
venv\Scripts\activate
set PYTHONPATH=.
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 - Queue Worker:**
```cmd
cd auto-video-dubbing\backend
venv\Scripts\activate
set PYTHONPATH=.
python -m app.workers.queue_worker
```

**Terminal 4 - Frontend:**
```cmd
cd auto-video-dubbing\frontend
npm run dev
```

### Access the Application

Open your browser and go to: **http://localhost:5173**

> **Note:** The first dubbing job will take longer as ML models are downloaded (~4GB total). Subsequent jobs will be much faster.

---

## macOS Installation

### Prerequisites

#### 1. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Python 3.11

```bash
brew install python@3.11
```

Verify:
```bash
python3.11 --version
```

#### 3. Install Node.js

```bash
brew install node
```

Verify:
```bash
node --version
npm --version
```

#### 4. Install FFmpeg

```bash
brew install ffmpeg
```

Verify:
```bash
ffmpeg -version
```

#### 5. Install Redis

```bash
brew install redis
brew services start redis
```

Verify:
```bash
redis-cli ping
# Should respond: PONG
```

### Setup

#### Clone the Repository

```bash
git clone https://github.com/Amitkr001/auto-video-dubbing.git
cd auto-video-dubbing
```

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install PyTorch
# Apple Silicon (M1/M2/M3/M4) or Intel Mac:
pip install torch torchvision torchaudio

# Install remaining dependencies
pip install -r requirements.txt
pip install "transformers>=4.40,<5"
```

> **Apple Silicon Note:** PyTorch supports MPS (Metal Performance Shaders) acceleration on M1/M2/M3/M4 chips. Most models will automatically use MPS for GPU-like acceleration.

#### Configure Environment

```bash
# Still in backend/ directory
cp .env.example .env
```

Edit `backend/.env` with your preferred editor:
```bash
nano .env
```

Set your HuggingFace token:
```
REDIS_URL=redis://localhost:6379/0
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
TEMP_DIR=./temp
WHISPER_MODEL=base
M2M100_MODEL=facebook/m2m100_418M
PYANNOTE_AUTH_TOKEN=your_huggingface_token_here
WAV2LIP_CHECKPOINT=./models/wav2lip.pth
COQUI_TTS_MODEL=tts_models/multilingual/multi-dataset/your_tts
MAX_UPLOAD_SIZE_MB=500
```

> **Get your HuggingFace token:** Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and create a token. Then accept the model agreements at:
> - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
> - [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)
> - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

#### Create Required Directories

```bash
mkdir -p uploads outputs temp models
```

#### Frontend Setup

```bash
cd ../frontend
npm install
```

### Running the Application

Open **4 separate Terminal windows** (or use tabs):

**Terminal 1 - Redis:**
```bash
# If installed with brew services, it's already running
# Otherwise:
redis-server
```

**Terminal 2 - Backend API:**
```bash
cd auto-video-dubbing/backend
source venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 - Queue Worker:**
```bash
cd auto-video-dubbing/backend
source venv/bin/activate
PYTHONPATH=. python -m app.workers.queue_worker
```

**Terminal 4 - Frontend:**
```bash
cd auto-video-dubbing/frontend
npm run dev
```

### Access the Application

Open your browser and go to: **http://localhost:5173**

> **Note:** The first dubbing job will take longer as ML models are downloaded (~4GB total). Subsequent jobs will be much faster.

---

## Docker Installation

This works on **Windows, macOS, and Linux**.

### Prerequisites

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. (Optional) For NVIDIA GPU support on Linux: Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### Setup & Run

```bash
git clone https://github.com/Amitkr001/auto-video-dubbing.git
cd auto-video-dubbing

# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env and set PYANNOTE_AUTH_TOKEN

# Build and start all services
docker-compose up --build
```

This starts 4 services:
- **Frontend** at http://localhost:3000
- **Backend API** at http://localhost:8000
- **Queue Worker** (background)
- **Redis** (background)

---

## Optional: Wav2Lip Setup (Lip Sync)

Wav2Lip provides lip sync correction so mouth movements match the dubbed audio. The pipeline works without it but lip movements won't match.

1. Download `wav2lip.pth` from the [Wav2Lip repository](https://github.com/Rudrabha/Wav2Lip#getting-the-weights)
2. Place it in `backend/models/wav2lip.pth`

---

## Supported Languages

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | en | Hindi | hi |
| French | fr | Japanese | ja |
| Spanish | es | Korean | ko |
| German | de | Portuguese | pt |
| Italian | it | Russian | ru |
| Chinese | zh | Arabic | ar |
| Dutch | nl | Turkish | tr |
| Polish | pl | Vietnamese | vi |
| Swedish | sv | Thai | th |
| Czech | cs | Indonesian | id |

---

## Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| GPU VRAM | Not required (CPU works) | 4+ GB (NVIDIA) |
| Disk Space | 10 GB (for models) | 20 GB |
| CPU | 4 cores | 8+ cores |

**GPU Support:**
- **NVIDIA (CUDA):** GTX 1050 Ti or better. Tested with GTX 1650.
- **Apple Silicon (MPS):** M1/M2/M3/M4 - automatic acceleration via Metal.
- **CPU only:** Works but significantly slower (5-10x).

---

## Troubleshooting

### Common Issues

**"Module not found" errors on Windows:**
- Make sure you activated the virtual environment: `venv\Scripts\activate`
- Make sure `PYTHONPATH=.` is set before running commands

**Redis connection refused:**
- Make sure Redis is running
- Windows: Check if Memurai service is started
- macOS: Run `brew services start redis`

**pyannote returns 403 error:**
- You need to accept the model agreements on HuggingFace (links above)
- Make sure your token is set correctly in `.env`

**Out of VRAM / CUDA out of memory:**
- Use a smaller Whisper model: set `WHISPER_MODEL=tiny` in `.env`
- Close other GPU-intensive applications
- The app will fall back to CPU if GPU memory is insufficient

**TTS language not supported:**
- The `your_tts` model supports: English, French, Portuguese
- For other languages, the system falls back to English voice
- You can try `tts_models/multilingual/multi-dataset/xtts_v2` for more languages (requires more VRAM)

**First run is very slow:**
- This is normal. ML models (~4GB) are being downloaded
- Subsequent runs reuse cached models and are much faster

---

## Project Structure

```
auto-video-dubbing/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── pipeline/
│   │   │   └── dubbing_pipeline.py  # 9-stage pipeline orchestrator
│   │   ├── services/
│   │   │   ├── audio_separator.py   # FFmpeg + Demucs
│   │   │   ├── diarization.py       # pyannote + VAD fallback
│   │   │   ├── transcriber.py       # Whisper STT
│   │   │   ├── translator.py        # M2M100 translation
│   │   │   ├── tts_generator.py     # Coqui TTS
│   │   │   ├── lipsync.py           # Wav2Lip
│   │   │   └── audio_merger.py      # Audio reconstruction
│   │   └── workers/
│   │       └── queue_worker.py      # Redis queue worker
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   ├── UploadPage.tsx
│   │   │   ├── ProgressPage.tsx
│   │   │   └── PreviewPage.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   └── api/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## License

MIT
