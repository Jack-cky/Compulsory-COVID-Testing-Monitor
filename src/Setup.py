import os
from pathlib import Path


PTH_LOG = Path(os.getenv("PTH_LOG", "logs"))
PTH_PDF = Path(os.getenv("PTH_PDF", "data/pdf"))
PTH_ZIP = Path(os.getenv("PTH_ZIP", "data/zip"))
PTH_TAB = Path(os.getenv("PTH_TAB", "data/table"))
PTH_GEO = Path(os.getenv("PTH_GEO", "data/geocode"))


class Setup:
    def __init__(self) -> None:
        """
        Set up ouput directory for processing.
        """
        PTH_LOG.mkdir(parents=True, exist_ok=True)
        PTH_PDF.mkdir(parents=True, exist_ok=True)
        PTH_ZIP.mkdir(parents=True, exist_ok=True)
        PTH_TAB.mkdir(parents=True, exist_ok=True)
        PTH_GEO.mkdir(parents=True, exist_ok=True)
