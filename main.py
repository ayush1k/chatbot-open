import streamlit as st
from openai import OpenAI

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
    st.session_state.selected_model = "nvidia/nemotron-3-super-120b-a12b:free"
if "is_configured" not in st.session_state:
    st.session_state.is_configured = False

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

    if st.button("Change API Key / Model ID", use_container_width=True):
        st.session_state.is_configured = False
        st.rerun()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

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

    with st.chat_message("assistant"):
        # We use a placeholder to stream the text chunk by chunk
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Create the API call with streaming enabled
            stream = client.chat.completions.create(
                model=st.session_state.selected_model,
                messages=st.session_state.messages,
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