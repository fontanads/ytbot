import pytest
from src.core.youtube import YouTube
from src.cloud.bigquery import BigQueryClient


@pytest.fixture(scope="module")
def youtube_api():
    return YouTube()


@pytest.fixture(scope="module")
def bigquery_client():
    return BigQueryClient(project_id="sandbox-381517")
