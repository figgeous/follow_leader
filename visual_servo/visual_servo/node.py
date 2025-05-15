import rclpy
from rclpy.node import Node
from .image_sources import GazeboImageSource, RobotImageSource, WebcamImageSource
from .controllers    import GazeboController, MavrosController
from .tag_detector   import TagDetector
import cv2
import numpy as np
import time
import signal
import sys

class VisualServoNode(Node):
    def __init__(self):
        """Initialize the Visual Servo Node."""
        super().__init__('visual_servo_node')
        
        signal.signal(signal.SIGINT, self._signal_handler)

        self.declare_parameter('image_source',    'robot')
        self.declare_parameter('image_topic',     '/image_raw')
        self.declare_parameter('controller',      'mavros')
        self.declare_parameter('wrench_topic',    '')
        self.declare_parameter('tag_size',        0.10)
        self.declare_parameter('processing_rate', 2.0)
        self.declare_parameter('camera_params',   [1000.0, 1000.0, 640.0, 360.0])
        self.declare_parameter('detection_threshold', 10.0)
        
        # Control gains & limits
        self.declare_parameter('forward_force',    5.0)
        self.declare_parameter('lateral_force',    0.0)
        self.declare_parameter('vertical_force',   0.0)  # keep it on the surface for now
        self.declare_parameter('yaw_torque',       5.0)
        self.declare_parameter('max_linear_force', 5.0)
        self.declare_parameter('max_angular_torque', 5.0)
        self.declare_parameter('target_distance',  2.0)

        img_src_type = self.get_parameter('image_source').value
        ctrl_type    = self.get_parameter('controller').value
        image_topic  = self.get_parameter('image_topic').value
        wrench_topic = self.get_parameter('wrench_topic').value
        rate         = self.get_parameter('processing_rate').value

        if img_src_type == 'sim':
            self.img_src = GazeboImageSource(self, topic=image_topic)
        elif img_src_type == 'webcam':
            self.img_src = WebcamImageSource(self, topic=image_topic)
        else:
            self.img_src = RobotImageSource(self, topic=image_topic)

        if ctrl_type == 'sim':
            self.controller = GazeboController(self, topic=wrench_topic)
        else:
            self.controller = MavrosController(self)

        # Initialize tag detector
        self.tag_detector = TagDetector(
            self,
            tag_size=self.get_parameter('tag_size').value,
            detection_threshold=self.get_parameter('detection_threshold').value,
            camera_params=self.get_parameter('camera_params').value
        )

        self.create_timer(1.0/rate, self.step)

        cv2.namedWindow('Visual Servo Debug', cv2.WINDOW_NORMAL)

    def _signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C) by cleaning up and exiting gracefully."""
        self.get_logger().info("Received SIGINT, cleaning up...")
        self.cleanup()
        self.destroy_node()
        rclpy.shutdown()
        sys.exit(0)

    def step(self):
        """Main step function to process the image and compute control outputs."""
        result = self.img_src.get_frame()
        if not result:
            self.get_logger().warning('No new frame')
            return
        frame, cam_params = result
        if frame is None or cam_params is None:
            self.get_logger().warning('No frame or camera params')
            return

        # Detect and visualize tags
        frame = self.tag_detector.detect_and_visualize(frame)

        # Compute control outputs
        if self.tag_detector.tag_detected:
            dist_err = self.tag_detector.tag_distance - self.get_parameter('target_distance').value
            lat_err_norm = self.tag_detector.tag_x_offset / (frame.shape[1]/2)

            forward_force = self.get_parameter('forward_force').value
            lateral_force = self.get_parameter('lateral_force').value
            vertical_force = self.get_parameter('vertical_force').value
            yaw_torque_gain = self.get_parameter('yaw_torque').value
            max_linear_force = self.get_parameter('max_linear_force').value
            max_angular_torque = self.get_parameter('max_angular_torque').value

            fx = np.clip(forward_force * dist_err, 
                        -max_linear_force, 
                        max_linear_force)
            fy = np.clip(-lateral_force * lat_err_norm, 
                        -max_linear_force, 
                        max_linear_force)
            fz = np.clip(-vertical_force * self.tag_detector.tag_z_offset, 
                        -max_linear_force, 
                        max_linear_force)
            yaw_torque = np.clip(-yaw_torque_gain * lat_err_norm, 
                                -max_angular_torque, 
                                max_angular_torque)

            fx = forward_force if dist_err > 0 else -forward_force

            self.get_logger().info(f"CMD ⇒ fx:{fx:.2f}, fy:{fy:.2f}, fz:{fz:.2f}, yaw:{yaw_torque:.2f}")
        else:
            fx = fy = fz = yaw_torque = 0.0
            self.get_logger().info("No tag detected - zeroing commands")

        # Send the commands
        self.controller.send_command(fx, fy, fz, yaw_torque)

        # Debug window
        cv2.imshow('Visual Servo Debug', frame)
        cv2.waitKey(1)

    def cleanup(self):
        """Cleanup method to zero thrusters before shutdown."""
        try:
            if rclpy.ok():
                self.get_logger().info("Zeroing thrusters before shutdown")
                # Send multiple zero commands to ensure it takes effect
                for _ in range(3):
                    self.controller.send_command(0.0, 0.0, 0.0, 0.0)
                    time.sleep(0.1)  # Small delay between commands
        except Exception as e:
            if rclpy.ok():
                self.get_logger().warn(f"Failed to zero thrusters during cleanup: {str(e)}")
        finally:
            cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    node = VisualServoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cleanup()
        node.destroy_node()

if __name__ == '__main__':
    main()
