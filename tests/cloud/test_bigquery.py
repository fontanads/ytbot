from src.cloud.bigquery import BigQueryClient
from tests.cloud.conftest import read_videos_table
from datetime import datetime, timedelta


def test_client(bigquery_client):
    print(bigquery_client.client.project)
    pass


def test_upload_dataframe(bigquery_client, videos_table):
    videos_table['dt'] = datetime.today() + timedelta(days=-1)
    bigquery_client.upload_dataframe(
        dataset_id="youtube",
        table_id="videos",
        df=videos_table,
        overwrite_partition=True,
        delete_table=False,
        partition_field="dt"
    )


def test_download_table(bigquery_client):
    columns = ["video_id", "title", "channel_id", "view_count", "published_at"]

    df = bigquery_client.download_table(
        dataset_id="youtube",
        table_id="videos",
        columns=columns,
        limit=5
    )
    print(df.info())
    assert df.shape[0] == 5
    assert set(df.columns) == set(columns)  # Check that all columns are present


if __name__ == "__main__":
    bigquery_client = BigQueryClient(project_id="sandbox-381517")
    videos_table = read_videos_table()
    test_client(bigquery_client)
    test_upload_dataframe(bigquery_client, videos_table)
    test_download_table(bigquery_client)
    pass
