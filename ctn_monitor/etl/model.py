import logging

import pandas as pd

from .path_setup import get_path
from .utils import write_excel_atomic

logger = logging.getLogger(__name__)


REGION_CHI = {"HK": "香港", "KLN": "九龍", "NT": "新界"}
DISTRICT_CHI = {
    "CENTRAL & WESTERN DISTRICT": "中西區",
    "EASTERN DISTRICT": "東區",
    "ISLANDS DISTRICT": "離島區",
    "KOWLOON CITY DISTRICT": "九龍城區",
    "KWAI TSING DISTRICT": "葵青區",
    "KWUN TONG DISTRICT": "觀塘區",
    "NORTH DISTRICT": "北區",
    "SAI KUNG DISTRICT": "西貢區",
    "SHA TIN DISTRICT": "沙田區",
    "SHAM SHUI PO DISTRICT": "深水埗區",
    "SOUTHERN DISTRICT": "南區",
    "TAI PO DISTRICT": "大埔區",
    "TSUEN WAN DISTRICT": "荃灣區",
    "TUEN MUN DISTRICT": "屯門區",
    "WAN CHAI DISTRICT": "灣仔區",
    "WONG TAI SIN DISTRICT": "黃大仙區",
    "YAU TSIM MONG DISTRICT": "油尖旺區",
    "YUEN LONG DISTRICT": "元朗區",
}
OUT_COLUMNS = [
    "date",
    "region_eng",
    "district_eng",
    "estate_eng",
    "building_eng",
    "address_eng",
    "region_chi",
    "district_chi",
    "estate_chi",
    "building_chi",
    "address_chi",
    "latitude",
    "longitude",
    "source",
]


def _fill_addr_pair(df: pd.DataFrame, tgt: str, src: str) -> pd.DataFrame:
    df[tgt] = df[tgt].replace("", None)
    df = df.sort_values(by=[src, tgt])
    df[tgt] = df.groupby(src, dropna=False)[tgt].ffill()
    return df


def fill_missing_addr(df: pd.DataFrame) -> pd.DataFrame:
    df = _fill_addr_pair(df, "address_eng", "address_chi")
    return _fill_addr_pair(df, "address_chi", "address_eng")


def enrich_columns(df: pd.DataFrame) -> pd.DataFrame:
    district = df["district"].str.replace("&amp;", "&", regex=False)
    df = df.assign(
        region_chi=df["region"].map(REGION_CHI),
        district_chi=district.map(DISTRICT_CHI),
        region_eng=df["region"],
        district_eng=district.str.title(),
        date=pd.to_datetime(
            df["source"].str.removesuffix(".parquet").str[-8:],
            format="%Y%m%d",
        ),
    )
    return df.sort_values(by="date", ignore_index=True)[OUT_COLUMNS]


def build_model() -> None:
    """Consolidates geocoded parquet files into a cleansed Excel dataset."""
    processed_pdfs = sorted(get_path("geo").glob("*.parquet"))
    logger.info("Loading %d geocoded parquet files", len(processed_pdfs))

    data = pd.concat(
        (pd.read_parquet(pdf) for pdf in processed_pdfs),
        ignore_index=True,
    )
    logger.info("Concatenated %d rows from source files", len(data))

    df = data.pipe(fill_missing_addr).pipe(enrich_columns)

    out_path = get_path("out") / "data.xlsx"
    write_excel_atomic(df, out_path)
    logger.info("Data model built: %d rows written to %s", len(df), out_path)
