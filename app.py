from flask import Flask, request, jsonify, render_template 
from flask_cors import CORS
import pandas as pd
import joblib
import logging
from pytube import YouTube, exceptions
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import scrape_code as scrape
from api_manager import api_key_manager 

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

model = joblib.load('final_nearest_neighbors.joblib')
vectorizer = joblib.load('final_tfidf_vectorizer.joblib')

grouped_lists = pd.read_csv('final_grouped_lists.csv')
grouped_lists['Transcript'] = grouped_lists['Transcript'].fillna('')

text_counts = vectorizer.transform(grouped_lists['Transcript'])
indices = pd.Series(grouped_lists.index, index=grouped_lists['Channel'])

def build_youtube_client():
    api_key = api_key_manager.get_api_key()
    if not api_key:
        logging.error("API key is missing")
        raise ValueError("API key is missing")
    return build('youtube', 'v3', developerKey=api_key)

def get_channel_id(url):
    try:
        ch = YouTube(url)
        return ch.channel_id
    except exceptions.RegexMatchError as e:
        logging.error(f"RegexMatchError: {e}")
        raise ValueError(f"Invalid YouTube URL: {url}")

def get_channel_name(url):
    try:
        ch = YouTube(url)
        return ch.author
    except exceptions.RegexMatchError as e:
        logging.error(f"RegexMatchError: {e}")
        raise ValueError(f"Invalid YouTube URL: {url}")

def get_profile_pic_from_video_id(video_id):
    youtube = build_youtube_client()
    retries = 0
    while retries < 5:
        try:
            video_response = youtube.videos().list(
                part="snippet",
                id=video_id
            ).execute()
            break
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in e.content.decode():
                logging.warning("Quota exceeded for current API key. Switching to next key.")
                youtube = build_youtube_client()
                retries += 1
            else:
                raise e

    if not video_response['items']:
        logging.error(f"No details found for the video with ID {video_id}")
        return None

    channel_id = video_response['items'][0]['snippet']['channelId']
    return get_profile_pic_direct(channel_id)

def get_profile_pic_direct(channel_id):
    youtube = build_youtube_client()
    retries = 0
    while retries < 5:
        try:
            channel_response = youtube.channels().list(
                part="snippet",
                id=channel_id
            ).execute()
            break
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in e.content.decode():
                logging.warning("Quota exceeded for current API key. Switching to next key.")
                youtube = build_youtube_client()
                retries += 1
            else:
                raise e

    if not channel_response['items']:
        logging.error(f"No details found for the channel with ID {channel_id}")
        return None

    profile_picture_url = channel_response['items'][0]['snippet']['thumbnails']['default']['url']
    return profile_picture_url

@app.route('/recommend', methods=['POST'])
def recommend():
    logging.debug("Received a request for recommendations.")
    data = request.get_json()
    if not data:
        logging.error("Invalid request data: No data provided.")
        return jsonify({"error": "Invalid request data"}), 400
    
    channel_name = data.get('channel')
    channel_url = data.get('url')
    if not channel_url:
        logging.error("Channel URL is required but not provided.")
        return jsonify({"error": "Channel URL is required"}), 400
 
    try:
        channel_id = get_channel_id(channel_url)
    except ValueError as e:
        logging.error(f"Error getting channel ID: {e}")
        return jsonify({"error": str(e)}), 400

    if not channel_name:
        logging.error("Channel name is required but not provided.")
        return jsonify({"error": "Channel name is required"}), 400
    
    logging.debug(f"Searching for channel: {channel_name}")

    if channel_name not in indices:
        logging.debug(f'\n{channel_name} is not present in Dataset. Going to scrape code\n')
        recommendations = scrape.get_similar_channels(channel_name, channel_id)
    else:
        logging.debug(f'{channel_name} present in dataset. Fetching recommendations.......\n')
        idx = indices[channel_name]
        distances, neighbor_indices = model.kneighbors(text_counts.getrow(idx), n_neighbors=6)
        recommendations = []

        for i in range(1, len(distances.flatten())):
            similar_channel = grouped_lists.iloc[neighbor_indices.flatten()[i]]
            profile_pic = get_profile_pic_from_video_id(similar_channel['Id'])
            channel_id = get_channel_id(f"https://www.youtube.com/watch?v={similar_channel['Id']}")
            channel_link = f"https://www.youtube.com/channel/{channel_id}"

            recommendations.append({
                "channel": similar_channel['Channel'],
                "distance": distances.flatten()[i],
                "profile": profile_pic,
                "link": channel_link
            })
        logging.debug(f"Recommendations: {recommendations}")

    if not recommendations:
        logging.warning("No recommendations found.")
        return jsonify({"error": "No recommendations found"}), 404

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
    

@app.route('/')
def home():
    logging.info('Home page accessed')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)


