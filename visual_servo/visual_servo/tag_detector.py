import cv2
import numpy as np
import pupil_apriltags

class TagDetector:
    def __init__(self, node, tag_size, detection_threshold, camera_params):
        self.node = node
        self.tag_size = tag_size
        self.detection_threshold = detection_threshold
        self.camera_params = camera_params
        
        # Initialize the AprilTag detector
        self.detector = pupil_apriltags.Detector(
            families='tagStandard41h12',
            nthreads=4,
            quad_decimate=1.0,
            quad_sigma=0.8,
            refine_edges=True,
            decode_sharpening=0.25,
            debug=False
        )
        
        # Detection state
        self.tag_detected = False
        self.tag_distance = None
        self.tag_z_offset = None
        self.tag_x_offset = None

    def preprocess_image(self, frame):
        """Apply image preprocessing to improve tag detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        return gray

    def detect_and_visualize(self, frame):
        """Detect tags and visualize them on the frame."""
        h, w = frame.shape[:2]
        processed_gray = self.preprocess_image(frame)
        
        dets = self.detector.detect(
            processed_gray,
            estimate_tag_pose=True,
            camera_params=self.camera_params,
            tag_size=self.tag_size
        )

        self.tag_detected = False
        closest_tag = None
        min_distance = float('inf')

        for det in dets:
            if det.decision_margin < self.detection_threshold:
                continue
                
            # Visualization code
            pts = det.corners.astype(int).reshape(4,2)
            cv2.polylines(frame, [pts], True, (0,255,0), 2)
            c = np.mean(pts, axis=0).astype(int)
            cv2.circle(frame, tuple(c), 5, (0,255,0), -1)
            
            confidence_text = f"ID {det.tag_id} ({det.decision_margin:.1f})"
            cv2.putText(frame, confidence_text, (c[0]+10,c[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            
            if hasattr(det, 'pose_t') and det.pose_t is not None:
                distance = np.linalg.norm(det.pose_t)
                cv2.putText(frame, f"{distance:.2f} m", (c[0]+10,c[1]+25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_tag = det

        if closest_tag is not None:
            self.tag_detected = True
            self.tag_distance = min_distance
            self.tag_z_offset = closest_tag.pose_t[2][0]
            center = np.mean(closest_tag.corners, axis=0)
            self.tag_x_offset = center[0] - (w/2)
            self.node.get_logger().info(f"Selected closest tag ID {closest_tag.tag_id} at {min_distance:.2f}m")

        return frame 