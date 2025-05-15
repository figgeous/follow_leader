from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
)

class BaseImageSource:
    def __init__(self, node, topic):
        self.node = node
        self.bridge = CvBridge()
        self.latest = None

        # build a profile identical to the publisher's
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            durability=DurabilityPolicy.VOLATILE
        )
        
        # use the "sensor data" QoS so we match Gazebo's publisher
        self.sub = node.create_subscription(Image, topic, self.cb, qos)

    def cb(self, msg):
        self.latest = (self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8'),
                       self.node.get_parameter('camera_params').value)
    def get_frame(self):
        f = self.latest
        self.latest = None
        return f

class GazeboImageSource(BaseImageSource):
    pass  # same as base

class RobotImageSource(BaseImageSource):
    pass  # same as base

class WebcamImageSource(BaseImageSource):
    """
    Image source for webcam input. This class handles webcam-specific image processing
    and ensures proper image format conversion.
    """
    def __init__(self, node, topic):
        super().__init__(node, topic)
        # Webcam typically needs different QoS settings for real-time performance
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            durability=DurabilityPolicy.VOLATILE
        )
        # Recreate subscription with webcam-appropriate QoS
        self.sub = node.create_subscription(Image, topic, self.cb, qos)
        node.get_logger().info(f'WebcamImageSource initialized with topic: {topic}')

    def cb(self, msg):
        try:
            # Convert the image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            # Get camera parameters from node
            camera_params = self.node.get_parameter('camera_params').value
            self.latest = (cv_image, camera_params)
            self.node.get_logger().debug(f'Received webcam frame: {cv_image.shape}')
        except Exception as e:
            self.node.get_logger().error(f'Error processing webcam image: {str(e)}')
            self.latest = None
