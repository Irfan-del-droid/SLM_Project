# ⚡ NEXUS — Advanced AI Code Engine

A sleek, production-grade coding assistant powered by **CodeGemma-2B** via Ollama, built with Streamlit.

---

## 🚀 Features

- **5 Modes** — Code Generation, Debug & Fix, Optimize, Explain Code, Enterprise Mode
- **Auto Language Detection** — Identifies language from code and syntax hints
- **Auto Project Type Detection** — CLI, API, ML, Web, Streamlit, and more
- **Complexity Analyzer** — Scores code as Beginner / Intermediate / Advanced
- **Code Download** — One-click `.py`, `.js`, `.html`, etc. download
- **ZIP Export** — Bundle multi-file outputs into a ZIP
- **Session Stats** — Live tracking of prompts, code blocks, and tokens
- **Dark Cyberpunk UI** — Glassmorphism, Orbitron font, scanlines, neon palette

---

## 📁 Project Structure

```
SLM_Project/
├── app.py           # Main Streamlit application
├── complexity.py    # Code complexity analysis module
├── detector.py      # Language & project type detection
├── requirements.txt # Python dependencies
└── README.md        # This file
```

---

## ⚙️ Setup

### 1. Install Ollama
Download from [https://ollama.ai](https://ollama.ai) and install.

### 2. Pull the Model
```bash
ollama pull hf.co/Maziyarpanahi/codegemma-2b-GGUF:Q4_K_M
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run NEXUS
```bash
streamlit run app.py
```

---

## 🎮 Usage

| Mode | Purpose |
|------|---------|
| **Code Generation** | Describe what you want to build |
| **Debug & Fix** | Paste buggy code for diagnosis |
| **Optimize** | Improve performance & structure |
| **Explain Code** | Step-by-step code breakdown |
| **Enterprise Mode** | Scalable, modular architecture |

---

## 🔧 Configuration

Edit `app.py` to change:
- `MODEL` — swap the Ollama model string
- `SYSTEM_PROMPT` — tune NEXUS's persona and rules

---

*Built with CodeGemma · Ollama · Streamlit*
