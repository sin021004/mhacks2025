import cv2
import mediapipe as mp
import numpy as np

class PostureDetector:
    """
    A class to detect posture using MediaPipe and OpenCV.
    This version is designed to be used with a Flask web server for streaming
    and data retrieval.
    """

    def __init__(self, video_source=0):
        """
        Initializes the detector with MediaPipe models, video capture,
        and instance variables to hold the current posture state.
        """
        # --- MediaPipe Setup ---
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        
        # --- Video Capture Setup ---
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open video source: {video_source}")

        # --- State Variables ---
        self.current_posture = "Unknown"
        self.current_angle = 0.0

    @staticmethod
    def calculate_angle(a, b, c):
        """Calculates the angle between three 2D points."""
        a = np.array(a)  # First point
        b = np.array(b)  # Mid point
        c = np.array(c)  # End point
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def generate_frames(self):
        """
        A generator function that processes video frames, detects posture,
        and yields JPEG-encoded frames for web streaming.
        """
        while self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            # Flip the image horizontally for a later selfie-view display
            image = cv2.flip(image, 1)
            
            # Recolor image to RGB for MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False # Performance optimization
            
            # Make detection
            results = self.pose.process(image_rgb)

            # Recolor back to BGR for OpenCV
            image.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            # Extract landmarks and calculate posture
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y]
                
                # Calculate angle and update state
                angle = self.calculate_angle(hip, shoulder, ear)
                self.current_posture = "GOOD" if angle > 165 else "BAD"
                self.current_angle = angle
                
                # Visualize the angle
                angle_text = f"{angle:.1f}"
                cv2.putText(image, angle_text, 
                            tuple(np.multiply(shoulder, [image.shape[1], image.shape[0]]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            except Exception as e:
                # Update state if landmarks are not detected
                self.current_posture = "Unknown"
                self.current_angle = 0.0
                pass

            # --- Render UI Overlay ---
            # Status box
            cv2.rectangle(image, (0, 0), (250, 73), (245, 117, 16), -1)
            cv2.putText(image, 'POSTURE', (15, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, self.current_posture, (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Draw the pose landmarks
            self.mp_drawing.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

            # --- Encode and Yield Frame ---
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        self.cap.release()

    def get_current_data(self):
        """
        Getter method for the Flask app to retrieve the current posture data.
        Returns a dictionary containing the latest status and angle.
        """
        return {
            "posture": self.current_posture,
            "angle": self.current_angle
        }