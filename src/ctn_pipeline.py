from ctn_downloader import Downloader
from ctn_modeller import Modeller


if __name__ == "__main__":
    Downloader().cache_ctn()
    Modeller().build_data_model()
