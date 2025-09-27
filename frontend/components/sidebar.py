
# components/sidebar.py
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict
from utils.api_client import APIClient

def render_sidebar():
    """Render the sidebar with chat history and controls"""

    st.sidebar.title("💬 Chat History")

    # New conversation button
    if st.sidebar.button("➕ New Conversation", use_container_width=True):
        start_new_conversation()

    st.sidebar.markdown("---")

    # Display chat history
    display_chat_history()

    # User settings section
    render_user_settings()

def display_chat_history():
    """Display user's chat history"""
    if not st.session_state.chat_history:
        st.sidebar.info("No chat history yet. Start a conversation!")
        return

    st.sidebar.subheader("Recent Conversations")

    # Group conversations by date
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    today_chats = []
    yesterday_chats = []
    this_week_chats = []
    older_chats = []

    for conversation in st.session_state.chat_history:
        try:
            conv_date = datetime.fromisoformat(conversation['timestamp']).date()
            if conv_date == today:
                today_chats.append(conversation)
            elif conv_date == yesterday:
                yesterday_chats.append(conversation)
            elif conv_date >= week_ago:
                this_week_chats.append(conversation)
            else:
                older_chats.append(conversation)
        except:
            older_chats.append(conversation)

    # Display grouped conversations
    if today_chats:
        st.sidebar.markdown("**Today**")
        display_conversation_group(today_chats)

    if yesterday_chats:
        st.sidebar.markdown("**Yesterday**")
        display_conversation_group(yesterday_chats)

    if this_week_chats:
        st.sidebar.markdown("**This Week**")
        display_conversation_group(this_week_chats)

    if older_chats:
        st.sidebar.markdown("**Older**")
        display_conversation_group(older_chats)

def display_conversation_group(conversations: List[Dict]):
    """Display a group of conversations"""
    for conversation in conversations:
        col1, col2 = st.sidebar.columns([4, 1])

        with col1:
            # Conversation button
            if st.button(
                conversation['title'], 
                key=f"conv_{conversation['id']}",
                help=f"Messages: {conversation.get('message_count', 0)}",
                use_container_width=True
            ):
                load_conversation(conversation['id'])

        with col2:
            # Delete conversation button
            if st.button("🗑️", key=f"del_{conversation['id']}", help="Delete conversation"):
                delete_conversation(conversation['id'])

def load_conversation(conversation_id: str):
    """Load a specific conversation"""
    try:
        api_client = APIClient(base_url="http://localhost:8000")
        response = api_client.get_conversation_messages(
            user_id=st.session_state.user_id,
            conversation_id=conversation_id
        )

        if response and response.get('success'):
            st.session_state.messages = response.get('messages', [])
            st.session_state.current_conversation_id = conversation_id
            st.rerun()
        else:
            st.sidebar.error("Failed to load conversation")

    except Exception as e:
        st.sidebar.error(f"Error loading conversation: {e}")

def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        api_client = APIClient(base_url="http://localhost:8000")
        response = api_client.delete_conversation(
            user_id=st.session_state.user_id,
            conversation_id=conversation_id
        )

        if response and response.get('success'):
            # Remove from local chat history
            st.session_state.chat_history = [
                conv for conv in st.session_state.chat_history 
                if conv['id'] != conversation_id
            ]

            # If this was the current conversation, clear it
            if st.session_state.current_conversation_id == conversation_id:
                start_new_conversation()
            else:
                st.rerun()
        else:
            st.sidebar.error("Failed to delete conversation")

    except Exception as e:
        st.sidebar.error(f"Error deleting conversation: {e}")

def start_new_conversation():
    """Start a new conversation"""
    st.session_state.messages = []
    st.session_state.current_conversation_id = None
    st.session_state.search_results = []
    st.rerun()

def render_user_settings():
    """Render user settings section"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Settings")

    # Search settings
    with st.sidebar.expander("🔍 Search Settings"):
        st.selectbox(
            "Search Engine",
            ["Google", "Bing", "DuckDuckGo"],
            key="search_engine",
            help="Choose your preferred search engine"
        )

        st.slider(
            "Max Search Results",
            min_value=3,
            max_value=10,
            value=5,
            key="max_search_results",
            help="Maximum number of search results to fetch"
        )

    # AI settings
    with st.sidebar.expander("🤖 AI Settings"):
        st.selectbox(
            "AI Model",
            ["GPT-4", "GPT-3.5-turbo", "Claude-3"],
            key="ai_model",
            help="Choose AI model for responses"
        )

        st.slider(
            "Response Length",
            min_value=1,
            max_value=5,
            value=3,
            key="response_length",
            help="1=Brief, 5=Detailed"
        )

    # Export/Import
    with st.sidebar.expander("📁 Data Management"):
        if st.button("Export Chat History"):
            export_chat_history()

        uploaded_file = st.file_uploader(
            "Import Chat History",
            type=['json'],
            help="Upload a previously exported chat history file"
        )
        if uploaded_file:
            import_chat_history(uploaded_file)

def export_chat_history():
    """Export chat history as JSON"""
    try:
        import json

        export_data = {
            "user": st.session_state.user_id,
            "export_date": datetime.now().isoformat(),
            "conversations": st.session_state.chat_history,
            "current_messages": st.session_state.messages
        }

        json_string = json.dumps(export_data, indent=2)

        st.sidebar.download_button(
            label="Download Chat History",
            data=json_string,
            file_name=f"chat_history_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

    except Exception as e:
        st.sidebar.error(f"Export failed: {e}")

def import_chat_history(uploaded_file):
    """Import chat history from JSON file"""
    try:
        import json

        data = json.load(uploaded_file)

        if "conversations" in data:
            st.session_state.chat_history = data["conversations"]
            st.sidebar.success("Chat history imported successfully!")
            st.rerun()
        else:
            st.sidebar.error("Invalid file format")

    except Exception as e:
        st.sidebar.error(f"Import failed: {e}")
