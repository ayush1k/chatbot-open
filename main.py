import re
import streamlit as st
from openai import OpenAI

# Developer Persona Instructions
DEV_MODES = {
    "Default Assistant": "You are an expert software developer.",
    "Bug Hunter": "Focus strictly on root-cause analysis, call-stack tracking, and edge cases. Provide minimal fixes and do not rewrite unchanged code blocks.",
    "Architect": "Focus on design patterns, modular code structures, scalability, and clean directory layouts instead of immediately writing low-level logic."
}

def extract_workspace_code():
    extracted_blocks = []
    code_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                matches = code_pattern.findall(msg["content"])
                for match in matches:
                    extracted_blocks.append(match.strip())
    if not extracted_blocks:
        return ""
    return "\n\n---\n\n".join(extracted_blocks)

# 1. Page Configuration
st.set_page_config(page_title="My Local AI Chat", page_icon="🤖")
st.title("My Local AI Chat 🤖")

# 2. Initialize App State
# Streamlit re-runs the script from top to bottom on every interaction.
# We use st.session_state to remember the chat history between re-runs.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
if "is_configured" not in st.session_state:
    st.session_state.is_configured = False
if "chat_summary" not in st.session_state:
    st.session_state.chat_summary = ""
if "readme_context" not in st.session_state:
    st.session_state.readme_context = ""
if "developer_mode" not in st.session_state:
    st.session_state.developer_mode = "Default Assistant"

# 3. Credentials Screen (shown first)
if not st.session_state.is_configured:
    st.subheader("Setup")
    st.write("Enter your OpenRouter API key and model ID to start chatting.")

    with st.form("credentials_form"):
        api_key_input = st.text_input(
            "OpenRouter API Key",
            value=st.session_state.api_key,
            type="password",
        )
        model_input = st.text_input(
            "OpenRouter Model ID",
            value=st.session_state.selected_model,
            help="Paste the exact model ID from OpenRouter (e.g. openai/gpt-4o-mini).",
        )
        st.markdown("[Find model IDs on OpenRouter](https://openrouter.ai/models)")
        submitted = st.form_submit_button("Start Chat")

    if submitted:
        if not api_key_input.strip():
            st.error("API key is required.")
            st.stop()
        if not model_input.strip():
            st.error("Model ID is required.")
            st.stop()

        st.session_state.api_key = api_key_input.strip()
        st.session_state.selected_model = model_input.strip()
        st.session_state.is_configured = True
        st.rerun()

    st.stop()

# 4. Chat Page Controls
with st.sidebar:
    st.header("Session")
    st.caption(f"Model: {st.session_state.selected_model}")

    # Developer Mode Selectbox
    selected_mode = st.selectbox(
        "Developer Mode",
        options=list(DEV_MODES.keys()),
        index=list(DEV_MODES.keys()).index(st.session_state.developer_mode)
    )
    st.session_state.developer_mode = selected_mode

    if st.button("Change API Key / Model ID", use_container_width=True):
        st.session_state.is_configured = False
        st.rerun()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_summary = ""
        st.rerun()

    # Active Working Memory Telemetry Expander
    with st.expander("Active Working Memory", expanded=True):
        st.write(f"**Messages in Buffer:** {len(st.session_state.messages)}")
        st.text_area(
            "Conversation Summary",
            value=st.session_state.chat_summary if st.session_state.chat_summary else "(No summary generated yet)",
            height=150,
            disabled=True,
            help="This summary is updated in the background as older messages are evicted."
        )

    # Export Generated Code Button
    compiled_code = extract_workspace_code()
    if compiled_code:
        st.download_button(
            label="Export Generated Code",
            data=compiled_code,
            file_name="workspace_export.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.download_button(
            label="Export Generated Code",
            data="",
            file_name="workspace_export.md",
            mime="text/markdown",
            disabled=True,
            help="No code blocks found in the chat history to export.",
            use_container_width=True
        )

    st.subheader("Context")
    # Text area for project context (supports file tags)
    readme_input = st.text_area(
        "Paste Project Context (supports file tags)",
        value=st.session_state.readme_context,
        height=200,
        help="Paste project files or README. Denote multiple files using '--- START FILE: filename ---' and '--- END FILE ---'."
    )
    st.session_state.readme_context = readme_input

    st.markdown("[Find more model IDs on OpenRouter](https://openrouter.ai/models)")

# 5. Display Past Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Handle User Input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7. Call OpenRouter and Stream the Response
    # Initialize the client pointing to OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.session_state.api_key,
    )

    # Construct the dynamic payload combining developer_mode instruction, readme_context, and chat_summary
    system_parts = []
    
    # Prepend the developer mode persona at the very top of the system prompt
    persona_instruction = DEV_MODES.get(st.session_state.developer_mode, DEV_MODES["Default Assistant"])
    system_parts.append(persona_instruction)
    
    if st.session_state.readme_context:
        context_instruction = (
            "The provided context may contain multiple files. "
            "Files will be denoted by the syntax '--- START FILE: filename ---' and '--- END FILE ---'. "
            "Treat these as distinct files in the project structure.\n\n"
            f"Project context:\n{st.session_state.readme_context}"
        )
        system_parts.append(context_instruction)
    if st.session_state.chat_summary:
        system_parts.append(f"Summary of previous conversation:\n{st.session_state.chat_summary}")

    system_instruction = "\n\n".join(system_parts)

    payload = [{"role": "system", "content": system_instruction}]
    payload.extend(st.session_state.messages)

    with st.chat_message("assistant"):
        # We use a placeholder to stream the text chunk by chunk
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Create the API call with streaming enabled
            stream = client.chat.completions.create(
                model=st.session_state.selected_model,
                messages=payload,
                stream=True, 
            )
            
            # Update the UI as chunks arrive
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Remove the cursor block when done
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "Sorry, I ran into an error."

    # 8. Save Assistant Response to History
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 9. Sliding Window & Summarization Logic
    MAX_MESSAGES = 10
    if len(st.session_state.messages) > MAX_MESSAGES:
        # Extract the oldest user-assistant message pair
        evicted_pair = st.session_state.messages[:2]
        
        try:
            # Background API call to OpenRouter (non-streaming, hidden from UI)
            current_summary = st.session_state.chat_summary if st.session_state.chat_summary else "(No summary yet)"
            summary_prompt = (
                "You are a technical assistant tasked with maintaining a running summary of a chat conversation.\n\n"
                f"Existing Conversation Summary:\n{current_summary}\n\n"
                "Newly evicted user-assistant message pair to incorporate:\n"
                f"User: {evicted_pair[0]['content']}\n"
                f"Assistant: {evicted_pair[1]['content']}\n\n"
                "Generate a concise, updated technical summary of the conversation based on the existing summary and the new message pair. "
                "Do not include any conversational filler; return ONLY the updated summary."
            )
            
            summary_response = client.chat.completions.create(
                model=st.session_state.selected_model,
                messages=[
                    {"role": "user", "content": summary_prompt}
                ],
                stream=False
            )
            new_summary = summary_response.choices[0].message.content.strip()
            st.session_state.chat_summary = new_summary
        except Exception as summary_err:
            # Log error to stderr/print, keeping it completely hidden from UI
            print(f"Error generating summary: {summary_err}")
        
        # Remove the evicted pair from the main st.session_state.messages list
        st.session_state.messages = st.session_state.messages[2:]
        st.rerun()