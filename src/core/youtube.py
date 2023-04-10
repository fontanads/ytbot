from datetime import datetime, timedelta
from decouple import config

# import googleapiclient.errors
from googleapiclient.discovery import build

from google_auth_oauthlib.flow import InstalledAppFlow

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


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

    def search_by_topic(
        self,
        topic=None,
        type="video",
        max_results=10,
        order="viewCount",
        published_after=None,
        published_before=None,
        region_code="US",
    ):
        """Search youtube videos by topic."""

        if not published_after:
            published_after = datetime.today() + timedelta(days=-7)
            published_after = published_after.strftime("%Y-%m-%dT%H:%M:%SZ")

        if not published_before:
            published_before = datetime.today()
            published_before = published_before.strftime("%Y-%m-%dT%H:%M:%SZ")

        assert (
            published_after < published_before
        ), "published_after must be before published_before"

        request = self.service.search().list(
            type=type,
            q=topic,
            channelType="any",
            regionCode=region_code,
            order=order,
            maxResults=max_results,
            publishedAfter=published_after,
            publishedBefore=published_before,
            part="snippet",
            fields="items(id/videoId,snippet(publishedAt, channelId, channelTitle, title))",
        )

        return request.execute()

    def get_channel_info(self, channel_id):
        request = self.service.channels().list(
            part="snippet,contentDetails,statistics", id=channel_id
        )

        return request.execute()

    def get_video_info(self, video_id):
        request = self.service.videos().list(
            part="snippet,contentDetails,statistics", id=video_id
        )

        return request.execute()
