import os
import uuid
import threading
from flask import Flask, render_template, Response, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from posture import PostureDetector
from gemini import GeminiAnalyzer

# --- 1. SETUP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-for-the-hackathon'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posture_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

detectors = {}
detector_lock = threading.Lock()
gemini_input = ""
import click

@app.cli.command("init-db")
@click.option("--drop", is_flag=True, help="Drop all tables before creating.")
def init_db_command(drop: bool):
    """Initialize database tables (optionally drop first)."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("✅ Database initialized" + (" (dropped first)" if drop else ""))

# --- 2. DATABASE MODELS ---
class UserSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    posture_events = db.relationship('PostureData', backref='user_session', lazy=True)

class PostureData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('user_session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    posture_status = db.Column(db.String(10), nullable=False)
    angle = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(50), nullable=True) # Final version includes this column

# --- 3. FLASK ROUTES ---
@app.route('/')
def index():
    if 'user_id' not in session:
        new_user = UserSession()
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
    return render_template('index.html')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No session found"}), 403

    with detector_lock:
        if user_id not in detectors:
            detectors[user_id] = PostureDetector(video_source=0)
            detectors[user_id].start_processing() # This line starts the camera logic
            print(f"Detector created and started for user {user_id}")
    return jsonify({"status": "started"}), 200

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No session found"}), 403
        
    with detector_lock:
        if user_id in detectors:
            detectors[user_id].stop_processing()
            
            good_bad_counts = (
                db.session.query(PostureData.posture_status, func.count().label("total"))
                .group_by(PostureData.posture_status)
                .all()
            )
            
            bad_reason_counts = (
                db.session.query(PostureData.reason, func.count().label("total"))
                .filter(PostureData.posture_status == "Bad")
                .group_by(PostureData.reason)
                .all()
            )
            
            text = ", ".join(f"{status}: {count}" for status, count in good_bad_counts)
            text2 = ", ".join(f"{reason}: {count}" for reason, count in bad_reason_counts)
            text += "\nPosture Issues Breakdown: " + text2
            
            analyzer = GeminiAnalyzer()
            global gemini_input
            gemini_output = analyzer.generate_report_from_data("Total Count: " + text + "; Chronological Raw Data: " + gemini_input)
            
            with open("instance/analyze.txt", "w") as f:
                f.write(gemini_output)
            
            print(gemini_output)
            del detectors[user_id]
            print(f"Detector stopped for user {user_id}")
            
    return jsonify({"status": "stopped"}), 200

@app.route('/video_feed')
def video_feed():
    user_id = session.get('user_id')
    if not user_id or user_id not in detectors:
        return "Detector not active for this session", 404
    
    detector = detectors[user_id]
    return Response(detector.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/posture_status')
def posture_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No session found"}), 403
    
    global gemini_input
    if user_id in detectors:
        detector = detectors[user_id]
        data = detector.get_current_data()

        if data['posture'] in ["GOOD", "BAD"]:
            bad_posture_reason = None
            gemini_input += "," + data['posture']
            if data['posture'] == "BAD":   
                bad_posture_reason = data.get('reason') 
                gemini_input += "(" + bad_posture_reason + ")"
            gemini_input += " "
            
            new_posture_event = PostureData(
                session_id=user_id,
                posture_status=data['posture'],
                angle=0,
                reason=bad_posture_reason
            )
            db.session.add(new_posture_event)
            db.session.commit()
        return jsonify(data)
    else:
        return jsonify({"posture": "NOT_ACTIVE"})

@app.route('/get_analysis_text')
def get_analysis_text():
    # Flask's instance folder path
    instance_path = app.instance_path 
    filename = 'analyze.txt'
    
    # Check if the file exists
    if not os.path.exists(os.path.join(instance_path, filename)):
        # Return a friendly message if the file hasn't been created yet
        return "No comprehensive AI analysis generated yet.", 404
        
    # Securely serves the content of the file
    return send_from_directory(instance_path, filename, mimetype='text/plain')


# --- 4. RUN THE APP ---
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  
        db.create_all()
        
    app.run(debug=True, threaded=True)