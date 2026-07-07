import streamlit as st
from core.memory_manager import initialize_state, clear_chat, manage_memory
from core.api import get_openai_client, assemble_payload, stream_chat_completion
from utils.exporter import extract_workspace_code

# Developer Persona Instructions
DEV_MODES = {
    "Default Assistant": "You are an expert software developer.",
    "Bug Hunter": "Focus strictly on root-cause analysis, call-stack tracking, and edge cases. Provide minimal fixes and do not rewrite unchanged code blocks.",
    "Architect": "Focus on design patterns, modular code structures, scalability, and clean directory layouts instead of immediately writing low-level logic."
}

# 1. Page Configuration
st.set_page_config(page_title="My Local AI Chat", page_icon="🤖")
st.title("My Local AI Chat 🤖")

# 2. Initialize App State
initialize_state()

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
        clear_chat()
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
    compiled_code = extract_workspace_code(st.session_state.messages)
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
    client = get_openai_client(st.session_state.api_key)

    # Construct the dynamic payload
    payload = assemble_payload(
        developer_mode=st.session_state.developer_mode,
        dev_modes_dict=DEV_MODES,
        readme_context=st.session_state.readme_context,
        chat_summary=st.session_state.chat_summary,
        messages=st.session_state.messages
    )

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream the response chunks from our api helper
            response_chunks = stream_chat_completion(
                client=client,
                model_id=st.session_state.selected_model,
                payload=payload
            )
            for chunk in response_chunks:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "Sorry, I ran into an error."

    # 8. Save Assistant Response to History
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 9. Sliding Window & Summarization Logic
    manage_memory(client=client, model_id=st.session_state.selected_model)