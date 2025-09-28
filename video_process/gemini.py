import os
import markdown
import PIL.Image
import google.generativeai as genai
from flask import Flask, render_template, Response, request, jsonify

# --- 1. Flask App and Gemini API Configuration ---
app = Flask(__name__)


# --- 2. Update the PostureAnalyzer Class ---
class PostureAnalyzer:
    """
    Generates posture analysis from a graph image and from raw data.
    """
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate_report_from_image(self, image_path: str) -> str | None:
        """Generates a report by analyzing a graph image."""
        try:
            img = PIL.Image.open(image_path)
            prompt = ["""You are an expert ergonomist analyzing the attached graph. Provide a detailed analysis based on the visual data presented in the bar chart, explaining the key postural issues and offering an action plan based on the highest percentages shown.""", img]
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in generate_report_from_image: {e}")
            return "An error occurred while analyzing the image."

    # ✨ --- NEW METHOD FOR DATA ANALYSIS --- ✨
    def generate_report_from_data(self, posture_data: dict) -> str | None:
        """Generates a report by analyzing a dictionary of posture data."""
        try:
            # Format the data into a string for the prompt
            data_string = "\n".join([f"- {key}: {value}%" for key, value in posture_data.items()])
            
            prompt = f"""You are an expert ergonomist. Analyze the following posture data, which represents the percentage of time a user exhibited a specific postural issue.

            **Posture Data:**
            {data_string}

            Please provide a concise analysis focusing on the top 2-3 issues based on the highest percentages. For each, suggest one simple corrective exercise. Maintain an encouraging tone.
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in generate_report_from_data: {e}")
            return "An error occurred while analyzing the data."

# --- 3. Update the Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report')
def report():
    """
    Generates TWO reports (from image and data) and displays them.
    """
    analyzer = PostureAnalyzer()
    
    # --- Input Data ---
    image_file_path = os.path.join('static', 'images', 'expenditure-pupil.jpg')
    # This is the raw data that corresponds to the graph
    posture_percentages = {
        "Forward Head": 45,
        "Shoulder Slouch": 30,
        "Spinal Slump": 15,
        "Shoulder Tilt": 10
    }
    
    # --- ✨ GENERATE BOTH REPORTS --- ✨
    # 1. Generate the report from the image
    image_report_text = analyzer.generate_report_from_image(image_path=image_file_path)
    image_report_html = markdown.markdown(image_report_text)
    
    # 2. Generate the report from the data dictionary
    data_report_text = analyzer.generate_report_from_data(posture_data=posture_percentages)
    data_report_html = markdown.markdown(data_report_text)
    
    # --- Render the template, passing BOTH reports ---
    return render_template(
        'report.html', 
        image_report=image_report_html, 
        data_report=data_report_html
    )

# ... (Add your other routes like /video_feed here) ...

if __name__ == '__main__':
    app.run(debug=True)