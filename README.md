🤖 Project Jarvis 2.0: A Deterministic, Schema-Enforced Windows OS AI Agent
Project Jarvis 2.0 transforms your computer into a remote-controlled AI workstation via a secure Telegram Bot interface. Leveraging the Gemini 2.5 Flash SDK, this project moves past brittle string-matching and implements strict Pydantic schema tool-calling alongside Multimodal Vision, allowing an LLM to predictably navigate and manipulate a live Windows host environment.

🌟 Key Architectural Features
0.0 Temperature Determinism: Strips the model of creative variance, forcing precise execution matching against specific programmatic boundaries.

Manual Function Routing (AFC: Disabled): Bypasses the SDK's default Automatic Function Calling loop to gain absolute control over transaction timing and eliminate 429 Too Many Requests free-tier rate limits.

Decoupled Configuration: Complete segregation of system runtime configurations from credentials via a zero-leak environment pipeline (.env & config.py).

User Identity Gating: A hardcoded, low-level authentication gate matching incoming payload signatures against a strict ALLOWED_USER_ID registry.

🛠️ System Architecture
The blueprint decouples the execution loop from the individual tool interfaces, allowing developers to easily add new subsystems without touching the core orchestration engine:
```python
[ Telegram Client ] 
                │ (Secure User ID Check)
                ▼
       [ jarvis.py (Core Engine) ] ◄───► [ config.py (.env Pipeline) ]
                │
                ├─► types.FunctionDeclaration (Strict Blueprints)
                │
                ▼
  ┌────────────────────────────────────────────────────────┐
  │         JARVIS PHYSICAL TOOL BELT SUB SYSTEMS          │
  ├───────────────────┬──────────────────┬─────────────────┤
  │  System Utilities │   Screen/Vision  │  Active UI Sync │
  │  (Volume, Cmd)    │  (pyautogui Engine)│  (pygetwindow)│
  └───────────────────┴──────────────────┴─────────────────┘
```
📦 Local Installation Guide
1. Clone & Environment Set Up
Ensure your development workspace isolates dependencies securely:
```
git clone https://github.com/yourusername/ProjectJarvis.git
cd ProjectJarvis
python -m venv .venv
source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate
pip install google-genai python-telegram-bot pyautogui pygetwindow pydantic pillow python-dotenv
```

2. Configure Local Environment Variables
Create a hidden .env file in the root directory:
```
JARVIS_TELEGRAM_TOKEN=YOUR_BOT_FATHER_TOKEN
JARVIS_GEMINI_API_KEY=YOUR_AI_STUDIO_KEY
JARVIS_ALLOWED_USER_ID=YOUR_NUMERIC_TELEGRAM_ID
```

3. Initialize the Workstation
```
python jarvis.py
```

📊 Live Execution Trace (Deterministic Validation):
When a command is transmitted, the system registers the user payload, 
executes a single-turn model resolution, handles state extraction cleanly via the Pydantic interface schema, 
and initiates synchronous processing loops without falling back into runaway multi-turn server pools:

```
Jarvis 2.0 is online. Next-gen tool routing active...
2026-07-04 21:19:06,391 - httpx - INFO - HTTP Request: POST .../getMe "HTTP/1.1 200 OK"
2026-07-04 21:19:06,577 - telegram.ext.Application - INFO - Application started
2026-07-04 21:19:21,144 - root - INFO - Jarvis received next-gen request: Take another screenshot
2026-07-04 21:19:22,025 - httpx - INFO - HTTP Request: POST .../generateContent "HTTP/1.1 200 OK"
2026-07-04 21:19:22,025 - root - INFO - Gemini invoked tool strictly: take_screenshot with args: {}
2026-07-04 21:19:24,387 - httpx - INFO - HTTP Request: POST .../sendPhoto "HTTP/1.1 200 OK"
```
