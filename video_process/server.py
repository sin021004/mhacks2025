import uuid
from flask import Flask, render_template, Response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from posture import PostureDetector

# --- 1. SETUP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-for-the-hackathon'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posture_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# A global dictionary to hold detector instances, mapped by user session ID
detectors = {}

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

# --- 3. FLASK ROUTES ---
@app.route('/')
def index():
    """Home page. Creates a user session if one doesn't exist."""
    if 'user_id' not in session:
        new_user = UserSession()
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
    return render_template('index.html')

def get_detector_for_user(user_id):
    """Safely gets or creates a detector for a given user ID."""
    if user_id not in detectors:
        print(f"Creating new detector for user {user_id}")
        detectors[user_id] = PostureDetector(video_source=0)
    return detectors[user_id]

@app.route('/video_feed')
def video_feed():
    """Video streaming for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return "No session found", 403
    
    detector = get_detector_for_user(user_id)
    return Response(detector.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/posture_status')
def posture_status():
    """Provides posture status and saves it to the database."""
    user_id = session.get('user_id')
    if not user_id:
        return "No session found", 403

    detector = get_detector_for_user(user_id)
    data = detector.get_current_data()

    if data['posture'] != "Unknown":
        new_posture_event = PostureData(
            session_id=user_id,
            posture_status=data['posture'],
            angle=data['angle']
        )
        db.session.add(new_posture_event)
        db.session.commit()

    return jsonify(data)

# --- 4. RUN THE APP ---
if __name__ == '__main__':
    # This block is executed when you run "python server.py"
    # It creates the database tables before the app starts
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, threaded=True)