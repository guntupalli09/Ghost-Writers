import streamlit as st
from agents.agent_manager import AgentManager
from utils.exporter import (
    format_campaign_kit,
    export_to_pdf,
    export_to_csv,
    export_by_section,
    export_per_platform_csv,
    create_calendar_matrix
)
from utils.display import (
    parse_calendar_to_df,
    format_score_indicator,
    create_timeline_chart
)
from datetime import datetime, timedelta
import pyperclip
import pandas as pd
import altair as alt
import asyncio
import subprocess
from utils.chunking import chunk_days
import plotly.express as px
from langchain.schema import HumanMessage, AIMessage
import requests
from streamlit_lottie import st_lottie
from typing import Dict, List, Any, Optional
import json
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Ghostwriter Teams - Content Calendar",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff6b6b;
    }
    .reportview-container {
        background: #f0f2f6;
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

def format_score_indicator(score: int) -> str:
    """Format a score as an indicator string with emojis."""
    if score >= 8:
        return f"🟢 {score}/10"
    elif score >= 6:
        return f"🟡 {score}/10"
    else:
        return f"🔴 {score}/10"

def create_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """Create a timeline visualization using Plotly."""
    # Convert date to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Create color mapping for platforms
    platform_colors = {
        'LinkedIn': '#0077B5',
        'Twitter': '#1DA1F2',
        'Instagram': '#E4405F',
        'Facebook': '#1877F2'
    }
    
    # Create the figure
    fig = px.timeline(
        df,
        x_start='Date',
        x_end='Date',
        y='Platform',
        color='Platform',
        hover_data=['Type', 'Topic', 'Copy'],
        color_discrete_map=platform_colors,
        title='Content Timeline'
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        height=400,
        xaxis_title='Date',
        yaxis_title='Platform',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Update traces
    fig.update_traces(
        marker_line_color='white',
        marker_line_width=2,
        opacity=0.8
    )
    
    return fig

def export_to_csv(df: pd.DataFrame) -> str:
    """Export the calendar data to CSV format."""
    return df.to_csv(index=False)

def export_to_pdf(df: pd.DataFrame) -> bytes:
    """Export the calendar data to PDF format."""
    # This is a placeholder - you would need to implement PDF generation
    # using a library like reportlab or weasyprint
    return b"PDF generation not implemented"

def create_calendar_matrix(df: pd.DataFrame) -> str:
    """Create a calendar matrix view of the content."""
    df['Date'] = pd.to_datetime(df['Date'])
    matrix = df.pivot_table(
        index='Platform',
        columns=pd.Grouper(key='Date', freq='W-MON'),
        values='Topic',
        aggfunc=lambda x: ', '.join(x)
    )
    return matrix.to_csv()

def export_per_platform_csv(df: pd.DataFrame, platforms: List[str]) -> str:
    """Export calendar data per platform."""
    platform_data = []
    for platform in platforms:
        platform_df = df[df['Platform'] == platform]
        if not platform_df.empty:
            platform_data.append(f"# {platform}\n")
            platform_data.append(platform_df.to_csv(index=False))
            platform_data.append("\n")
    return "\n".join(platform_data)

def export_by_section(
    df: pd.DataFrame,
    calendar_text: str,
    sections: List[str],
    content_focus: str,
    num_weeks: int,
    platforms: List[str]
) -> str:
    """Export selected sections of the calendar report."""
    export_data = []
    
    if "Overview" in sections:
        export_data.extend([
            "# Content Calendar Overview",
            f"Focus: {content_focus}",
            f"Duration: {num_weeks} weeks",
            f"Platforms: {', '.join(platforms)}",
            f"Total Posts: {len(df)}",
            "\n"
        ])
    
    if "Calendar" in sections:
        export_data.extend([
            "# Content Calendar",
            df.to_markdown(index=False),
            "\n"
        ])
    
    if "Timeline" in sections:
        export_data.extend([
            "# Timeline Analysis",
            "## Posts per Platform",
            df['Platform'].value_counts().to_markdown(),
            "\n",
            "## Posts per Type",
            df['Type'].value_counts().to_markdown(),
            "\n"
        ])
    
    if "Agent Insights" in sections:
        export_data.extend([
            "# Agent Insights",
            calendar_text,
            "\n"
        ])
    
    return "\n".join(export_data)

def load_lottie_url(url: str) -> Optional[Dict]:
    """Load a Lottie animation from a URL."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def format_score(score: int) -> str:
    """Format a score with an emoji indicator."""
    if score >= 8:
        return "🟢 " + str(score)
    elif score >= 5:
        return "🟡 " + str(score)
    else:
        return "🔴 " + str(score)

def display_agent_insights(insights: Dict[str, Any]):
    """Display insights from all agents in an organized manner."""
    if not insights:
        st.warning("No agent insights available yet. Generate a calendar first!")
        return
    
    # Display Mira's insights
    if 'mira' in insights:
        st.subheader("🔍 Market Trends Analysis (Mira)")
        mira_insights = insights['mira']
        
        with st.expander("View Market Analysis", expanded=True):
            # Key Trends
            st.markdown("#### 📈 Key Trends")
            for trend in mira_insights.get('key_trends', []):
                st.markdown(f"- {trend}")
            
            # Opportunities
            st.markdown("#### 💡 Opportunities")
            for opp in mira_insights.get('opportunities', []):
                st.markdown(f"- {opp}")
            
            # Recommendations
            st.markdown("#### 🎯 Recommendations")
            for rec in mira_insights.get('recommendations', []):
                st.markdown(f"- {rec}")
    
    # Display Eva's evaluation
    if 'eva' in insights:
        st.subheader("📊 Content Evaluation (Eva)")
        eva_insights = insights['eva']
        
        with st.expander("View Content Evaluation", expanded=True):
            # Scores
            scores = eva_insights.get('scores', {})
            cols = st.columns(len(scores))
            for col, (metric, score) in zip(cols, scores.items()):
                col.metric(metric, format_score(score))
            
            # Analysis
            if 'analysis' in eva_insights:
                st.markdown("#### 📝 Detailed Analysis")
                for aspect, analysis in eva_insights['analysis'].items():
                    st.markdown(f"**{aspect}**: {analysis}")
            
            # Strengths and Improvements
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ✅ Strengths")
                for strength in eva_insights.get('strengths', []):
                    st.markdown(f"- {strength}")
            
            with col2:
                st.markdown("#### 🔄 Areas for Improvement")
                for improvement in eva_insights.get('improvements', []):
                    st.markdown(f"- {improvement}")
    
    # Display Leo's brand check
    if 'leo' in insights:
        st.subheader("🎯 Brand Alignment (Leo)")
        leo_insights = insights['leo']
        
        with st.expander("View Brand Analysis", expanded=True):
            # Scores
            scores = leo_insights.get('scores', {})
            cols = st.columns(len(scores))
            for col, (metric, score) in zip(cols, scores.items()):
                col.metric(metric, format_score(score))
            
            # Analysis
            if 'analysis' in leo_insights:
                st.markdown("#### 📝 Brand Analysis")
                st.write(leo_insights['analysis'])
            
            # Tone Review
            if 'tone_review' in leo_insights:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### ✅ Tone Strengths")
                    for strength in leo_insights['tone_review'].get('strengths', []):
                        st.markdown(f"- {strength}")
                
                with col2:
                    st.markdown("#### ⚠️ Tone Concerns")
                    for concern in leo_insights['tone_review'].get('concerns', []):
                        st.markdown(f"- {concern}")
            
            # Recommendations
            if 'recommendations' in leo_insights:
                st.markdown("#### 🎯 Recommendations")
                for rec in leo_insights['recommendations']:
                    st.markdown(f"- {rec}")

def export_calendar_data(calendar_df: pd.DataFrame, insights: Dict[str, Any], selected_sections: List[str], selected_platforms: List[str]) -> Dict:
    """Export calendar data and insights based on selected sections and platforms."""
    export_data = {}
    
    # Filter calendar by selected platforms
    filtered_df = calendar_df[calendar_df['Platform'].isin(selected_platforms)]
    
    # Export calendar if selected
    if 'calendar' in selected_sections:
        export_data['calendar'] = filtered_df.to_dict('records')
    
    # Export insights if selected
    if 'insights' in selected_sections:
        export_data['insights'] = {}
        if 'mira' in insights and 'market_analysis' in selected_sections:
            export_data['insights']['market_analysis'] = insights['mira']
        if 'eva' in insights and 'content_evaluation' in selected_sections:
            export_data['insights']['content_evaluation'] = insights['eva']
        if 'leo' in insights and 'brand_alignment' in selected_sections:
            export_data['insights']['brand_alignment'] = insights['leo']
    
    return export_data

def main():
    # Initialize session state
    if "mode" not in st.session_state:
        st.session_state.mode = "Full Team Brainstorm"

    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = AgentManager()

    if "campaign_history" not in st.session_state:
        st.session_state.campaign_history = []

    # Main app layout
    st.title("📅 Ghostwriter Teams - Content Calendar")
    st.markdown("### AI-Powered Content Calendar Generation")

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        num_weeks = st.slider("Number of Weeks", min_value=1, max_value=12, value=4)
        platforms = st.multiselect(
            "Select Platforms",
            ["LinkedIn", "Twitter", "Instagram", "Facebook"],
            default=["LinkedIn", "Twitter"]
        )
        theme = st.text_input("Content Theme", placeholder="e.g., AI Technology Trends")
        
        st.markdown("---")
        st.markdown("### Agent Team")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("👩‍💼 **Max**")
            st.caption("Content Creator")
            st.markdown("🔍 **Mira**")
            st.caption("Trend Analyst")
        with col2:
            st.markdown("👨‍💼 **Leo**")
            st.caption("Brand Guardian")
            st.markdown("👩‍🏫 **Eva**")
            st.caption("Quality Assessor")

    # Main content area
    tab1, tab2, tab3 = st.tabs(["Calendar", "Analytics", "Team Insights"])
    
    with tab1:
        if st.button("Generate Calendar"):
            if not theme:
                st.error("Please enter a content theme")
            elif not platforms:
                st.error("Please select at least one platform")
            else:
                with st.spinner("Generating your content calendar..."):
                    try:
                        # Generate calendar using agent manager
                        calendar_text = st.session_state.agent_manager.generate_calendar(
                            num_weeks=num_weeks,
                            platforms=platforms,
                            theme=theme
                        )
                        
                        if calendar_text:
                            # Parse calendar to DataFrame
                            df = parse_calendar_to_df(calendar_text)
                            
                            if not df.empty:
                                # Display calendar overview
                                st.success("Calendar generated successfully!")
                                st.markdown("### 📅 Content Calendar")
                                
                                # Add filters
                                col1, col2 = st.columns(2)
                                with col1:
                                    selected_platform = st.selectbox(
                                        "Filter by Platform",
                                        ["All"] + list(df["Platform"].unique())
                                    )
                                with col2:
                                    selected_type = st.selectbox(
                                        "Filter by Type",
                                        ["All"] + list(df["Type"].unique())
                                    )
                                
                                # Apply filters
                                filtered_df = df.copy()
                                if selected_platform != "All":
                                    filtered_df = filtered_df[filtered_df["Platform"] == selected_platform]
                                if selected_type != "All":
                                    filtered_df = filtered_df[filtered_df["Type"] == selected_type]
                                
                                # Display calendar
                                st.dataframe(
                                    filtered_df,
                                    use_container_width=True,
                                    column_config={
                                        "Date": st.column_config.DateColumn(
                                            "Date",
                                            format="MMM DD, YYYY"
                                        ),
                                        "Platform": st.column_config.Column(
                                            "Platform",
                                            width="small"
                                        ),
                                        "Type": st.column_config.Column(
                                            "Type",
                                            width="small"
                                        ),
                                        "Topic": st.column_config.Column(
                                            "Topic",
                                            width="medium"
                                        ),
                                        "Copy": st.column_config.TextColumn(
                                            "Copy",
                                            width="large",
                                            help="The content copy for this post"
                                        )
                                    }
                                )
                                
                                # Export options
                                st.markdown("### 📥 Export Options")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    csv = export_to_csv(filtered_df)
                                    st.download_button(
                                        "📊 Export to CSV",
                                        csv,
                                        file_name=f"content_calendar_{datetime.now().strftime('%Y%m%d')}.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                                
                                with col2:
                                    pdf = export_to_pdf(filtered_df)
                                    st.download_button(
                                        "📄 Export to PDF",
                                        pdf,
                                        file_name=f"content_calendar_{datetime.now().strftime('%Y%m%d')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                            else:
                                st.error("Could not parse the calendar data. Please try again.")
                        else:
                            st.error("Could not generate the calendar. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.error("Please try again with different parameters or contact support if the issue persists.")

    with tab2:
        st.markdown("### 📊 Content Analytics")
        
        if "calendar_text" not in st.session_state:
            st.warning("Please generate a content calendar first to view analytics.")
        else:
            try:
                # Get Eva's scores
                scores = st.session_state.agent_manager.score_calendar_with_eva(st.session_state.calendar_text)
                
                if scores:
                    # Display scores
                    st.markdown("#### Content Quality Scores")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Content Variety",
                            format_score_indicator(scores["Content Variety"]),
                            help="How diverse and engaging the content mix is"
                        )
                    
                    with col2:
                        st.metric(
                            "Message Clarity",
                            format_score_indicator(scores["Message Clarity"]),
                            help="How clear and effective the messaging is"
                        )
                    
                    with col3:
                        st.metric(
                            "Platform Fit",
                            format_score_indicator(scores["Platform Fit"]),
                            help="How well content is optimized for each platform"
                        )
                    
                    with col4:
                        st.metric(
                            "Overall Impact",
                            format_score_indicator(scores["Overall Impact"]),
                            help="The predicted effectiveness of the content strategy"
                        )
                    
                    # Display Eva's analysis
                    if "analysis" in scores:
                        st.markdown("#### Detailed Analysis")
                        st.markdown(scores["analysis"])
                    
                    # Display strengths and improvements
                    if "strengths" in scores and "improvements" in scores:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 💪 Strengths")
                            for strength in scores["strengths"]:
                                st.markdown(f"- {strength}")
                        
                        with col2:
                            st.markdown("#### 🎯 Areas for Improvement")
                            for improvement in scores["improvements"]:
                                st.markdown(f"- {improvement}")
                    
                    # Display content distribution
                    st.markdown("#### 📈 Content Distribution")
                    
                    # Parse calendar to get distribution data
                    df = parse_calendar_to_df(st.session_state.calendar_text)
                    
                    if not df.empty:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Platform distribution
                            platform_counts = df["Platform"].value_counts()
                            st.bar_chart(platform_counts)
                            st.caption("Content Distribution by Platform")
                        
                        with col2:
                            # Content type distribution
                            type_counts = df["Type"].value_counts()
                            st.bar_chart(type_counts)
                            st.caption("Content Distribution by Type")
                else:
                    st.error("Could not analyze the calendar. Please try generating a new one.")
                
            except Exception as e:
                st.error(f"An error occurred while analyzing the calendar: {str(e)}")
                st.error("Please try generating a new calendar or contact support if the issue persists.")

    with tab3:
        st.markdown("### Team Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Trend Analysis")
            # TODO: Add Mira's insights
            
        with col2:
            st.markdown("#### Brand Alignment")
            # TODO: Add Leo's feedback

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ by Ghostwriter Teams</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
