from datetime import date

import requests
import os
import json
import urllib3

# Suppress SSL warnings when verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from airflow.decorators import task
from airflow.models import Variable

max_results = 50

# Disable SSL verification (workaround for Docker SSL issues)
# TODO: Fix properly by configuring SSL certs in container
SSL_VERIFY = False


def _get_api_credentials():
    """Get API credentials from env vars (local) or Airflow Variables (DAG)."""
    api_key = os.getenv("API_KEY") or Variable.get("API_KEY", default_var=None)
    channel_handle = os.getenv("CHANNEL_HANDLE") or Variable.get(
        "CHANNEL_HANDLE", default_var=None
    )
    return api_key, channel_handle


# Core functions (no decorators)
def _get_playlist_id():
    api_key, channel_handle = _get_api_credentials()
    url = "https://youtube.googleapis.com/youtube/v3/channels"
    params = {"part": "contentDetails", "forHandle": channel_handle, "key": api_key}

    try:
        response = requests.get(url, params=params, verify=SSL_VERIFY)
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


def _get_playlist_items(playlist_id: str) -> list[str]:
    api_key, _ = _get_api_credentials()
    playlist_items_urls = "https://youtube.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "maxResults": max_results,
        "playlistId": playlist_id,
        "key": api_key,
    }
    page_token = None
    all_video_ids = []

    try:
        while True:
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(
                playlist_items_urls, params=params, verify=SSL_VERIFY
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            video_ids = [item["contentDetails"]["videoId"] for item in items]
            all_video_ids.extend(video_ids)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return all_video_ids

    except Exception as e:
        print(f"Error fetching playlist items: {e}")
        return []


def batch_list(video_ids, batch_size=50):
    for i in range(0, len(video_ids), batch_size):
        yield video_ids[i : i + batch_size]


def _extract_video_stats(video_ids: list[str]) -> list[dict[str, str]]:
    api_key, _ = _get_api_credentials()
    video_stats = []
    videos_url = "https://youtube.googleapis.com/youtube/v3/videos"

    try:
        for batch in batch_list(video_ids):
            params = {
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(batch),
                "key": api_key,
            }
            response = requests.get(videos_url, params=params, verify=SSL_VERIFY)
            response.raise_for_status()
            data = response.json()

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


def _save_stats_to_json(extracted_stats: list[dict[str, str]]) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"video_stats_{date.today()}.json")

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(extracted_stats, json_file, indent=4, ensure_ascii=False)
    print(f"Saved to {file_path}")


# Airflow tasks (wrap core functions)
@task
def get_playlist_id():
    return _get_playlist_id()


@task
def get_playlist_items(playlist_id: str) -> list[str]:
    return _get_playlist_items(playlist_id)


@task
def extract_video_stats(video_ids: list[str]) -> list[dict[str, str]]:
    return _extract_video_stats(video_ids)


@task
def save_stats_to_json(extracted_stats: list[dict[str, str]]) -> None:
    return _save_stats_to_json(extracted_stats)


if __name__ == "__main__":
    playlist_id = _get_playlist_id()
    if playlist_id:
        print(f"Playlist ID: {playlist_id}")
        video_ids = _get_playlist_items(playlist_id)
        print(f"Found {len(video_ids)} videos")
        video_stats = _extract_video_stats(video_ids)
        print(f"Extracted stats for {len(video_stats)} videos")
        _save_stats_to_json(video_stats)
        print("Done!")
    else:
        print("Failed to retrieve playlist ID.")
