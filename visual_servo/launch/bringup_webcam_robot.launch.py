# launch/bringup_webcam_robot.launch.py

from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = FindPackageShare('visual_servo')
    webcam_robot_params = PathJoinSubstitution([pkg_share, 'params', 'webcam_robot.yaml'])

    # Create the webcam node
    webcam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='webcam',
        output='screen',
        parameters=[{
            'video_device': '/dev/video0',
            'image_width': 1280,
            'image_height': 720,
            'pixel_format': 'yuyv',
            'camera_frame_id': 'webcam',
            'camera_name': 'webcam'
        }]
    )

    # Create the MAVROS node
    mavros_node = Node(
        package='mavros',
        executable='mavros_node',
        name='mavros_node',
        output='screen',
        parameters=[webcam_robot_params]
    )

    # Create the visual servo node
    visual_servo_node = Node(
        package='visual_servo',
        executable='visual_servo_node',
        name='visual_servo_node',
        output='screen',
        parameters=[webcam_robot_params]
    )

    # Handle graceful shutdown for all nodes
    webcam_shutdown = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=webcam_node,
            on_exit=lambda event, context: print(f"Webcam node exited with code {event.returncode}")
        )
    )

    mavros_shutdown = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=mavros_node,
            on_exit=lambda event, context: print(f"MAVROS node exited with code {event.returncode}")
        )
    )

    visual_servo_shutdown = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=visual_servo_node,
            on_exit=lambda event, context: print(f"Visual servo node exited with code {event.returncode}")
        )
    )

    return LaunchDescription([
        webcam_node,
        mavros_node,
        visual_servo_node,
        webcam_shutdown,
        mavros_shutdown,
        visual_servo_shutdown,
    ]) 