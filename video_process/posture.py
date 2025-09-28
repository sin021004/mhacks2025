import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from posture_analyzer import PostureAnalyzer

class PostureDetector:
    def __init__(self, video_source=1):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open video source: {video_source}")
        
        self.analyzer = PostureAnalyzer()
        self.frame_counter = 0
        self.CALIBRATION_FRAMES = 90

        self.latest_frame = None
        self.lock = threading.Lock()
        self.processing_thread = None
        self.is_running = False
        self.current_posture = "CALIBRATING"
        self.posture_reason = "Get ready..."

    def _processing_loop(self):
        while self.is_running:
            success, image = self.cap.read()
            if not success:
                time.sleep(0.1); continue

            self.frame_counter += 1
            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                if not self.analyzer.calibrated:
                    countdown = (self.CALIBRATION_FRAMES - self.frame_counter) // 30
                    self.posture_reason = f"Calibrating in {countdown+1}..."
                    if self.frame_counter >= self.CALIBRATION_FRAMES:
                        self.analyzer.calibrate(landmarks)
                else:
                    status, reason = self.analyzer.analyze_posture(landmarks)
                    self.current_posture = status
                    self.posture_reason = reason
            except Exception:
                self.current_posture = "UNKNOWN"
                self.posture_reason = "Not fully visible"

            color = (0, 0, 255) if self.current_posture == "BAD" else (0, 255, 0)
            if not self.analyzer.calibrated: color = (255, 165, 0)

            # cv2.rectangle(image, (0, 0), (450, 73), color, -1)
            # cv2.putText(image, f'STATUS: {self.current_posture}', (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            # cv2.putText(image, self.posture_reason, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            with self.lock:
                self.latest_frame = image.copy()
        self.cap.release()

    def get_current_data(self):
        return {"posture": self.current_posture, "reason": self.posture_reason}

    def start_processing(self):
        self.frame_counter = 0
        if not self.is_running:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()

    def stop_processing(self):
        if self.is_running:
            self.is_running = False
            if self.processing_thread:
                self.processing_thread.join()

    def generate_frames(self):
        while self.is_running:
            with self.lock:
                if self.latest_frame is None:
                    time.sleep(0.01); continue
                ret, buffer = cv2.imencode('.jpg', self.latest_frame)
                if not ret: continue
                frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03)