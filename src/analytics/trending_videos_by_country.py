from src.cloud.bigquery import BigQueryClient
from src.core.youtube import YouTube
import pandas as pd
from datetime import datetime, timedelta


if __name__ == "__main__":

    youtube_api = YouTube()

    max_videos_per_batch = 50
    max_trending_videos = 1000
    regions = ["US", "UK", "BR", "DE", "FR", "MX"]
    for region_code in regions:
        print(f"Getting trending videos for {region_code}")

        published_after = (datetime.today() - timedelta(days=7))\
            .strftime("%Y-%m-%dT%H:%M:%SZ")

        trending_videos = youtube_api.search_by_topic(
            max_results=max_trending_videos,
            region_code=region_code,
            published_after=published_after)

        videos_ids = [video["id"]["videoId"] for video in trending_videos]
        videos_info = youtube_api.get_video_info(videos_ids, max_videos_per_batch=max_videos_per_batch)
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
                'published_after': published_after,
            }
            results.append(vid_info)
        df = pd.DataFrame(results)
        df['region_code'] = region_code

        # TODO: overwrite partition masked by region_code
        # Upload to BigQuery
        bigquery_client = BigQueryClient(project_id="sandbox-381517")
        df['dt'] = datetime.today()
        df['dt'] = pd.to_datetime(df['dt'])
        bigquery_client.upload_dataframe(
            dataset_id="youtube",
            table_id="trending",
            df=df,
            overwrite_partition=False,
            delete_table=False,
            partition_field="dt"
        )
