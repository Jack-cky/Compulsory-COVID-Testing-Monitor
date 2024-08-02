import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from AddressParser import Address
from utils import setup_logger


load_dotenv("config/.env")

PTH_LOG = Path(os.getenv("PTH_LOG", "logs"))
PTH_TAB = Path(os.getenv("PTH_TAB", "data/table"))
PTH_GEO = Path(os.getenv("PTH_GEO", "data/geocode"))


class Geocoder:
    tmp_msg = "Failed to fetch geocode from {} address (Tier {}): {}"
    
    def __init__(self) -> None:
        """
        Define a list of Parquets to be geocoded.
        """
        self.logger = setup_logger("Geocoder", PTH_LOG / "Geocoder.log")
        
        self.outstanding_pdfs = self._get_outstanding_pdf()
    
    def _get_outstanding_pdf(self) -> set:
        """
        Find out a list of Parquets that have not been parsed.
        
        Returns:
            A set of unprocessed Parquets.
        """
        tabs = {file.stem for file in PTH_TAB.glob("*.parquet")}
        geos = {file.stem for file in PTH_GEO.glob("*.parquet")}
        
        return tabs - geos
    
    def _split_address(self, place: str) -> tuple:
        """
        Separate address by language.
        
        Returns:
            A tuple of Chinese and English Addresses.
        """
        addr = place.replace("_x000D_", " ")
        
        chr_chi = re.findall(r"[\u4e00-\u9fff]", addr)
        
        if chr_chi:
            ptr_start = addr.find(chr_chi[0])
            ptr_end = addr.rfind(chr_chi[-1]) + 1
            
            addr_chi = addr[ptr_start:ptr_end]
            addr_eng = addr[ptr_end:]
        else:
            addr_chi = ""
            addr_eng = addr
        
        addr_chi = addr_chi.strip()
        addr_eng = addr_eng.strip()
        
        return addr_chi, addr_eng
    
    def _get_geocode(self, addr: str) -> pd.DataFrame:
        """
        Query geocode from an address.
        
        Returns:
            A dataframe of geographic information.
        """
        addr_chi, addr_eng = self._split_address(addr)
        addr_full = f"{addr_chi}, {addr_eng}"
        
        if addr_chi and addr_eng:
            ad = Address(addr_full)
            result = ad.ParseAddress()
        else:
            result = None
        
        if not result and addr_eng:
            self.logger.warning(self.tmp_msg.format("full", 1, addr_full))
            
            ad = Address(f"{addr_eng}")
            result = ad.ParseAddress()
        
        if not result and addr_chi:
            self.logger.warning(self.tmp_msg.format("English", 2, addr_eng))
            
            ad = Address(f"{addr_chi}")
            result = ad.ParseAddress()
        
        if not result:
            self.logger.warning(self.tmp_msg.format("Chinese", 3, addr_chi))
            
            df = pd.DataFrame()
        else:
            geo_dict = {}
            
            geo_dict.update({
                "address_chi": addr_chi,
                "address_eng": addr_eng,
            })
            
            geo_dict.update({
                "region": result["eng"].get("Region", None),
                "district": result["eng"].get("EngDistrict", {}) \
                    .get("DcDistrict", None),
            })
            
            geo_dict.update({
                "estate_chi": result["chi"].get("ChiEstate", {}) \
                    .get("EstateName", None),
                "building_chi": result["chi"].get("BuildingName", None),
                "estate_eng": result["eng"].get("EngEstate", {}) \
                    .get("EstateName", None),
                "building_eng": result["eng"].get("BuildingName", None),
            })
            
            geo_dict.update({
                "latitude": result["geo"].get("Latitude", None),
                "longitude": result["geo"].get("Longitude", None),
            })
            
            df = pd.DataFrame.from_dict(geo_dict, orient="index").T
        
        return df
    
    def _geocode_address_from_tab(self, ctn: str) -> None:
        """
        Parse addresses from a single PDF.
        
        Args:
            ctn: Parquet file name to be processed.
        """
        df_tab = pd.read_parquet(PTH_TAB / f"{ctn}.parquet")
        
        row_lst = [
            [val for val in r if pd.notna(val)]
            for r in df_tab.values.tolist()
        ]
        df_lst = pd.DataFrame(row_lst)
        
        df_addr = df_lst[df_lst[0].str.contains("^\d")][[1]]
        df_addr.columns = ["address"]
        
        dfs = []
        
        for addr in df_addr["address"]:
            geo = self._get_geocode(addr)
            dfs.append(geo)
        
        df = pd.concat(dfs, ignore_index=True) \
            .assign(source=ctn)
        df.to_parquet(PTH_GEO / f"{ctn}.parquet")
    
    def geocode_address(self) -> None:
        """
        Parse addresses from outstanding PDFs.
        """
        for idx, pdf in enumerate(self.outstanding_pdfs):
            if idx % 50 == 0:
                cnt = len(self.outstanding_pdfs) - idx
                self.logger.info(f"Pending {cnt} PDFs to be geocoded.")
            
            self._geocode_address_from_tab(pdf)


if __name__ == "__main__":
    Geocoder().geocode_address()
