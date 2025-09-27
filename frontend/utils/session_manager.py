
# utils/session_manager.py
import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import json

class SessionManager:
    """Manage Streamlit session state for the chatbot application"""

    @staticmethod
    def initialize_session():
        """Initialize all required session state variables"""
        defaults = {
            "messages": [],
            "chat_history": [],
            "current_conversation_id": None,
            "user_id": None,
            "search_results": [],
            "user_preferences": {
                "search_engine": "Google",
                "max_search_results": 5,
                "ai_model": "GPT-4",
                "response_length": 3,
                "theme": "light"
            },
            "jwt_token": None,
            "last_activity": datetime.now().isoformat(),
            "conversation_count": 0
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def clear_session():
        """Clear all session data"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]

    @staticmethod
    def update_user_preferences(preferences: Dict[str, Any]):
        """Update user preferences in session"""
        if "user_preferences" not in st.session_state:
            st.session_state.user_preferences = {}

        st.session_state.user_preferences.update(preferences)

    @staticmethod
    def get_user_preference(key: str, default: Any = None) -> Any:
        """Get a user preference value"""
        return st.session_state.get("user_preferences", {}).get(key, default)

    @staticmethod
    def add_message(role: str, content: str, **kwargs):
        """Add a message to the current conversation"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }

        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.session_state.messages.append(message)

    @staticmethod
    def clear_current_conversation():
        """Clear the current conversation"""
        st.session_state.messages = []
        st.session_state.current_conversation_id = None
        st.session_state.search_results = []

    @staticmethod
    def update_last_activity():
        """Update the last activity timestamp"""
        st.session_state.last_activity = datetime.now().isoformat()

    @staticmethod
    def is_session_expired(hours: int = 24) -> bool:
        """Check if the session has expired"""
        if "last_activity" not in st.session_state:
            return True

        try:
            last_activity = datetime.fromisoformat(st.session_state.last_activity)
            return datetime.now() - last_activity > timedelta(hours=hours)
        except:
            return True

    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """Get session statistics"""
        return {
            "total_messages": len(st.session_state.get("messages", [])),
            "conversation_count": len(st.session_state.get("chat_history", [])),
            "current_conversation_id": st.session_state.get("current_conversation_id"),
            "user_id": st.session_state.get("user_id"),
            "last_activity": st.session_state.get("last_activity"),
            "is_authenticated": st.session_state.get("authentication_status", False)
        }

    @staticmethod
    def export_session_data() -> str:
        """Export session data as JSON string"""
        export_data = {
            "messages": st.session_state.get("messages", []),
            "chat_history": st.session_state.get("chat_history", []),
            "user_preferences": st.session_state.get("user_preferences", {}),
            "export_timestamp": datetime.now().isoformat()
        }

        return json.dumps(export_data, indent=2, ensure_ascii=False)

    @staticmethod
    def import_session_data(json_data: str) -> bool:
        """Import session data from JSON string"""
        try:
            data = json.loads(json_data)

            if "messages" in data:
                st.session_state.messages = data["messages"]
            if "chat_history" in data:
                st.session_state.chat_history = data["chat_history"]
            if "user_preferences" in data:
                st.session_state.user_preferences.update(data["user_preferences"])

            return True
        except Exception as e:
            st.error(f"Failed to import session data: {e}")
            return False
