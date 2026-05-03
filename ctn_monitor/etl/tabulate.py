import logging
from zipfile import ZipFile

import pandas as pd

from .path_setup import get_path
from .utils import is_nonempty_file, write_parquet_atomic

logger = logging.getLogger(__name__)


def tabulate_zipped_excel(ctn_zip: str) -> str:
    """
    Tabulate tables from a single ZIP.

    Args:
        ctn_zip: ZIP file name to be processed.

    Raises:
        RuntimeError: If the ZIP cannot be read or processed.
        ValueError: If no Excel table is found in the ZIP.
    """
    ctn_parquet = ctn_zip.removesuffix(".zip") + ".parquet"
    pth_tab = get_path("tab") / ctn_parquet

    if is_nonempty_file(pth_tab):
        logger.info("%s already cached; skipping tabulation", ctn_parquet)
        return ctn_parquet

    dfs = []
    try:
        with ZipFile(get_path("zip") / ctn_zip, "r") as zip_files:
            for zip_file in zip_files.namelist():
                if zip_file.endswith(".xlsx"):
                    with zip_files.open(zip_file) as excel:
                        df = pd.read_excel(excel)
                        df.columns = [f"col_{c+1}" for c in range(df.shape[1])]
                        dfs.append(df)
    except (FileNotFoundError, ValueError, OSError) as err:
        raise RuntimeError(f"Failed to tabulate tables from {ctn_zip}: {err}") from err

    if not dfs:
        raise ValueError(f"No Excel table found in {ctn_zip}")

    df = pd.concat(dfs, ignore_index=True).assign(source=ctn_zip)
    write_parquet_atomic(df, pth_tab)

    return ctn_parquet
