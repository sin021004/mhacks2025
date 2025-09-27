import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

class PostureAnalyzer:
    """
    Analyzes posture based on MediaPipe landmarks, using a calibration baseline.
    """
    def __init__(self):
        # --- Configuration Thresholds ---
        self.SLOUCH_THRESHOLD = 15
        self.HEAD_FORWARD_THRESHOLD = 20
        self.SHOULDER_TILT_THRESHOLD = 5

        # --- State Variables ---
        self.calibrated = False
        self.baseline_metrics = {}

    @staticmethod
    def _calculate_angle(point1, point2):
        """Calculates the angle of the line between two points from horizontal."""
        return np.degrees(np.arctan2(point2.y - point1.y, point2.x - point1.x))

    def calibrate(self, landmarks):
        """Establishes the baseline for good posture."""
        try:
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
            left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]

            # Vertical distance from nose to shoulder midpoint
            shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2
            self.baseline_metrics['vertical_dist'] = abs(nose.y - shoulder_midpoint_y)

            # Horizontal distance from ear to shoulder
            self.baseline_metrics['horizontal_dist'] = abs(left_ear.x - left_shoulder.x)

            # Shoulder line angle
            self.baseline_metrics['shoulder_angle'] = self._calculate_angle(left_shoulder, right_shoulder)

            self.calibrated = True
            print("Calibration successful.")
            return True, "Calibration Complete!"
        except Exception as e:
            print(f"Calibration failed: {e}")
            return False, "Could not see landmarks."

    def analyze_posture(self, landmarks):
        """Analyzes current posture against the calibrated baseline."""
        if not self.calibrated:
            return "CALIBRATE", "Please calibrate first."

        try:
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
            left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]

            # Check for Slouching
            shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2
            current_vertical_dist = abs(nose.y - shoulder_midpoint_y)
            slouch_percentage = ((self.baseline_metrics['vertical_dist'] - current_vertical_dist) / self.baseline_metrics['vertical_dist']) * 100
            if slouch_percentage > self.SLOUCH_THRESHOLD:
                return "BAD", "Slouch Detected"

            # Check for Forward Head (Tech Neck)
            current_horizontal_dist = abs(left_ear.x - left_shoulder.x)
            forward_head_percentage = ((current_horizontal_dist - self.baseline_metrics['horizontal_dist']) / self.baseline_metrics['horizontal_dist']) * 100
            if forward_head_percentage > self.HEAD_FORWARD_THRESHOLD:
                return "BAD", "Forward Head Detected"

            # Check for Shoulder Tilt
            current_shoulder_angle = self._calculate_angle(left_shoulder, right_shoulder)
            shoulder_tilt_diff = abs(current_shoulder_angle - self.baseline_metrics['shoulder_angle'])
            if shoulder_tilt_diff > self.SHOULDER_TILT_THRESHOLD:
                return "BAD", "Shoulder Tilt Detected"
            
            return "GOOD", "Excellent Posture"
        except Exception:
            return "UNKNOWN", "Landmarks not visible."