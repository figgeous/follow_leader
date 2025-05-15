# launch/bringup_webcam_sim.launch.py

from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = FindPackageShare('visual_servo')
    webcam_sim_params = PathJoinSubstitution([pkg_share, 'params', 'webcam_sim.yaml'])

    # Create the webcam node
    webcam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='webcam',
        output='screen',
        parameters=[{
            'video_device': '/dev/video0',
            'image_width': 640,
            'image_height': 480,
            'pixel_format': 'yuyv',
            'camera_frame_id': 'webcam',
            'camera_name': 'webcam',
            'framerate': 30.0,
            'brightness': 50,
            'contrast': 50,
            'saturation': 50,
            'sharpness': 7,
            'white_balance_automatic': True,
            'auto_exposure': True,
            'exposure_dynamic_framerate': True,
            'power_line_frequency': 1,  # 50 Hz
            'gamma': 120
        }]
    )

    # Create the visual servo node
    visual_servo_node = Node(
        package='visual_servo',
        executable='visual_servo_node',
        name='visual_servo_node',
        output='screen',
        parameters=[webcam_sim_params]
    )

    # Handle graceful shutdown for both nodes
    webcam_shutdown = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=webcam_node,
            on_exit=lambda event, context: print(f"Webcam node exited with code {event.returncode}")
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
        visual_servo_node,
        webcam_shutdown,
        visual_servo_shutdown,
    ]) 