import os
import re
import shutil
import tabula
import pandas as pd
from datetime import datetime
from collections import defaultdict

from utils import Address


class Modeller:
    def __init__(self) -> None:
        self.create_done_folder()
        self.update_unprocessed_cache()
        self.get_subdistricts()
        
        self.df_ctn = pd.DataFrame()
        self.df_geo = pd.DataFrame()
        
        return None
    
    def create_done_folder(self) -> None:
        # make directory for the first execution
        if not os.path.exists("data/done"):
            os.makedirs("data/done")
        
        return None
    
    def update_unprocessed_cache(self) -> None:
        # get files which have not yet processed
        self.files = os.listdir("data/cache")
        self.files.remove(".DS_Store") \
            if ".DS_Store" in self.files else None
        
        return None
    
    def get_subdistricts(self) -> None:
        # get sub-districts for validating address
        self.subdistricts = pd.read_excel("data/areas_and_districts.xlsx")
        self.subdistricts = self.subdistricts["subdistricts"] \
            .str.replace(r"\s", "", regex=True) \
            .str.upper() \
            .unique()
        
        return None
    
    def extract_tables_from_ctn(self, file_name) -> pd.DataFrame:
        # load tables from PDF
        pages = tabula.read_pdf_with_template(
            f"data/cache/{file_name}",
            template_path="config/ctn_template.json",
            lattice=True,
            pandas_options={"header": None}
        )
        
        # append page table
        ctn = pd.DataFrame()
        for page in pages:
            page = page.astype(str)
            # keep only column valued with `Specified place`
            dc = [page[col].str.contains("Specified place").any() \
                for col in page.columns]
            ctn = pd.concat(
                [ctn, page.loc[:, dc]],
                ignore_index=True
            ).astype(str)
        
        return ctn

    def wrangle_raw_ctn(self, df) -> pd.DataFrame:
        ctn = df.copy()
        
        # remove rows without non-ASCII characters
        df_filter = pd.DataFrame()
        for col in ctn.columns:
            df_merge = ctn.fillna("na")[col] \
                .str.contains(r"[^\x00-\x7F]", regex=True)
            df_filter = pd.concat(
                [df_filter, df_merge]
                , axis=1
            )
        ctn = ctn[df_filter.any(axis=1)]
        
        # remove cells without sub-districts
        match = re.compile(r"\r|\s")
        df_filter = pd.DataFrame()
        for col in ctn.columns:
            df_merge = ctn[col].apply(
                lambda y: any(
                    subdistrict in match.sub("", y.upper()) \
                    for subdistrict in self.subdistricts
                )
            )
            df_filter = pd.concat(
                [df_filter, df_merge],
                axis=1
            )
        ctn = ctn[df_filter]
        
        # concatenate row values while removing unnecessary values
        pattern = r"\r|\s|nan|Specified place"
        ctn = ctn.apply(lambda y: "".join(y.dropna()), axis=1) \
            .str.replace(pattern, "", regex=True)
        
        # remove rows without English characters
        df_filter = ctn.str.contains(r"[A-Za-z]", regex=True)
        ctn = ctn[df_filter].reset_index(drop=True)
        
        # remove address written in English
        ctn = ctn.str.replace(r"é|â|’||–", "", regex=True) \
            .str.extract(r"(.*[^\x00-\x7F]\)?)")
        ctn.columns = ["specified_place"]
        
        return ctn
    
    def extract_geo_info(self, address) -> pd.DataFrame:
        # query geographic information
        ad = Address(address)
        try:
            result = ad.ParseAddress()
        except:
            result = defaultdict(lambda: {})
        
        # get geographic information
        geo_info_dict = {
            "region": result["eng"].get("Region", None),
            "district": result["eng"].get("EngDistrict", {}) \
                .get("DcDistrict", None),
        }
        
        # get geocode
        geocode_dict = {
            "latitude": result["geo"].get("Latitude", None),
            "longitude": result["geo"].get("Longitude", None),
        }
        
        # convert geographic information to data frame
        geo_dict = {}
        geo_dict.update(geo_info_dict)
        geo_dict.update(geocode_dict)
        geo = pd.DataFrame.from_dict(geo_dict, orient='index').T
        geo["specified_place"] = address
        
        return geo
    
    def wrangle_raw_geo(self, df) -> pd.DataFrame:
        geo = df.copy()
        
        # address to be removed if no geographic information available
        if geo["region"].values[0] is None:
            geo = pd.DataFrame()
        # cleanse geographic information
        else:
            geo["district"] = geo["district"].str.replace(" DISTRICT", "") \
                .str.replace("&amp;", "AND")
            dc = ["latitude", "longitude"]
            geo[dc] = geo[dc].astype(float)
        
        return geo
    
    def process_ctn(self) -> None:
        for file in sorted(self.files):
            # get and wrangle CTN
            df_merge = self.extract_tables_from_ctn(file)
            df_merge = self.wrangle_raw_ctn(df_merge)
            date = datetime.strptime(re.findall(r"(\d+)", file)[0], "%Y%m%d")
            df_merge = df_merge.assign(ingestion_file=file, date=date)
            
            self.df_ctn = pd.concat(
                [self.df_ctn, df_merge],
                ignore_index=True
            )
            
            # move CTN to done to indicate processed CTN
            shutil.move(f"data/cache/{file}", f"data/done/{file}")
            
            print(f"- CTN '{file}' has been cleansed.")
        
        return None
    
    def process_geo_info(self) -> None:
        for address in self.df_ctn["specified_place"].unique():
            # get and wrangle geographic information
            df_merge = self.extract_geo_info(address)
            df_merge = self.wrangle_raw_geo(df_merge)
            
            self.df_geo = pd.concat(
                [self.df_geo, df_merge],
                ignore_index=True
            )
            
            print(f"- Geographic information cached for '{address}'.")
        
        return None
    
    def build_data_model(self) -> None:
        if len(self.files):
            # get CTN and geographic information
            self.process_ctn()
            self.process_geo_info()
            
            # join CTN with geographic information
            df_new = self.df_ctn.merge(
                self.df_geo,
                on="specified_place", how="inner"
            )
            
            # append records with pervious data model
            if os.path.exists("data/ctn_data.xlsx"):
                df_old = pd.read_excel("data/ctn_data.xlsx")
                df_new = pd.concat(
                    [df_new, df_old],
                    ignore_index=True
                )
            
            # output data model
            df_new.to_excel("data/ctn_data.xlsx", index=False)
        
        return None


if __name__ == "__main__":
    Modeller().build_data_model()
