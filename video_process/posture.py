import cv2
import mediapipe as mp
import numpy as np

class PostureDetector:
    """
    A class to detect posture using MediaPipe and OpenCV.
    It encapsulates the video capture, pose detection, angle calculation,
    and feedback visualization.
    """

    def __init__(self, video_source):
        """
        Initializes the PostureDetector.

        Args:
            video_source (int or str): The video source index (for webcams) or file path.
        """
        # Initialize MediaPipe solutions
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open video source: {video_source}")

    @staticmethod
    def calculate_angle(a, b, c):
        """
        Calculates the angle between three points. This method is static as it
        doesn't rely on the instance's state.

        Args:
            a, b, c (list or np.array): The three points (landmarks).

        Returns:
            float: The calculated angle in degrees.
        """
        a = np.array(a)  # First point
        b = np.array(b)  # Mid point
        c = np.array(c)  # End point
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def run(self):
        """
        Starts the main loop for posture detection and visualization.
        """
        posture = "Unknown"

        while self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Improve performance by making the image non-writeable
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process the image to find pose landmarks
            results = self.pose.process(image_rgb)

            # Make the image writeable again to draw on it
            image.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            # Extract landmarks and calculate posture
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates for the left side of the body
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x,
                       landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y]
                
                # Calculate and classify posture
                angle = self.calculate_angle(hip, shoulder, ear)
                posture = "GOOD" if angle > 165 else "BAD"
                
                # Visualize the angle on the image
                angle_text = f"{angle:.2f}"
                cv2.putText(image, angle_text, 
                            tuple(np.multiply(shoulder, [image.shape[1], image.shape[0]]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            except Exception:
                # Pass if landmarks are not detected
                pass

            # Display posture status box
            cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)
            cv2.putText(image, 'POSTURE', (15, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, posture, (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Draw the pose landmarks
            self.mp_drawing.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

            # Display the resulting frame
            cv2.imshow('MediaPipe Posture Detection', image)

            # Exit on 'q' key
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
        
        self.cleanup()

    def cleanup(self):
        """
        Releases the video capture and destroys all OpenCV windows.
        """
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # To use your primary webcam, you might need to change video_source to 0
    # To use a video file, pass the file path: PostureDetector("path/to/video.mp4")
    detector = PostureDetector(video_source=0)
    detector.run()