# German Voice LLM Tutor 🎧🇩🇪

A complete voice-based German conversation tutor for intermediate learners. Practice topic-specific conversations (football training, restaurant visits, doctor appointments) with real-time corrections and natural dialogue.

**Pipeline:** Voice Input → Whisper STT → Ollama LLM → German Corrections & Conversation → Edge TTS → Voice Output

## 🚀 Features

- **Voice-to-Voice**: Record German audio, get spoken responses
- **Topic-Based Roleplay**: Coach, waiter, doctor, colleague, etc.
- **Gentle Corrections**: Natural error correction with explanations  
- **Conversation History**: Track your progress and vocabulary
- **Local & Private**: Runs entirely on your PC with Ollama
- **Multi-Engine Support**: Whisper CLI/API, Edge TTS, pyttsx3 fallbacks

## 📁 Repository Structure

```
german-voice-llm-tutor/
├── backend/
│   ├── app.py                 # FastAPI server
│   ├── ollama_client.py       # LLM interface
│   ├── whisper_service.py     # Speech-to-text
│   ├── tts_service.py         # Text-to-speech
│   └── prompts/
│       └── system_prompt.txt  # German tutor prompt
├── ui/
│   └── streamlit_app.py       # Web interface
├── data/
│   ├── history/               # Conversation logs
│   └── audio/                 # Generated TTS files
├── requirements.txt
└── README.md
```

## 🛠️ Complete Setup (Windows)

### Prerequisites

1. **Python 3.10+** - [Download from python.org](https://www.python.org/downloads/)
2. **Ollama** - [Download from ollama.ai](https://ollama.ai/download)
3. **Git** (optional) - For cloning the repo

### Step 1: Install Ollama & Models

```powershell
# Install Ollama (download installer from ollama.ai)
# Then in PowerShell:
ollama serve
```

In a new PowerShell window:
```powershell
# Install a German-capable model (choose one):
ollama pull mistral          # Good for German, 7B params
ollama pull llama2          # Alternative, 7B params  
ollama pull codellama:7b    # If you prefer CodeLlama

# Test it works:
ollama run mistral "Hallo! Wie geht es dir?"
```

### Step 2: Set Up the Project

```powershell
# Create project directory
mkdir "c:\dev\german-voice-tutor"
cd "c:\dev\german-voice-tutor"

# Clone or download the code
git clone <your-repo-url> .
# OR manually create the files from this README

# Create Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Test components
python backend\ollama_client.py    # Test Ollama connection
python backend\whisper_service.py  # Test Whisper
python backend\tts_service.py      # Test TTS
```

### Step 3: Start the Services

**Terminal 1 - Backend API:**
```powershell
cd "c:\dev\german-voice-tutor"
.\.venv\Scripts\Activate.ps1
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Streamlit UI:**
```powershell
cd "c:\dev\german-voice-tutor"  
.\.venv\Scripts\Activate.ps1
streamlit run ui\streamlit_app.py
```

### Step 4: Test the System

1. Open http://localhost:8501 in your browser
2. Choose a topic (e.g., "Fußballtraining")
3. Click the microphone and say: *"Hallo, ich bin Stürmer im Team"*
4. Click "Send to Tutor" 
5. Listen to the German response and corrections!

## 🎯 Usage Examples

**Football Training Conversation:**
- You: *"Ich trainiere zwei Mal die Woche"*
- Tutor: *"Richtig wäre: 'Ich trainiere zweimal pro Woche.' Das ist schon gut! Aber für einen Stürmer könnte es mehr sein. Was machst du zusätzlich zum Teamtraining?"*

**Restaurant Visit:**
- You: *"Ich möchte einen Tisch für zwei Person"*  
- Tutor: *"Richtig: 'für zwei Personen.' Gerne! Haben Sie eine Reservierung? Raucher- oder Nichtrauchertisch?"*

## 🐛 Troubleshooting

### Backend Won't Start
```powershell
# Check if port 8000 is in use:
netstat -an | findstr :8000

# Try a different port:
uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

### Ollama Connection Issues
```powershell
# Check if Ollama is running:
curl http://localhost:11434/api/tags

# Restart Ollama service:
# Stop any running ollama processes, then:
ollama serve
```

### Whisper Not Found
```powershell
# Install Whisper:
pip install openai-whisper

# Or use the faster implementation:
pip install git+https://github.com/openai/whisper.git

# Test:
whisper --help
```

### Audio/Microphone Issues
- Windows: Settings → Privacy & Security → Microphone → Allow apps to access
- Chrome: Click the microphone icon in address bar, allow permissions
- Test with: https://mictests.com/

### TTS Not Working
```powershell
# Install edge-tts:
pip install edge-tts

# Test from command line:
edge-tts --text "Hallo Welt" --voice de-DE-KatjaNeural --write-media test.wav
```

## 🔧 Customization

### Adding New Topics
Edit `ui/streamlit_app.py`, add to the `topics` list:
```python
topics = [
    "existing topics...",
    "Jobinterview (job interview)",
    "Beim Arzt (at the doctor)",  
    # Your custom topic
]
```

### Changing AI Models
Edit `backend/ollama_client.py`:
```python
def ask_ollama(prompt: str, model: str = "llama2"):  # Change default model
```

### Different TTS Voices
Available German voices in `backend/tts_service.py`:
- `de-DE-KatjaNeural` (Female, standard)
- `de-DE-ConradNeural` (Male, standard)  
- `de-DE-AmalaNeural` (Female, friendly)

## 🚀 Next Steps / Roadmap

### Version 1.1 (Immediate)
- [ ] Add conversation export (PDF/CSV)  
- [ ] Grammar scoring system
- [ ] Vocabulary extraction and spaced repetition
- [ ] Audio quality improvements

### Version 2.0 (Mobile)  
- [ ] Flutter mobile app (see `mobile/ARCHITECTURE.md`)
- [ ] Offline mode with cached models
- [ ] Push notifications for practice reminders

### Version 3.0 (Advanced)
- [ ] Multiple language support (Spanish, French)
- [ ] Advanced pronunciation scoring
- [ ] Social features (share progress)
- [ ] Teacher dashboard

## 📄 License

MIT License - feel free to adapt for your needs!

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)  
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Ready to practice German?** Follow the setup steps above and start your first conversation! 🇩🇪✨