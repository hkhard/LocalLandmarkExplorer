from flask import Flask, render_template, jsonify, request
import requests
import logging
import json
import hashlib
import os
import time
from functools import lru_cache
import threading

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

CACHE_DIR = 'landmark_cache'
CACHE_EXPIRATION = 3600  # 1 hour

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def generate_cache_key(params):
    param_string = json.dumps(params, sort_keys=True)
    return hashlib.md5(param_string.encode()).hexdigest()

def get_file_cache_path(cache_key):
    return os.path.join(CACHE_DIR, f"{cache_key}.json")

@lru_cache(maxsize=100)
def get_cached_landmarks(cache_key):
    # Check file cache
    file_path = get_file_cache_path(cache_key)
    if os.path.exists(file_path):
        if time.time() - os.path.getmtime(file_path) < CACHE_EXPIRATION:
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            os.remove(file_path)  # Remove expired cache file
    return None

def set_cached_landmarks(cache_key, data):
    # Set file cache
    file_path = get_file_cache_path(cache_key)
    with open(file_path, 'w') as f:
        json.dump(data, f)
    
    # Clear the lru_cache to ensure it picks up the new file cache
    get_cached_landmarks.cache_clear()
    
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
    params = {
        'lat': request.args.get('lat'),
        'lon': request.args.get('lon'),
        'search': request.args.get('search', '').strip(),
        'specific': request.args.get('specific', 'false').lower() == 'true',
        'north': request.args.get('north'),
        'south': request.args.get('south'),
        'east': request.args.get('east'),
        'west': request.args.get('west')
    }

    cache_key = generate_cache_key(params)
    cached_data = get_cached_landmarks(cache_key)

    if cached_data is not None:
        logging.debug("Returning data from cache")
        return jsonify(cached_data)

    if params['lat'] and params['lon']:
        center_lat = float(params['lat'])
        center_lon = float(params['lon'])
    else:
        north = float(params['north'] or 59.2753)
        south = float(params['south'] or 59.2753)
        east = float(params['east'] or 15.2134)
        west = float(params['west'] or 15.2134)
        center_lat = (north + south) / 2
        center_lon = (east + west) / 2

    logging.debug(f"Search query: {params['search']}")
    logging.debug(f"Is specific landmark: {params['specific']}")
    logging.debug(f"Center coordinates: Lat: {center_lat}, Lon: {center_lon}")

    url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={center_lat}|{center_lon}&gsradius=10000&gslimit=50&format=json"
    
    if params['search']:
        url += f"&gsearch={params['search']}"
    
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

            if params['specific'] and params['search'].lower() != landmark['title'].lower():
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

        if params['specific'] and len(landmarks) == 0:
            logging.debug(f"No exact match found for specific landmark search: {params['search']}")
            return jsonify([])

        logging.debug(f"Returning {len(landmarks)} landmarks")

        # Cache the results
        set_cached_landmarks(cache_key, landmarks)

        return jsonify(landmarks)
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from Wikipedia API: {e}")
        return jsonify([])

@app.route('/clear_cache')
def clear_cache():
    get_cached_landmarks.cache_clear()
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)
        os.remove(file_path)
    return jsonify({"message": "Cache cleared"})

def cleanup_cache():
    current_time = time.time()
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)
        if current_time - os.path.getmtime(file_path) > CACHE_EXPIRATION:
            os.remove(file_path)

def run_cleanup():
    while True:
        time.sleep(3600)  # Sleep for 1 hour
        cleanup_cache()

cleanup_thread = threading.Thread(target=run_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
