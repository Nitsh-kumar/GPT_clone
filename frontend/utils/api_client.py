
# utils/api_client.py
import requests
import json
from typing import Optional, Dict, List
import streamlit as st

class APIClient:
    """Client for communicating with FastAPI backend"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication if available"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Add JWT token if available
        if hasattr(st.session_state, 'jwt_token'):
            headers["Authorization"] = f"Bearer {st.session_state.jwt_token}"

        return headers

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with backend"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                # Store JWT token
                if 'access_token' in data:
                    st.session_state.jwt_token = data['access_token']
                return data
            else:
                return None

        except Exception as e:
            st.error(f"Authentication failed: {e}")
            return None

    def register_user(self, user_data: Dict) -> Optional[Dict]:
        """Register new user"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 201:
                return response.json()
            else:
                return None

        except Exception as e:
            st.error(f"Registration failed: {e}")
            return None

    def chat_with_search(
        self, 
        user_id: str, 
        message: str, 
        conversation_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Send chat message with web search capabilities"""
        try:
            payload = {
                "user_id": user_id,
                "message": message,
                "conversation_id": conversation_id,
                "search_enabled": True,
                "max_search_results": getattr(st.session_state, 'max_search_results', 5),
                "search_engine": getattr(st.session_state, 'search_engine', 'Google').lower()
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/chat/message",
                json=payload,
                headers=self._get_headers(),
                timeout=120  # Extended timeout for search operations
            )

            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Chat request failed: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            st.error("Request timeout. The server is taking too long to respond.")
            return None
        except Exception as e:
            st.error(f"Chat request failed: {e}")
            return None

    def get_chat_history(self, user_id: str) -> Optional[Dict]:
        """Get user's chat history"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/chat/history/{user_id}",
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            st.error(f"Failed to load chat history: {e}")
            return None

    def get_conversation_messages(
        self, 
        user_id: str, 
        conversation_id: str
    ) -> Optional[Dict]:
        """Get messages for a specific conversation"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/chat/conversation/{conversation_id}",
                headers=self._get_headers(),
                params={"user_id": user_id}
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            st.error(f"Failed to load conversation: {e}")
            return None

    def delete_conversation(
        self, 
        user_id: str, 
        conversation_id: str
    ) -> Optional[Dict]:
        """Delete a conversation"""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/v1/chat/conversation/{conversation_id}",
                headers=self._get_headers(),
                params={"user_id": user_id}
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            st.error(f"Failed to delete conversation: {e}")
            return None

    def search_web(self, query: str, max_results: int = 5) -> Optional[Dict]:
        """Perform web search"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/search/web",
                json={
                    "query": query,
                    "max_results": max_results,
                    "search_engine": getattr(st.session_state, 'search_engine', 'Google').lower()
                },
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            st.error(f"Search failed: {e}")
            return None

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile information"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/users/{user_id}",
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            st.error(f"Failed to load user profile: {e}")
            return None

    def update_user_profile(self, user_id: str, profile_data: Dict) -> Optional[Dict]:
        """Update user profile"""
        try:
            response = self.session.put(
                f"{self.base_url}/api/v1/users/{user_id}",
                json=profile_data,
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            st.error(f"Failed to update profile: {e}")
            return None

    def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
