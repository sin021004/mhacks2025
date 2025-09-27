from flask import Flask, render_template, Response
# Make sure your PostureDetector class is in a file you can import
from posture import PostureDetector 

app = Flask(__name__)
detector = PostureDetector(0)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('/Users/sincheolyang/Desktop/mhacks2025/video_process/templates/index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # The Response object takes our generator and streams it
    return Response(detector.get_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)