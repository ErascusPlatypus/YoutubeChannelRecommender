from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import logging
import requests
from bs4 import BeautifulSoup
from pytube import YouTube

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

model = joblib.load('new_nearest_neighbors.joblib')
vectorizer = joblib.load('new_tfidf_vectorizer.joblib')
grouped_lists = pd.read_csv('new_grouped_lists.csv')
grouped_lists['Transcript'] = grouped_lists['Transcript'].fillna('')
text_counts = vectorizer.fit_transform(grouped_lists['Transcript'])
indices = pd.Series(grouped_lists.index, index=grouped_lists['Channel'])

def get_channel_name(url):
    ch = YouTube(url)
    return ch.author

def get_similar_channels(channel_name):
    try:
        channel_name = channel_name.replace(" ", "-")
        url = f"https://similarchannels.com/c/{channel_name}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        channel_list = soup.select('#channel_list .l-row.grid .l-info a h5.l-title')
        
        if not channel_list:
            logging.error(f"Channel '{channel_name}' not found in the dataset.")
            return jsonify({"error": f"'{channel_name}' not found in the dataset."}), 404
        
        channel_titles = [{'channel': title.get_text(strip=True), 'distance': 1.0} for title in channel_list]
        print(channel_titles)
        return channel_titles[:5]
    
    except requests.exceptions.RequestException as e:
        print(f"Error during requests: {e}")
        return []
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

@app.route('/recommend', methods=['POST'])
def recommend():
    logging.debug("Received a request for recommendations.")
    try:
        data = request.json
        logging.debug(f"Request data: {data}")
        channel_name = data.get('channel')
    except Exception as e:
        logging.error(f"Error parsing request data: {e}")
        return jsonify({"error": "Invalid request data"}), 400

    if not channel_name:
        logging.error("Channel name is required but not provided.")
        return jsonify({"error": "Channel name is required"}), 400
    
    logging.debug(f"Searching for channel: {channel_name}")

    if channel_name not in indices:
        recommendations = get_similar_channels(channel_name)
    else:
        idx = indices[channel_name]
        distances, neighbor_indices = model.kneighbors(text_counts.getrow(idx), n_neighbors=6)
        names_similar = pd.Series(neighbor_indices.flatten()).map(grouped_lists.reset_index()['Channel'])

        recommendations = []
        for i in range(1, len(distances.flatten())):
            print(names_similar[i], end=' , ')
            recommendations.append({
                "channel": names_similar[i],
                "distance": distances.flatten()[i]
            })
        logging.debug(f"Recommendations: {recommendations}")

    return jsonify({
        "channel": channel_name,
        "recommendations": recommendations
    })

@app.route('/get_channel', methods=['POST'])
def get_channel():
    data = request.json
    youtube_url = data.get('url')
    if not youtube_url:
        return jsonify({"error": "Invalid URL"}), 400
    try:
        channel_name = get_channel_name(youtube_url)
        return jsonify({"channel": channel_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
