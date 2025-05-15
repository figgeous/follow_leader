#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import glob
from datetime import datetime
import os

def load_latest_csv_files():
    """Load the most recent CSV files for both BlueROV2s from the logs directory."""
    log_dir = Path('logs')
    if not log_dir.exists():
        raise FileNotFoundError("No logs directory found!")
    
    # Get the most recent files for both BlueROV2s
    bluerov1_files = sorted(log_dir.glob('bluerov2_1_pose_*.csv'))
    bluerov2_files = sorted(log_dir.glob('bluerov2_2_pose_*.csv'))
    
    if not bluerov1_files or not bluerov2_files:
        raise FileNotFoundError("No pose CSV files found!")
    
    latest_file1 = bluerov1_files[-1]
    latest_file2 = bluerov2_files[-1]
    
    print(f"Processing files:\n{latest_file1}\n{latest_file2}")
    
    return pd.read_csv(latest_file1), pd.read_csv(latest_file2)

def plot_trajectories(df1, df2):
    """Plot the horizontal trajectories of both BlueROV2s."""
    # Create figure and axis with compact layout
    plt.figure(figsize=(8, 6))
    
    # Plot the trajectories
    plt.plot(df1['x'], df1['y'], 'b-', label='Follower', linewidth=1.5)
    plt.plot(df2['x'], df2['y'], 'r-', label='Leader', linewidth=1.5)
    
    # Plot start and end points for both robots
    plt.plot(df1['x'].iloc[0], df1['y'].iloc[0], 'bo', label='Follower Start', markersize=6)
    plt.plot(df1['x'].iloc[-1], df1['y'].iloc[-1], 'b*', label='Follower End', markersize=6)
    plt.plot(df2['x'].iloc[0], df2['y'].iloc[0], 'ro', label='Leader Start', markersize=6)
    plt.plot(df2['x'].iloc[-1], df2['y'].iloc[-1], 'r*', label='Leader End', markersize=6)
    
    # Add arrows to show direction of travel
    # Plot arrows every 100 points (adjust this number as needed)
    arrow_interval = 100
    
    # Arrows for Follower
    for i in range(0, len(df1)-1, arrow_interval):
        dx = df1['x'].iloc[i+1] - df1['x'].iloc[i]
        dy = df1['y'].iloc[i+1] - df1['y'].iloc[i]
        plt.arrow(df1['x'].iloc[i], df1['y'].iloc[i], dx, dy,
                 head_width=0.05, head_length=0.1, fc='blue', ec='blue', alpha=0.5)
    
    # Arrows for Leader
    for i in range(0, len(df2)-1, arrow_interval):
        dx = df2['x'].iloc[i+1] - df2['x'].iloc[i]
        dy = df2['y'].iloc[i+1] - df2['y'].iloc[i]
        plt.arrow(df2['x'].iloc[i], df2['y'].iloc[i], dx, dy,
                 head_width=0.05, head_length=0.1, fc='red', ec='red', alpha=0.5)
    
    # Customize the plot
    plt.xlabel('X Position (m)', fontsize=10)
    plt.ylabel('Y Position (m)', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axis('equal')  # Equal aspect ratio
    
    # Create a custom legend with fewer entries to avoid clutter
    handles, labels = plt.gca().get_legend_handles_labels()
    # Only keep unique labels
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8)
    
    # Add timestamp information with smaller font
    start_time = min(
        datetime.fromtimestamp(df1['timestamp'].iloc[0]),
        datetime.fromtimestamp(df2['timestamp'].iloc[0])
    )
    end_time = max(
        datetime.fromtimestamp(df1['timestamp'].iloc[-1]),
        datetime.fromtimestamp(df2['timestamp'].iloc[-1])
    )
    duration = end_time - start_time
    plt.figtext(0.02, 0.02, 
                f'Start: {start_time.strftime("%H:%M:%S")}\n'
                f'End: {end_time.strftime("%H:%M:%S")}\n'
                f'Duration: {duration}',
                fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
    
    # Adjust layout to be more compact
    plt.tight_layout()
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plt.savefig(f'results/bluerov2s_trajectories_{timestamp}.png', 
                dpi=300, bbox_inches='tight')
    plt.savefig(f'results/bluerov2s_trajectories_{timestamp}.pdf', 
                bbox_inches='tight')
    
    # Show the plot
    plt.show()

def main():
    try:
        # Load the most recent CSV files
        df1, df2 = load_latest_csv_files()
        
        # Plot the trajectories
        plot_trajectories(df1, df2)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main() 