# 👥 Ghostwriter Teams

> An AI-powered creative marketing workspace — driven by multi-agent collaboration, local LLMs, and real-time strategy generation.
> Instead of a single AI assistant, Ghostwriter Teams gives you **5 specialized AI agents**, each with a unique personality, tone, and strategic purpose. They interact with each other (and the user) to simulate dynamic, intelligent brainstorms — resulting in more original, well-rounded, and deeply personalized outputs.

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

## 👥 The Team: Agent Personas

| Agent | Role | Personality | Primary Tasks |
|-------|------|-------------|----------------|
| **Zara** | Creative Strategist | Bold, visionary, campaign-minded | Campaign ideas, emotional hooks, storytelling angles |
| **Max** | Content Architect | Fast, witty, pragmatic | Writes content (tweets, blogs, emails, captions) |
| **Mira** | Research Analyst | Calm, data-driven, insightful | Brings in trends, competitors, audience insights |
| **Eva** | Challenger & Critic | Honest, sharp, no-BS | Critiques, rewrites, challenges weak ideas |
| **Leo** | Brand Guardian | Thoughtful, consistent, classy | Maintains voice, tone, and message alignment |

---

## 🧠 How It Works

1. The user submits a request (e.g., "Help me launch my AI journaling app").
2. The 5 agents process the input independently, using their specialized roles.
3. They respond in a **Slack-style threaded interface**, giving diverse perspectives.
4. They can **respond to each other**, creating a collaborative debate.
5. Final output includes:  
   - Content assets (tweet thread, blog, landing page copy)  
   - Campaign concept and structure  
   - Brand review and suggested tone edits  
   - Research-informed insights or warnings  
   - Critique and sharpened phrasing


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
## Screenshots
1. ![GW Content Calendar](Assets/GW-content%20calender.png)
   
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


