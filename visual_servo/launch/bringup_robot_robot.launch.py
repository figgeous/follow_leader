# launch/bringup_robot_robot.launch.py

from launch import LaunchDescription
from launch.actions import RegisterEventHandler, SetEnvironmentVariable
from launch.event_handlers import OnProcessExit
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('visual_servo')
    real_params = PathJoinSubstitution([pkg_share, 'params', 'robot_robot.yaml'])

    # Set GSCAM configuration
    gscam_config = SetEnvironmentVariable(
        'GSCAM_CONFIG',
        'udpsrc port=5600 caps="application/x-rtp, media=(string)video, encoding-name=(string)H264, clock-rate=(int)90000, payload=(int)96" ! rtph264depay ! avdec_h264 ! videoconvert'
    )

    # Create the GSCAM node
    gscam_node = Node(
        package='gscam2',
        executable='gscam_main',
        name='gscam_node',
        output='screen'
    )

    # Create the MAVROS node
    mavros_node = Node(
        package='mavros',
        executable='mavros_node',
        name='mavros_node',
        output='screen',
        parameters=[real_params]
    )

    # Create the visual servo node
    visual_servo_node = Node(
        package='visual_servo',
        executable='visual_servo_node',
        name='visual_servo_node',
        output='screen',
        parameters=[real_params]
    )

    # Handle graceful shutdown
    shutdown_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=visual_servo_node,
            on_exit=lambda event, context: print(f"Visual servo node exited with code {event.returncode}")
        )
    )

    return LaunchDescription([
        gscam_config,
        gscam_node,
        mavros_node,
        visual_servo_node,
        shutdown_handler,
    ])