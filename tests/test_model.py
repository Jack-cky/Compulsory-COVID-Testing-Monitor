import pytest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from ctn_monitor.etl.model import build_model

_PATCH_GET_PATH = "ctn_monitor.etl.model.get_path"


def _make_geocoded_parquet(path: Path, date_suffix: str) -> None:
    df = pd.DataFrame({
        "address_chi": ["大角咀"],
        "address_eng": ["Tai Kok Tsui"],
        "region": ["KLN"],
        "district": ["YAU TSIM MONG DISTRICT"],
        "estate_chi": ["大角咀邨"],
        "building_chi": ["大角咀大廈"],
        "estate_eng": ["Tai Kok Tsui Estate"],
        "building_eng": ["Tai Kok Tsui Mansion"],
        "latitude": ["22.32"],
        "longitude": ["114.16"],
        "source": [f"ctn_{date_suffix}.parquet"],
    })
    df.to_parquet(path)


def _path_router(geo_dir, out_dir):
    return lambda k: geo_dir if k == "geo" else out_dir


class TestBuildModel:
    def test_builds_excel_from_parquets(self, tmp_path):
        geo_dir = tmp_path / "geocode"
        geo_dir.mkdir()
        _make_geocoded_parquet(
            geo_dir / "ctn_20220426.parquet", "20220426"
        )
        _make_geocoded_parquet(
            geo_dir / "ctn_20220428.parquet", "20220428"
        )

        with patch(_PATCH_GET_PATH) as mock_path:
            mock_path.side_effect = _path_router(
                geo_dir, tmp_path
            )
            build_model()

        out = tmp_path / "data.xlsx"
        assert out.exists()
        df = pd.read_excel(out)
        assert len(df) == 2
        assert "date" in df.columns
        assert "region_chi" in df.columns
        assert df["region_chi"].iloc[0] == "九龍"
        assert (
            df["district_eng"].iloc[0]
            == "Yau Tsim Mong District"
        )

    def test_empty_geo_directory(self, tmp_path):
        geo_dir = tmp_path / "geocode"
        geo_dir.mkdir()

        with patch(_PATCH_GET_PATH) as mock_path:
            mock_path.side_effect = _path_router(
                geo_dir, tmp_path
            )
            with pytest.raises(ValueError):
                build_model()

    def test_sorted_by_date(self, tmp_path):
        geo_dir = tmp_path / "geocode"
        geo_dir.mkdir()
        _make_geocoded_parquet(
            geo_dir / "ctn_20220430.parquet", "20220430"
        )
        _make_geocoded_parquet(
            geo_dir / "ctn_20220426.parquet", "20220426"
        )

        with patch(_PATCH_GET_PATH) as mock_path:
            mock_path.side_effect = _path_router(
                geo_dir, tmp_path
            )
            build_model()

        df = pd.read_excel(tmp_path / "data.xlsx")
        dates = df["date"].tolist()
        assert dates == sorted(dates)
