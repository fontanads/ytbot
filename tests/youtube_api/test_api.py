from src.core.youtube import YouTube
from tests.youtube_api.conftest import get_mock_response, sample_video_ids


def test_search_by_topic(youtube_api):
    """Test search by topic."""

    data = youtube_api.search_by_topic(topic="python", max_results=5)

    # check results
    assert len(data) == 5
    for video in data:
        assert video["id"]["videoId"] is not None
        assert video["snippet"]["channelId"] is not None
        assert video["snippet"]["channelTitle"] is not None
        assert video["snippet"]["title"] is not None
        assert video["snippet"]["publishedAt"] is not None


def test_pagination(youtube_api):
    max_results = 500
    data = youtube_api.search_by_topic(topic="python", max_results=max_results)
    # check results
    assert len(data) == max_results
    assert len(list(filter(None, [video['id'].get('videoId') for video in data]))) == max_results


def test_get_channel_info(youtube_api):
    """Test get channel info."""

    response = youtube_api.get_channel_info(channel_id="UC8butISFwT-Wl7EV0hUK0BQ")
    channel = response["items"][0]
    assert channel["id"] == "UC8butISFwT-Wl7EV0hUK0BQ"
    assert channel["snippet"]["title"] == "freeCodeCamp.org"
    assert channel["snippet"]["customUrl"] == "@freecodecamp"
    # sleep(3)


def test_get_videos_info(youtube_api, mock_get_videos, max_videos_per_batch=50):
    """Test get video info."""
    # mock data
    video_ids, full_request_execution = mock_get_videos
    video_ids = [f"{i}_{video_id}" for i, video_id in enumerate(video_ids)]
    data = []
    req_num = 0

    ids_gen = youtube_api.get_ids_batch(video_ids, max_videos_per_batch)  # batch generator
    while len(data) < len(video_ids):
        # generate next batch of ids
        ids_batch = next(ids_gen)
        assert len(ids_batch) <= max_videos_per_batch

        # mock get_video_info request
        batch_items = full_request_execution["items"][req_num:req_num + max_videos_per_batch]
        data.extend(batch_items)

        # update request number
        req_num += max_videos_per_batch
        if req_num > len(video_ids):
            raise Exception("Request number is greater than number of video ids")
    # check results
    assert len(data) == len(video_ids)


if __name__ == "__main__":

    # manual inputs instead of pytest fixtures
    youtube_api = YouTube()
    num_batch = 10
    mock_response = num_batch * sample_video_ids, get_mock_response(sample_video_ids, num_batch)

    # run tests manualy
    # test_search_by_topic(youtube_api)
    # test_pagination(youtube_api)
    # test_get_channel_info(youtube_api)
    test_get_videos_info(youtube_api, mock_response, max_videos_per_batch=50)
    print("All tests passed!")
