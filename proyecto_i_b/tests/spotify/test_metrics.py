import pandas as pd

from spotify_app.metrics import (
    library_summary,
    quality_report,
    saves_per_year,
    top_artists,
    tracks_by_decade,
)


def test_top_artists_counts_collaborations(valid_tracks):
    
    result = top_artists(valid_tracks, n=2)
    assert result["artist"].tolist() == ["X", "Y"]
    assert result["n_tracks"].tolist() == [2, 2]


def test_saves_per_year(valid_tracks):
    result = saves_per_year(valid_tracks)
    assert result.to_dict("list") == {"year": [2023, 2024], "n_saved": [2, 2]}


def test_tracks_by_decade(valid_tracks):
    result = tracks_by_decade(valid_tracks)
    assert result["decade"].tolist() == [1990, 2010]
    assert result["n_tracks"].tolist() == [2, 2]
    assert result["avg_duration_min"].tolist() == [3.5, 3.5]


def test_library_summary(valid_tracks):
    assert library_summary(valid_tracks) == {
        "n_tracks": 4,
        "n_artists": 3,
        "avg_duration_min": 3.5,
        "explicit_pct": 50.0,
    }


def test_library_summary_empty():
    assert library_summary(pd.DataFrame())["n_tracks"] == 0


def test_quality_report_counts_reasons(valid_tracks):
    invalid = pd.DataFrame({"motivo": ["duplicate_id", "missing_id; local_file", "local_file"]})
    report = quality_report(pd.DataFrame(index=range(7)), valid_tracks, invalid)
    assert report["filas_totales"] == 7
    assert report["filas_validas"] == 4
    assert report["filas_invalidas"] == 3
    assert report["motivos"] == {"duplicate_id": 1, "local_file": 2, "missing_id": 1}
