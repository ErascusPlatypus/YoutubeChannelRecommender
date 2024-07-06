from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import jsonify
import logging
from api_manager import api_key_manager

logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)

# main function - called in both app.py and scrape_code.py
def get_recommendations_from_api(channel_id, channel_name):
    logging.debug('\nUsing the API to find recommendations...........\n')
    def build_youtube_client():
        api_key = api_key_manager.get_api_key()
        return build('youtube', 'v3', developerKey=api_key)
    
    youtube = build_youtube_client()

    try:
        # Get uploaded videos playlist ID
        channel_response = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Fetch videos from the playlist
        video_ids = []
        next_page_token = None
        while True:
            playlist_response = youtube.playlistItems().list(
                part="contentDetails",
                maxResults=50,
                playlistId=uploads_playlist_id,
                pageToken=next_page_token
            ).execute()

            video_ids += [item['contentDetails']['videoId'] for item in playlist_response['items']]
            if len(video_ids) >= 50:
                video_ids = video_ids[:50]
                break

            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

        # Fetch video details
        video_details = youtube.videos().list(
            part="snippet",
            id=",".join(video_ids)
        ).execute()

        tags = []
        categories = []
        for video in video_details['items']:
            if 'tags' in video['snippet']:
                tags += video['snippet']['tags']
            categories.append(video['snippet']['categoryId'])

        # Get unique tags and categories
        tags = list(set(tags))
        categories = list(set(categories))

        similar_channels = set()
        max_results_per_search = 50

        def search_channels_by_query(query, max_results=max_results_per_search):
            search_response = youtube.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=max_results
            ).execute()
            for item in search_response['items']:
                channel_id = item['snippet']['channelId']
                channel_response = youtube.channels().list(
                    part="statistics",
                    id=channel_id
                ).execute()
                if channel_response['items'][0]['statistics'].get('subscriberCount') and int(channel_response['items'][0]['statistics']['subscriberCount']) >= 15000:
                    similar_channels.add(channel_id)
                    if len(similar_channels) >= 5:
                        break

        for tag in tags:
            search_channels_by_query(tag)
            if len(similar_channels) >= 5:
                break

        if len(similar_channels) < 5:
            for category in categories:
                search_response = youtube.search().list(
                    part="snippet",
                    type="channel",
                    videoCategoryId=category,
                    maxResults=10
                ).execute()
                for item in search_response['items']:
                    channel_id = item['snippet']['channelId']
                    channel_response = youtube.channels().list(
                        part="statistics",
                        id=channel_id
                    ).execute()
                    if channel_response['items'][0]['statistics'].get('subscriberCount') and int(channel_response['items'][0]['statistics']['subscriberCount']) >= 15000:
                        similar_channels.add(channel_id)
                        if len(similar_channels) >= 5:
                            break
                if len(similar_channels) >= 5:
                    break

        # Remove the target channel from the results
        similar_channels.discard(channel_id)

        # Limit to 5 channels
        similar_channels = list(similar_channels)[:5]

        # Fetch details for similar channels in one request
        if similar_channels:
            channel_response = youtube.channels().list(
                part="snippet,statistics",
                id=",".join(similar_channels)
            ).execute()

            channel_titles = [
                {
                    "channel": channel["snippet"]["title"],
                    "distance": 1.0,
                    "profile": channel["snippet"]["thumbnails"]["default"]["url"],
                    "link": f"https://www.youtube.com/channel/{channel['id']}"
                } for channel in channel_response["items"]
            ]
            
            return channel_titles[:5]
        else:
            logging.error(f"Channel '{channel_name}' not found in the dataset.")
            return jsonify({"error": f"'{channel_name}' not found in the dataset."}), 404

    except HttpError as e:
        if e.resp.status == 403 and 'quotaExceeded' in e.content.decode():
            logging.warning("Quota exceeded for current API key. Switching to next key.")
            youtube = build_youtube_client()
            return get_recommendations_from_api(channel_id, channel_name)  # Retry with the new key
        else:
            logging.error(f"HttpError: {e}")
            return jsonify({"error": "An error occurred with the YouTube API."}), 500
