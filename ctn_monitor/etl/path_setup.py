from pathlib import Path

AIRFLOW_DATA_ROOT = Path("/opt/airflow/data")

PATH_DATA = {
    "pdf": "pdf",
    "zip": "zip",
    "tab": "table",
    "geo": "geocode",
    "out": "",
}


def get_path(kind: str) -> Path:
    return AIRFLOW_DATA_ROOT / PATH_DATA[kind]


def initialise_paths() -> None:
    """Set up output directories for processing."""
    for pth in PATH_DATA:
        get_path(pth).mkdir(parents=True, exist_ok=True)
