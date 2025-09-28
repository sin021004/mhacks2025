✨ AlignAI - Your Personal AI Posture Coach
AlignAI is a smart web application that uses your webcam to analyze your posture in real-time. It acts as a friendly AI companion, helping you build healthier habits by providing instant feedback and detailed session summaries to prevent slouching, tech neck, and shoulder strain.

🌟 Key Features
Real-Time Posture Analysis: Uses your webcam and a MediaPipe machine learning model to detect your posture second-by-second.

Automatic Calibration: No complicated setup needed! Simply start a session, and the app automatically calibrates your "good" posture after 3 seconds.

Multi-Factor Detection: Goes beyond simple slouching to detect and provide specific feedback for:

Slouching

Forward Head Posture (Tech Neck)

Shoulder Tilt (Left and Right)

Persistent User Data: Tracks each user's session individually using a secure Flask session and saves all posture data to a local SQLite database.

Detailed Session Analysis: At the end of a session, view a detailed summary, including your overall good posture percentage and a breakdown of your most common issues.

AI-Powered Summaries (Optional): Includes a module to connect to the Gemini API, allowing for generative AI to provide a narrative summary of your posture habits.

🚀 How It Works
The application uses a client-server architecture to provide a seamless experience.

Frontend (Client-Side): A user-friendly interface built with HTML, CSS, and JavaScript captures the video feed and displays real-time timers and status updates.

Backend (Server-Side): A Flask server written in Python manages user sessions, processes requests, and serves the video stream.

AI Analysis: The PostureDetector class uses the MediaPipe library to analyze video frames in a background thread, running the PostureAnalyzer algorithm to determine posture quality.

Data Persistence: All posture events (Good, Bad, and the specific reason for bad posture) are logged in an SQLite database, linked to a unique session ID for each user.

💻 Tech Stack
Category

Technology / Library

Backend

Python, Flask, Flask-SQLAlchemy

AI / CV

MediaPipe, OpenCV, NumPy

Database

SQLite

Frontend

HTML5, CSS3, JavaScript

Deployment

Development server (can be deployed with Gunicorn/Nginx)

⚙️ Setup and Installation
Follow these steps to get AlignAI running on your local machine.

Prerequisites
Python 3.7+

pip (Python package installer)

A webcam

Installation Steps
Clone the Repository

git clone <your-repository-url>
cd <your-repository-directory>

Create a Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies.

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install Dependencies
Install all the required Python packages from the requirements.txt file.

pip install -r requirements.txt

(If you don't have a requirements.txt file, run pip install Flask Flask-SQLAlchemy opencv-python mediapipe numpy)

Run the Server
The server script will automatically create the database file (posture_data.db) the first time it's run.

python server.py

Access the Application
Open your web browser and navigate to:
http://127.0.0.1:5000

📖 How to Use
Open the Webpage: Launch the app by going to the URL above.

Start a Session: Click the "Start Session" button. The application will request access to your webcam.

Calibrate: Sit up straight and look at the camera. The app will display a "Calibrating..." message and automatically set your baseline posture after 3 seconds.

Get Feedback: The app will now analyze your posture in real-time. The status card will update with feedback.

End Session: When you're done, click "End Session".

View Analysis: A pop-up modal will appear with your session summary and overall good posture percentage.

📂 File Structure
.
├── instance/
│   └── posture_data.db    # The SQLite database file (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css      # All styling for the frontend
│   ├── js/
│   │   └── script.js      # Frontend logic, timers, and API calls
│   └── img/
│       └── placeholder.jpeg # Initial image for the video feed
├── templates/
│   └── index.html         # The main HTML structure of the application
├── .gitignore             # Tells Git to ignore files like the database
├── posture.py             # Main class for video processing and threading
├── posture_analyzer.py    # The core algorithm for posture detection
├── server.py              # The Flask web server and database logic
└── README.md              # This file
