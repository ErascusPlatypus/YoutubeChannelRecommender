import requests
from bs4 import BeautifulSoup
import api_code as api
import helper as profile
import logging

def get_similar_channels(channel_name, channel_id):
    try:
        logging.debug(f'Scraping the web for recommendations.......\n')
        channel_name = channel_name.replace(" ", "-")
        url = f"https://similarchannels.com/c/{channel_name}"
        response = requests.get(url)
        
        if response.status_code != 200:
            logging.debug(f'{channel_name} not found. Switching to API..........\n')
            return api.get_recommendations_from_api(channel_id, channel_name)
        
        logging.debug('Found recommendations on scraping......')
        soup = BeautifulSoup(response.content, 'html.parser')
        channel_list = soup.select('#channel_list .l-row.grid .l-info a h5.l-title')
        channel_list = [title.get_text(strip=True) for title in channel_list]
        print("Channel List:", channel_list)
        
        channel_img = []
        channel_ids = []
        for channel in channel_list:
            channel_code = channel.replace(" ", "-")
            url = f'https://similarchannels.com/c/{channel_code}'
            img = profile.get_pic(url)
            channel_id = profile.get_channel_id_scraping(url)
            
            print(f"Channel: {channel}, URL: {url}, Img: {img}, Channel ID: {channel_id}")
            
            if img is None or channel_id is None:
                print(f"Skipping channel due to missing data: {channel}")
                continue
            
            channel_img.append(img)
            channel_ids.append(channel_id)
        
        print("Channel Images:", channel_img)
        print("Channel IDs:", channel_ids)
        
        if len(channel_list) < 5:
            logging.debug('Channel list found less than 5 elements. Switching to API..........')
            api_recommendations = api.get_recommendations_from_api(channel_id, channel_name)
            api_recommendations_titles = [
                {
                    "channel": rec["channel"],
                    "distance": 1.0,
                    "profile": rec["profile"],
                    "link": rec["link"]
                } for rec in api_recommendations
            ]
            return api_recommendations_titles
        
        channel_list = channel_list[:5]

        if not channel_list:
            logging.debug('Channel List empty. Switching to API........')
            return api.get_recommendations_from_api(channel_id, channel_name)
        
        channel_titles = [
            {
                "channel": title,
                "distance": 1.0,
                "profile": channel_img[i],
                "link": f"https://www.youtube.com/channel/{channel_ids[i]}"
            } for i, title in enumerate(channel_list)
        ]
        
        print("Channel Titles:", channel_titles)
        return channel_titles
    
    except requests.exceptions.RequestException as e:
        print(f"\nError during requests: {e}")
        return []
    
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return api.get_recommendations_from_api(channel_id, channel_name)
