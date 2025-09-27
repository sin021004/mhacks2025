import os
import google.generativeai as genai

def get_posture_feedback(angle: float, duration_seconds: int) -> str:
    """
    Generates posture feedback using the Gemini API.

    Args:
        angle: The user's back posture angle in degrees.
        duration_seconds: The duration in seconds the posture was held.

    Returns:
        A string containing AI-generated feedback.
    """
    # --- Step 1: Configure the API Key ---
    # Make sure to set your GEMINI_API_KEY as an environment variable
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    except KeyError:
        return "Error: GEMINI_API_KEY environment variable not set."

    # --- Step 2: Create a detailed prompt for the model ---
    # This prompt gives the AI a role, context, and clear instructions.
    prompt = f"""
    You are an expert posture coach. Your goal is to provide encouraging, actionable feedback.
    Do not give medical advice.

    A user's back posture was measured. An angle of 90-105 degrees is considered good (upright),
    while an angle greater than 110 degrees suggests slouching.

    Here is the user's data:
    - Posture Angle: {angle:.1f} degrees
    - Duration: {duration_seconds} seconds

    Based on this data, provide a short, 2-3 sentence feedback.
    - If the posture is good, offer encouragement.
    - If the posture is poor, provide a gentle, corrective suggestion.
    """

    # --- Step 3: Call the Gemini API ---
    try:
        # Note: 'gemini-1.5-flash-latest' is a valid and current model name.
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while calling the API: {e}"


# --- Main execution block to demonstrate the function ---
if __name__ == "__main__":
    print("Running posture feedback examples...\n")

    # Example 1: Good posture (upright)
    good_posture_angle = 98.5
    good_posture_duration = 300  # 5 minutes
    print(f"--- Feedback for Angle: {good_posture_angle}° (Duration: {good_posture_duration}s) ---")
    feedback1 = get_posture_feedback(good_posture_angle, good_posture_duration)
    print(feedback1)
    print("-" * 50)

    # Example 2: Bad posture (slouching)
    bad_posture_angle = 122.0
    bad_posture_duration = 600  # 10 minutes
    print(f"--- Feedback for Angle: {bad_posture_angle}° (Duration: {bad_posture_duration}s) ---")
    feedback2 = get_posture_feedback(bad_posture_angle, bad_posture_duration)
    print(feedback2)
    print("-" * 50)