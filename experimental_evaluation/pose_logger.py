#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import csv
from datetime import datetime
import os

class PoseLogger(Node):
    def __init__(self):
        super().__init__('pose_logger')
        
        # Create subscribers for both BlueROV2s
        self.sub1 = self.create_subscription(
            Pose,
            '/bluerov2_1/pose_gt',
            self.pose1_callback,
            10)
        self.sub2 = self.create_subscription(
            Pose,
            '/bluerov2_2/pose_gt',
            self.pose2_callback,
            10)
            
        # Create CSV files
        self.create_csv_files()
        
        self.get_logger().info('Pose logger node started')
        
    def create_csv_files(self):
        # Create directory for logs if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create CSV files with headers
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # File for BlueROV2_1
        self.file1 = open(f'logs/bluerov2_1_pose_{timestamp}.csv', 'w')
        self.writer1 = csv.writer(self.file1)
        self.writer1.writerow(['timestamp', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'])
        
        # File for BlueROV2_2
        self.file2 = open(f'logs/bluerov2_2_pose_{timestamp}.csv', 'w')
        self.writer2 = csv.writer(self.file2)
        self.writer2.writerow(['timestamp', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'])
        
    def pose1_callback(self, msg):
        timestamp = self.get_clock().now().to_msg()
        self.writer1.writerow([
            timestamp.sec + timestamp.nanosec * 1e-9,
            msg.position.x,
            msg.position.y,
            msg.position.z,
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ])
        self.file1.flush()
        
    def pose2_callback(self, msg):
        timestamp = self.get_clock().now().to_msg()
        self.writer2.writerow([
            timestamp.sec + timestamp.nanosec * 1e-9,
            msg.position.x,
            msg.position.y,
            msg.position.z,
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ])
        self.file2.flush()
        
    def __del__(self):
        # Close CSV files when the node is destroyed
        if hasattr(self, 'file1'):
            self.file1.close()
        if hasattr(self, 'file2'):
            self.file2.close()

def main(args=None):
    rclpy.init(args=args)
    node = PoseLogger()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 