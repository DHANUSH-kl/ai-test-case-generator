from flask import Flask, request, jsonify
from flask_cors import CORS
from .model.generate import generate_test_cases

app = Flask(__name__)
CORS(app)  # Allow requests from Streamlit

@app.route('/')
def home():
    return jsonify({"message": "AI Test Case Generator Backend is running."})

@app.route('/generate_test_cases', methods=['POST'])
def generate():
    data = request.get_json()
    srs_text = data.get('srs', '')

    if not srs_text:
        return jsonify({"error": "No SRS content provided"}), 400

    test_cases = generate_test_cases(srs_text)
    return jsonify({"test_cases": test_cases})

if __name__ == '__main__':
    app.run(debug=True)
