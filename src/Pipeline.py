import os

from dotenv import load_dotenv

from Setup import Setup
from Downloader import Downloader
from Extractor import Extractor
from Tabular import Tabular
from Geocoder import Geocoder
from DataModeller import DataModeller


load_dotenv("config/.env")

DATE_FROM = os.getenv("DATE_FROM")
DATE_TO = os.getenv("DATE_TO")


class Pipeline:
    def __init__(self) -> None:
        Setup()
        Downloader(DATE_FROM, DATE_TO).download_pdf()
        Extractor().extract_table()
        Tabular().tabulate_pdf()
        Geocoder().geocode_address()
        DataModeller().build_model()


if __name__ == "__main__":
    Pipeline()
