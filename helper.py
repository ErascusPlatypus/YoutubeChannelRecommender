from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from lxml import html
import requests
from pytube import YouTube, exceptions
import logging
from api_manager import api_key_manager

logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)

# used in this file only
def get_channel_id(url):
    try:
        ch = YouTube(url)
        return ch.channel_id
    except exceptions.RegexMatchError as e:
        logging.error(f"RegexMatchError: {e}")
        raise ValueError(f"Invalid YouTube URL: {url}")

# used in this file only
def extract_video_id(video_url):
    # Regular expression to match the video ID in the URL
    video_id_match = re.match(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)", video_url)
    if video_id_match:
        return video_id_match.group(1)
    return None

# used in this file only
def build_youtube_client():
    api_key = api_key_manager.get_api_key()
    return build('youtube', 'v3', developerKey=api_key)

# used in app.py
def get_profile_pic_from_video_id(video_id):
    youtube = build_youtube_client()

    while True:
        try:
            # Retrieve the video details using the video ID
            video_response = youtube.videos().list(
                part="snippet",
                id=video_id
            ).execute()
            break
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in e.content.decode():
                logging.warning("Quota exceeded for current API key. Switching to next key.")
                youtube = build_youtube_client()
            else:
                raise e

    if not video_response['items']:
        logging.error(f"No details found for the video with ID {video_id}")
        return None

    # Get the channel ID
    channel_id = video_response['items'][0]['snippet']['channelId']

    return get_channel_pic_direct(channel_id)

#used in app.py
def get_channel_pic_direct(channel_id):
    youtube = build_youtube_client()

    while True:
        try:
            # Retrieve the channel details using the channel ID
            channel_response = youtube.channels().list(
                part="snippet",
                id=channel_id
            ).execute()
            break
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in e.content.decode():
                logging.warning("Quota exceeded for current API key. Switching to next key.")
                youtube = build_youtube_client()
            else:
                raise e

    if not channel_response['items']:
        logging.error(f"No details found for the channel with ID {channel_id}")
        return None

    # Get the profile picture URL
    profile_picture_url = channel_response['items'][0]['snippet']['thumbnails']['default']['url']

    return profile_picture_url

# used in scrape code file
def get_channel_id_scraping(url):
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content
    tree = html.fromstring(html_content)

    # Get the element using XPath
    element = tree.xpath('/html/body/div[1]/main/div[4]/div[1]/a[2]')

    # Extract the href attribute
    if element:
        href = element[0].get('href')
        logging.debug(f"Found href: {href}")
    else:
        href = ''
        logging.error("Element not found")

    vid_id = extract_video_id(href)
    ch_id = get_channel_id(f"https://www.youtube.com/watch?v={vid_id}")

    return ch_id

# used in scrape code file
def get_pic(url):
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content
    tree = html.fromstring(html_content)

    # Get the element using XPath
    element = tree.xpath('/html/body/div[1]/main/div[4]/div[1]/a[2]')

    # Extract the href attribute
    if element:
        href = element[0].get('href')
        logging.debug(f"Found href: {href}")
    else:
        href = ''
        logging.error("Element not found")

    vid_id = extract_video_id(href)
    ch_id = get_channel_id(f"https://www.youtube.com/watch?v={vid_id}")
    return get_channel_pic_direct(ch_id)
