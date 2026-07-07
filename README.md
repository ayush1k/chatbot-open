# chatbot-open

A modern, lightweight Streamlit chatbot UI that connects to OpenRouter using the OpenAI Python client. It features dynamic prompt context loading and sliding-window conversation memory with automated background summarization to keep your API tokens and context size optimized.

## Key Features

- **Quick Credentials Setup**: Configure your OpenRouter API key and desired model ID on first launch.
- **Dynamic Context Injection**: A sidebar text area lets you paste a project's README or files (e.g. source code, API docs) to inject them directly into the system prompt context.
- **Sliding Window Memory**: Keeps the active chat payload short and fast by maintaining a maximum of 10 messages in the active memory buffer.
- **Background Conversational Summarization**: Whenever message history exceeds the buffer limit, the oldest message pair is evicted and summarized in the background, updating a running technical summary. This summary is injected back into the LLM context to ensure no long-term memory is lost.
- **Real-Time Streaming**: Outputs responses dynamically chunk-by-chunk for a responsive user experience.
- **Sidebar Actions**: Switch model credentials or clear chat history and summaries instantly.

## Prerequisites

- Python 3.10+
- An OpenRouter API key

## Setup (Virtual Environment + Installation)

Run these commands from the project root:

```bash
# 1) Create a Python virtual environment
python3 -m venv .venv

# 2) Activate the virtual environment
source .venv/bin/activate

# 3) Upgrade pip (recommended)
python -m pip install --upgrade pip

# 4) Install required libraries
pip install -r requirements.txt
```

## Running the App

Run the following command while the virtual environment is active:

```bash
streamlit run main.py
```

Then open the local URL shown in your terminal (usually `http://localhost:8501`).

## Running with Docker

Build the Docker image from the project root:

```bash
docker build -t chatbot-open .
```

Run the container and expose Streamlit on port `8501`:

```bash
docker run --rm -p 8501:8501 chatbot-open
```

Then navigate to `http://localhost:8501` in your browser.

## How to Use

1. **Configure Credentials**: Enter your OpenRouter API key and model ID (for example, the default `nvidia/nemotron-3-ultra-550b-a55b:free` or other choices such as `google/gemini-2.5-flash`). You can find model IDs on the [OpenRouter Models page](https://openrouter.ai/models).
2. **Launch Chat**: Click **Start Chat** to enter the main messaging workspace.
3. **Set Project Context (Optional)**: Paste any relevant code files or documentation under **Project README Context** in the sidebar. This guides the assistant's domain knowledge.
4. **Chat**: Type a message in the chat box and press Enter.
5. **Manage History**: Use the sidebar buttons to change credentials or reset the current conversation state.

## Troubleshooting

- **Command Not Found (`streamlit`)**: Make sure you have activated your virtual environment before running the command:
  ```bash
  source .venv/bin/activate
  ```
- **API Errors / Key Authentication**: Verify that your OpenRouter API key has sufficient credits and has permissions to call the requested model ID. You can test with a free-tier model (e.g. models ending in `:free`).
