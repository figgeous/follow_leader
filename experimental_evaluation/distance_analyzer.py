#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path
import glob
import os
from datetime import datetime

def load_latest_csv_files():
    """Load the most recent CSV files from the logs directory."""
    log_dir = Path('logs')
    if not log_dir.exists():
        raise FileNotFoundError("No logs directory found!")
    
    # Get the most recent files for each robot
    bluerov1_files = sorted(log_dir.glob('bluerov2_1_pose_*.csv'))
    bluerov2_files = sorted(log_dir.glob('bluerov2_2_pose_*.csv'))
    
    if not bluerov1_files or not bluerov2_files:
        raise FileNotFoundError("No pose CSV files found!")
    
    latest_file1 = bluerov1_files[-1]
    latest_file2 = bluerov2_files[-1]
    
    print(f"Processing files:\n{latest_file1}\n{latest_file2}")
    
    return pd.read_csv(latest_file1), pd.read_csv(latest_file2)

def calculate_distances(df1, df2):
    """Calculate Euclidean distances between poses using interpolation."""
    # Convert timestamps to datetime index for better interpolation
    df1 = df1.set_index('timestamp')
    df2 = df2.set_index('timestamp')
    
    # Get the time range that covers both datasets
    start_time = max(df1.index.min(), df2.index.min())
    end_time = min(df1.index.max(), df2.index.max())
    
    # Create a new time index with regular intervals
    # Use the average time step from both datasets
    time_step1 = np.mean(np.diff(df1.index))
    time_step2 = np.mean(np.diff(df2.index))
    time_step = min(time_step1, time_step2)  # Use the smaller time step for better resolution
    
    new_index = np.arange(start_time, end_time, time_step)
    
    # Interpolate positions for both robots
    interpolated_pos1 = pd.DataFrame(index=new_index)
    interpolated_pos2 = pd.DataFrame(index=new_index)
    
    # Interpolate each coordinate separately
    for coord in ['x', 'y', 'z']:
        interpolated_pos1[coord] = np.interp(new_index, df1.index, df1[coord])
        interpolated_pos2[coord] = np.interp(new_index, df2.index, df2[coord])
    
    # Calculate distances
    distances = np.sqrt(
        (interpolated_pos1['x'] - interpolated_pos2['x'])**2 +
        (interpolated_pos1['y'] - interpolated_pos2['y'])**2 +
        (interpolated_pos1['z'] - interpolated_pos2['z'])**2
    )
    
    return distances.values, new_index

def calculate_statistics(distances):
    """Calculate basic statistics of the distances."""
    stats = {
        'mean': np.mean(distances),
        'std': np.std(distances),
        'min': np.min(distances),
        'max': np.max(distances),
        'median': np.median(distances),
        'q1': np.percentile(distances, 25),
        'q3': np.percentile(distances, 75)
    }
    return stats

def save_results(distances, timestamps, stats):
    """Save the results to a CSV file and print statistics."""
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Save distances and timestamps
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_df = pd.DataFrame({
        'timestamp': timestamps,
        'distance': distances
    })
    results_df.to_csv(f'results/distance_analysis_{timestamp}.csv', index=False)
    
    # Save statistics
    stats_df = pd.DataFrame([stats])
    stats_df.to_csv(f'results/distance_stats_{timestamp}.csv', index=False)
    
    # Print statistics
    print("\nDistance Statistics:")
    print(f"Mean distance: {stats['mean']:.3f} meters")
    print(f"Standard deviation: {stats['std']:.3f} meters")
    print(f"Minimum distance: {stats['min']:.3f} meters")
    print(f"Maximum distance: {stats['max']:.3f} meters")
    print(f"Median distance: {stats['median']:.3f} meters")
    print(f"25th percentile: {stats['q1']:.3f} meters")
    print(f"75th percentile: {stats['q3']:.3f} meters")

def main():
    try:
        # Load the most recent CSV files
        df1, df2 = load_latest_csv_files()
        
        # Calculate distances
        distances, timestamps = calculate_distances(df1, df2)
        
        # Calculate statistics
        stats = calculate_statistics(distances)
        
        # Save results and print statistics
        save_results(distances, timestamps, stats)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main() 