from flask import Flask, render_template, Response
from posture import PostureDetector  # Import your class from posture.py

app = Flask(__name__)

@app.route('/')
def index():
    """The home page."""
    return render_template('index.html')

def gen(detector):
    """A generator function that wraps the detector's frame generator."""
    yield from detector.generate_frames()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. This will be the src of our img tag."""
    # Create an instance of the detector for each client
    detector = PostureDetector(video_source=0) 
    return Response(gen(detector),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)