import os
from dotenv import load_dotenv

load_dotenv()

class ApiKeyManager:
    def __init__(self):
        self.api_keys = os.getenv('YOUTUBE_API_KEYS').split(',')
        self.current_index = 2

    def get_api_key(self):
        key = self.api_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        return key

# Initialize a single instance to be used across the application
api_key_manager = ApiKeyManager()
