import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

class PostureAnalyzer:
    def __init__(self):
        self.SLOUCH_THRESHOLD = 15
        self.HEAD_FORWARD_THRESHOLD = 20
        self.SHOULDER_TILT_THRESHOLD = 5
        self.calibrated = False
        self.baseline_metrics = {}

    @staticmethod
    def _calculate_angle(point1, point2):
        return np.degrees(np.arctan2(point2.y - point1.y, point2.x - point1.x))

    def calibrate(self, landmarks):
        try:
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
            left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]

            shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2
            self.baseline_metrics['vertical_dist'] = abs(nose.y - shoulder_midpoint_y)
            self.baseline_metrics['horizontal_dist'] = abs(left_ear.x - left_shoulder.x)
            self.baseline_metrics['shoulder_angle'] = self._calculate_angle(left_shoulder, right_shoulder)

            self.calibrated = True
            print("Calibration successful.")
            return True, "Calibration Complete!"
        except Exception as e:
            print(f"Calibration failed: {e}")
            return False, "Could not see landmarks."

    def analyze_posture(self, landmarks):
        if not self.calibrated:
            return "CALIBRATING", "Calibrating..."

        try:
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
            left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]

            shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2
            current_vertical_dist = abs(nose.y - shoulder_midpoint_y)
            slouch_percentage = ((self.baseline_metrics['vertical_dist'] - current_vertical_dist) / self.baseline_metrics['vertical_dist']) * 100
            if slouch_percentage > self.SLOUCH_THRESHOLD:
                return "BAD", "Slouch Detected"

            current_horizontal_dist = abs(left_ear.x - left_shoulder.x)
            forward_head_percentage = ((current_horizontal_dist - self.baseline_metrics['horizontal_dist']) / self.baseline_metrics['horizontal_dist']) * 100
            if forward_head_percentage > self.HEAD_FORWARD_THRESHOLD:
                return "BAD", "Forward Head Detected"

            current_shoulder_angle = self._calculate_angle(left_shoulder, right_shoulder)
            shoulder_tilt_diff = current_shoulder_angle - self.baseline_metrics['shoulder_angle']
            
            if abs(shoulder_tilt_diff) > self.SHOULDER_TILT_THRESHOLD:
                return "BAD", "Shoulder Tilted to Right" if shoulder_tilt_diff > 0 else "Shoulder Tilted to Left"
            
            return "GOOD", "Excellent Posture"
        except Exception:
            return "UNKNOWN", "Landmarks not visible."