import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ctn_monitor.etl.extract import extract_pdf_table


class TestExtractPdfTable:
    @patch("ctn_monitor.etl.extract.is_nonempty_file", return_value=True)
    @patch("ctn_monitor.etl.extract.get_path")
    def test_skips_extraction_when_cached(self, mock_path, mock_nonempty):
        mock_path.return_value = Path("/fake/zip")

        result = extract_pdf_table("ctn_20220426.pdf", "id", "secret")

        assert result == "ctn_20220426.zip"

    @patch("ctn_monitor.etl.extract.is_nonempty_file", return_value=False)
    @patch("ctn_monitor.etl.extract.get_path")
    def test_raises_value_error_without_credentials(
        self, mock_path, mock_nonempty
    ):
        mock_path.return_value = Path("/fake")

        with pytest.raises(
            ValueError,
            match="CLIENT_ID and CLIENT_SECRET are required",
        ):
            extract_pdf_table("ctn_20220426.pdf", "", "")

    @patch("ctn_monitor.etl.extract.write_bytes_atomic")
    @patch("ctn_monitor.etl.extract.ExtractPDFJob")
    @patch("ctn_monitor.etl.extract.PDFServices")
    @patch("ctn_monitor.etl.extract.ServicePrincipalCredentials")
    @patch("ctn_monitor.etl.extract.is_nonempty_file", return_value=False)
    @patch("ctn_monitor.etl.extract.get_path")
    def test_extracts_and_returns_zip_filename(
        self, mock_path, mock_nonempty, mock_creds, mock_pdf_svc_cls,
        mock_job_cls, mock_write,
    ):
        mock_pdf_dir = MagicMock()
        mock_pdf_dir.__truediv__ = (
            lambda self, x: Path(f"/fake/pdf/{x}")
        )
        mock_zip_dir = MagicMock()
        mock_zip_dir.__truediv__ = (
            lambda self, x: Path(f"/fake/zip/{x}")
        )
        mock_path.side_effect = (
            lambda k: mock_zip_dir if k == "zip" else mock_pdf_dir
        )

        mock_pdf_svc = mock_pdf_svc_cls.return_value
        mock_stream = MagicMock()
        mock_stream.get_input_stream.return_value = b"zipdata"
        job_result = mock_pdf_svc.get_job_result.return_value
        get_resource = job_result.get_result.return_value
        get_resource.get_resource.return_value = MagicMock()
        mock_pdf_svc.get_content.return_value = mock_stream

        with patch.object(Path, "read_bytes", return_value=b"%PDF"):
            result = extract_pdf_table("ctn_20220426.pdf", "id", "secret")

        assert result == "ctn_20220426.zip"
        mock_write.assert_called_once()
