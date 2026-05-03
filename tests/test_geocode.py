from pathlib import Path
from unittest.mock import patch
from collections import defaultdict

import pandas as pd

from ctn_monitor.etl.geocode import geocode_tab_address


def _make_tab_parquet(path: Path) -> None:
    df = pd.DataFrame({
        "col_1": ["1", "2"],
        "col_2": [
            "大角咀_x000D_ Tai Kok Tsui",
            "旺角_x000D_ Mong Kok",
        ],
        "col_3": [None, None],
    })
    df.to_parquet(path)


def _fake_geocode_result():
    return {
        "chi": {
            "ChiEstate": {"EstateName": "大角咀邨"},
            "BuildingName": "大角咀大廈",
        },
        "eng": {
            "Region": "KLN",
            "EngDistrict": {"DcDistrict": "YAU TSIM MONG DISTRICT"},
            "EngEstate": {"EstateName": "Tai Kok Tsui Estate"},
            "BuildingName": "Tai Kok Tsui Mansion",
        },
        "geo": {
            "Latitude": "22.32",
            "Longitude": "114.16",
        },
    }


class TestGeocodeTabAddress:
    @patch("ctn_monitor.etl.geocode.is_nonempty_file", return_value=True)
    @patch("ctn_monitor.etl.geocode.get_path")
    def test_skips_when_cached(self, mock_path, mock_nonempty):
        mock_path.return_value = Path("/fake/geo")

        geocode_tab_address("ctn_20220426.parquet")

        mock_nonempty.assert_called_once()

    @patch("ctn_monitor.etl.geocode.Address")
    def test_geocodes_and_writes_parquet(self, mock_addr_cls, tmp_path):
        tab_dir = tmp_path / "table"
        geo_dir = tmp_path / "geocode"
        tab_dir.mkdir()
        geo_dir.mkdir()

        _make_tab_parquet(tab_dir / "ctn_20220426.parquet")

        mock_addr_cls.return_value.ParseAddress.return_value = (
            _fake_geocode_result()
        )

        with patch(
            "ctn_monitor.etl.geocode.get_path"
        ) as mock_path:
            mock_path.side_effect = (
                lambda k: geo_dir if k == "geo" else tab_dir
            )
            with patch(
                "ctn_monitor.etl.geocode.is_nonempty_file",
                return_value=False,
            ):
                geocode_tab_address("ctn_20220426.parquet")

        df = pd.read_parquet(geo_dir / "ctn_20220426.parquet")
        assert len(df) == 2
        assert "latitude" in df.columns
        assert "source" in df.columns

    @patch("ctn_monitor.etl.geocode.Address")
    def test_handles_no_geocode_results(self, mock_addr_cls, tmp_path):
        tab_dir = tmp_path / "table"
        geo_dir = tmp_path / "geocode"
        tab_dir.mkdir()
        geo_dir.mkdir()

        _make_tab_parquet(tab_dir / "ctn_20220426.parquet")

        mock_addr_cls.return_value.ParseAddress.return_value = (
            defaultdict(lambda: {})
        )

        with patch(
            "ctn_monitor.etl.geocode.get_path"
        ) as mock_path:
            mock_path.side_effect = (
                lambda k: geo_dir if k == "geo" else tab_dir
            )
            with patch(
                "ctn_monitor.etl.geocode.is_nonempty_file",
                return_value=False,
            ):
                geocode_tab_address("ctn_20220426.parquet")

        df = pd.read_parquet(geo_dir / "ctn_20220426.parquet")
        assert len(df) == 0
