# Ghostwriter Teams – Your AI Creative Department

Ghostwriter Teams is a multi-agent AI platform where distinct AI personas collaborate to generate high-quality creative content, strategy, and brand storytelling — just like a real-world team.

It’s designed for creators, solo founders, startups, and marketers who want the power of a creative department without the cost, delay, or burnout.

---

## ✨ Core Concept

Instead of a single AI assistant, Ghostwriter Teams gives you **5 specialized AI agents**, each with a unique personality, tone, and strategic purpose. They interact with each other (and the user) to simulate dynamic, intelligent brainstorms — resulting in more original, well-rounded, and deeply personalized outputs.

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

## ⚙️ Tech Stack Overview

| Layer | Tool / Framework |
|-------|------------------|
| **Frontend** | Streamlit (for MVP UI) |
| **Agent Framework** | LangChain or CrewAI (for agent behavior orchestration) |
| **LLM API** | OpenAI GPT-4 Turbo (or Claude 3) |
| **Vector Store** | Chroma or Pinecone (for agent memory + RAG) |
| **Data Retrieval** | LangChain Tools / SerpAPI / PDF ingestion (optional) |
| **Deployment** | Streamlit Sharing / HuggingFace Spaces / Replit (for MVP) |

---

## 🚀 MVP Goals

- [ ] Set up Streamlit app with agent response interface
- [ ] Define basic prompt templates for all 5 agents
- [ ] Add GPT-4 or Claude API integration
- [ ] Simulate team brainstorm with distinct agent replies
- [ ] Visualize each agent’s message in a unique color block
- [ ] Enable basic user input memory (simple context store)
- [ ] Deploy app publicly for demo/testing

---

## 💡 Sample User Input Scenarios

> “I’m launching an AI productivity tool for Gen Z freelancers. Help me plan the launch and create content.”

> “Give me a blog post outline and social captions for a course on personal branding.”

> “Critique this product description and rewrite it in a more confident tone.”

---

## 🔍 Why This Matters

Ghostwriter Teams introduces a **new interface paradigm** for creative work:
- **Multi-agent thinking** creates better results than single AI prompts
- **Personalities** make users feel connected to the tool
- **Collaborative reasoning** mimics real-world team dynamics
- **Modular agent design** lets users eventually swap or train their own agents

---

## ✍️ Future Features (Post-MVP)

- Agent memory and long-term learning (per user/project)
- Customizable agents (tone, goals, knowledge)
- Shareable agent conversations as case studies
- Chrome extension for content drafting in real time
- API for integration into Notion, Slack, email

---

## ✅ Status

> Currently in active development (MVP phase).  
> AI agents operate independently using OpenAI API.  
> UI is in Streamlit with chat-based interface.

---

## 📁 File Structure (Proposed)

ghostwriter-teams/ │ ├── app.py # Main Streamlit app ├── agents/ │ ├── zara.py # Creative Strategist logic │ ├── max.py # Content Architect logic │ ├── mira.py # Trend Researcher logic │ ├── eva.py # Critic logic │ └── leo.py # Brand Guardian logic ├── prompts/ │ └── agent_prompts.json # All agent personas and prompt templates ├── utils/ │ └── memory.py # Context storage (optional) ├── requirements.txt └── README.md


---

## 🧠 Built With the Help of:

- [Cursor](https://cursor.sh) – AI-powered coding assistant  
- [OpenAI](https://openai.com) – LLM for agent dialogue  
- [LangChain](https://www.langchain.com) – Agent orchestration  
- [Streamlit](https://streamlit.io) – MVP UI  
- [ChromaDB](https://www.trychroma.com/) – Lightweight vector memory

---

## 🧩 Contribution

This project welcomes collaborators in:
- Prompt design
- Agent logic
- LLM optimization
- Design / UX
- Product feedback

Let’s co-build the future of AI teams.

---

## 📫 Contact

> Creator: [Your Name]  
> Twitter / LinkedIn: [Your Handle]  
> Email: [Your Email]

---

