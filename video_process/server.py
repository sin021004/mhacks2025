from flask import Flask, render_template, Response, jsonify, request
# Import your PostureDetector class and a FrameGenerator utility if needed
from posture import PostureDetector 
import threading
import time

app = Flask(__name__)

# --- GLOBAL VARIABLES TO MANAGE THE SESSION STATE ---
# This holds the active detector instance
global_detector = None 
# Thread to run the detector logic
detector_thread = None 
# Lock for safe multi-threaded access
detector_lock = threading.Lock() 

# --- SESSION CONTROL ENDPOINTS ---

@app.route('/')
def index():
    """The home page."""
    return render_template('index.html')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global global_detector, detector_thread
    with detector_lock:
        if global_detector is None:
            # 1. Initialize the detector
            global_detector = PostureDetector(video_source=1)
            
            # 2. Start the detector's processing logic in a separate thread
            # NOTE: Your PostureDetector needs a start() method or similar
            # to begin internal processing and updating the posture status.
            global_detector.start_processing()
            
            print("Detector initialized and started.")
            return jsonify({"status": "started"}), 200
        else:
            print("Detector already running.")
            return jsonify({"status": "already running"}), 200

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global global_detector
    with detector_lock:
        if global_detector is not None:
            # Tell the detector to stop processing and release resources
            global_detector.stop_processing()
            global_detector = None
            print("Detector stopped and resources released.")
            return jsonify({"status": "stopped"}), 200
        else:
            print("Detector was not running.")
            return jsonify({"status": "not running"}), 200

# --- STATUS ENDPOINT (Used by JavaScript to update the timer) ---

@app.route('/posture_status')
def posture_status():
    global global_detector
    with detector_lock:
        if global_detector is not None:
            # Your PostureDetector must expose its current status (e.g., self.current_posture)
            current_posture = global_detector.get_current_posture()
            # This is the crucial return format the JavaScript expects
            return jsonify({"posture": current_posture}), 200
        else:
            # If not running, return a default status (prevents JS connection errors)
            return jsonify({"posture": "NOT_ACTIVE"}), 200

# --- VIDEO FEED ENDPOINT ---

def gen():
    global global_detector
    # This loop waits until the detector is available
    while global_detector is None:
        time.sleep(0.1)
        
    # Now, yield frames from the running detector
    yield from global_detector.generate_frames()


@app.route('/video_feed')
def video_feed():
    """Video streaming route. This will be the src of our img tag."""
    # This route just pulls frames from the globally running detector
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Turn debug=False in a production environment
    app.run(debug=True, threaded=True)

# NOTE: You will need to modify your PostureDetector class 
# to include methods like start_processing(), stop_processing(), and get_current_posture().