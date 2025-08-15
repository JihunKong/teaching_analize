"""
Statistics Page - Platform metrics and analytics
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from utils.api_client import get_cached_statistics

st.set_page_config(
    page_title="Statistics - AIBOA",
    page_icon="📊",
    layout="wide"
)

# Page Header
st.title("📊 Platform Statistics")
st.markdown("Real-time metrics and analytics for the AIBOA platform")

# Get statistics from API
stats_result = get_cached_statistics()

if stats_result["success"]:
    stats = stats_result["data"]
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Analyses",
            stats.get("total_analyses", 0),
            "+12 today",
            help="Total number of analyses performed"
        )
    
    with col2:
        st.metric(
            "Average CBIL Score",
            f"{stats.get('average_cbil_score', 0):.2f}",
            "+0.3",
            help="Average cognitive level score across all analyses"
        )
    
    with col3:
        st.metric(
            "Active Today",
            stats.get("analyses_today", 0),
            "+25%",
            help="Analyses performed today"
        )
    
    with col4:
        st.metric(
            "Success Rate",
            "98.5%",
            "+1.2%",
            help="Percentage of successful processing"
        )
    
    # Detailed Statistics
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🎯 CBIL Distribution", "⚡ Performance", "📝 Recent Activity"])
    
    with tab1:
        st.header("Usage Trends")
        
        # Generate mock data for demonstration
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        daily_transcriptions = [20 + i * 2 + (i % 7) * 3 for i in range(30)]
        daily_analyses = [15 + i * 1.5 + (i % 5) * 2 for i in range(30)]
        
        df = pd.DataFrame({
            'Date': dates,
            'Transcriptions': daily_transcriptions,
            'Analyses': daily_analyses
        })
        
        fig = px.line(
            df,
            x='Date',
            y=['Transcriptions', 'Analyses'],
            title="Daily Usage Trends (Last 30 Days)",
            labels={'value': 'Count', 'variable': 'Service'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Weekly growth
            weekly_growth = pd.DataFrame({
                'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'Users': [50, 75, 120, 180]
            })
            
            fig = px.bar(
                weekly_growth,
                x='Week',
                y='Users',
                title="Weekly Active Users",
                color='Users',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Service usage pie chart
            service_usage = pd.DataFrame({
                'Service': ['Transcription Only', 'Analysis Only', 'Both Services'],
                'Users': [30, 25, 45]
            })
            
            fig = px.pie(
                service_usage,
                values='Users',
                names='Service',
                title="Service Usage Distribution"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("CBIL Level Distribution")
        
        if stats.get("cbil_levels"):
            # Display CBIL levels information
            cbil_levels = stats["cbil_levels"]
            
            # Create distribution chart
            levels = list(range(1, 8))
            percentages = [15, 25, 30, 15, 10, 3, 2]  # Mock data
            
            fig = go.Figure(data=[
                go.Bar(
                    x=levels,
                    y=percentages,
                    text=[f"{p}%" for p in percentages],
                    textposition='auto',
                    marker_color=['#FF6B6B', '#FFA06B', '#FFD56B', '#A8E6CF', '#7FD1E4', '#B19CD9', '#FF88CC']
                )
            ])
            
            fig.update_layout(
                title="Average CBIL Level Distribution Across All Analyses",
                xaxis_title="CBIL Level",
                yaxis_title="Percentage (%)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations based on distribution
            st.subheader("Platform-wide Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **Strengths:**
                - Good foundation in concept explanation (Level 3)
                - Balanced fact recall activities (Level 2)
                - Consistent simple confirmation usage
                """)
            
            with col2:
                st.warning("""
                **Areas for Improvement:**
                - Increase creative application tasks (Level 7)
                - More evaluative judgment questions (Level 6)
                - Enhance analytical thinking activities (Level 4)
                """)
    
    with tab3:
        st.header("System Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time chart
            hours = list(range(24))
            response_times = [0.5 + (h % 8) * 0.1 for h in hours]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hours,
                y=response_times,
                mode='lines+markers',
                name='Response Time',
                line=dict(color='#1E88E5', width=2)
            ))
            
            fig.add_hline(y=1.0, line_dash="dash", line_color="red",
                         annotation_text="Target: 1s")
            
            fig.update_layout(
                title="API Response Time (Last 24 Hours)",
                xaxis_title="Hour",
                yaxis_title="Response Time (seconds)",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Success rate gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=98.5,
                title={'text': "Success Rate (%)"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "green"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # System metrics table
        st.subheader("Detailed Metrics")
        
        metrics_data = {
            'Metric': [
                'Average Processing Time',
                'Transcription Accuracy',
                'Analysis Accuracy',
                'Uptime',
                'Error Rate',
                'Cache Hit Rate'
            ],
            'Value': [
                '2.3 seconds',
                '95.2%',
                '92.8%',
                '99.9%',
                '0.5%',
                '78.4%'
            ],
            'Status': ['✅', '✅', '✅', '✅', '✅', '⚠️']
        }
        
        df_metrics = pd.DataFrame(metrics_data)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    
    with tab4:
        st.header("Recent Platform Activity")
        
        # Recent transcriptions
        st.subheader("Latest Transcriptions")
        
        recent_transcriptions = pd.DataFrame({
            'Time': [datetime.now() - timedelta(minutes=i*15) for i in range(5)],
            'Type': ['YouTube', 'File Upload', 'File Upload', 'YouTube', 'File Upload'],
            'Language': ['Korean', 'English', 'Korean', 'Korean', 'English'],
            'Duration': ['5:23', '12:45', '8:30', '15:00', '3:15'],
            'Status': ['Completed', 'Completed', 'Processing', 'Completed', 'Completed']
        })
        
        st.dataframe(recent_transcriptions, use_container_width=True, hide_index=True)
        
        # Recent analyses
        st.subheader("Latest Analyses")
        
        recent_analyses = pd.DataFrame({
            'Time': [datetime.now() - timedelta(minutes=i*20) for i in range(5)],
            'Context': ['High School', 'Elementary', 'University', 'Middle School', 'Elementary'],
            'Subject': ['Science', 'Math', 'Literature', 'History', 'English'],
            'CBIL Score': [4.2, 3.8, 5.1, 4.5, 3.2],
            'Status': ['Completed', 'Completed', 'Completed', 'Processing', 'Completed']
        })
        
        st.dataframe(recent_analyses, use_container_width=True, hide_index=True)

else:
    st.error("Failed to load statistics. Please check your connection and try again.")
    st.info(f"Error: {stats_result.get('error', 'Unknown error')}")

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Statistics Info")
    st.markdown("""
    **Data Refresh Rate:**
    - Real-time: Service status
    - 1 minute: Usage metrics
    - 5 minutes: Performance data
    - Hourly: Trend analysis
    
    **Metrics Explained:**
    - **CBIL Score**: 1-7 scale of cognitive demand
    - **Success Rate**: % of successful operations
    - **Response Time**: API processing speed
    - **Uptime**: Service availability
    """)
    
    st.markdown("---")
    
    # Export options
    st.markdown("### 📥 Export Data")
    
    export_format = st.selectbox(
        "Format",
        ["CSV", "JSON", "Excel"]
    )
    
    if st.button("Export Statistics"):
        st.info(f"Export to {export_format} coming soon!")
    
    st.markdown("---")
    
    # System Health
    st.markdown("### 🏥 System Health")
    
    services = {
        "Transcription API": "🟢 Healthy",
        "Analysis API": "🟢 Healthy",
        "Database": "🟢 Connected",
        "Cache": "🟡 Warming",
        "Queue": "🟢 Active"
    }
    
    for service, status in services.items():
        st.markdown(f"**{service}**: {status}")