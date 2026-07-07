import streamlit as st

MAX_MESSAGES = 10

def initialize_state():
    """
    Initialize all session state keys needed for the application.
    """
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

def clear_chat():
    """
    Clears the active chat messages and summary.
    """
    st.session_state.messages = []
    st.session_state.chat_summary = ""

def manage_memory(client, model_id: str):
    """
    Enforces the MAX_MESSAGES sliding window on st.session_state.messages.
    If the threshold is exceeded, the oldest user-assistant pair is evicted
    and summarized in the background using the OpenRouter client.
    """
    if len(st.session_state.messages) > MAX_MESSAGES:
        evicted_pair = st.session_state.messages[:2]
        
        try:
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
                model=model_id,
                messages=[
                    {"role": "user", "content": summary_prompt}
                ],
                stream=False
            )
            new_summary = summary_response.choices[0].message.content.strip()
            st.session_state.chat_summary = new_summary
        except Exception as summary_err:
            print(f"Error generating summary: {summary_err}")
            
        st.session_state.messages = st.session_state.messages[2:]
        st.rerun()
