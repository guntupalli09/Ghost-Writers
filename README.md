# 👥 Ghostwriter Teams

> An AI-powered creative marketing workspace — driven by multi-agent collaboration, local LLMs, and real-time strategy generation.

---

## 🚀 Features

### 🤖 AI Agent Collaboration
- Multiple specialized AI agents working together in real time
- Supports brainstorming, critique, rewriting, and campaign planning

### 📅 Content Calendar Generator
- Auto-generates multi-week, platform-specific campaign calendars
- Exportable to CSV, Markdown, PDF

### ✍️ Rewrite Assistant (Eva Mode)
- Critiques your content and suggests two improved versions

### 🌐 Multilingual Output
- Translate responses to major world languages
- Keeps brand names, code, and URLs in English

### 📊 Agent Insights Dashboard
- View per-agent responses and memory
- Compare campaign strategies side-by-side

### 📤 Export Tools
- Export by platform, agent, or section
- Download options: Markdown, PDF, CSV

### 🛠️ Memory + History
- Conversational memory per agent
- Save and reload previous campaigns and drafts

---

## 🧠 AI Agents

| Agent | Role | Responsibilities |
|-------|------|------------------|
| `Zara` | 🎨 Creative Strategist | Hooks, emotional angles, story arcs |
| `Max`  | ✍️ Content Architect  | Writes Tweets, Blogs, Posts |
| `Mira` | 📊 Research Analyst    | Audience insights, trends, best times |
| `Eva`  | 🔍 Critic & Challenger | Critiques and rewrites with scores |
| `Leo`  | 🛡️ Brand Guardian     | Checks tone, consistency, branding |

---

## 🧰 Technologies Used

- **💬 LLM Orchestration**: [LangChain](https://github.com/langchain-ai/langchain)
- **📦 Local LLM Hosting**: [Ollama](https://ollama.com/)
- **🎛️ UI Framework**: [Streamlit](https://streamlit.io/)
- **📊 Visualization**: Plotly, Altair, Pandas
- **📄 PDF Exports**: ReportLab, FPDF
- **📋 Clipboard**: Pyperclip

---

## 🧠 LLMs Supported

Ghostwriter Teams runs **entirely locally** using models hosted via **Ollama**.

✅ Compatible models:
- `llama2` (default)
- `mistral`
- `gemma`
- `codellama`
- Any other Ollama-supported chat models

> You can switch models via environment variable:  
`LLM_MODEL=mistral streamlit run app.py`

---

## 🧱 System Architecture

```text
User ↔ Streamlit UI
           ↓
     AgentManager (LangChain)
     ↙        ↓        ↘
Zara    Max    Mira   Eva   Leo
 ↘       ↘      ↘     ↘     ↘
LangChain  →  ChatOllama (local model)
           ↘
     Memory + Prompt Templates
