# main.py - Main Streamlit application with integrated modern login
import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import List, Dict
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from utils.api_client import APIClient
from utils.auth_handler import AuthHandler
from utils.session_manager import SessionManager

# Configure page
st.set_page_config(
    page_title="AI Assistant Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply modern CSS styles with proper Streamlit targeting
st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main app background */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

/* Remove default padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Column styling */
div[data-testid="column"] {
    padding: 0.5rem !important;
}

/* Custom panels */
.info-panel {
    background: linear-gradient(45deg, #2c3e50, #3498db) !important;
    color: white !important;
    padding: 3rem 2rem !important;
    border-radius: 20px !important;
    margin: 0.5rem !important;
    min-height: 500px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2) !important;
}

.login-panel {
    background: white !important;
    border-radius: 20px !important;
    padding: 3rem 2rem !important;
    margin: 0.5rem !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.1) !important;
    min-height: 500px !important;
}

/* Typography */
.info-panel h1 {
    font-size: 2.5rem !important;
    margin-bottom: 1rem !important;
    font-weight: 300 !important;
    color: white !important;
}

.info-panel h2 {
    font-size: 1.8rem !important;
    margin-bottom: 2rem !important;
    color: #ecf0f1 !important;
    font-weight: 300 !important;
}

.form-title {
    text-align: center !important;
    color: #2c3e50 !important;
    font-size: 2rem !important;
    margin-bottom: 2rem !important;
    font-weight: 300 !important;
}

/* Feature items */
.feature-item {
    display: flex !important;
    align-items: center !important;
    margin: 1rem 0 !important;
    font-size: 1.1rem !important;
    color: white !important;
}

.feature-icon {
    font-size: 1.5rem !important;
    margin-right: 1rem !important;
    width: 30px !important;
}

/* Stats */
.stats-container {
    display: flex !important;
    justify-content: space-around !important;
    margin: 2rem 0 !important;
    text-align: center !important;
}

.stat-item {
    background: rgba(255,255,255,0.1) !important;
    padding: 1rem !important;
    border-radius: 10px !important;
    min-width: 80px !important;
}

.stat-number {
    font-size: 2rem !important;
    font-weight: bold !important;
    display: block !important;
    color: white !important;
}

.stat-label {
    font-size: 0.9rem !important;
    opacity: 0.8 !important;
    color: white !important;
}

/* Messages */
.success-message {
    background: #d4edda !important;
    color: #155724 !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    border: 1px solid #c3e6cb !important;
    text-align: center !important;
    margin: 1rem 0 !important;
}

.error-message {
    background: #f8d7da !important;
    color: #721c24 !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    border: 1px solid #f5c6cb !important;
    text-align: center !important;
    margin: 1rem 0 !important;
}

/* Streamlit form elements */
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border: 2px solid #e9ecef !important;
    padding: 12px !important;
    font-size: 16px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #3498db !important;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1) !important;
}

.stButton > button {
    background: linear-gradient(45deg, #3498db, #2ecc71) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: #f8f9fa !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
}

.stTabs [aria-selected="true"] {
    background-color: #3498db !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# Configuration
FASTAPI_BASE_URL = "http://localhost:8000"

def init_session_state():
    """Initialize session state variables using SessionManager"""
    SessionManager.initialize_session()

def login_user(username, password):
    """Login user via FastAPI backend"""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/v1/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except requests.RequestException as e:
        return False, {"detail": f"Connection error: {str(e)}"}

def register_user(username, email, password, first_name="", last_name=""):
    """Register user via FastAPI backend"""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/v1/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "first_name": first_name or username,
                "last_name": last_name or "User"
            }
        )
        return response.status_code == 200, response.json()
    except requests.RequestException as e:
        return False, {"detail": f"Connection error: {str(e)}"}

def render_login_interface():
    """Render the modern login interface"""
    
    # CSS is working - using inline styles for better compatibility
    
    # Create two-column layout
    col1, col2 = st.columns([1, 1])

    # Left Panel - Info Section
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #2c3e50, #3498db); color: white; padding: 3rem 2rem; border-radius: 20px; margin: 0.5rem; min-height: 500px; box-shadow: 0 20px 60px rgba(0,0,0,0.2);">
            <h1 style="font-size: 2.5rem; margin-bottom: 1rem; font-weight: 300; color: white;">🤖 AI ChatBot</h1>
            <h2 style="font-size: 1.8rem; margin-bottom: 2rem; color: #ecf0f1; font-weight: 300;">Your Intelligent AI Assistant</h2>
            
            <div style="display: flex; align-items: center; margin: 1rem 0; font-size: 1.1rem; color: white;">
                <span style="font-size: 1.5rem; margin-right: 1rem; width: 30px;">🧠</span>
                <span>Powered by advanced AI with enhanced reasoning</span>
            </div>
            
            <div style="display: flex; align-items: center; margin: 1rem 0; font-size: 1.1rem; color: white;">
                <span style="font-size: 1.5rem; margin-right: 1rem; width: 30px;">🔍</span>
                <span>Real-time web search integration</span>
            </div>
            
            <div style="display: flex; align-items: center; margin: 1rem 0; font-size: 1.1rem; color: white;">
                <span style="font-size: 1.5rem; margin-right: 1rem; width: 30px;">💾</span>
                <span>Persistent conversation memory</span>
            </div>
            
            <div style="display: flex; align-items: center; margin: 1rem 0; font-size: 1.1rem; color: white;">
                <span style="font-size: 1.5rem; margin-right: 1rem; width: 30px;">🔒</span>
                <span>Secure authentication & data protection</span>
            </div>
            
            <div style="display: flex; align-items: center; margin: 1rem 0; font-size: 1.1rem; color: white;">
                <span style="font-size: 1.5rem; margin-right: 1rem; width: 30px;">⚡</span>
                <span>Lightning-fast responses</span>
            </div>
            
            <div style="display: flex; align-items: center; margin: 1rem 0; font-size: 1.1rem; color: white;">
                <span style="font-size: 1.5rem; margin-right: 1rem; width: 30px;">🎨</span>
                <span>Customizable chat experience</span>
            </div>
            
            <div style="display: flex; justify-content: space-around; margin: 2rem 0; text-align: center;">
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; min-width: 80px;">
                    <span style="font-size: 2rem; font-weight: bold; display: block; color: white;">24/7</span>
                    <span style="font-size: 0.9rem; opacity: 0.8; color: white;">Available</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; min-width: 80px;">
                    <span style="font-size: 2rem; font-weight: bold; display: block; color: white;">∞</span>
                    <span style="font-size: 0.9rem; opacity: 0.8; color: white;">Conversations</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; min-width: 80px;">
                    <span style="font-size: 2rem; font-weight: bold; display: block; color: white;">🚀</span>
                    <span style="font-size: 0.9rem; opacity: 0.8; color: white;">Fast</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Right Panel - Login Form
    with col2:
        st.markdown('<div style="background: white; border-radius: 20px; padding: 3rem 2rem; margin: 0.5rem; box-shadow: 0 20px 60px rgba(0,0,0,0.1); min-height: 500px;">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #2c3e50; font-size: 2rem; margin-bottom: 2rem; font-weight: 300;">Welcome Back</h2>', unsafe_allow_html=True)

        # Login/Register Tabs
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Register"])

        with tab1:
            st.markdown("### Sign In to Your Account")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    remember_me = st.checkbox("Remember me")
                
                login_button = st.form_submit_button("🚀 Sign In", use_container_width=True)

                if login_button:
                    if username and password:
                        with st.spinner("Signing you in..."):
                            success, response = login_user(username, password)
                            
                            if success and response.get('success'):
                                # Store authentication info using SessionManager
                                st.session_state.authenticated = True
                                st.session_state.user_id = username
                                st.session_state.username = username
                                st.session_state.user_info = {
                                    'username': username,
                                    'token': response.get('access_token'),
                                    'user_data': response.get('user', {})
                                }
                                
                                # Update session manager
                                SessionManager.update_last_activity()
                                
                                st.markdown('<div style="background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border: 1px solid #c3e6cb; text-align: center; margin: 1rem 0;">✅ Welcome back! Loading chat...</div>', unsafe_allow_html=True)
                                time.sleep(1)
                                st.rerun()
                            else:
                                error_msg = response.get('message', 'Login failed')
                                st.markdown(f'<div style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; margin: 1rem 0;">❌ {error_msg}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; margin: 1rem 0;">⚠️ Please fill in all fields</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("### Create Your Account")
            
            with st.form("register_form"):
                col_reg1, col_reg2 = st.columns(2)
                with col_reg1:
                    reg_first_name = st.text_input("First Name", placeholder="First name")
                with col_reg2:
                    reg_last_name = st.text_input("Last Name", placeholder="Last name")
                
                reg_username = st.text_input("Username", placeholder="Choose a username")
                reg_email = st.text_input("Email", placeholder="Enter your email")
                reg_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                register_button = st.form_submit_button("🎉 Create Account", use_container_width=True)

                if register_button:
                    if reg_username and reg_email and reg_password and confirm_password:
                        if reg_password != confirm_password:
                            st.markdown('<div style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; margin: 1rem 0;">❌ Passwords do not match</div>', unsafe_allow_html=True)
                        elif not agree_terms:
                            st.markdown('<div style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; margin: 1rem 0;">⚠️ Please agree to the terms</div>', unsafe_allow_html=True)
                        else:
                            with st.spinner("Creating your account..."):
                                success, response = register_user(
                                    reg_username, 
                                    reg_email, 
                                    reg_password,
                                    reg_first_name,
                                    reg_last_name
                                )
                                
                                if success and response.get('success'):
                                    st.markdown('<div style="background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border: 1px solid #c3e6cb; text-align: center; margin: 1rem 0;">🎉 Account created successfully! Please sign in.</div>', unsafe_allow_html=True)
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    error_msg = response.get('message', 'Registration failed')
                                    st.markdown(f'<div style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; margin: 1rem 0;">❌ {error_msg}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; margin: 1rem 0;">⚠️ Please fill in all fields</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

def render_chat_application():
    """Render the main chat application"""
    # Initialize API client
    api_client = APIClient(base_url=FASTAPI_BASE_URL)
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.write(f'Welcome **{st.session_state.get("username", "User")}**!')
        
        if st.button("Logout", use_container_width=True):
            # Clear session using SessionManager
            SessionManager.clear_session()
            st.session_state.authenticated = False
            st.rerun()
        st.markdown("---")
        
        # Load user's chat history
        load_user_chat_history(api_client)
        
        # Render sidebar with chat history
        render_sidebar()

    # Main chat interface
    st.title("🤖 AI Assistant with Web Search")
    st.markdown("---")

    # Render main chat interface
    render_chat_interface(api_client)

def load_user_chat_history(api_client):
    """Load user's chat history from backend"""
    try:
        user_id = st.session_state.user_id
        response = api_client.get_chat_history(user_id)
        if response and response.get('success'):
            st.session_state.chat_history = response.get('conversations', [])
    except Exception as e:
        st.error(f"Failed to load chat history: {e}")

def main():
    """Main application function"""
    init_session_state()

    # Check authentication status
    if not st.session_state.get('authenticated', False):
        # Show login interface
        render_login_interface()
    else:
        # Show chat application
        render_chat_application()

if __name__ == "__main__":
    main()