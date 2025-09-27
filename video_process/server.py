import uuid
import threading
from flask import Flask, render_template, Response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from posture import PostureDetector # Make sure this is the threaded version

# --- 1. SETUP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-for-the-hackathon'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posture_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

detectors = {}
detector_lock = threading.Lock()

# --- 2. DATABASE MODELS (Unchanged) ---
class UserSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    posture_events = db.relationship('PostureData', backref='user_session', lazy=True)

class PostureData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('user_session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    posture_status = db.Column(db.String(10), nullable=False)
    angle = db.Column(db.Float, nullable=False)

# --- 3. FLASK ROUTES ---
@app.route('/')
def index():
    if 'user_id' not in session:
        new_user = UserSession(); db.session.add(new_user); db.session.commit()
        session['user_id'] = new_user.id
    return render_template('index.html')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"error": "No session found"}), 403

    with detector_lock:
        if user_id not in detectors:
            detectors[user_id] = PostureDetector(video_source=0)
            # --- THIS IS THE FIX ---
            # Start the background thread that processes video frames
            detectors[user_id].start_processing()
            print(f"Detector created and started for user {user_id}")
        else:
            print(f"Detector already exists for user {user_id}")
            
    return jsonify({"status": "started"}), 200

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"error": "No session found"}), 403
        
    with detector_lock:
        if user_id in detectors:
            # Tell the thread to stop and clean up resources
            detectors[user_id].stop_processing()
            del detectors[user_id]
            print(f"Detector stopped for user {user_id}")
            
    return jsonify({"status": "stopped"}), 200

@app.route('/video_feed')
def video_feed():
    user_id = session.get('user_id')
    if not user_id or user_id not in detectors:
        return "Detector not active for this session", 404
    
    return Response(detectors[user_id].generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/posture_status')
def posture_status():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"error": "No session found"}), 403

    if user_id in detectors:
        data = detectors[user_id].get_current_data()
        if data['posture'] != "Unknown":
            new_posture_event = PostureData(session_id=user_id, posture_status=data['posture'], angle=data['angle'])
            db.session.add(new_posture_event); db.session.commit()
        return jsonify(data)
    else:
        return jsonify({"posture": "NOT_ACTIVE"})

# --- 4. RUN THE APP (Unchanged) ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, threaded=True)