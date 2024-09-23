from flask import Flask, render_template, jsonify, request
import requests
import logging
import re

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def categorize_landmark(description):
    categories = {
        "Historical": ["history", "historic", "ancient", "old", "heritage"],
        "Cultural": ["art", "museum", "theater", "culture", "music"],
        "Natural": ["park", "garden", "nature", "mountain", "lake", "river"],
        "Educational": ["university", "school", "college", "library", "institute"],
        "Religious": ["church", "temple", "mosque", "synagogue", "religious"],
        "Commercial": ["shop", "store", "market", "mall", "restaurant"]
    }
    
    description = description.lower()
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    return "Other"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_landmarks')
def get_landmarks():
    # Updated default coordinates to Örebro, Sweden
    north = float(request.args.get('north', 59.2753))
    south = float(request.args.get('south', 59.2753))
    east = float(request.args.get('east', 15.2134))
    west = float(request.args.get('west', 15.2134))
    
    # Get selected categories from the request
    selected_categories = request.args.get('categories', '').split(',')
    logging.debug(f"Selected categories: {selected_categories}")

    center_lat = (north + south) / 2
    center_lon = (east + west) / 2

    url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={center_lat}|{center_lon}&gsradius=10000&gslimit=50&format=json"
    response = requests.get(url)
    data = response.json()

    logging.debug(f"Raw Wikipedia API response: {data}")

    landmarks = []
    for place in data['query']['geosearch']:
        landmark = {
            "title": place['title'],
            "lat": float(place['lat']),
            "lon": float(place['lon']),
            "pageid": place['pageid']
        }
        logging.debug(f"Processing landmark: {landmark['title']}")

        details_url = f"https://en.wikipedia.org/w/api.php?action=query&pageids={place['pageid']}&prop=extracts&exintro&format=json&explaintext"
        details_response = requests.get(details_url)
        details_data = details_response.json()
        extract = details_data['query']['pages'][str(place['pageid'])]['extract']
        landmark['summary'] = extract[:200] + '...' if len(extract) > 200 else extract
        landmark['category'] = categorize_landmark(extract)
        logging.debug(f"Categorized {landmark['title']} as {landmark['category']}")
        
        # Check if the landmark is within the specified bounding box
        if south <= landmark['lat'] <= north and west <= landmark['lon'] <= east:
            # Only add the landmark if its category is in the selected categories or if no categories are selected
            if not selected_categories or landmark['category'] in selected_categories:
                landmarks.append(landmark)
                logging.debug(f"Added landmark: {landmark['title']}")
            else:
                logging.debug(f"Skipped landmark {landmark['title']} due to category filter")
        else:
            logging.debug(f"Skipped landmark {landmark['title']} as it's outside the bounding box")

    logging.debug(f"Returning {len(landmarks)} landmarks")
    return jsonify(landmarks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
