import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv


load_dotenv("config/.env")

PTH_LOG = Path(os.getenv("PTH_LOG", "logs"))
PTH_GEO = Path(os.getenv("PTH_GEO", "data/geocode"))
PTH_OUT = Path(os.getenv("PTH_OUT", "data"))

logging.basicConfig(
    filename=PTH_LOG / "DataModeller.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class DataModeller:
    map_region = {
        "HK": "香港",
        "NT": "新界",
        "KLN": "九龍",
    }
    
    map_district = {
        "EASTERN DISTRICT": "東區",
        "TUEN MUN DISTRICT": "屯門區",
        "KWAI TSING DISTRICT": "葵青區",
        "SHAM SHUI PO DISTRICT": "深水埗區",
        "KOWLOON CITY DISTRICT": "九龍城區",
        "WAN CHAI DISTRICT": "灣仔區",
        "SAI KUNG DISTRICT": "西貢區",
        "WONG TAI SIN DISTRICT": "黃大仙區",
        "NORTH DISTRICT": "北區",
        "YUEN LONG DISTRICT": "元朗區",
        "TSUEN WAN DISTRICT": "荃灣區",
        "SHA TIN DISTRICT": "沙田區",
        "KWUN TONG DISTRICT": "觀塘區",
        "ISLANDS DISTRICT": "離島區",
        "SOUTHERN DISTRICT": "南區",
        "TAI PO DISTRICT": "大埔區",
        "YAU TSIM MONG DISTRICT": "油尖旺區",
        "CENTRAL & WESTERN DISTRICT": "中西區",
    }
    
    def __init__(self) -> None:
        """
        Define a list of Parquets to be modelled; and address mapping tables.
        """
        self.processed_pdfs = {file.stem for file in PTH_GEO.glob("*.parquet")}
        
        logging.info(f"- Total of {len(self.processed_pdfs)} PDFs to be modelled.")
        
    
    def _build_data_model_from_tab(self, data: pd.DataFrame) -> None:
        """
        Build data model from available data.
        
        Args:
            data: dataframe to be modelled.
        """
        def fill_missing_addr(df: pd.DataFrame, lang: str) -> pd.DataFrame:
            src = "chi" if lang == "eng" else "eng"
            addr_tgt, addr_src = f"address_{lang}", f"address_{src}"
            
            df[addr_tgt] = df[addr_tgt].replace("", None)
            df.sort_values(by=[addr_src, addr_tgt], inplace=True)
            df[addr_tgt] = df.groupby(addr_src, dropna=False)[addr_tgt].ffill()
            
            return df
        
        def cleanse_district(df: pd.DataFrame) -> pd.DataFrame:
            df["district"] = df["district"].str.replace("&amp;", "&")
            
            return df
        
        def map_chi_addr(df: pd.DataFrame) -> pd.DataFrame:
            df["region_chi"] = df["region"].map(self.map_region)
            df["district_chi"] = df["district"].map(self.map_district)
            
            return df
        
        def add_eng_suffix(df: pd.DataFrame, cols: list) -> pd.DataFrame:
            col = {col: f"{col}_eng" for col in cols}
            df.rename(columns=col, inplace=True)
            
            return df
        
        def convert_title_case(df: pd.DataFrame, cols: list) -> pd.DataFrame:
            for col in cols:
                df[f"{col}_eng"] = df[f"{col}_eng"].str.title()
            
            return df
        
        def add_dates(df: pd.DataFrame) -> pd.DataFrame:
            df["date"] = pd.to_datetime(df["source"].str[-8:])
            df.sort_values(by="date", ignore_index=True, inplace=True)
            
            return df
        
        def select_column(df: pd.DataFrame) -> pd.DataFrame:
            col = [
                "date", "region_eng", "district_eng",
                "estate_eng", "building_eng", "address_eng",
                "region_chi", "district_chi", "estate_chi",
                "building_chi", "address_chi", "latitude",
                "longitude", "source",
            ]
            
            df = df[col]
            
            return df
        
        df = data.pipe(fill_missing_addr, "eng") \
            .pipe(fill_missing_addr, "chi") \
            .pipe(cleanse_district) \
            .pipe(map_chi_addr) \
            .pipe(add_eng_suffix, ["region", "district"]) \
            .pipe(convert_title_case, ["district", "estate", "building"]) \
            .pipe(add_dates) \
            .pipe(select_column)
        
        df.to_excel(PTH_OUT / f"data.xlsx", index=False)
    
    def build_model(self) -> None:
        """
        Build data model from processed PDFs.
        """
        dfs = []
        
        for pdf in self.processed_pdfs:
            ctn = pd.read_parquet(PTH_GEO / f"{pdf}.parquet")
            dfs.append(ctn)
        
        df = pd.concat(dfs, ignore_index=True)
        self._build_data_model_from_tab(df)


if __name__ == "__main__":
    DataModeller().build_model()
