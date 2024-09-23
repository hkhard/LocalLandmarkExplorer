from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_landmarks')
def get_landmarks():
    # This function will fetch landmarks from Wikipedia API
    # For demonstration, we'll return some sample data
    sample_landmarks = [
        {"title": "Eiffel Tower", "lat": 48.8584, "lon": 2.2945, "summary": "Iconic iron tower in Paris."},
        {"title": "Statue of Liberty", "lat": 40.6892, "lon": -74.0445, "summary": "Colossal statue in New York Harbor."},
        {"title": "Colosseum", "lat": 41.8902, "lon": 12.4922, "summary": "Ancient amphitheater in Rome."}
    ]
    return jsonify(sample_landmarks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
