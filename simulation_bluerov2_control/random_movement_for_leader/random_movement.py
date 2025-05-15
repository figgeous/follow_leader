#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Wrench, Vector3
import time
import random
import signal
import sys

# Set fixed random seed for reproducibility
random.seed(42)

class RandomMovementController(Node):
    def __init__(self):
        super().__init__('random_movement_controller')
        
        # Set up signal handler
        self._shutdown_requested = False
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Create publisher for wrench commands
        self.wrench_pub = self.create_publisher(
            Wrench,
            '/bluerov2_2/wrench',
            10)
        
        # Parameters (with defaults)
        self.declare_parameter('forward_force', 2.0)
        self.declare_parameter('yaw_torque', 5.0)
        self.declare_parameter('turn_duration_ms', 1000)
        self.declare_parameter('interval_between_turns_ms', 2000)
        self.declare_parameter('total_runtime_sec', 300.0)
        
        # Load parameters
        self.forward_force = self.get_parameter('forward_force').value
        self.yaw_torque = self.get_parameter('yaw_torque').value
        self.turn_duration = self.get_parameter('turn_duration_ms').value / 1000.0  # convert to seconds
        self.interval_between_turns = self.get_parameter('interval_between_turns_ms').value / 1000.0  # convert to seconds
        self.total_runtime = self.get_parameter('total_runtime_sec').value
        
        # Movement states
        self.FORWARD = 0
        self.TURNING_LEFT = 1
        self.TURNING_RIGHT = 2
        
        # Initialize state
        self.current_state = self.FORWARD
        self.last_state_change = time.time()
        self.start_time = time.time()
        
        # Create timer for control loop (10Hz)
        self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info('random movement Controller started!')
        self.get_logger().info(f'Forward force: {self.forward_force}')
        self.get_logger().info(f'Yaw torque: {self.yaw_torque}')
        self.get_logger().info(f'Turn duration: {self.turn_duration} seconds')
        self.get_logger().info(f'Interval between turns: {self.interval_between_turns} seconds')
        self.get_logger().info(f'Total runtime: {self.total_runtime} seconds')

    def _signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C) by cleaning up and exiting gracefully."""
        if not self._shutdown_requested:
            self._shutdown_requested = True
            self.get_logger().info("Received SIGINT, cleaning up...")
            # Stop the robot first
            self.stop_robot()
            # Then destroy the node
            self.destroy_node()
            # Finally shutdown ROS
            rclpy.shutdown()

    def control_loop(self):
        current_time = time.time()
        
        # Check if total runtime has elapsed
        if current_time - self.start_time > self.total_runtime:
            self.stop_robot()
            self.get_logger().info('Motion completed, stopping robot')
            rclpy.shutdown()
            return
        
        # Check if it's time to change state
        elapsed_since_last_change = current_time - self.last_state_change
        
        if self.current_state == self.FORWARD and elapsed_since_last_change > self.interval_between_turns:
            # Switch between left and right turns
            if self.current_state == self.FORWARD:
                # Randomly choose between left and right turns
                self.current_state = random.choice([self.TURNING_LEFT, self.TURNING_RIGHT])
                
                self.last_state_change = current_time
                self.get_logger().info(f'Changed state to: {"LEFT" if self.current_state == self.TURNING_LEFT else "RIGHT"} turn')
                
        elif (self.current_state == self.TURNING_LEFT or self.current_state == self.TURNING_RIGHT) and elapsed_since_last_change > self.turn_duration:
            # Return to forward motion after turn completes
            self.current_state = self.FORWARD
            self.last_state_change = current_time
            self.get_logger().info('Changed state to: FORWARD')
            
        # Apply the appropriate control based on current state
        self.apply_control()

    def apply_control(self):
        # Create wrench command
        wrench = Wrench()
        
        # Always apply forward force
        wrench.force = Vector3(x=float(self.forward_force), y=0.0, z=0.0)
        
        # Apply yaw torque based on state
        if self.current_state == self.TURNING_LEFT:
            wrench.torque = Vector3(x=0.0, y=0.0, z=float(self.yaw_torque))
        elif self.current_state == self.TURNING_RIGHT:
            wrench.torque = Vector3(x=0.0, y=0.0, z=float(-self.yaw_torque))
        else:  # FORWARD
            wrench.torque = Vector3(x=0.0, y=0.0, z=0.0)
        
        # Publish the wrench command
        self.get_logger().info(f'Publishing wrench: {wrench}')
        self.wrench_pub.publish(wrench)

    def stop_robot(self):
        """Stop the robot by sending zero wrench"""
        try:
            if rclpy.ok():
                wrench = Wrench()
                wrench.force = Vector3(x=0.0, y=0.0, z=0.0)
                wrench.torque = Vector3(x=0.0, y=0.0, z=0.0)
                self.wrench_pub.publish(wrench)
                self.get_logger().info('Robot stopped')
        except Exception as e:
            if rclpy.ok():
                self.get_logger().warn(f"Failed to stop robot during cleanup: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = RandomMovementController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('random movement interrupted')
    except Exception as e:
        node.get_logger().error(f'Error occurred: {str(e)}')
    finally:
        # Only cleanup if shutdown hasn't been requested
        if not node._shutdown_requested:
            if rclpy.ok():
                node.stop_robot()
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main() 