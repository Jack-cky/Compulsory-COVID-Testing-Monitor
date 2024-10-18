import os
from datetime import datetime, timedelta
from pathlib import Path

import requests

from .utils import setup_logger


PTH_LOG = Path(os.getenv("PTH_LOG", "logs"))
PTH_PDF = Path(os.getenv("PTH_PDF", "data/pdf"))


class Downloader:
    tmp_url = "https://www.chp.gov.hk/files/pdf/{}"
    tmp_file_name = "ctn_{}.pdf"
    
    def __init__(self, date_from: str=None, date_to: str=None) -> None:
        """
        Defines download date range.
        - Default downloads today's PDF.
        - Date range should be bounded between 20220111 and 20221223.
        
        Args:
            date_from: starting date formatted as YYYYMMDD.
            date_to: ending date formatted as YYYYMMDD.
        
        Raises:
            ValueError: if dates are not correctly formatted.  
        """
        self.logger = setup_logger("Downloader", PTH_LOG / "Downloader.log")
        
        if not (date_from and date_to):
            self.date_from = datetime.now()
            self.date_to = self.date_from
        else:
            try:
                self.date_from = datetime.strptime(date_from, "%Y%m%d")
                self.date_to = datetime.strptime(date_to, "%Y%m%d")
            except ValueError as e:
                self.logger.error(f"Incorrect date format: {e}")
                raise
        
        self.outstanding_days = (self.date_to - self.date_from).days + 1
    
    def _download_ctn_from_chp(self, date: str) -> None:
        """
        Downloads CTN for a given date.
        
        Args:
            date: date formatted as YYYYMMDD.
        
        Raises:
            RequestException: the given date does not have CTN.
        """
        try:
            file_name = self.tmp_file_name.format(date)
            url = self.tmp_url.format(file_name)
            
            response = requests.get(url)
            response.raise_for_status()
            
            with open(PTH_PDF / file_name, "wb") as file:
                file.write(response.content)
        
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"There is no CTN for {file_name}: {e}")
    
    def download_pdf(self) -> None:
        """
        Downloads CTN from the defined date range.
        """
        for delta in range(self.outstanding_days):
            if delta % 50 == 0:
                cnt = self.outstanding_days - delta
                self.logger.info(f"Pending {cnt} PDFs to be downloaded.")
            
            download_date = self.date_from + timedelta(days=delta)
            download_date = download_date.strftime("%Y%m%d")
            
            self._download_ctn_from_chp(download_date)
