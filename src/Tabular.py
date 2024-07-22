import logging
import os
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from dotenv import load_dotenv


load_dotenv("config/.env")

PTH_LOG = Path(os.getenv("PTH_LOG", "logs"))
PTH_ZIP = Path(os.getenv("PTH_ZIP", "data/zip"))
PTH_TAB = Path(os.getenv("PTH_TAB", "data/table"))

logging.basicConfig(
    filename=PTH_LOG / "Tabular.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class Tabular:
    def __init__(self) -> None:
        """
        Define a list of ZIPs to be tabulated.
        """
        PTH_TAB.mkdir(parents=True, exist_ok=True)
        
        self.outstanding_tabs = self._get_outstanding_tab()
    
    def _get_outstanding_tab(self) -> set:
        """
        Find out a list of ZIPs that have not been processed to Parquets.
        
        Returns:
            A set of unprocessed ZIPs.
        """
        zips = {file.stem for file in PTH_ZIP.glob("*.zip")}
        tabs = {file.stem for file in PTH_TAB.glob("*.parquet")}
        
        return zips - tabs
    
    def _tabulate_excel_from_zip(self, ctn: str) -> None:
        """
        Tabulate tables from a single ZIP.
        
        Args:
            ctn: ZIP file name to be processed.
        """
        dfs = []
        
        try:
            with ZipFile(PTH_ZIP / f"{ctn}.zip", "r") as zip_files:
                for file in zip_files.namelist():
                    if file.endswith(".xlsx"):
                        with zip_files.open(file) as excel:
                            _df = pd.read_excel(excel)
                            cols = [f"col_{c+1}" for c in range(_df.shape[1])]
                            _df.columns = cols
                            dfs.append(_df)
        
        except Exception as e:
            logging.warning(f"Failed to tabulate tables from {ctn}: {str(e)}")
        
        else:
            df = pd.concat(dfs, ignore_index=True) \
                .assign(source=ctn)
            df.to_parquet(PTH_TAB / f"{ctn}.parquet")
    
    def tabulate_pdf(self) -> None:
        """
        Tabulate tables from outstanding ZIPs.
        """
        for idx, pdf in enumerate(self.outstanding_tabs):
            if idx % 50 == 0:
                cnt = len(self.outstanding_tabs) - idx
                logging.info(f"- Pending {cnt} ZIPs to be tabularised.")
            
            self._tabulate_excel_from_zip(pdf)


if __name__ == "__main__":
    Tabular().tabulate_pdf()
