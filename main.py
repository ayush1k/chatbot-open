import streamlit as st
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(page_title="My Local AI Chat", page_icon="🤖")
st.title("My Local AI Chat 🤖")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    # Input for OpenRouter API Key
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    # Dropdown to select models
    selected_model = st.selectbox(
        "Choose a Model",
        [
            "nvidia/nemotron-3-super-120b-a12b:free",
        ]
    )
    st.markdown("[Find more model IDs on OpenRouter](https://openrouter.ai/models)")

# 3. Initialize Chat History
# Streamlit re-runs the script from top to bottom on every interaction.
# We use st.session_state to remember the chat history between re-runs.
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Past Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle User Input
if prompt := st.chat_input("What's on your mind?"):
    
    # Stop if no API key is provided
    if not api_key:
        st.info("Please add your OpenRouter API key in the sidebar to continue.")
        st.stop()

    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. Call OpenRouter and Stream the Response
    # Initialize the client pointing to OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    with st.chat_message("assistant"):
        # We use a placeholder to stream the text chunk by chunk
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Create the API call with streaming enabled
            stream = client.chat.completions.create(
                model=selected_model,
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

    # 7. Save Assistant Response to History
    st.session_state.messages.append({"role": "assistant", "content": full_response})