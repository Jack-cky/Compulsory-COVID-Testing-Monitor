from Downloader import Downloader
from Extractor import Extractor
from Tabular import Tabular
from Geocoder import Geocoder
from DataModeller import DataModeller


def menu() -> None:
    Downloader().download_pdf()
    Extractor().extract_table()
    Tabular().tabulate_pdf()
    Geocoder().geocode_address()
    DataModeller().build_model()


if __name__ == "__main__":
    menu()
