from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_landmarks')
def get_landmarks():
    # Get map bounds from request parameters
    north = float(request.args.get('north'))
    south = float(request.args.get('south'))
    east = float(request.args.get('east'))
    west = float(request.args.get('west'))

    # Calculate the center point of the map
    center_lat = (north + south) / 2
    center_lon = (east + west) / 2

    # Make a request to the Wikipedia API
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={center_lat}|{center_lon}&gsradius=10000&gslimit=10&format=json"
    response = requests.get(url)
    data = response.json()

    landmarks = []
    for place in data['query']['geosearch']:
        landmark = {
            "title": place['title'],
            "lat": place['lat'],
            "lon": place['lon'],
            "pageid": place['pageid']
        }
        # Fetch additional details for each landmark
        details_url = f"https://en.wikipedia.org/w/api.php?action=query&pageids={place['pageid']}&prop=extracts&exintro&format=json&explaintext"
        details_response = requests.get(details_url)
        details_data = details_response.json()
        extract = details_data['query']['pages'][str(place['pageid'])]['extract']
        landmark['summary'] = extract[:200] + '...' if len(extract) > 200 else extract
        landmarks.append(landmark)

    return jsonify(landmarks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
