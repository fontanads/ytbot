from datetime import datetime, timedelta
from decouple import config

# import googleapiclient.errors
from googleapiclient.discovery import build

from google_auth_oauthlib.flow import InstalledAppFlow

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


# pagination wrapper for methods of api
def paginate(func):
    def wrapper(*args, **kwargs):
        # paginated search
        data = []
        while len(data) < kwargs.get("max_results", 100):
            response = func(*args, **kwargs)
            data.extend(response["items"])
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return data
    return wrapper


class YouTube:
    # initialize youtube api credentials
    def __init__(self):
        """Initialize youtube api credentials."""
        self.api_key = config("YOUTUBE_CLIENT_SECRET_FILE")
        self.service_name = "youtube"
        self.version = "v3"
        # get youtube api credentials
        flow = InstalledAppFlow.from_client_secrets_file(self.api_key, scopes)
        self.credentials = flow.run_local_server()
        # get youtube api service
        self.service = build(
            self.service_name, self.version, credentials=self.credentials
        )

    @paginate
    def search_by_topic(
        self,
        topic=None,
        obj_type="video",
        max_results=10,
        order="viewCount",
        published_after=None,
        published_before=None,
        region_code="US",
        pageToken=""
    ):
        """Search youtube videos by topic."""

        if not published_after:
            published_after = datetime.today() + timedelta(days=-14)
            published_after = published_after.strftime("%Y-%m-%dT%H:%M:%SZ")

        if not published_before:
            published_before = datetime.today()
            published_before = published_before.strftime("%Y-%m-%dT%H:%M:%SZ")

        assert (
            published_after < published_before
        ), "published_after must be before published_before"

        request = self.service.search().list(
            type=obj_type,
            q=topic,
            channelType="any",
            regionCode=region_code,
            order=order,
            maxResults=max_results,
            publishedAfter=published_after,
            publishedBefore=published_before,
            part="id,snippet",
            fields="kind,pageInfo,nextPageToken,items(id/videoId,snippet(publishedAt, channelId, channelTitle, title))",
            pageToken=pageToken
        )
        return request.execute()

    def get_channel_info(self, channel_id):
        request = self.service.channels().list(
            part="snippet,contentDetails,statistics", id=channel_id
        )

        return request.execute()

    def get_video_info(self, video_ids, max_videos_per_batch=50):
        data = []
        ids_gen = self.get_ids_batch(video_ids, max_videos_per_batch)  # batch generator
        while len(data) < len(video_ids):
            ids_batch = next(ids_gen)
            request = self.service.videos().list(
                part="snippet,contentDetails,statistics", id=ids_batch,
                maxResults=max_videos_per_batch
            )
            data.extend(request.execute()["items"])
        return data

    @staticmethod
    def get_ids_batch(ids, batch_size):
        for i in range(0, len(ids), batch_size):
            yield ids[i:i + batch_size]
