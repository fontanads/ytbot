from datetime import datetime, timedelta
import pandas as pd
from googleapiclient.errors import HttpError
from src.cloud.bigquery import BigQueryClient
from src.core.youtube import YouTube
from src.constants import (DEFAULT_BQ_DATASET,
                           DEFAULT_GCP_PROJECT,
                           MAX_VIDEOS_PER_BATCH,
                           TRENDING_TABLE_ID)


if __name__ == "__main__":

    youtube_api = YouTube()

    max_trending_videos = 1000
    regions = ["US", "UK", "BR", "DE", "FR", "MX"]
    dataframes_list = []
    for region_code in regions:
        print(f"\n\nGetting trending videos for {region_code}")

        published_after = (datetime.today() - timedelta(days=7))\
            .strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            trending_videos = youtube_api.search_by_topic(
                max_results=max_trending_videos,
                region_code=region_code,
                published_after=published_after)

            videos_ids = [video["id"]["videoId"] for video in trending_videos]
            videos_info = youtube_api.get_video_info(videos_ids, max_videos_per_batch=MAX_VIDEOS_PER_BATCH)
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
                    'channel_title': video['snippet'].get('channelTitle'),
                    'published_after': published_after,
                }
                results.append(vid_info)
            df = pd.DataFrame(results)
            df['region_code'] = region_code
            dataframes_list.append(df)
        except HttpError as e:
            print(f"Error getting trending videos for {region_code}")
            print(e.status_code)
            # print(e.reason)
            for error in e.error_details:
                print("Reason: ", error.get('reason'))
                print("Domain: ", error.get('domain'))
                print("Message: ", error.get('message'))
            continue
        except Exception as e:
            print(f"Error getting trending videos for {region_code}")
            print(e.status_code)
            for error in e.error_details:
                print("Reason: ", error.get('reason'))
                print("Domain: ", error.get('domain'))
                print("Message: ", error.get('message'))
            continue

    if len(dataframes_list) == 0:
        raise Exception("No data to upload")

    df = pd.concat(dataframes_list)

    # TODO: overwrite partition masked by region_code
    # Upload to BigQuery
    bigquery_client = BigQueryClient(project_id=DEFAULT_GCP_PROJECT)
    df['dt'] = datetime.today()
    df['dt'] = pd.to_datetime(df['dt'])
    bigquery_client.upload_dataframe(
        dataset_id=DEFAULT_BQ_DATASET,
        table_id=TRENDING_TABLE_ID,
        df=df,
        overwrite_partition=True,
        delete_table=False,
        partition_field="dt"
    )
