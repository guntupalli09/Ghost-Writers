import pandas as pd
import re
from typing import List, Dict
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging

def parse_calendar_to_df(calendar_text: str) -> pd.DataFrame:
    """Convert calendar markdown text into a pandas DataFrame."""
    try:
        # Split the text into lines and filter out empty lines
        lines = [line.strip() for line in calendar_text.split('\n') if line.strip()]
        
        # Find the start of the table (first line with |)
        table_start = next((i for i, line in enumerate(lines) if line.startswith('|')), -1)
        if table_start == -1:
            raise ValueError("No table found in calendar text")
        
        # Extract header and data rows
        header = lines[table_start]
        data_rows = lines[table_start + 2:]  # Skip header and separator line
        
        # Parse header
        columns = [col.strip() for col in header.split('|')[1:-1]]
        if not columns:
            raise ValueError("No columns found in table header")
        
        # Parse data rows
        data = []
        for row in data_rows:
            if not row.startswith('|'):
                continue
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            if len(cells) != len(columns):
                continue  # Skip malformed rows
            data.append(dict(zip(columns, cells)))
        
        if not data:
            raise ValueError("No valid data rows found in calendar")
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Convert Date column to datetime if it exists
        if 'Date' in df.columns:
            try:
                df['Date'] = pd.to_datetime(df['Date'])
            except:
                # If date parsing fails, keep as string
                pass
        
        return df
        
    except Exception as e:
        logging.error(f"Error parsing calendar: {str(e)}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['Date', 'Platform', 'Type', 'Topic', 'Copy'])

def chunk_calendar_by_weeks(calendar_text: str) -> List[str]:
    """
    Split calendar text into weekly chunks.
    
    Args:
        calendar_text (str): The calendar markdown text
        
    Returns:
        List[str]: List of weekly calendar chunks
    """
    return [chunk.strip() for chunk in calendar_text.split("---\n\n") if chunk.strip()]

def format_score_indicator(score: int) -> str:
    """
    Format score with appropriate emoji indicator.
    
    Args:
        score (int): The score value
        
    Returns:
        str: Formatted score with emoji
    """
    if score < 6:
        return f"🔴 {score}/10"
    elif score < 9:
        return f"🟡 {score}/10"
    else:
        return f"🟢 {score}/10"

def create_platform_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates a pie chart showing the distribution of posts across platforms.
    
    Args:
        df (pd.DataFrame): Calendar DataFrame with platform information
        
    Returns:
        go.Figure: Plotly figure object containing the pie chart
    """
    platform_counts = df['Platform'].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=platform_counts.index,
        values=platform_counts.values,
        hole=.3
    )])
    fig.update_layout(
        showlegend=True,
        height=300,
        margin=dict(t=0, b=0, l=0, r=0)
    )
    return fig

def get_campaign_summary(df: pd.DataFrame) -> Dict:
    """
    Generates a summary of campaign metrics from a DataFrame.
    
    Args:
        df (pd.DataFrame): Campaign DataFrame
        
    Returns:
        Dict: Dictionary containing campaign metrics
    """
    if df is None or df.empty:
        return {
            'total_posts': 0,
            'posts_per_week': 0,
            'duration_weeks': 0,
            'platforms': [],
            'platform_distribution': {}
        }
    
    # Convert dates to datetime if they aren't already
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate basic metrics
    date_range = (df['date'].max() - df['date'].min()).days
    duration_weeks = max(1, date_range / 7)  # Avoid division by zero
    total_posts = len(df)
    posts_per_week = total_posts / duration_weeks
    
    # Get platform distribution
    platform_counts = df['platform'].value_counts().to_dict()
    platforms = list(platform_counts.keys())
    
    return {
        'total_posts': total_posts,
        'posts_per_week': round(posts_per_week, 2),
        'duration_weeks': round(duration_weeks, 1),
        'platforms': platforms,
        'platform_distribution': platform_counts
    }

def format_campaign_title(date: str, platforms: list) -> str:
    """
    Creates a formatted title for a campaign entry.
    
    Args:
        date (str): Campaign creation date
        platforms (list): List of platforms used in the campaign
        
    Returns:
        str: Formatted campaign title
    """
    platform_str = ', '.join(platforms) if platforms else 'No platforms'
    return f"{date} ({platform_str})"

def create_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create an interactive timeline visualization of the content calendar using Plotly.
    
    Args:
        df (pd.DataFrame): DataFrame containing calendar data with columns:
            - date: Date of the content
            - platform: Platform for the content
            - content: Content description
            - time: Time of posting (optional)
    
    Returns:
        go.Figure: Plotly figure object containing the timeline visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for visualization",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig
    
    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Create color map for platforms
    platforms = df['platform'].unique()
    colors = px.colors.qualitative.Set3[:len(platforms)]
    color_map = dict(zip(platforms, colors))
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each platform
    for platform in platforms:
        platform_data = df[df['platform'] == platform]
        
        fig.add_trace(go.Scatter(
            x=platform_data['date'],
            y=[platform] * len(platform_data),
            mode='markers+text',
            name=platform,
            marker=dict(
                size=12,
                color=color_map[platform],
                line=dict(width=1, color='DarkSlateGrey')
            ),
            text=platform_data['content'],
            hovertemplate=(
                "<b>Date:</b> %{x|%Y-%m-%d}<br>" +
                "<b>Platform:</b> " + platform + "<br>" +
                "<b>Content:</b> %{text}<br>" +
                "<extra></extra>"
            )
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Content Calendar Timeline",
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        height=400,
        xaxis=dict(
            title="Date",
            showgrid=True,
            rangeslider=dict(visible=True)
        ),
        yaxis=dict(
            title="Platform",
            showgrid=True
        ),
        hovermode='closest'
    )
    
    return fig

def compare_campaigns(df1: pd.DataFrame, df2: pd.DataFrame, name1: str = "Campaign 1", name2: str = "Campaign 2") -> Dict:
    """
    Compares two campaigns and generates comparison metrics and visualizations.
    
    Args:
        df1 (pd.DataFrame): First campaign DataFrame
        df2 (pd.DataFrame): Second campaign DataFrame
        name1 (str): Name of first campaign
        name2 (str): Name of second campaign
        
    Returns:
        Dict: Dictionary containing comparison metrics and figures
    """
    if df1 is None or df2 is None or df1.empty or df2.empty:
        return {}
        
    # Get summaries for both campaigns
    summary1 = get_campaign_summary(df1)
    summary2 = get_campaign_summary(df2)
    
    # Calculate differences
    diff_metrics = {
        'total_posts_diff': summary2['total_posts'] - summary1['total_posts'],
        'posts_per_week_diff': summary2['posts_per_week'] - summary1['posts_per_week'],
        'duration_diff': summary2['duration_weeks'] - summary1['duration_weeks'],
        'platform_overlap': len(set(summary1['platforms']).intersection(set(summary2['platforms']))),
        'unique_platforms': {
            name1: list(set(summary1['platforms']) - set(summary2['platforms'])),
            name2: list(set(summary2['platforms']) - set(summary1['platforms']))
        }
    }
    
    # Create comparison bar chart
    comparison_fig = go.Figure(data=[
        go.Bar(name=name1, x=['Total Posts', 'Posts/Week', 'Duration (weeks)'],
               y=[summary1['total_posts'], summary1['posts_per_week'], summary1['duration_weeks']]),
        go.Bar(name=name2, x=['Total Posts', 'Posts/Week', 'Duration (weeks)'],
               y=[summary2['total_posts'], summary2['posts_per_week'], summary2['duration_weeks']])
    ])
    
    comparison_fig.update_layout(
        barmode='group',
        title='Campaign Comparison',
        plot_bgcolor='white',
        showlegend=True,
        height=400,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return {
        'summary1': summary1,
        'summary2': summary2,
        'differences': diff_metrics,
        'comparison_chart': comparison_fig
    }