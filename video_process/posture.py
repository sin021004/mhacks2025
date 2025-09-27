import cv2
import mediapipe as mp
import numpy as np
import threading
import time

class PostureDetector:
    def __init__(self, video_source=0):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open video source: {video_source}")
        
        self.latest_frame = None
        self.lock = threading.Lock()
        self.processing_thread = None
        self.is_running = False
        self.current_posture = "Unknown"
        self.current_angle = 0.0

    @staticmethod
    def calculate_angle(a, b, c):
        a = np.array(a); b = np.array(b); c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def _processing_loop(self):
        while self.is_running:
            success, image = self.cap.read()
            if not success:
                time.sleep(0.1)
                continue

            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            image = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)

            try:
                landmarks = results.pose_landmarks.landmark
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y]
                
                angle = self.calculate_angle(hip, shoulder, ear)
                self.current_posture = "GOOD" if angle > 165 else "BAD"
                self.current_angle = angle
            except:
                self.current_posture = "Unknown"
                self.current_angle = 0.0

            cv2.rectangle(image, (0, 0), (250, 73), (245, 117, 16), -1)
            cv2.putText(image, 'POSTURE', (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, self.current_posture, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            with self.lock:
                self.latest_frame = image.copy()
        
        self.cap.release()

    def start_processing(self):
        if not self.is_running:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._processing_loop)
            self.processing_thread.daemon = True
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
                    time.sleep(0.01)
                    continue
                ret, buffer = cv2.imencode('.jpg', self.latest_frame)
                if not ret:
                    continue
                frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03)

    def get_current_data(self):
        return {"posture": self.current_posture, "angle": self.current_angle}