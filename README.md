✨ AlignAI - Your Personal AI Posture Coach

AlignAI is a smart web app that uses your webcam to analyze posture in real-time. It acts as a friendly AI companion, giving instant feedback and session summaries to prevent slouching, tech neck, and shoulder strain.

🌟 Features

Real-Time Analysis with MediaPipe & OpenCV

Auto Calibration in 3 seconds

Multi-Factor Detection: Slouching, Forward Head, Shoulder Tilt

Persistent Data stored in SQLite per session

Session Summary with good posture % and issue breakdown

AI Summaries (Optional) using Gemini API

🚀 How It Works

Frontend: HTML, CSS, JS – captures video & shows live feedback

Backend: Flask + Python – manages sessions & database

AI Engine: MediaPipe + PostureAnalyzer thread for detection

Database: SQLite logs posture events with session IDs

💻 Tech Stack

Backend: Python, Flask, Flask-SQLAlchemy

AI / CV: MediaPipe, OpenCV, NumPy

Database: SQLite

Frontend: HTML5, CSS3, JavaScript

Deployment: Flask dev server (can extend with Gunicorn/Nginx)

⚙️ Setup
# Clone repo
git clone <repo-url> && cd <repo-dir>

# Create virtual env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py


Open http://127.0.0.1:5000
 🎉

📖 Usage

Open the webpage & start a session

Sit upright for 3s calibration

Get live posture feedback

End session → view summary & analysis

📂 File Structure
.
├── instance/           # posture_data.db (auto)
├── static/             # CSS, JS, Images
├── templates/          # index.html
├── posture.py          # Video processing
├── posture_analyzer.py # Detection logic
├── server.py           # Flask backend
└── README.md
