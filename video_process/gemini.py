import os
import markdown
import PIL.Image
import google.generativeai as genai
from flask import Flask, render_template, Response, request, jsonify

# --- 1. Flask App and Gemini API Configuration ---
app = Flask(__name__)


# --- 2. Update the PostureAnalyzer Class ---
class GeminiAnalyzer:
    """
    Generates posture analysis from a graph image and from raw data.
    """
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)

 
    def generate_report_from_data(self, posture_data) -> str:
        """Generates a report by analyzing a dictionary of posture data."""
        try:
            # Format the data into a string for the prompt
            
            
            prompt = f"""You are an expert ergonomist. Analyze the following posture data, which represents the percentage of time a user exhibited a specific postural issue.
            With the given input (Reasons for Bad postures in Chroonological raw data is in '()').

            **Posture Data:**
            {posture_data}
            
            Explain how the posture changes over time and summarize the overall in 1 sentence. Tell what problem could arise from a persom's pattern in 1 sentence. Provide how to improve the posture in a daily basis at home in 2 sentences. Format your response in markdown.
            In 100 words.
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in generate_report_from_data: {e}")
            return "An error occurred while analyzing the data."

# ... (Add your other routes like /video_feed here) ...

if __name__ == '__main__':
    app.run(debug=True)