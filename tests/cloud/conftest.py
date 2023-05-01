import pytest
import pandas as pd


def read_videos_table():
    return pd.read_json("tests/data/videos_table.json")


@pytest.fixture(scope="module")
def videos_table():
    return read_videos_table()


if __name__ == "__main__":
    # load json file as pandas dataframe
    df = read_videos_table()
    print(df)
    pass
