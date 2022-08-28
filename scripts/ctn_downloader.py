import os
import re
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Downloader:
    def __init__(self) -> None:
        self.create_cache_folder()
        self.update_download_dates()
        
        return None
    
    def create_cache_folder(self) -> None:
        # make directory for the first execution
        if not os.path.exists("data/cache"):
            os.makedirs("data/cache")
        
        return None

    def update_download_dates(self) -> None:
        # get date of last cached CTN
        if os.path.exists("data/done"):
            files = os.listdir("data/done")
            files.remove(".DS_Store") if ".DS_Store" in files else None
            last_update = max(re.findall(r"\d+", file)[0] for file in files)
        else:
            last_update = "20220113"
        
        # define range of date to download CTN
        self.date_start = datetime.strptime(last_update, "%Y%m%d") \
            + relativedelta(days=1)
        date_end = datetime.today()
        
        # define length of download period
        self.outstanding_days = date_end - self.date_start
        self.outstanding_days = self.outstanding_days.days
        
        return None

    def download_ctn_from_chp(self, date_ctn) -> None:
        # request CTN from CHP webiste
        file_name = f"ctn_{date_ctn}.pdf"
        uri = f"https://www.chp.gov.hk/files/pdf/{file_name}"
        response = requests.get(uri)
        
        # cache CTN
        if response.status_code == 200:
            with open(f"data/cache/{file_name}", "wb") as file:
                file.write(response.content)
            
            print(f"- CTN '{file_name}' has been downloaded.")
        
        return None

    def cache_ctn(self) -> None:
        for delta in range(self.outstanding_days):
            # donwload CTN for given date
            download_date = self.date_start + relativedelta(days=delta)
            download_date = download_date.strftime("%Y%m%d")
            self.download_ctn_from_chp(download_date)
        
        return None


if __name__ == "__main__":
    Downloader().cache_ctn()
