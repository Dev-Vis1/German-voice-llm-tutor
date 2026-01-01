import streamlit as st
import requests
import tempfile
import os
from pathlib import Path
import json
import time

# Set page config
st.set_page_config(
    page_title="German Voice LLM Tutor",
    page_icon="🎧",
    layout="centered"
)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_voice_chat(audio_file, topic):
    """Send audio to backend for processing"""
    try:
        files = {"audio": audio_file}
        data = {"topic": topic}
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/voice/chat",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure it's running on http://127.0.0.1:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Try again with a shorter audio clip.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_conversation_history():
    """Get recent conversation history"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/history", timeout=10)
        if response.status_code == 200:
            return response.json().get("conversations", [])
        return []
    except:
        return []

def main():
    st.title("🎧🇩🇪 German Voice LLM Tutor")
    st.markdown("Practice German conversation with AI voice interaction!")
    
    # Check backend status
    if not check_backend_status():
        st.error("⚠️ Backend is not running!")
        st.markdown("""
        **To start the backend:**
        ```bash
        cd backend
        uvicorn app:app --reload --host 127.0.0.1 --port 8000
        ```
        """)
        st.stop()
    
    st.success("✅ Backend is running!")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Topic selection
        topics = [
            "general conversation",
            "Fußballtraining (football training)",
            "Restaurant besuch (restaurant visit)",
            "Arztbesuch (doctor visit)",
            "Einkaufen (shopping)",
            "Büro gespräch (office talk)",
            "Reisen (travel)",
            "Custom..."
        ]
        
        selected_topic = st.selectbox("Choose conversation topic:", topics)
        
        if selected_topic == "Custom...":
            custom_topic = st.text_input("Enter custom topic (in German):")
            topic = custom_topic if custom_topic else "general conversation"
        else:
            topic = selected_topic
        
        st.markdown(f"**Current topic:** {topic}")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Voice Chat")
        
        # Audio recorder
        audio_file = st.audio_input("🎤 Record your German")
        
        if audio_file is not None:
            st.audio(audio_file, format="audio/wav")
            
            if st.button("Send to Tutor", type="primary"):
                with st.spinner("Processing your audio..."):
                    # Save audio temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(audio_file.read())
                        tmp_path = tmp_file.name
                    
                    try:
                        # Send to backend
                        with open(tmp_path, 'rb') as f:
                            result = send_voice_chat(f, topic)
                        
                        if result:
                            st.success("Got response from tutor!")
                            
                            # Show transcription
                            st.markdown("**What you said:**")
                            st.info(result["user_text"])
                            
                            # Show tutor response
                            st.markdown("**Tutor's response:**")
                            st.success(result["reply_text"])
                            
                            # Try to play TTS audio
                            if "tts_url" in result:
                                try:
                                    audio_url = f"{BACKEND_URL}{result['tts_url']}"
                                    st.audio(audio_url, format="audio/wav")
                                except Exception as e:
                                    st.warning(f"Could not play audio: {e}")
                    
                    finally:
                        # Clean up temp file
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
    
    with col2:
        st.header("Conversation History")
        
        history = get_conversation_history()
        if history:
            for i, conv in enumerate(reversed(history[-5:])):  # Show last 5
                with st.expander(f"Chat {len(history)-i}", expanded=False):
                    st.markdown(f"**Topic:** {conv.get('topic', 'N/A')}")
                    st.markdown(f"**You:** {conv.get('user_text', '')}")
                    st.markdown(f"**Tutor:** {conv.get('reply_text', '')}")
                    st.caption(conv.get('timestamp', ''))
        else:
            st.info("No conversation history yet. Start chatting!")
    
    # Instructions
    with st.expander("How to use", expanded=False):
        st.markdown("""
        1. **Choose a topic** from the sidebar (e.g., football training)
        2. **Record yourself** speaking German using the microphone
        3. **Click "Send to Tutor"** to get AI feedback and conversation
        4. **Listen to the response** and continue the conversation!
        
        **Tips:**
        - Speak clearly and not too fast
        - The AI will gently correct mistakes and explain
        - Try different topics to practice various vocabulary
        - The tutor will stay in role (e.g., as a football coach)
        """)
    
    # System info
    with st.expander("System Status", expanded=False):
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                st.success("✅ Backend API is healthy")
            else:
                st.warning("⚠️ Backend API returned unexpected status")
        except:
            st.error("❌ Cannot reach backend API")

if __name__ == "__main__":
    main()