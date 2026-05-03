import io
import pytest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pandas as pd

from ctn_monitor.etl.tabulate import tabulate_zipped_excel

_PATCH_PATH = "ctn_monitor.etl.tabulate.get_path"
_PATCH_NONEMPTY = (
    "ctn_monitor.etl.tabulate.is_nonempty_file"
)


def _make_zip_with_excel(zip_path: Path) -> None:
    buf = io.BytesIO()
    pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_excel(
        buf, index=False
    )
    with ZipFile(zip_path, "w") as zf:
        zf.writestr("tables/table_0.xlsx", buf.getvalue())


class TestTabulateZippedExcel:
    @patch(_PATCH_NONEMPTY, return_value=True)
    @patch(_PATCH_PATH)
    def test_skips_when_cached(
        self, mock_path, mock_nonempty
    ):
        mock_path.return_value = Path("/fake/tab")

        result = tabulate_zipped_excel("ctn_20220426.zip")

        assert result == "ctn_20220426.parquet"

    def test_tabulates_excel_from_zip(self, tmp_path):
        zip_dir = tmp_path / "zip"
        tab_dir = tmp_path / "table"
        zip_dir.mkdir()
        tab_dir.mkdir()

        _make_zip_with_excel(zip_dir / "ctn_20220426.zip")

        with patch(_PATCH_PATH) as mock_path:
            mock_path.side_effect = (
                lambda k: zip_dir if k == "zip"
                else tab_dir
            )
            with patch(
                _PATCH_NONEMPTY, return_value=False
            ):
                result = tabulate_zipped_excel(
                    "ctn_20220426.zip"
                )

        assert result == "ctn_20220426.parquet"
        df = pd.read_parquet(
            tab_dir / "ctn_20220426.parquet"
        )
        assert len(df) == 2
        assert "source" in df.columns

    def test_raises_on_missing_zip(self, tmp_path):
        with patch(_PATCH_PATH, return_value=tmp_path):
            with patch(
                _PATCH_NONEMPTY, return_value=False
            ):
                with pytest.raises(
                    RuntimeError,
                    match="Failed to tabulate",
                ):
                    tabulate_zipped_excel(
                        "nonexistent.zip"
                    )

    def test_raises_on_zip_without_excel(self, tmp_path):
        zip_dir = tmp_path / "zip"
        zip_dir.mkdir()
        with ZipFile(zip_dir / "empty.zip", "w") as zf:
            zf.writestr("readme.txt", "no excel here")

        with patch(_PATCH_PATH, return_value=zip_dir):
            with patch(
                _PATCH_NONEMPTY, return_value=False
            ):
                with pytest.raises(
                    ValueError,
                    match="No Excel table found",
                ):
                    tabulate_zipped_excel("empty.zip")
