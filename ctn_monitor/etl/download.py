import logging

import requests

from .path_setup import get_path
from .utils import is_nonempty_file, write_bytes_atomic

TMP_URL = "https://www.chp.gov.hk/files/pdf/{}"
TMP_FILE_NAME = "ctn_{}.pdf"

logger = logging.getLogger(__name__)

_session = requests.Session()


def download_chp_ctn(date: str) -> str:
    """
    Downloads CTN for a given date.

    Args:
        date: date formatted as YYYYMMDD.

    Raises:
        RuntimeError: the given date does not have CTN.
    """
    ctn_pdf = TMP_FILE_NAME.format(date)
    pth_pdf = get_path("pdf") / ctn_pdf

    if is_nonempty_file(pth_pdf):
        logger.info("%s already cached; skipping download", ctn_pdf)
        return ctn_pdf

    try:
        response = _session.get(TMP_URL.format(ctn_pdf), timeout=5)
        response.raise_for_status()
    except requests.RequestException as err:
        raise RuntimeError(f"Failed to download {ctn_pdf}: {err}") from err

    write_bytes_atomic(response.content, pth_pdf)

    return ctn_pdf
