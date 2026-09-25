"""
Green Minds - Backend Server (Day 2)
Flask API server that securely connects to Google Gemini AI
"""

import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 1. Load environment variables from the private .env file
load_dotenv()

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so your frontend
# (index.html) can communicate with this backend server seamlessly
CORS(app)

# Load prompt template from GreenMinds_AI_Prompt.txt if it exists
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "GreenMinds_AI_Prompt.txt"


def build_prompt(farmer_data):
    """
    Builds the AI prompt using the farmer's details and the structure
    defined in GreenMinds_AI_Prompt.txt.
    """
    name = farmer_data.get("name", "Farmer")
    state = farmer_data.get("state", "Not specified")
    district = farmer_data.get("district", "Not specified")
    crop = farmer_data.get("crop", "Not specified")
    soil = farmer_data.get("soilType", "Not specified")
    weather = farmer_data.get("weatherCondition", "Not specified")

    prompt = f"""You are Green Minds, an AI-powered agricultural assistant for Indian farmers.

Based on the farmer's information, provide simple, practical and localized agricultural guidance.

Farmer details:
Name: {name}
State: {state}
District: {district}
Crop: {crop}
Soil Type: {soil}
Weather Condition: {weather}

Provide:
1. Crop care advice
2. Water management
3. Soil and nutrient guidance
4. Weather-related advice
5. Possible crop risks
6. Recommended next steps

Use simple language.
Avoid making unsafe or highly specific chemical recommendations.
If important information is missing, clearly say what information is needed.
"""
    return prompt


@app.route("/", methods=["GET"])
def health_check():
    """
    Simple status check endpoint.
    Opening http://localhost:5000 in your browser shows if the backend is running
    and whether the Gemini API key has been configured.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    is_key_configured = bool(api_key and api_key != "your_actual_gemini_api_key_here")

    return jsonify({
        "status": "online",
        "service": "Green Minds Backend",
        "apiKeyConfigured": is_key_configured,
        "message": "Backend server is running smoothly!" if is_key_configured else "Backend is running, but GEMINI_API_KEY is not set in .env yet."
    })


@app.route("/api/advice", methods=["POST"])
def get_advice():
    """
    Receives farmer information from the frontend, prepares the prompt,
    securely calls the Gemini API, and returns agricultural advice.
    """
    # Verify API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_actual_gemini_api_key_here":
        return jsonify({
            "success": False,
            "error": "Gemini API key is not configured. Please add your GEMINI_API_KEY to the .env file."
        }), 400

    # Parse JSON payload sent from frontend
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "error": "No farmer data was received."
        }), 400

    try:
        # Import the official Google GenAI SDK
        from google import genai

        # Initialize the client with the private API key
        client = genai.Client(api_key=api_key)

        # Build prompt from farmer inputs
        prompt = build_prompt(data)

        # Call Gemini model with robust fallback across latest available models
        candidate_models = [
            os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
            "gemini-2.5-flash-lite",
            "gemini-3.6-flash"
        ]
        
        response = None
        last_error = None
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    break
            except Exception as err:
                last_error = err
                continue

        if not response or not response.text:
            raise last_error or Exception("Could not generate advice from Gemini.")

        return jsonify({
            "success": True,
            "advice": response.text,
            "farmerName": data.get("name")
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error communicating with Gemini AI: {str(e)}"
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🌱 Green Minds backend starting on http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
