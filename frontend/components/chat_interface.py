
# components/chat_interface.py
import streamlit as st
import asyncio
from datetime import datetime
from typing import List, Dict
from utils.api_client import APIClient

def render_chat_interface(api_client: APIClient):
    """Render the main chat interface"""

    # Display existing messages
    display_chat_messages()

    # Chat input
    if prompt := st.chat_input("Ask me anything or search the web..."):
        handle_user_input(prompt, api_client)

def display_chat_messages():
    """Display all messages in the current conversation"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                # Assistant message with potential search results
                st.markdown(message["content"])

                # Display search results if available
                if "search_results" in message:
                    display_search_results(message["search_results"])

def display_search_results(search_results: List[Dict]):
    """Display web search results in an expandable section"""
    if search_results:
        with st.expander(f"🔍 Web Search Results ({len(search_results)} sources)", expanded=False):
            for i, result in enumerate(search_results, 1):
                st.markdown(f"""
                **{i}. {result.get('title', 'No Title')}**

                {result.get('snippet', 'No description available')}

                🔗 [{result.get('link', '#')}]({result.get('link', '#')})
                """)
                st.divider()

def handle_user_input(prompt: str, api_client: APIClient):
    """Handle user input and generate response"""

    # Add user message to chat
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Show loading spinner
            with st.spinner("Searching and generating response..."):
                # Call backend API
                response_data = api_client.chat_with_search(
                    user_id=st.session_state.user_id,
                    message=prompt,
                    conversation_id=st.session_state.current_conversation_id
                )

            if response_data and response_data.get('success'):
                full_response = response_data.get('response', '')
                search_results = response_data.get('search_results', [])
                conversation_id = response_data.get('conversation_id')

                # Update conversation ID if this is a new conversation
                if not st.session_state.current_conversation_id:
                    st.session_state.current_conversation_id = conversation_id

                # Display the response
                message_placeholder.markdown(full_response)

                # Add assistant message to chat
                assistant_message = {
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat(),
                    "search_results": search_results
                }
                st.session_state.messages.append(assistant_message)

                # Display search results if available
                if search_results:
                    display_search_results(search_results)

                # Update chat history in sidebar
                update_chat_history_sidebar(conversation_id, prompt)

            else:
                error_msg = "Sorry, I couldn't process your request. Please try again."
                message_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": error_msg,
                "timestamp": datetime.now().isoformat()
            })

def update_chat_history_sidebar(conversation_id: str, first_message: str):
    """Update the chat history in sidebar"""
    # Create a summary for the conversation
    summary = first_message[:50] + "..." if len(first_message) > 50 else first_message

    # Check if conversation already exists in history
    existing_conv = next(
        (conv for conv in st.session_state.chat_history if conv['id'] == conversation_id), 
        None
    )

    if not existing_conv:
        # Add new conversation to history
        new_conversation = {
            'id': conversation_id,
            'title': summary,
            'timestamp': datetime.now().isoformat(),
            'message_count': 1
        }
        st.session_state.chat_history.insert(0, new_conversation)
    else:
        # Update existing conversation
        existing_conv['message_count'] += 1
        existing_conv['timestamp'] = datetime.now().isoformat()

def start_new_conversation():
    """Start a new conversation"""
    st.session_state.messages = []
    st.session_state.current_conversation_id = None
    st.session_state.search_results = []
    st.rerun()
