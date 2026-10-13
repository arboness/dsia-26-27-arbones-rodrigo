import json

import pytest

from spotify_app.cli import build_parser, main

EXPECTED_FILES = [
    "clean.csv",
    "invalid_tracks.csv",
    "quality.json",
    "top_artists.csv",
    "saves_per_year.csv",
    "tracks_by_decade.csv",
]


def test_parser_requires_arguments():
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args([])
    assert exc.value.code == 2


def test_main_smoke_with_api_json(tmp_path, api_json, capsys):
    
    out_dir = tmp_path / "salida"
    
    code = main(["--input", str(api_json), "--output", str(out_dir / "clean.csv")])
    
    assert code == 0
    for name in EXPECTED_FILES:
        assert (out_dir / name).is_file(), name
    report = json.loads((out_dir / "quality.json").read_text(encoding="utf-8"))
    assert report["filas_validas"] == 2
    assert "OK: 2 valid tracks, 2 invalid tracks" in capsys.readouterr().out


def test_main_returns_1_on_missing_input(tmp_path, capsys):
    code = main(["--input", str(tmp_path / "nope.csv"), "--output", str(tmp_path / "out.csv")])
    assert code == 1
    assert "Error" in capsys.readouterr().err


def test_main_returns_1_on_missing_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("track_id,track_name\nt1,Song\n", encoding="utf-8")
    assert main(["--input", str(bad), "--output", str(tmp_path / "out.csv")]) == 1


@pytest.mark.integration
def test_main_on_sample(tmp_path, sample_csv):
    output = tmp_path / "clean.csv"
    assert main(["--input", str(sample_csv), "--output", str(output)]) == 0
    report = json.loads((tmp_path / "quality.json").read_text(encoding="utf-8"))
    assert report["filas_validas"] == 2044
    assert report["motivos"] == {"duration_out_of_range": 1}
