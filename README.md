# chatbot-open

A simple Streamlit chatbot UI that connects to OpenRouter using the OpenAI Python client.

## What this app does

- Starts a local chat interface in Streamlit
- Lets you paste your OpenRouter API key in the sidebar
- Sends your messages to the selected OpenRouter model
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

## How to use

1. In the app sidebar, paste your OpenRouter API key.
2. Keep or change the selected model.
3. Type a message in the chat box and press Enter.

## Troubleshooting

- If `streamlit` is not found, your virtual environment is likely not activated. Run:

```bash
source .venv/bin/activate
```

- If you get API errors, confirm your OpenRouter key is valid and has access to the selected model.
