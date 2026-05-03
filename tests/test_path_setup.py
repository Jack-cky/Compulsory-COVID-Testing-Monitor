from unittest.mock import patch, MagicMock

from ctn_monitor.etl.path_setup import initialise_paths, PATH_DATA


class TestInitialisePaths:
    @patch("ctn_monitor.etl.path_setup.get_path")
    def test_creates_all_directories(self, mock_get_path):
        mock_dir = MagicMock()
        mock_get_path.return_value = mock_dir

        initialise_paths()

        assert mock_get_path.call_count == len(PATH_DATA)
        for key in PATH_DATA:
            mock_get_path.assert_any_call(key)
        mock_dir.mkdir.assert_called_with(parents=True, exist_ok=True)

    def test_creates_real_directories(self, tmp_path):
        with patch("ctn_monitor.etl.path_setup.AIRFLOW_DATA_ROOT", tmp_path):
            initialise_paths()

            for sub in PATH_DATA.values():
                assert (tmp_path / sub).is_dir()
