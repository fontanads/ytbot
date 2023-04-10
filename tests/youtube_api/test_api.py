from src.core.youtube import YouTube


def test_search_by_topic(youtube_api):
    """Test search by topic."""

    response = youtube_api.search_by_topic(topic="python", max_results=5)

    assert len(response["items"]) == 5
    for video in response["items"]:
        assert video["id"]["videoId"] is not None
        assert video["snippet"]["channelId"] is not None
        assert video["snippet"]["channelTitle"] is not None
        assert video["snippet"]["title"] is not None
        assert video["snippet"]["publishedAt"] is not None


def test_get_channel_info(youtube_api):
    """Test get channel info."""

    response = youtube_api.get_channel_info(channel_id="UC8butISFwT-Wl7EV0hUK0BQ")
    channel = response["items"][0]
    assert channel["id"] == "UC8butISFwT-Wl7EV0hUK0BQ"
    assert channel["snippet"]["title"] == "freeCodeCamp.org"
    assert channel["snippet"]["customUrl"] == "@freecodecamp"
    # sleep(3)


if __name__ == "__main__":
    youtube_api = YouTube()
    test_search_by_topic(youtube_api)
    test_get_channel_info(youtube_api)