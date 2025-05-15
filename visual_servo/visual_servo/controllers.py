from geometry_msgs.msg import Wrench, Vector3, TwistStamped
from mavros_msgs.srv import SetMode, CommandBool
import time
import rclpy

class GazeboController:
    def __init__(self, node, topic):
        self.pub = node.create_publisher(Wrench, topic, 10)
    def send_command(self, fx, fy, fz, yaw_torque):
        w = Wrench()
        w.force.x, w.force.y, w.force.z = fx, fy, fz
        w.torque.z = yaw_torque
        self.pub.publish(w)

class MavrosController:
    def __init__(self, node):
        self.node = node
        self.pub = node.create_publisher(TwistStamped, '/mavros/setpoint_velocity/cmd_vel', 10)
        
        # Set up MAVROS service clients
        self.set_mode_client = node.create_client(SetMode, '/mavros/set_mode')
        self.arm_client = node.create_client(CommandBool, '/mavros/cmd/arming')
        
        # Wait for services
        while not self.set_mode_client.wait_for_service(timeout_sec=5.0):
            node.get_logger().info('Waiting for /mavros/set_mode service...')
        while not self.arm_client.wait_for_service(timeout_sec=5.0):
            node.get_logger().info('Waiting for /mavros/cmd/arming service...')

        # Initialize robot
        self.send_initial_setpoints()
        self.arm_robot()
        if not self.set_mode('GUIDED'):
            node.get_logger().error('Failed to enter GUIDED mode')
            return

    def send_initial_setpoints(self):
        """Send initial setpoints before switching to GUIDED mode"""
        self.node.get_logger().info('Sending initial setpoints...')
        msg = TwistStamped()
        msg.header.frame_id = ''
        msg.twist.linear.x = 0.0
        msg.twist.linear.y = 0.0
        msg.twist.linear.z = 0.0
        msg.twist.angular.x = 0.0
        msg.twist.angular.y = 0.0
        msg.twist.angular.z = 0.0

        # Send setpoints for 2 seconds
        start_time = time.time()
        while time.time() - start_time < 2.0:
            msg.header.stamp = self.node.get_clock().now().to_msg()
            self.pub.publish(msg)
            time.sleep(0.1)
        self.node.get_logger().info('Initial setpoints sent')

    def set_mode(self, mode_name: str) -> bool:
        req = SetMode.Request()
        req.base_mode = 0
        req.custom_mode = mode_name

        future = self.set_mode_client.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)
        return bool(future.result() and future.result().mode_sent)

    def arm_robot(self):
        req = CommandBool.Request()
        req.value = True
        future = self.arm_client.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)
        
        if future.result().success:
            self.node.get_logger().info('Successfully armed the robot')
        else:
            self.node.get_logger().error(f'Failed to arm: result={future.result().result}')

    def send_command(self, vx, vy, vz, yaw):
        msg = TwistStamped()
        msg.header.frame_id = ''
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.twist.linear.x = float(vx)
        msg.twist.linear.y = float(vy)
        msg.twist.linear.z = float(vz)
        msg.twist.angular.z = float(yaw)
        self.pub.publish(msg)
