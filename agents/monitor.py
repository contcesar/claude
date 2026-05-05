import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


def get_client():
    return build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))


def get_channel_id(client, handle):
    resp = client.channels().list(
        part='id',
        forHandle=handle
    ).execute()
    items = resp.get('items', [])
    if not items:
        return None
    return items[0]['id']


def get_uploads_playlist_id(client, channel_id):
    resp = client.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    items = resp.get('items', [])
    if not items:
        return None
    return items[0]['contentDetails']['relatedPlaylists']['uploads']


def get_recent_video_ids(client, playlist_id, max_results=30):
    resp = client.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=max_results
    ).execute()
    return [item['contentDetails']['videoId'] for item in resp.get('items', [])]


def get_video_stats(client, video_ids):
    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        resp = client.videos().list(
            part='snippet,statistics',
            id=','.join(batch)
        ).execute()
        for item in resp.get('items', []):
            stats = item['statistics']
            snippet = item['snippet']
            thumbs = snippet.get('thumbnails', {})
            thumbnail = (
                thumbs.get('maxres', thumbs.get('high', thumbs.get('medium', {}))).get('url', '')
            )
            videos.append({
                'id': item['id'],
                'title': snippet['title'],
                'description': snippet.get('description', '')[:600],
                'published_at': snippet['publishedAt'],
                'thumbnail': thumbnail,
                'channel_title': snippet['channelTitle'],
                'channel_id': snippet['channelId'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
            })
    return videos


def analyze_channels(channels):
    client = get_client()
    all_outliers = []

    for ch in channels:
        name = ch['name']
        handle = ch['handle']
        try:
            channel_id = get_channel_id(client, handle)
            if not channel_id:
                print(f"Channel not found: {handle}")
                continue

            playlist_id = get_uploads_playlist_id(client, channel_id)
            if not playlist_id:
                continue

            video_ids = get_recent_video_ids(client, playlist_id)
            if not video_ids:
                continue

            videos = get_video_stats(client, video_ids)
            if not videos:
                continue

            avg_views = sum(v['views'] for v in videos) / len(videos)

            for video in videos:
                score = round(video['views'] / avg_views, 1) if avg_views else 0.0
                video['outlier_score'] = score
                video['channel_avg_views'] = round(avg_views)

            outliers = sorted(
                [v for v in videos if v['outlier_score'] >= 2.0],
                key=lambda x: x['outlier_score'],
                reverse=True
            )
            all_outliers.extend(outliers[:3])

        except Exception as e:
            print(f"Error processing {name}: {e}")

    return sorted(all_outliers, key=lambda x: x['outlier_score'], reverse=True)
