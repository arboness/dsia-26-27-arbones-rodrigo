import pytest

from spotify_app.exceptions import ValidationError
from spotify_app.loader import flatten_saved_tracks
from spotify_app.validator import SavedTracksValidator, saved_tracks_validator


def test_api_items_split_valid_and_invalid(api_items):
    
    df = flatten_saved_tracks(api_items)
    
    valid, invalid = saved_tracks_validator(df)
    
    assert valid["track_id"].tolist() == ["t1", "t2"]
    assert len(invalid) == 2


def test_invalid_rows_explain_why(api_items):
    _, invalid = saved_tracks_validator(flatten_saved_tracks(api_items))
    assert invalid["motivo"].tolist() == ["duplicate_id", "missing_id; local_file"]


def test_valid_rows_get_derived_columns(api_items):
    valid, _ = saved_tracks_validator(flatten_saved_tracks(api_items))
    assert valid["release_year"].tolist() == [2020, 1999]
    assert valid["duration_min"].tolist() == [3.0, 3.33]


def test_missing_column_raises_validation_error(tracks_df):
    with pytest.raises(ValidationError, match="duration_ms"):
        saved_tracks_validator(tracks_df.drop(columns="duration_ms"))


@pytest.mark.parametrize(
    ("duration_ms", "is_valid"),
    [
        (29_999, False),   
        (30_000, True),    
        (1_800_000, True),  
        (1_800_001, False),
        (None, False),
        (-1, False),
    ],
)
def test_duration_range(tracks_df, duration_ms, is_valid):
    df = tracks_df.assign(duration_ms=[duration_ms])
    valid, _ = saved_tracks_validator(df)
    assert len(valid) == int(is_valid)


@pytest.mark.parametrize(
    ("release_date", "is_valid"),
    [
        ("2020", True),        
        ("2020-07", True),     
        ("2025-01-01", True),  
        ("2026-01-01", False),  
        ("1899-12-31", False),
        ("0000", False),
        (None, False),
    ],
)
def test_release_date_rules(tracks_df, release_date, is_valid):
    df = tracks_df.assign(release_date=[release_date])
    valid, _ = saved_tracks_validator(df)
    assert len(valid) == int(is_valid)


@pytest.mark.parametrize(
    ("column", "value", "rule"),
    [
        ("track_name", "  ", "missing_name"),
        ("artists", None, "missing_artist"),
        ("is_local", "True", "local_file"),
        ("added_at", "ayer", "bad_added_at"),
    ],
)
def test_each_rule_is_reported(tracks_df, column, value, rule):
    df = tracks_df.assign(**{column: [value]})
    _, invalid = saved_tracks_validator(df)
    assert rule in invalid.loc[0, "motivo"]


def test_violations_table_has_one_column_per_rule(tracks_df):
    validator = SavedTracksValidator()
    table = validator.violations(tracks_df)
    assert list(table.columns) == list(validator.rules)
    assert not table.any(axis=None)
