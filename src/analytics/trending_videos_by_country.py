from src.core.youtube import YouTube
import pandas as pd


if __name__ == "__main__":

    youtube_api = YouTube()

    trending_videos = youtube_api.search_by_topic(max_results=10)
    videos_ids = [video["id"]["videoId"] for video in trending_videos["items"]]
    videos_info = youtube_api.get_video_info(','.join(videos_ids))['items']
    results = []
    for video in videos_info:
        vid_info = {
            'video_id': video['id'],
            'title': video['snippet'].get('title'),
            'view_count': int(video['statistics'].get('viewCount', 0)),
            'like_count': int(video['statistics'].get('likeCount', 0)),
            'dislike_count': int(video['statistics'].get('dislikeCount', 0)),
            'comment_count': int(video['statistics'].get('commentCount', 0)),
            'published_at': video['snippet'].get('publishedAt'),
            'channel_id': video['snippet'].get('channelId'),
        }
        results.append(vid_info)
    df = pd.DataFrame(results)
    pass
