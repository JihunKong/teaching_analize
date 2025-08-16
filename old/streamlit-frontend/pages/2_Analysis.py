"""
Analysis Page - Analyze text for CBIL cognitive classification
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.config import get_config
from utils.api_client import AIBOAClient, format_cbil_scores
import pandas as pd

st.set_page_config(
    page_title="Analysis - AIBOA",
    page_icon="🎯",
    layout="wide"
)

# Initialize API client
if "api_client" not in st.session_state:
    st.session_state.api_client = AIBOAClient()

# Page Header
st.title("🎯 CBIL Analysis Service")
st.markdown("Analyze teaching content using the 7-level Cognitive Burden of Instructional Language classification")

# CBIL Level Information
with st.expander("📚 Understanding CBIL Levels", expanded=False):
    config = get_config()
    cbil_levels = config["CBIL_LEVELS"]
    
    for level, info in cbil_levels.items():
        st.markdown(f"""
        **Level {level}: {info['name']} ({info['description']})**
        - Cognitive demand: {'Low' if level <= 3 else 'Medium' if level <= 5 else 'High'}
        - Example questions: {
            '"Is this correct?" "What is the answer?"' if level == 1 else
            '"What did we learn yesterday?" "Can you recall...?"' if level == 2 else
            '"Can you explain this concept?" "Describe how..."' if level == 3 else
            '"Why do you think...?" "What are the differences?"' if level == 4 else
            '"How does this relate to...?" "Summarize the main ideas"' if level == 5 else
            '"Do you agree with...?" "What is your opinion?"' if level == 6 else
            '"How would you design...?" "Create a new solution"'
        }
        """)

# Main content area
tab1, tab2, tab3 = st.tabs(["✍️ Text Input", "📊 Results", "📈 Trends"])

with tab1:
    st.header("Input Teaching Content")
    
    # Check if there's a transcript from the previous page
    if "current_transcript" in st.session_state and st.session_state.current_transcript:
        st.info("📝 Transcript loaded from previous transcription")
        text_input = st.text_area(
            "Teaching Content",
            value=st.session_state.current_transcript.get("text", ""),
            height=300,
            help="Edit the transcript if needed before analysis"
        )
        # Clear the transcript after use
        del st.session_state.current_transcript
    else:
        text_input = st.text_area(
            "Teaching Content",
            placeholder="""Enter teaching transcript or lesson content here...

Example:
Teacher: "오늘은 광합성에 대해 배워보겠습니다. 광합성이 무엇인지 아는 사람?"
Student: "식물이 빛을 이용해서 양분을 만드는 과정이요."
Teacher: "맞습니다. 그럼 왜 광합성이 중요할까요? 우리 생활과 어떤 관련이 있을까요?"
""",
            height=300,
            help="Paste or type the teaching content you want to analyze"
        )
    
    # Additional options
    col1, col2 = st.columns(2)
    
    with col1:
        context = st.selectbox(
            "Teaching Context",
            ["General", "Elementary School", "Middle School", "High School", "University", "Professional Training"],
            help="Select the educational context for more accurate analysis"
        )
    
    with col2:
        subject = st.selectbox(
            "Subject Area",
            ["General", "Mathematics", "Science", "Language Arts", "Social Studies", "Technology", "Arts", "Physical Education"],
            help="Select the subject area for domain-specific analysis"
        )
    
    # Analyze button
    if st.button("🔬 Analyze Content", type="primary", disabled=not text_input):
        if text_input:
            with st.spinner("Analyzing cognitive levels..."):
                # Prepare metadata
                metadata = {
                    "context": context,
                    "subject": subject,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Call API
                result = st.session_state.api_client.analyze_text(text_input, metadata)
                
                if result["success"]:
                    analysis_data = result["data"]
                    
                    # Store in session state
                    if "analyses" not in st.session_state:
                        st.session_state.analyses = []
                    
                    st.session_state.analyses.append({
                        "id": analysis_data.get("analysis_id"),
                        "text": text_input[:200] + "..." if len(text_input) > 200 else text_input,
                        "cbil_scores": analysis_data.get("cbil_scores"),
                        "overall_score": analysis_data.get("overall_score"),
                        "recommendations": analysis_data.get("recommendations"),
                        "created_at": datetime.now().isoformat(),
                        "context": context,
                        "subject": subject
                    })
                    
                    # Store current analysis for display
                    st.session_state.current_analysis = analysis_data
                    
                    st.success("✅ Analysis completed!")
                    st.rerun()
                else:
                    st.error(f"❌ Analysis failed: {result.get('error')}")

with tab2:
    st.header("Analysis Results")
    
    if "current_analysis" in st.session_state and st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        
        # Overall Score Display
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Create a gauge chart for overall score
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = analysis.get("overall_score", 0),
                title = {'text': "Overall CBIL Score"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': 4.0, 'increasing': {'color': "green"}},
                gauge = {
                    'axis': {'range': [1, 7], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [1, 3], 'color': '#FFE5E5'},
                        {'range': [3, 5], 'color': '#FFFACD'},
                        {'range': [5, 7], 'color': '#E5FFE5'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 4.5
                    }
                }
            ))
            
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        # CBIL Distribution
        st.markdown("---")
        st.subheader("📊 Cognitive Level Distribution")
        
        cbil_scores = analysis.get("cbil_scores", {})
        config = get_config()
        
        # Prepare data for visualization
        levels = []
        names = []
        scores = []
        colors = []
        
        for level, score in cbil_scores.items():
            level_info = config["CBIL_LEVELS"].get(int(level), {})
            levels.append(f"Level {level}")
            names.append(level_info.get("name", f"Level {level}"))
            scores.append(score * 100)  # Convert to percentage
            colors.append(level_info.get("color", "#888888"))
        
        # Create bar chart
        df = pd.DataFrame({
            'Level': levels,
            'Name': names,
            'Percentage': scores
        })
        
        fig = px.bar(
            df, 
            x='Level', 
            y='Percentage',
            hover_data=['Name'],
            color='Percentage',
            color_continuous_scale='Viridis',
            title="Distribution of Cognitive Levels in Teaching Content"
        )
        
        fig.update_layout(
            showlegend=False,
            yaxis_title="Percentage (%)",
            xaxis_title="CBIL Level",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Level distribution summary
        col1, col2, col3 = st.columns(3)
        
        distribution = analysis.get("cbil_level_distribution", {})
        
        with col1:
            st.metric(
                "Low-Level Thinking",
                f"{distribution.get('low_level', 0) * 100:.1f}%",
                "Levels 1-3",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "Mid-Level Thinking",
                f"{distribution.get('mid_level', 0) * 100:.1f}%",
                "Levels 4-5"
            )
        
        with col3:
            st.metric(
                "High-Level Thinking",
                f"{distribution.get('high_level', 0) * 100:.1f}%",
                "Levels 6-7"
            )
        
        # Recommendations
        st.markdown("---")
        st.subheader("💡 Recommendations for Improvement")
        
        recommendations = analysis.get("recommendations", [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.info(f"**{i}.** {rec}")
        else:
            st.success("Great balance of cognitive levels! Keep up the good work.")
        
        # Download Report
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col2:
            if st.button("📄 Generate PDF Report", type="primary"):
                st.info("PDF report generation coming soon!")
        
    else:
        st.info("No analysis results yet. Enter text in the 'Text Input' tab to begin analysis.")

with tab3:
    st.header("Analysis Trends")
    
    if "analyses" in st.session_state and len(st.session_state.analyses) > 1:
        # Create trend data
        analyses = st.session_state.analyses
        
        # Overall score trend
        timestamps = [a["created_at"] for a in analyses]
        scores = [a["overall_score"] for a in analyses]
        
        fig = px.line(
            x=timestamps,
            y=scores,
            title="CBIL Score Trend Over Time",
            labels={'x': 'Time', 'y': 'Overall CBIL Score'},
            markers=True
        )
        
        fig.add_hline(y=4.5, line_dash="dash", line_color="green", 
                     annotation_text="Target Score")
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Subject/Context breakdown
        if len(analyses) >= 3:
            st.subheader("Performance by Context")
            
            context_scores = {}
            for a in analyses:
                ctx = a.get("context", "General")
                if ctx not in context_scores:
                    context_scores[ctx] = []
                context_scores[ctx].append(a["overall_score"])
            
            # Calculate averages
            context_avg = {k: sum(v)/len(v) for k, v in context_scores.items()}
            
            if context_avg:
                df = pd.DataFrame(list(context_avg.items()), columns=['Context', 'Average Score'])
                
                fig = px.bar(
                    df,
                    x='Context',
                    y='Average Score',
                    title="Average CBIL Score by Teaching Context"
                )
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Analyze at least 2 texts to see trends over time.")

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Analysis Guide")
    st.markdown("""
    **What is CBIL?**
    
    The Cognitive Burden of Instructional Language (CBIL) framework classifies teaching questions and statements into 7 levels based on cognitive demand.
    
    **Ideal Distribution:**
    - Level 1-3: 30-40%
    - Level 4-5: 40-50%
    - Level 6-7: 10-20%
    
    **Tips for Improvement:**
    1. Include more "why" and "how" questions
    2. Ask students to compare and contrast
    3. Encourage creative problem-solving
    4. Request evaluations and opinions
    5. Design synthesis activities
    """)
    
    # Service status
    st.markdown("---")
    st.markdown("### 🟢 Service Status")
    
    if st.session_state.api_client.check_analysis_health():
        st.success("Analysis Service: Online")
    else:
        st.error("Analysis Service: Offline")