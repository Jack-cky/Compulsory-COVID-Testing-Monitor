from dotenv import load_dotenv
load_dotenv("config/.env")

import os

from src import Setup, Downloader, Extractor, Tabular, Geocoder, DataModeller


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
