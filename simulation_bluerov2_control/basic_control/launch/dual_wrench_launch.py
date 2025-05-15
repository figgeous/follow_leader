from simple_launch import SimpleLauncher

def generate_launch_description():
    sl = SimpleLauncher(use_sim_time=True)
    
    sl.declare_arg('rviz', default_value=True)
    
    # First robot group
    with sl.group(ns='bluerov2_1'):
        # Launch slider_publisher for first robot
        sl.node('slider_publisher', 'slider_publisher', name='wrench_control',
                arguments=[sl.find('bluerov2_control', 'wrench_bluerov2_1.yaml', 'config')])
        
        # Launch thruster manager for first robot
        sl.node('thruster_manager', 'thruster_manager_node', 
                parameters=[{
                    'control_frame': 'bluerov2_1/base_link',
                    'publish_joint_state': True,
                    'tam': {
                        'deadzone': 1.0,
                        'max_thrust': 40.0,
                        'min_thrust': -40.0,
                        'thruster_prefix': '',
                        'use_gz_plugin': True
                    },
                    'use_sim_time': True
                }])
    
    # Second robot group
    with sl.group(ns='bluerov2_2'):
        # Launch slider_publisher for second robot
        sl.node('slider_publisher', 'slider_publisher', name='wrench_control',
                arguments=[sl.find('bluerov2_control', 'wrench_bluerov2_2.yaml', 'config')])
        
        # Launch thruster manager for second robot
        sl.node('thruster_manager', 'thruster_manager_node',
                parameters=[{
                    'control_frame': 'bluerov2_2/base_link',
                    'publish_joint_state': True,
                    'tam': {
                        'deadzone': 1.0,
                        'max_thrust': 40.0,
                        'min_thrust': -40.0,
                        'thruster_prefix': '',
                        'use_gz_plugin': True
                    },
                    'use_sim_time': True
                }])
    
    # Launch RViz if requested
    with sl.group(if_arg='rviz'):
        sl.include('bluerov2_control', 'rviz_launch.py',
                   launch_arguments={'namespace': 'bluerov2_1', 'use_sim_time': sl.sim_time})
    
    return sl.launch_description() 