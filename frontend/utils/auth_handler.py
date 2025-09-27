
# utils/auth_handler.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from typing import Dict, Optional, Tuple
from utils.api_client import APIClient
from utils.session_manager import SessionManager

class AuthHandler:
    """Handle authentication logic for the Streamlit application"""

    def __init__(self, config_path: str = "config/auth_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.authenticator = self._initialize_authenticator()
        self.api_client = APIClient()

    def _load_config(self) -> Optional[Dict]:
        """Load authentication configuration"""
        try:
            with open(self.config_path) as file:
                return yaml.load(file, Loader=SafeLoader)
        except FileNotFoundError:
            st.error(f"Configuration file not found: {self.config_path}")
            return None
        except Exception as e:
            st.error(f"Failed to load configuration: {e}")
            return None

    def _initialize_authenticator(self) -> Optional[stauth.Authenticate]:
        """Initialize the authenticator object"""
        if not self.config:
            return None

        try:
            return stauth.Authenticate(
                self.config['credentials'],
                self.config['cookie']['name'],
                self.config['cookie']['key'],
                self.config['cookie']['expiry_days']
            )
        except Exception as e:
            st.error(f"Failed to initialize authenticator: {e}")
            return None

    def render_login(self) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
        """Render login widget and return authentication status"""
        if not self.authenticator:
            return None, None, None

        try:
            return self.authenticator.login('Login', 'main')
        except Exception as e:
            st.error(f"Login error: {e}")
            return None, False, None

    def render_logout(self, location: str = 'sidebar') -> None:
        """Render logout button"""
        if self.authenticator and st.session_state.get('authentication_status'):
            try:
                self.authenticator.logout('Logout', location)
            except Exception as e:
                st.error(f"Logout error: {e}")

    def render_registration(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Render user registration widget"""
        if not self.authenticator:
            return None, None, None

        try:
            return self.authenticator.register_user(
                'Register user', 
                'main',
                pre_authorized=self.config.get('pre-authorized', {}).get('emails', [])
            )
        except Exception as e:
            st.error(f"Registration error: {e}")
            return None, None, None

    def render_reset_password(self) -> bool:
        """Render reset password widget for logged-in users"""
        if not self.authenticator or not st.session_state.get('authentication_status'):
            return False

        try:
            return self.authenticator.reset_password(
                st.session_state.get('username'),
                'Reset password'
            )
        except Exception as e:
            st.error(f"Reset password error: {e}")
            return False

    def render_forgot_password(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Render forgot password widget"""
        if not self.authenticator:
            return None, None, None

        try:
            return self.authenticator.forgot_password('Forgot password', 'main')
        except Exception as e:
            st.error(f"Forgot password error: {e}")
            return None, None, None

    def render_forgot_username(self) -> Tuple[Optional[str], Optional[str]]:
        """Render forgot username widget"""
        if not self.authenticator:
            return None, None

        try:
            return self.authenticator.forgot_username('Forgot username', 'main')
        except Exception as e:
            st.error(f"Forgot username error: {e}")
            return None, None

    def update_user_details(self) -> bool:
        """Render update user details widget"""
        if not self.authenticator or not st.session_state.get('authentication_status'):
            return False

        try:
            return self.authenticator.update_user_details(
                st.session_state.get('username'),
                'Update user details'
            )
        except Exception as e:
            st.error(f"Update user details error: {e}")
            return False

    def save_config(self) -> bool:
        """Save configuration changes"""
        if not self.config:
            return False

        try:
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            return True
        except Exception as e:
            st.error(f"Failed to save configuration: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authentication_status', False)

    def get_user_info(self) -> Dict[str, any]:
        """Get current user information"""
        if not self.is_authenticated():
            return {}

        return {
            'username': st.session_state.get('username'),
            'name': st.session_state.get('name'),
            'authentication_status': st.session_state.get('authentication_status'),
            'roles': st.session_state.get('roles', [])
        }

    def has_role(self, role: str) -> bool:
        """Check if current user has a specific role"""
        user_roles = st.session_state.get('roles', [])
        return role in user_roles if isinstance(user_roles, list) else False

    def logout_user(self) -> None:
        """Programmatically logout user and clear session"""
        if self.authenticator:
            try:
                self.authenticator.logout('Logout', 'unrendered')
                SessionManager.clear_session()
            except Exception as e:
                st.error(f"Logout failed: {e}")
