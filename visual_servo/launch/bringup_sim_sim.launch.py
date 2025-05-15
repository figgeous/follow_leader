# launch/bringup_sim_sim.launch.py

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share     = FindPackageShare('visual_servo')
    sim_params    = PathJoinSubstitution([pkg_share, 'params', 'sim_sim.yaml'])

    # let us override the topic on the command line if we need to
    declare_topic = DeclareLaunchArgument(
        'image_topic',
        default_value='/bluerov2_1/image',
        description='The raw Image topic from Gazebo'
    )
    image_topic = LaunchConfiguration('image_topic')

    # Create the visual servo node
    visual_servo_node = Node(
        package='visual_servo',
        executable='visual_servo_node',
        name='visual_servo_node',
        output='screen',
        # first load sim_sim.yaml, then override...
        parameters=[
            sim_params,
            {
                'image_topic':    image_topic,
                'use_sim_time':   True,
                # ensure camera_params is never empty
                'camera_params':  [1000.0, 1000.0, 640.0, 360.0],
            }
        ],
    )

    # Handle graceful shutdown
    shutdown_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=visual_servo_node,
            on_exit=lambda event, context: print(f"Visual servo node exited with code {event.returncode}")
        )
    )

    return LaunchDescription([
        declare_topic,
        visual_servo_node,
        shutdown_handler,

        # # bring up RQt Image View so you can *see* whether images are actually
        # # on the topic or not
        # Node(
        #     package='rqt_image_view',
        #     executable='rqt_image_view',
        #     name='rqt_image_view',
        #     output='screen',
        #     arguments=['--force-discover', image_topic],
        # ),
    ])
