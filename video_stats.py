import requests
import os
import json

API_KEY = os.getenv('API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')

url = f"https://youtube.googleapis.com/youtube/v3/channels"
params = {
    'part': 'contentDetails',
    'forHandle': CHANNEL_ID,
    'key': API_KEY
}

def get_playlist_id():
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        channel_items = data.get('items', [])
        if not channel_items:
            print("No channel found with the provided handle.")
            return None

        channel_playlist_id = channel_items[0]['contentDetails']['relatedPlaylists']['uploads']

        return channel_playlist_id
    except Exception as e:
        print(f"Error fetching playlist ID: {e}")
        return None


if __name__ == "__main__":
    playlist_id = get_playlist_id()
    if playlist_id:
        print(f"Playlist ID: {playlist_id}")
    else:
        print("Failed to retrieve playlist ID.")