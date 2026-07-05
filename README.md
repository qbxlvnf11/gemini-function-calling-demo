# Native Function Calling Chatbot Demo

This project is a test/demo application designed to overcome the limitations of traditional string concatenation-based chatbots by implementing Google Gemini's **Native Function Calling** architecture.

## 🚀 Features

1. **Native Tool Calling Architecture (Loop System)**
   - Conversation history is managed not as simple strings, but as strict JSON-based `contents` arrays.
   - When the LLM outputs a `function_call`, the backend executes the corresponding logic and returns a `function_response`, automatically triggering a loop to recall the LLM (`backend/agent/engine.py`).

2. **State-of-the-Art Intent Routing & Dynamic Tool Selection (Dispatcher)**
   - Instead of blindly injecting all tools into the prompt, the system analyzes the user's intent to **dynamically inject only the required tool schemas** (`backend/agent/dispatcher.py`).
   - This is a modern agent design pattern that prevents token waste and mitigates hallucinations.

3. **Ultra-Fast Response Optimization (WebSockets)**
   - Utilizes FastAPI's WebSockets to maintain a continuous connection between the client and server.
   - Status messages like "Searching...", "Execution Complete" are instantly streamed to the frontend during tool execution, significantly reducing perceived latency.

4. **Agentic Self-Correction**
   - If an error occurs in an API or tool, the LLM reads the error message, automatically corrects its parameters, and retries the execution. This ensures strong resilience against format mismatches.

5. **Real-time Streaming**
   - The UI doesn't wait for the entire response to be generated. Text is smoothly rendered on the UI with a typing effect as soon as it is generated.

6. **Agentic State Tracking Dashboard (Live Customer Ticket)**
   - Going beyond simple Q&A, the LLM actively tracks the customer's Intent, Order Number, Urgency, etc., and updates the right-side dashboard in real-time.

7. **Router Configuration (Dynamic LLM Selection)**
   - Through the Settings tab, you can freely change not only the main conversational LLM but also the dedicated Router LLM model used for intent classification and tool selection.

8. **Perfect Separation of Concerns (Clean Architecture)**
   - The router (API), agent loop logic (Agent), and backend business logic (Tools) are strictly separated into different directories.

9. **Premium UI/UX Design**
   - Provides a high-quality frontend environment featuring Glassmorphism, smooth micro-animations, and a modern dark theme.

---

## 🛠 Directory Structure

```text
gemini-function-calling-demo/
├── .env                       # Environment variables (GCP and Gemini Auth)
├── requirements.txt           # Python dependencies
├── backend/
│   ├── main.py                # FastAPI entry point (Web server)
│   ├── api/
│   │   └── chat_router.py     # WebSocket connection and message routing
│   ├── agent/
│   │   ├── engine.py          # Gemini multi-turn session & Function Calling loop
│   │   ├── dispatcher.py      # User intent classification & dynamic toolset allocation
│   │   ├── schemas.py         # Data schemas
│   │   └── prompts.py         # System prompt separation
│   ├── tools/
│   │   ├── manual_tools.py    # Mock DB policy search and order status logic
│   │   └── tool_registry.py   # Gemini schema declarations and Python function mapping
│   └── core/
│       └── config.py          # Configuration loader
└── frontend/
    ├── index.html             # Chat main layout UI
    ├── css/style.css          # Premium dark theme styling
    └── js/app.js              # WebSocket logic and state updates
```

---

## 💻 How to Run

### 1. Environment Setup & API Key Registration
Navigate to the project directory, create a Conda virtual environment, and install dependencies.

```bash
# Navigate to the directory
cd gemini-function-calling-demo

# Create .env file and enter API key
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```
*(Note: All environment variables are strictly managed in `.env` to prevent hardcoding absolute paths or exposing API keys in the source code.)*

```bash
# Create Anaconda virtual environment (e.g., Python 3.10)
conda create -n gemini-demo python=3.10 -y

# Activate virtual environment
conda activate gemini-demo

# Install packages
pip install -r requirements.txt
```

### 2. Run the Server
Start the FastAPI backend server with the virtual environment activated.
```bash
# If the virtual environment is not activated: conda activate gemini-demo
python -m backend.main
```
If the server starts successfully, you will see a message like `Uvicorn running on http://0.0.0.0:8001`.

### 3. Connect & Test
Open your web browser and navigate to:
👉 **http://localhost:8001**

**Example Test Prompts:**
- "Tell me the refund policy" (Tests Policy Tool routing)
- "I'm so angry because my item hasn't arrived. My order number is 123." (Demonstrates Agentic Self-Correction and Live State Tracking updates)

Real-time typing streaming will proceed in the left chat window, while the right dashboard will blink and update the customer's ticket state extracted by the AI. You can also transparently inspect the raw JSON of all tool executions and self-correction processes in the "Logs" tab.