#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, LogInfo
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare launch arguments
    forward_force_arg = DeclareLaunchArgument(
        'forward_force',
        default_value='2.0',
        description='Constant forward force to apply'
    )
    
    yaw_torque_arg = DeclareLaunchArgument(
        'yaw_torque',
        default_value='5.0',
        description='Yaw torque to apply during turns'
    )
    
    turn_duration_arg = DeclareLaunchArgument(
        'turn_duration_ms',
        default_value='1000',
        description='Duration of each turn in milliseconds'
    )
    
    interval_arg = DeclareLaunchArgument(
        'interval_between_turns_ms',
        default_value='2000',
        description='Interval between turns in milliseconds'
    )
    
    runtime_arg = DeclareLaunchArgument(
        'total_runtime_sec',
        default_value='300.0',
        description='Total runtime for the random movement in seconds'
    )
    
    # Create the node
    random_movement_node = Node(
        package='random_movement_for_leader',
        executable='random_movement.py',
        name='random_movement_controller',
        output='screen',
        parameters=[{
            'forward_force': LaunchConfiguration('forward_force'),
            'yaw_torque': LaunchConfiguration('yaw_torque'),
            'turn_duration_ms': LaunchConfiguration('turn_duration_ms'),
            'interval_between_turns_ms': LaunchConfiguration('interval_between_turns_ms'),
            'total_runtime_sec': LaunchConfiguration('total_runtime_sec')
        }]
    )

    # Handle startup
    startup_handler = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=random_movement_node,
            on_start=lambda event, context: print("Starting random movement node...")
        )
    )

    # Handle graceful shutdown
    shutdown_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=random_movement_node,
            on_exit=lambda event, context: print(f"Random movement node completed with exit code {event.returncode}")
        )
    )
    
    return LaunchDescription([
        forward_force_arg,
        yaw_torque_arg,
        turn_duration_arg,
        interval_arg,
        runtime_arg,
        startup_handler,
        random_movement_node,
        shutdown_handler
    ]) 