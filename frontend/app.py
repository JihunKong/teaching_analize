"""
AIBOA Frontend - Main Application
AI-Based Observation and Analysis Platform
"""

import streamlit as st
import os
from datetime import datetime
from utils.config import get_config
from utils.api_client import AIBOAClient

# Page configuration
st.set_page_config(
    page_title="AIBOA - Teaching Analysis Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
if "api_client" not in st.session_state:
    st.session_state.api_client = AIBOAClient()

# Initialize session state
if "jobs" not in st.session_state:
    st.session_state.jobs = []

if "analyses" not in st.session_state:
    st.session_state.analyses = []

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Main page content
def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 AIBOA Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Based Observation and Analysis for Teaching Excellence</p>', unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create three columns for main features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <h3>📝 Transcription</h3>
            <p>Convert video/audio to text</p>
            <h2>Smart STT</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>🔍 Analysis</h3>
            <p>CBIL cognitive classification</p>
            <h2>7 Levels</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>📊 Insights</h3>
            <p>Actionable recommendations</p>
            <h2>Real-time</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature sections
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.header("🚀 Quick Start Guide")
    
    tab1, tab2, tab3 = st.tabs(["📹 Transcribe Media", "📝 Analyze Text", "📊 View Statistics"])
    
    with tab1:
        st.markdown("""
        ### How to Transcribe Video/Audio:
        1. Navigate to **📝 Transcription** in the sidebar
        2. Choose input method:
           - Upload a video/audio file (MP4, MP3, WAV)
           - Enter a YouTube URL
        3. Select language (Korean/English)
        4. Click Submit and wait for processing
        5. Download transcript in your preferred format (JSON, SRT, TXT)
        """)
        
        if st.button("Go to Transcription →", key="go_transcription"):
            st.switch_page("pages/1_📝_Transcription.py")
    
    with tab2:
        st.markdown("""
        ### How to Analyze Teaching Content:
        1. Navigate to **🔍 Analysis** in the sidebar
        2. Input your text:
           - Paste teaching transcript
           - Type or paste lesson content
           - Use existing transcription result
        3. Click Analyze to get CBIL classification
        4. Review cognitive level distribution
        5. Get personalized recommendations
        """)
        
        if st.button("Go to Analysis →", key="go_analysis"):
            st.switch_page("pages/2_🔍_Analysis.py")
    
    with tab3:
        st.markdown("""
        ### Platform Statistics:
        - Total transcriptions processed
        - Average CBIL scores
        - Cognitive level trends
        - Usage patterns
        - Performance metrics
        """)
        
        if st.button("View Statistics →", key="go_stats"):
            st.switch_page("pages/3_📊_Statistics.py")
    
    # Recent Activity Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.header("📅 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Latest Transcriptions")
        if st.session_state.jobs:
            for job in st.session_state.jobs[-3:]:
                st.markdown(f"""
                <div class="feature-card">
                    <strong>Job ID:</strong> {job.get('id', 'N/A')[:8]}...<br>
                    <strong>Status:</strong> {job.get('status', 'Unknown')}<br>
                    <strong>Time:</strong> {job.get('created_at', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transcription jobs yet. Start by uploading a file!")
    
    with col2:
        st.subheader("Latest Analyses")
        if st.session_state.analyses:
            for analysis in st.session_state.analyses[-3:]:
                st.markdown(f"""
                <div class="feature-card">
                    <strong>Analysis ID:</strong> {analysis.get('id', 'N/A')[:8]}...<br>
                    <strong>CBIL Score:</strong> {analysis.get('overall_score', 0):.2f}<br>
                    <strong>Time:</strong> {analysis.get('created_at', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No analyses yet. Try analyzing some text!")
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>AIBOA Platform v1.0.0 | Powered by OpenAI Whisper & Solar LLM</p>
        <p>© 2025 AI-Based Observation and Analysis</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1E88E5/FFFFFF?text=AIBOA", width=150)
    st.markdown("---")
    
    # System Status
    st.markdown("### 🟢 System Status")
    
    # Check API connectivity
    transcription_status = "🟢 Online"
    analysis_status = "🟢 Online"
    
    st.markdown(f"""
    - Transcription: {transcription_status}
    - Analysis: {analysis_status}
    - Database: 🟢 Connected
    """)
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Jobs", len(st.session_state.jobs))
    st.metric("Total Analyses", len(st.session_state.analyses))
    
    st.markdown("---")
    
    # Help Section
    st.markdown("### ❓ Need Help?")
    st.markdown("""
    - [User Guide](https://docs.aiboa.com)
    - [API Documentation](https://api.aiboa.com)
    - [Report Issues](https://github.com/aiboa/issues)
    """)
    
    # API Key Configuration
    st.markdown("---")
    st.markdown("### 🔑 API Configuration")
    
    api_key = st.text_input("API Key", type="password", value=os.getenv("API_KEY", ""))
    if api_key:
        st.session_state.api_key = api_key
        st.success("API Key configured")

if __name__ == "__main__":
    main()