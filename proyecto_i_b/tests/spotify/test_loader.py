import json

import pytest

from spotify_app.constants import COLUMNS
from spotify_app.exceptions import DataLoadError
from spotify_app.loader import flatten_saved_tracks, load_saved_tracks
from spotify_app.validator import saved_tracks_validator


def test_flatten_one_row_per_track(api_items):
    
    df = flatten_saved_tracks(api_items)
    
    assert list(df.columns) == COLUMNS
    assert len(df) == 4
    assert df.loc[0, "artists"] == "Artist A; Artist B"
    assert df.loc[0, "main_artist"] == "Artist A"


def test_flatten_missing_track_gives_nulls():
    df = flatten_saved_tracks([{"added_at": "2024-01-01T00:00:00Z", "track": None}])
    assert df.loc[0, "track_id"] is None
    assert df.loc[0, "artists"] is None


def test_loads_api_json(api_json):
    df = load_saved_tracks(api_json)
    assert len(df) == 4
    assert df["track_id"].tolist()[:2] == ["t1", "t2"]


def test_loads_json_with_items_key(tmp_path, api_items):
    path = tmp_path / "page.json"
    path.write_text(json.dumps({"items": api_items, "next": None}), encoding="utf-8")
    assert len(load_saved_tracks(path)) == 4


def test_loads_flat_csv(tmp_path, tracks_df):
    path = tmp_path / "tracks.csv"
    tracks_df.to_csv(path, index=False)
    df = load_saved_tracks(str(path))
    assert df.shape == tracks_df.shape


def test_missing_path_raises_data_load_error(tmp_path):
    with pytest.raises(DataLoadError, match="not valid"):
        load_saved_tracks(tmp_path / "nope.json")


@pytest.mark.parametrize("route", ["", "  ", None])
def test_empty_path_raises_data_load_error(route):
    with pytest.raises(DataLoadError, match="empty"):
        load_saved_tracks(route)


def test_invalid_extension_raises_data_load_error(tmp_path):
    path = tmp_path / "tracks.xlsx"
    path.write_text("x")
    with pytest.raises(DataLoadError, match="extension"):
        load_saved_tracks(path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("{not json", "not valid JSON"),
        ('{"tracks": []}', "list of saved tracks"),
        ('"just a string"', "list of saved tracks"),
    ],
)
def test_bad_json_raises_data_load_error(tmp_path, content, message):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(DataLoadError, match=message):
        load_saved_tracks(path)


@pytest.mark.integration
def test_sample_has_2044_valid_and_1_invalid(sample_csv):
    df = load_saved_tracks(sample_csv)
    valid, invalid = saved_tracks_validator(df)
    assert len(df) == 2045
    assert len(valid) == 2044
    assert invalid["motivo"].tolist() == ["duration_out_of_range"]
