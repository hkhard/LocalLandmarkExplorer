from flask import Flask, render_template, jsonify, request
import requests
import logging
import json
from functools import lru_cache
from datetime import datetime, timedelta

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# In-memory cache configuration
CACHE_EXPIRATION = timedelta(hours=1)

@lru_cache(maxsize=100)
def get_cached_landmarks(cache_key, timestamp):
    # This function will be automatically memoized by lru_cache
    return None

def set_cached_landmarks(cache_key, data):
    # Update the cache with new data
    get_cached_landmarks.cache_clear()
    get_cached_landmarks(cache_key, datetime.now().timestamp())
    return data

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
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    search_query = request.args.get('search', '').strip()
    is_specific_landmark = request.args.get('specific', 'false').lower() == 'true'

    if lat and lon:
        center_lat = float(lat)
        center_lon = float(lon)
    else:
        north = float(request.args.get('north', 59.2753))
        south = float(request.args.get('south', 59.2753))
        east = float(request.args.get('east', 15.2134))
        west = float(request.args.get('west', 15.2134))
        center_lat = (north + south) / 2
        center_lon = (east + west) / 2

    logging.debug(f"Search query: {search_query}")
    logging.debug(f"Is specific landmark: {is_specific_landmark}")
    logging.debug(f"Center coordinates: Lat: {center_lat}, Lon: {center_lon}")

    # Generate a cache key based on the request parameters
    cache_key = f"landmarks:{center_lat}:{center_lon}:{search_query}:{is_specific_landmark}"

    # Try to get data from cache
    cached_data = get_cached_landmarks(cache_key, datetime.now().timestamp())
    if cached_data is not None:
        # Check if the cached data is still valid
        cache_timestamp = datetime.fromtimestamp(cached_data[1])
        if datetime.now() - cache_timestamp < CACHE_EXPIRATION:
            logging.debug("Returning data from cache")
            return jsonify(cached_data[0])

    url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={center_lat}|{center_lon}&gsradius=10000&gslimit=50&format=json"
    
    if search_query:
        url += f"&gsearch={search_query}"
    
    logging.debug(f"Sending request to Wikipedia API: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        logging.debug(f"Wikipedia API response status code: {response.status_code}")
        logging.debug(f"Raw Wikipedia API response: {data}")

        if 'query' not in data or 'geosearch' not in data['query']:
            logging.error(f"Unexpected API response format: {data}")
            return jsonify([])

        landmarks = []
        for place in data['query']['geosearch']:
            landmark = {
                "title": place['title'],
                "lat": float(place['lat']),
                "lon": float(place['lon']),
                "pageid": place['pageid']
            }
            logging.debug(f"Processing landmark: {landmark['title']}")

            if is_specific_landmark and search_query.lower() != landmark['title'].lower():
                logging.debug(f"Skipped landmark {landmark['title']} as it's not an exact match")
                continue

            details_url = f"https://en.wikipedia.org/w/api.php?action=query&pageids={place['pageid']}&prop=extracts&exintro&format=json&explaintext"
            details_response = requests.get(details_url)
            details_data = details_response.json()
            extract = details_data['query']['pages'][str(place['pageid'])]['extract']
            landmark['summary'] = extract[:200] + '...' if len(extract) > 200 else extract
            landmark['category'] = categorize_landmark(extract)
            logging.debug(f"Categorized {landmark['title']} as {landmark['category']}")
            
            landmarks.append(landmark)
            logging.debug(f"Added landmark: {landmark['title']}")

        if is_specific_landmark and len(landmarks) == 0:
            logging.debug(f"No exact match found for specific landmark search: {search_query}")
            return jsonify([])

        logging.debug(f"Returning {len(landmarks)} landmarks")

        # Cache the results
        set_cached_landmarks(cache_key, (landmarks, datetime.now().timestamp()))

        return jsonify(landmarks)
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from Wikipedia API: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
