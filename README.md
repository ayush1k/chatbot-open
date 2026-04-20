# chatbot-open

A simple Streamlit chatbot UI that connects to OpenRouter using the OpenAI Python client.

## What this app does

- Starts a local chat interface in Streamlit
- Shows a setup screen first to enter your OpenRouter API key and model ID
- Opens the chat page after setup, with quick controls to change credentials and clear chat
- Sends your messages to the configured OpenRouter model
- Streams model responses in real time

## Prerequisites

- Python 3.10+
- An OpenRouter API key

## Setup (virtual environment + install libraries)

Run these commands from the project root.

```bash
# 1) Create a Python virtual environment
python3 -m venv .venv

# 2) Activate the virtual environment
source .venv/bin/activate

# 3) Upgrade pip (recommended)
python -m pip install --upgrade pip

# 4) Install required libraries
pip install streamlit openai
```

## Run the app

Use this command after the virtual environment is activated:

```bash
streamlit run main.py
```

Then open the local URL shown in your terminal (usually http://localhost:8501).

## Run with Docker

Build the image from the project root:

```bash
docker build -t chatbot-open .
```

Run the container and expose Streamlit on port 8501:

```bash
docker run --rm -p 8501:8501 chatbot-open
```

Then open http://localhost:8501 in your browser.

## How to use

1. Launch the app and enter your OpenRouter API key.
2. Enter the OpenRouter model ID you want to use (for example, `nvidia/nemotron-3-super-120b-a12b:free`).
3. Click **Start Chat** to open the chat page.
4. Type a message in the chat box and press Enter.
5. Use **Change API Key / Model ID** in the sidebar whenever you want to update credentials.
6. Use **Clear Chat** in the sidebar to reset conversation history.

## Troubleshooting

- If `streamlit` is not found, your virtual environment is likely not activated. Run:

```bash
source .venv/bin/activate
```

- If you get API errors, confirm your OpenRouter key is valid and has access to the model ID you entered.
