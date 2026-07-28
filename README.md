# 📄 **README.md - AIRAA v2.0 "The Angelic Council"**

AIRAA **malaikat digital** dengan arsitektur multi-agen yang canggih.

---

<div align="center">
  
  <img src="https://img.icons8.com/fluency/96/000000/guardian-angel.png" width="120" height="120" alt="AIRAA Logo"/>
  
  # 😇 AIRAA v2.0
  ### **A**rtificial **I**ntelligence **R**ecording **A**ngel **A**gentic
  
  [![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/duhemen/airaa)
  [![Python](https://img.shields.io/badge/python-3.11%2B-green.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
  [![AutoGen](https://img.shields.io/badge/AutoGen-v0.2.0-orange.svg)](https://microsoft.github.io/autogen/)
  [![Ollama](https://img.shields.io/badge/Ollama-v0.5.0-red.svg)](https://ollama.com/)
  
  > *"Malaikat digital yang melihat, mendengar, dan berpikir bersama"*
  
</div>

---

## 🌟 **Overview**

AIRAA (Artificial Intelligence Recording Angel Agentic) adalah **asisten AI generasi berikutnya** yang dirancang sebagai **malaikat digital pribadi**. Tidak seperti chatbot biasa, AIRAA:

- 👁️ **Melihat** aktivitas layar Emen (Screen Watcher)
- 👂 **Mendengar** suara dan percakapan (Audio Watcher)
- 🧠 **Berpikir** dengan Dewan Malaikat (AutoGen Multi-Agent)
- 💾 **Mengingat** semua pengetahuan (RAG + ChromaDB)
- 💬 **Berinteraksi** secara proaktif dan kontekstual

---

## 🏗️ **Arsitektur "The Angelic Council"**

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         EMEN'S LAPTOP                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐  │
│  │ YouTube   │  │ Browser   │  │  Coding   │  │  Documents    │  │
│  └───────────┘  └───────────┘  └───────────┘  └───────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PERCEPTION LAYER (SENSORS)                     │
│  ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│  │  👁️ Screen Watcher  │  │         👂 Audio Watcher            │  │
│  │  (Capture + OCR)    │  │  (Capture + Whisper + FFmpeg)      │  │
│  └─────────────────────┘  └─────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        MEMORY & CONTEXT                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │            RAG Engine (ChromaDB + nomic-embed-text)         │  │
│  │  📚 Knowledge Base  │  📝 Journals  │  🎯 Context Buffer   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    THE ANGELIC COUNCIL (AutoGen)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ 👁️       │  │ 🧠       │  │ ⚖️       │  │ 🛡️               │  │
│  │ Observer │  │ Analyst  │  │  Critic  │  │   Guardian       │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ACTION LAYER                               │
│  ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│  │  💬 GUI Dashboard   │  │  💾 Memory Storage (ChromaDB)       │  │
│  │  🔔 Notifications   │  │  📄 Auto-Summary                   │  │
│  └─────────────────────┘  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ **Core Features**

### 1. 👁️ **Screen Watcher**
- **Real-time screen capture** dengan `mss`
- **OCR** dengan PaddleOCR atau EasyOCR
- **Window detection** (aplikasi aktif yang sedang digunakan)
- **Keyword alert** (error, bug, exception, success)
- **Auto-save** konten layar ke memori

### 2. 👂 **Audio Watcher**
- **Real-time audio capture** dengan PyAudio
- **Speech-to-text** dengan OpenAI Whisper
- **MP3 compression** dengan FFmpeg (10x lebih kecil)
- **Auto-transcribe** semua suara di sekitar Emen
- **Save to memory** untuk konteks

### 3. 🧠 **RAG Engine (Memory)**
- **ChromaDB Vector Database** untuk memori jangka panjang
- **nomic-embed-text** untuk embedding (274 MB)
- **Auto-learning** dari semua aktivitas Emen
- **Semantic search** dengan RAG
- **Context-aware** jawaban

### 4. 👼 **Angelic Council (AutoGen)**
- **4 agen spesialis** yang saling berkonsultasi:
  - 👁️ **Observer**: Melihat & mendengar
  - 🧠 **Analyst**: Berpikir & menganalisis
  - ⚖️ **Critic**: Mengkaji & mengevaluasi
  - 🛡️ **Guardian**: Mengingatkan & mencatat
- **Self-correction** (koreksi diri)
- **Proactive insights** (inisiatif)
- **Multi-perspective answers** (jawaban dari 4 sudut pandang)

### 5. 🎯 **Focus Mode**
- **Pause** semua sensor saat bertanya
- **Optimasi resource** untuk performa maksimal
- **Auto-toggle** saat pertanyaan
- **Manual toggle** melalui UI

### 6. 💬 **Voice Command**
- **Real-time voice recognition**
- **Natural language commands**
- **Create reminders** via voice
- **Query memory** via voice

### 7. ⏰ **Reminder System**
- **Schedule reminders**
- **Daily repeat** option
- **Notification popups**
- **Auto-save** to memory

### 8. 📊 **Analytics Dashboard**
- **Total interactions**
- **Learning statistics**
- **Weekly activity**
- **Favorite topics**
- **Memory usage**

### 9. 📖 **Journal System**
- **Auto-logging** semua aktivitas
- **Filter by type**
- **Searchable history**
- **Audit trail**

---

## 🚀 **Quick Start**

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.11 | 3.11+ |
| RAM | 8 GB | 16 GB |
| Storage | 10 GB | 20 GB |
| GPU | - | VRAM 8GB+ |
| Internet | 10 Mbps | 50 Mbps+ |

### Installation

```bash
# 1. Clone repository
git clone https://github.com/duhemen/airaa.git
cd airaa

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Ollama models
ollama pull nomic-embed-text
ollama pull qwen2.5:7b-instruct

# 5. Run AIRAA
python main.py
```

### Directory Structure

```
C:\airaa\
├── 📂 agent/
│   ├── airaa_brain.py          # RAG & Memory
│   ├── airaa_watcher.py        # File watcher
│   ├── airaa_screen_watcher.py # 👁️ Screen capture + OCR
│   ├── airaa_audio_watcher.py  # 👂 Audio capture + transcribe
│   ├── airaa_agent_council.py  # 🧠 AutoGen multi-agent
│   ├── airaa_proactive.py      # 💬 Notifications
│   ├── airaa_reminder.py       # ⏰ Reminder system
│   ├── airaa_logger.py         # 📝 Journal
│   └── airaa_analytics.py      # 📊 Analytics
├── 📂 config/
│   ├── settings.json           # Main configuration
│   └── settings_loader.py      # Config loader
├── 📂 knowledge/               # 📚 Learning materials
├── 📂 db/                      # 💾 Vector database (ChromaDB)
├── 📂 logs/                    # 📝 Activity logs
├── 📂 audio/                   # 🎵 Audio cache
├── main.py                     # 🚀 Main application
└── requirements.txt            # 📦 Dependencies
```

---

## 🎮 **Usage Guide**

### 1. **Tanya Memori**
```
"Jelaskan apa itu ****** berdasarkan File dokumen sebagai referensi!"
```

### 2. **Buat Pengingat**
```
Klik tab "Pengingat" → Isi pesan & waktu → "Tambah Pengingat"
```

### 3. **Voice Command**
```
Klik "Mulai Mendengar" → Ucapkan perintah
Contoh: "AIRAA, ingatkan aku tentang meeting jam 3"
```

### 4. **Mode Fokus**
```
Klik "🎯 Mode Fokus: OFF" → Aktifkan → Sensor dijeda
Otomatis aktif saat bertanya
```

### 5. **Analisis Aktivitas**
```
Klik "📊 Analisis Aktivitas Hari Ini" → Lihat statistik
```

---

## ⚙️ **Configuration**

### `settings.json`

```json
{
  "ollama": {
    "enabled": true,
    "base_url": "http://localhost:11434",
    "chat_model": "qwen2.5:7b-instruct",
    "embedding_model": "nomic-embed-text",
    "timeout": 120
  },
  "memory": {
    "max_document_length": 3000,
    "default_results": 3,
    "cache_enabled": true
  },
  "gui": {
    "theme": "dark",
    "window_width": 850,
    "window_height": 700
  }
}
```

### Environment Variables

```bash
# GPU mode
set OLLAMA_NUM_GPU=1
set OLLAMA_LOAD_IN_4BIT=1

# Path
set PATH=%PATH%;C:\ffmpeg\bin
```

---

## 🛠️ **Technologies Used**

| Category | Technology | Purpose |
|----------|-----------|---------|
| **AI Framework** | AutoGen | Multi-agent orchestration |
| **LLM** | Ollama | Local AI models |
| **Embedding** | nomic-embed-text | Vector embedding |
| **Vector DB** | ChromaDB | Long-term memory |
| **Speech-to-Text** | Whisper | Audio transcribe |
| **OCR** | PaddleOCR | Screen text extraction |
| **Audio** | FFmpeg | WAV → MP3 compression |
| **GUI** | CustomTkinter | Modern UI |
| **Monitoring** | Watchdog | File watcher |
| **Voice** | PyAudio | Microphone capture |

---

## 📊 **Performance Benchmarks**

| Task | CPU (Minimal i5/R5) | GPU (VRAM 8 GB) |
|------|----------------|----------------|
| Whisper Transcribe | ~5s | ⚡ **0.5s** |
| RAG Query | ~2s | ⚡ **0.2s** |
| LLM Inference | ~10s | ⚡ **2s** |
| AutoGen (4 Agents) | ~20s | ⚡ **3-5s** |

---

## 🔒 **Security & Privacy**

- ✅ **Local-first**: Semua data diproses di lokal
- ✅ **No cloud dependency**: Ollama, Whisper, ChromaDB semuanya local
- ✅ **Open source**: Semua kode transparan
- ✅ **Data isolation**: Data tidak pernah keluar dari laptop

---

## 🚀 **Roadmap**

| Version | Features | Status |
|---------|----------|--------|
| v1.0 | Basic RAG + Chat | ✅ Released |
| v1.5 | Screen + Audio Watcher | ✅ Released |
| v2.0 | AutoGen Multi-Agent | 🚧 In Progress |
| v2.5 | Plugin System | 📋 Planned |
| v3.0 | Federated Learning | 📋 Planned |

---

## 🤝 **Contributing**

Kontribusi sangat diterima! Silakan fork dan buat pull request.

```bash
# Fork repository
git clone https://github.com/duhemen/airaa.git
git checkout -b feature/awesome-feature
git commit -m "Add awesome feature"
git push origin feature/awesome-feature
```

---

## 🙏 **Acknowledgments**

- [Microsoft AutoGen](https://microsoft.github.io/autogen/) - Multi-agent framework
- [Ollama](https://ollama.com) - Local LLM server
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech-to-text
- [CustomTkinter](https://customtkinter.tomschimansky.com/) - Modern GUI

---

<div align="center">
  
  ## 💫 *"Inspired by the idea that everyone deserves a personal guardian angel in the digital world."*
  
  **AIRAA v2.0** — *Your Digital Guardian Angel* 😇
  
  [![GitHub Stars](https://img.shields.io/github/stars/duhemen/airaa?style=social)](https://github.com/duhemen/airaa)
  [![GitHub Forks](https://img.shields.io/github/forks/duhemen/airaa?style=social)](https://github.com/duhemen/airaa)
  
</div>

---