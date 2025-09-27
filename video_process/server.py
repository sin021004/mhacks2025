# my_pose_app/server.py
from flask import Flask, render_template  # Import render_template!

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def index():
    # Flask automatically looks in the 'templates' folder for this file
    return render_template('index.html') 

# Your other routes will go here...

if __name__ == '__main__':
    app.run(debug=True)