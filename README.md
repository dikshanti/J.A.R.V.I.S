# J.A.R.V.I.S. – AI Workflow Automation Assistant

**Voice-controlled AI assistant** that interprets natural language commands and executes real‑world actions on a Windows machine. Built to demonstrate **advanced prompt engineering, multi‑turn LLM conversation design, and AI‑assisted workflow automation** using locally hosted LLaMA 3 via Ollama.

> *“Hey Jarvis, set the RGB to purple.”*  
> *“Fan mode to silent.”*  
> *“Open VS Code.”*

All executed within a sub‑second response, without touching the keyboard.

---

## 🔧 Why This Project?

Most “AI assistant” demos stop at canned responses. J.A.R.V.I.S. proves that **a well‑engineered prompt chain + a local LLM can replace repetitive desktop workflows** — saving time, reducing context switching, and enabling hands‑free operation.

This project was built to:

- **Design and iterate high‑quality prompts** for intent classification, entity extraction, and action routing.
- **Chain multiple LLM calls** (wake‑word detection → intent parsing → command validation → confirmation) in a stateful, multi‑turn loop.
- **Integrate LLM reasoning with real system APIs** (display settings, RGB lighting, fan profiles, application launching).
- **Handle edge cases and fallbacks gracefully** — ambiguous input, timeouts, and unrecognized commands.

---

## 🧠 Prompt Engineering Highlights

### 1. Intent Parsing Chain
A single prompt is rarely enough. J.A.R.V.I.S. uses a **three‑stage prompt pipeline**:

| Stage | Prompt Goal | Example |
|-------|-------------|---------|
| Wake‑word detection | Filter irrelevant speech | `"if 'hey jarvis' in input: enter active mode"` |
| Intent classification | Map command to action category | `"Classify: 'set rgb to red' → category: rgb_control"` |
| Entity extraction | Pull parameters from unstructured text | `"Extract color from 'make my keyboard green': green"` |

### 2. Context Management
Active mode keeps a **short‑term memory window** (60 seconds) so follow‑up commands don’t require re‑stating the wake word. This mirrors production chatbot conversation management.

### 3. Fallback & Recovery
When a command is unclear, the system doesn’t crash — it prompts the user for clarification, mirrors the input back for confirmation, and re‑attempts parsing. This makes the interaction robust, not brittle.

### 4. Ollama Integration
The initial version used local keyword matching, but the architecture is designed to replace `process_command()` with an **Ollama‑powered LLM call** that processes the entire command in one prompt. The prompt template would look like:
