"""
Transcription Page - Upload files or YouTube URLs for transcription
"""

import streamlit as st
import time
from datetime import datetime
from utils.config import get_config, validate_file_size, validate_file_format
from utils.api_client import AIBOAClient, format_transcript_for_display
import json

st.set_page_config(
    page_title="Transcription - AIBOA",
    page_icon="📝",
    layout="wide"
)

# Initialize API client
if "api_client" not in st.session_state:
    st.session_state.api_client = AIBOAClient()

# Page Header
st.title("📝 Transcription Service")
st.markdown("Convert video/audio files or YouTube videos to text using AI-powered speech recognition")

# Create tabs for different input methods
tab1, tab2, tab3 = st.tabs(["📁 File Upload", "🎥 YouTube URL", "📜 Recent Jobs"])

with tab1:
    st.header("Upload Media File")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a video or audio file",
            type=["mp4", "mp3", "wav", "m4a", "avi", "mov"],
            help="Maximum file size: 200MB"
        )
        
        if uploaded_file:
            # Validate file
            file_valid, file_type = validate_file_format(uploaded_file.name)
            
            if not file_valid:
                st.error(f"Unsupported file format: {uploaded_file.name}")
            elif not validate_file_size(uploaded_file.size):
                st.error(f"File too large. Maximum size is {get_config()['MAX_FILE_SIZE']}MB")
            else:
                st.success(f"✅ File ready: {uploaded_file.name} ({file_type})")
                
                # File info
                st.markdown(f"""
                **File Details:**
                - Name: {uploaded_file.name}
                - Type: {file_type}
                - Size: {uploaded_file.size / 1024 / 1024:.2f} MB
                """)
    
    with col2:
        st.markdown("### Settings")
        
        config = get_config()
        language = st.selectbox(
            "Language",
            options=list(config["SUPPORTED_LANGUAGES"].keys()),
            format_func=lambda x: config["SUPPORTED_LANGUAGES"][x],
            index=0
        )
        
        output_format = st.multiselect(
            "Output Formats",
            ["JSON", "SRT", "TXT"],
            default=["TXT"]
        )
        
        st.markdown("### Options")
        timestamps = st.checkbox("Include timestamps", value=True)
        speaker_detection = st.checkbox("Detect speakers", value=False)
    
    # Submit button
    if st.button("🚀 Start Transcription", type="primary", disabled=not uploaded_file):
        if uploaded_file and file_valid and validate_file_size(uploaded_file.size):
            with st.spinner("Uploading and processing file..."):
                # Upload file
                result = st.session_state.api_client.upload_file_for_transcription(
                    uploaded_file,
                    uploaded_file.name,
                    language
                )
                
                if result["success"]:
                    job_id = result["data"].get("job_id")
                    st.success(f"✅ Job created: {job_id}")
                    
                    # Add to session state
                    if "jobs" not in st.session_state:
                        st.session_state.jobs = []
                    
                    st.session_state.jobs.append({
                        "id": job_id,
                        "type": "file",
                        "name": uploaded_file.name,
                        "status": "processing",
                        "created_at": datetime.now().isoformat()
                    })
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Poll for completion
                    def update_progress(status, data):
                        if status == "processing":
                            progress_bar.progress(50)
                            status_text.text("⏳ Processing transcription...")
                        elif status == "completed":
                            progress_bar.progress(100)
                            status_text.text("✅ Transcription completed!")
                    
                    # Wait for completion
                    final_result = st.session_state.api_client.wait_for_transcription(
                        job_id, 
                        update_progress
                    )
                    
                    if final_result["success"]:
                        st.balloons()
                        
                        # Display results
                        st.markdown("---")
                        st.header("📄 Transcription Results")
                        
                        transcript_data = final_result["data"].get("result", {})
                        
                        # Display transcript
                        st.text_area(
                            "Transcript",
                            format_transcript_for_display(transcript_data),
                            height=300
                        )
                        
                        # Download options
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if "JSON" in output_format:
                                json_str = json.dumps(transcript_data, ensure_ascii=False, indent=2)
                                st.download_button(
                                    "📥 Download JSON",
                                    json_str,
                                    f"transcript_{job_id}.json",
                                    "application/json"
                                )
                        
                        with col2:
                            if "TXT" in output_format:
                                txt_content = transcript_data.get("text", "")
                                st.download_button(
                                    "📥 Download TXT",
                                    txt_content,
                                    f"transcript_{job_id}.txt",
                                    "text/plain"
                                )
                        
                        with col3:
                            if st.button("🔍 Analyze This Transcript"):
                                st.session_state.current_transcript = transcript_data
                                st.switch_page("pages/2_🔍_Analysis.py")
                    else:
                        st.error(f"❌ Transcription failed: {final_result.get('error')}")
                else:
                    st.error(f"❌ Upload failed: {result.get('error')}")

with tab2:
    st.header("YouTube Video Transcription")
    
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Enter a valid YouTube video URL"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if youtube_url:
            # Simple YouTube URL validation
            if "youtube.com" in youtube_url or "youtu.be" in youtube_url:
                st.success("✅ Valid YouTube URL")
                
                # Try to extract video ID and show preview
                try:
                    if "watch?v=" in youtube_url:
                        video_id = youtube_url.split("watch?v=")[1].split("&")[0]
                    elif "youtu.be/" in youtube_url:
                        video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                    else:
                        video_id = None
                    
                    if video_id:
                        st.markdown(f"**Video ID:** {video_id}")
                        st.video(youtube_url)
                except:
                    pass
            else:
                st.error("❌ Invalid YouTube URL")
    
    with col2:
        st.markdown("### Settings")
        
        config = get_config()
        yt_language = st.selectbox(
            "Language",
            options=list(config["SUPPORTED_LANGUAGES"].keys()),
            format_func=lambda x: config["SUPPORTED_LANGUAGES"][x],
            index=0,
            key="yt_language"
        )
        
        use_captions = st.checkbox("Use YouTube captions if available", value=True)
        auto_translate = st.checkbox("Auto-translate to selected language", value=False)
    
    if st.button("🎥 Transcribe YouTube Video", type="primary", disabled=not youtube_url):
        if youtube_url and ("youtube.com" in youtube_url or "youtu.be" in youtube_url):
            with st.spinner("Processing YouTube video..."):
                result = st.session_state.api_client.transcribe_youtube(
                    youtube_url,
                    yt_language
                )
                
                if result["success"]:
                    job_id = result["data"].get("job_id")
                    st.success(f"✅ Job created: {job_id}")
                    
                    # Add to session state
                    if "jobs" not in st.session_state:
                        st.session_state.jobs = []
                    
                    st.session_state.jobs.append({
                        "id": job_id,
                        "type": "youtube",
                        "url": youtube_url,
                        "status": "processing",
                        "created_at": datetime.now().isoformat()
                    })
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Poll for completion
                    def update_progress(status, data):
                        if status == "processing":
                            progress_bar.progress(50)
                            status_text.text("⏳ Processing YouTube video...")
                        elif status == "completed":
                            progress_bar.progress(100)
                            status_text.text("✅ Transcription completed!")
                    
                    # Wait for completion
                    final_result = st.session_state.api_client.wait_for_transcription(
                        job_id,
                        update_progress
                    )
                    
                    if final_result["success"]:
                        st.balloons()
                        
                        # Display results
                        st.markdown("---")
                        st.header("📄 YouTube Transcription Results")
                        
                        transcript_data = final_result["data"].get("result", {})
                        
                        # Display transcript
                        st.text_area(
                            "Transcript",
                            format_transcript_for_display(transcript_data),
                            height=300
                        )
                        
                        # Download and analyze options
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            json_str = json.dumps(transcript_data, ensure_ascii=False, indent=2)
                            st.download_button(
                                "📥 Download Transcript",
                                json_str,
                                f"youtube_transcript_{job_id}.json",
                                "application/json"
                            )
                        
                        with col2:
                            if st.button("🔍 Analyze This Transcript", key="analyze_yt"):
                                st.session_state.current_transcript = transcript_data
                                st.switch_page("pages/2_🔍_Analysis.py")
                    else:
                        st.error(f"❌ Transcription failed: {final_result.get('error')}")
                else:
                    st.error(f"❌ Failed to process YouTube URL: {result.get('error')}")

with tab3:
    st.header("Recent Transcription Jobs")
    
    if "jobs" in st.session_state and st.session_state.jobs:
        # Display jobs in reverse chronological order
        for job in reversed(st.session_state.jobs[-10:]):  # Show last 10 jobs
            with st.expander(f"Job: {job['id'][:8]}... - {job.get('status', 'Unknown')}"):
                st.markdown(f"""
                **Job Details:**
                - ID: {job['id']}
                - Type: {job['type']}
                - Status: {job.get('status', 'Unknown')}
                - Created: {job.get('created_at', 'N/A')}
                """)
                
                if job['type'] == 'file':
                    st.markdown(f"- File: {job.get('name', 'N/A')}")
                elif job['type'] == 'youtube':
                    st.markdown(f"- URL: {job.get('url', 'N/A')}")
                
                # Check status button
                if st.button(f"Check Status", key=f"check_{job['id']}"):
                    result = st.session_state.api_client.get_transcription_job_status(job['id'])
                    if result["success"]:
                        st.json(result["data"])
                    else:
                        st.error(f"Failed to get status: {result.get('error')}")
    else:
        st.info("No transcription jobs yet. Upload a file or enter a YouTube URL to get started!")

# Sidebar info
with st.sidebar:
    st.markdown("### 📝 Transcription Tips")
    st.markdown("""
    **For best results:**
    - Use high-quality audio/video files
    - Ensure clear speech with minimal background noise
    - Select the correct language for better accuracy
    - YouTube captions (if available) often provide better accuracy
    
    **Supported formats:**
    - Video: MP4, AVI, MOV, MKV
    - Audio: MP3, WAV, M4A, FLAC
    
    **Processing time:**
    - Files under 10MB: ~30 seconds
    - Files 10-50MB: 1-2 minutes
    - Files 50-200MB: 2-5 minutes
    - YouTube videos: 1-3 minutes
    """)
    
    # Service status
    st.markdown("---")
    st.markdown("### 🟢 Service Status")
    
    if st.session_state.api_client.check_transcription_health():
        st.success("Transcription Service: Online")
    else:
        st.error("Transcription Service: Offline")