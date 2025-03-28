import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

def generate_build_success_chart(build_data: List[Dict[str, Any]]) -> str:
    """
    Generate a chart showing build success rate over time
    
    Args:
        build_data: List of build prediction data
        
    Returns:
        Base64 encoded image
    """
    # Convert to DataFrame
    df = pd.DataFrame(build_data)
    
    # Ensure datetime format
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Group by day and calculate success rate
    df['day'] = df['created_at'].dt.date
    df['success'] = df['status'] == 'success'
    success_rate = df.groupby('day')['success'].mean() * 100
    
    # Create figure
    plt.figure(figsize=(10, 6))
    plt.plot(success_rate.index, success_rate.values, marker='o', linestyle='-', color='#4CAF50')
    plt.title('Build Success Rate Over Time')
    plt.xlabel('Date')
    plt.ylabel('Success Rate (%)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def generate_build_time_chart(build_data: List[Dict[str, Any]]) -> str:
    """
    Generate a chart showing actual vs estimated build time
    
    Args:
        build_data: List of build prediction data
        
    Returns:
        Base64 encoded image
    """
    # Convert to DataFrame
    df = pd.DataFrame(build_data)
    
    # Filter out builds without actual build time
    df = df.dropna(subset=['actual_build_time'])
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Scatter plot
    plt.scatter(df['estimated_build_time'], df['actual_build_time'], 
                alpha=0.7, s=50, c='#2196F3')
    
    # Perfect prediction line
    max_time = max(df['estimated_build_time'].max(), df['actual_build_time'].max())
    plt.plot([0, max_time], [0, max_time], 'r--', alpha=0.7)
    
    plt.title('Estimated vs Actual Build Time')
    plt.xlabel('Estimated Build Time (seconds)')
    plt.ylabel('Actual Build Time (seconds)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def generate_system_metrics_chart(metrics_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Generate a chart showing system metrics over time
    
    Args:
        metrics_data: Dictionary with metric types as keys and lists of metric data as values
        
    Returns:
        Base64 encoded image
    """
    # Create figure with subplots
    fig, axes = plt.subplots(len(metrics_data), 1, figsize=(10, 3*len(metrics_data)), sharex=True)
    
    # If only one metric, axes will not be an array
    if len(metrics_data) == 1:
        axes = [axes]
    
    # Colors for different metrics
    colors = {
        'cpu': '#F44336',
        'memory': '#2196F3',
        'disk': '#4CAF50',
        'network': '#FFC107'
    }
    
    # Plot each metric
    for i, (metric_type, data) in enumerate(metrics_data.items()):
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Ensure datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Plot
        color = colors.get(metric_type, '#9C27B0')
        axes[i].plot(df['timestamp'], df['value'], marker='.', linestyle='-', color=color)
        axes[i].set_title(f'{metric_type.capitalize()} Usage')
        axes[i].set_ylabel('Usage (%)')
        axes[i].grid(True, linestyle='--', alpha=0.7)
        
        # Add threshold line if available
        if 'threshold' in df.columns:
            threshold = df['threshold'].iloc[0]
            axes[i].axhline(y=threshold, color='r', linestyle='--', alpha=0.7)
    
    # Set x-label for the bottom subplot
    axes[-1].set_xlabel('Time')
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def generate_anomaly_chart(anomalies_data: List[Dict[str, Any]]) -> str:
    """
    Generate a chart showing anomalies
    
    Args:
        anomalies_data: List of anomaly data
        
    Returns:
        Base64 encoded image
    """
    # Convert to DataFrame
    df = pd.DataFrame(anomalies_data)
    
    # Ensure datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Count anomalies by metric type and severity
    severity_counts = df.groupby(['metric_type', 'severity']).size().unstack(fill_value=0)
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Create bar chart
    severity_counts.plot(kind='bar', stacked=True, ax=plt.gca(),
                         color=['#4CAF50', '#FFC107', '#F44336'])
    
    plt.title('Anomalies by Metric Type and Severity')
    plt.xlabel('Metric Type')
    plt.ylabel('Number of Anomalies')
    plt.legend(title='Severity')
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def generate_feature_importance_chart(feature_importance: Dict[str, float]) -> str:
    """
    Generate a chart showing feature importance
    
    Args:
        feature_importance: Dictionary mapping feature names to importance values
        
    Returns:
        Base64 encoded image
    """
    # Sort features by importance
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    features = [x[0] for x in sorted_features]
    importance = [x[1] for x in sorted_features]
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Create horizontal bar chart
    plt.barh(features, importance, color='#2196F3')
    
    plt.title('Feature Importance')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.grid(True, linestyle='--', alpha=0.7, axis='x')
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def generate_dashboard_summary_charts(
    build_data: List[Dict[str, Any]],
    metrics_data: Dict[str, List[Dict[str, Any]]],
    anomalies_data: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Generate all charts for dashboard summary
    
    Args:
        build_data: List of build prediction data
        metrics_data: Dictionary with metric types as keys and lists of metric data as values
        anomalies_data: List of anomaly data
        
    Returns:
        Dictionary with chart names as keys and base64 encoded images as values
    """
    charts = {}
    
    # Generate build success chart
    try:
        charts['build_success'] = generate_build_success_chart(build_data)
    except Exception as e:
        print(f"Error generating build success chart: {e}")
    
    # Generate build time chart
    try:
        charts['build_time'] = generate_build_time_chart(build_data)
    except Exception as e:
        print(f"Error generating build time chart: {e}")
    
    # Generate system metrics chart
    try:
        charts['system_metrics'] = generate_system_metrics_chart(metrics_data)
    except Exception as e:
        print(f"Error generating system metrics chart: {e}")
    
    # Generate anomaly chart
    try:
        charts['anomalies'] = generate_anomaly_chart(anomalies_data)
    except Exception as e:
        print(f"Error generating anomaly chart: {e}")
    
    return charts
