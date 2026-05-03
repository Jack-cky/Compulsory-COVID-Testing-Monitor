import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import requests

from ctn_monitor.etl.download import download_chp_ctn


class TestDownloadChpCtn:
    @patch("ctn_monitor.etl.download._session")
    @patch("ctn_monitor.etl.download.write_bytes_atomic")
    @patch("ctn_monitor.etl.download.is_nonempty_file", return_value=False)
    @patch("ctn_monitor.etl.download.get_path")
    def test_downloads_and_returns_filename(
        self, mock_path, mock_nonempty, mock_write, mock_session
    ):
        mock_path.return_value = Path("/fake/pdf")
        mock_resp = MagicMock()
        mock_resp.content = b"%PDF-fake"
        mock_session.get.return_value = mock_resp

        result = download_chp_ctn("20220426")

        assert result == "ctn_20220426.pdf"
        mock_resp.raise_for_status.assert_called_once()
        mock_write.assert_called_once_with(
            b"%PDF-fake", Path("/fake/pdf/ctn_20220426.pdf")
        )

    @patch("ctn_monitor.etl.download.is_nonempty_file", return_value=True)
    @patch("ctn_monitor.etl.download.get_path")
    def test_skips_download_when_cached(self, mock_path, mock_nonempty):
        mock_path.return_value = Path("/fake/pdf")

        result = download_chp_ctn("20220426")

        assert result == "ctn_20220426.pdf"

    @patch("ctn_monitor.etl.download._session")
    @patch("ctn_monitor.etl.download.is_nonempty_file", return_value=False)
    @patch("ctn_monitor.etl.download.get_path")
    def test_raises_runtime_error_on_failure(
        self, mock_path, mock_nonempty, mock_session
    ):
        mock_path.return_value = Path("/fake/pdf")
        mock_session.get.side_effect = requests.RequestException("timeout")

        with pytest.raises(RuntimeError, match="Failed to download"):
            download_chp_ctn("20220426")
