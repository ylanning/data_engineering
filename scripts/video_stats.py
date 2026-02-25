import requests
import os
import json

API_KEY = os.getenv("API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
max_results = 50


def get_playlist_id():
    url = "https://youtube.googleapis.com/youtube/v3/channels"
    params = {"part": "contentDetails", "forHandle": CHANNEL_ID, "key": API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        channel_items = data.get("items", [])
        if not channel_items:
            print("No channel found with the provided handle.")
            return None

        channel_playlist_id = channel_items[0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]

        return channel_playlist_id
    except Exception as e:
        print(f"Error fetching playlist ID: {e}")
        return None


def get_playlist_items(playlist_id: str) -> list[str]:
    playlist_items_urls = "https://youtube.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "maxResults": max_results,
        "playlistId": playlist_id,
        "key": API_KEY,
    }
    page_token = None

    try:
        while True:
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(playlist_items_urls, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            video_ids = [item["contentDetails"]["videoId"] for item in items]

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return video_ids

    except Exception as e:
        print(f"Error fetching playlist items: {e}")
        return []


def batch_list(video_ids, batch_size=50):
    for id in range(0, len(video_ids), batch_size):
        yield video_ids[id : id + batch_size]


def extract_video_stats(video_ids: list[str]) -> list[dict[str, str]]:
    video_stats = []
    videos_url = "https://youtube.googleapis.com/youtube/v3/videos"
    params = {
        "part": "contentDetails",
        "part": "snippet",
        "part": "statistics",
        "key": API_KEY,
    }

    try:
        for batch in batch_list(video_ids):
            params["id"] = ",".join(batch)
            response = requests.get(videos_url, params=params)
            response.raise_for_status()
            data = response.json()
            # print(json.dumps(data, indent=2))

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item.get("snippet", {})
                content_details = item.get("contentDetails", {})
                statistics = item.get("statistics", {})

                video_entry = {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "published_at": snippet.get("publishedAt"),
                    "duration": content_details.get("duration"),
                    "view_count": statistics.get("viewCount"),
                    "like_count": statistics.get("likeCount"),
                    "comment_count": statistics.get("commentCount"),
                }

                video_stats.append(video_entry)

        return video_stats

    except requests.exceptions.RequestException as e:
        raise e


from pprint import pprint

if __name__ == "__main__":
    playlist_id = get_playlist_id()
    if playlist_id:
        print(f"Playlist ID: {playlist_id}")
        video_ids = get_playlist_items(playlist_id)
        # print(f"Video IDs: {video_ids}")
        extract_video_stats(video_ids)
        pprint(extract_video_stats(video_ids))
    else:
        print("Failed to retrieve playlist ID.")
