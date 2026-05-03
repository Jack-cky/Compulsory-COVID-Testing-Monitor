from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pandas as pd


def is_nonempty_file(path: Path) -> bool:
    try:
        return path.stat().st_size > 0
    except OSError:
        return False


@contextmanager
def _atomic_write(target: Path) -> Iterator[Path]:
    temp = target.with_suffix(f"{target.suffix}.tmp")
    try:
        yield temp
        temp.replace(target)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def write_bytes_atomic(content: bytes, target: Path) -> None:
    with _atomic_write(target) as temp:
        temp.write_bytes(content)


def write_parquet_atomic(df: pd.DataFrame, target: Path) -> None:
    with _atomic_write(target) as temp:
        df.to_parquet(temp)


def write_excel_atomic(df: pd.DataFrame, target: Path) -> None:
    with _atomic_write(target) as temp:
        df.to_excel(temp, index=False)
