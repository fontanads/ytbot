import pytest

sample_video_ids = ['syevpJ-vovM', '24X_z6919Os', 'Qo7wNOxyZ2g', 'K_l3k7c5-Uo', 'lvIexkQrl2o',
                    'wq71OtMamuo', '4G8bm3zz1ck', '4PUcfFJQxjg', '7IDIfGDuew0', '5Djy_pzI13o']


def get_mock_response(video_ids: list, num_batches: int):
    mock_sample = [{"id": video_id,
                    "snippet": {"title": "Python Tutorial for Beginners",
                                "channelId": "UCkw4JCwteGrDHIsyIIKo4tQ",
                                "channelTitle": "edureka!", "publishedAt": "2020-12-14T11:30:01Z"},
                    "statistics": {"viewCount": str(i * 10),
                                   "likeCount": str(i * 10),
                                   "dislikeCount": str(i * 10),
                                   "commentCount": str(i * 10)}}
                   for video_id, i in enumerate(video_ids)]

    return {"kind": "youtube#videoListResponse",
            "pageInfo": {"totalResults": num_batches * len(video_ids)},
            "items": num_batches * mock_sample}


@pytest.fixture(params=[10], scope="module")
def mock_get_videos(request):
    """test sample: a list of video ids (strings)"""
    num_batches = request.param
    return num_batches * sample_video_ids, get_mock_response(sample_video_ids, num_batches)


if __name__ == "__main__":
    output = get_mock_response(sample_video_ids, 10)
    print(type(output))
    print("done")
