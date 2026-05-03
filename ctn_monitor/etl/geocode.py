import logging
import re

import pandas as pd

from .address_lookup import Address
from .path_setup import get_path
from .utils import is_nonempty_file, write_parquet_atomic

logger = logging.getLogger(__name__)


_RE_CHI_SPAN = re.compile(r"[\u4e00-\u9fff](?:.*[\u4e00-\u9fff])?")


def _split_address(place: str) -> tuple[str, str]:
    addr = place.replace("_x000D_", " ")
    m = _RE_CHI_SPAN.search(addr)

    if m:
        addr_chi = m.group().strip()
        addr_eng = addr[m.end():].strip()
    else:
        addr_chi = ""
        addr_eng = addr.strip()

    return addr_chi, addr_eng


def _get_geocode(addr: str) -> dict | None:
    addr_chi, addr_eng = _split_address(addr)

    candidates = []
    if addr_chi and addr_eng:
        candidates.append(f"{addr_chi}, {addr_eng}")
    if addr_eng:
        candidates.append(addr_eng)
    if addr_chi:
        candidates.append(addr_chi)

    result = None
    for i, query in enumerate(candidates):
        result = Address(query).ParseAddress()
        if result:
            break
        logger.warning("Geocode lookup failed (tier %d) for: %s", i + 1, query)

    if not result:
        return None

    chi, eng, geo = result["chi"], result["eng"], result["geo"]
    return {
        "address_chi": addr_chi,
        "address_eng": addr_eng,
        "region": eng.get("Region"),
        "district": eng.get("EngDistrict", {}).get("DcDistrict"),
        "estate_chi": chi.get("ChiEstate", {}).get("EstateName"),
        "building_chi": chi.get("BuildingName"),
        "estate_eng": eng.get("EngEstate", {}).get("EstateName"),
        "building_eng": eng.get("BuildingName"),
        "latitude": geo.get("Latitude"),
        "longitude": geo.get("Longitude"),
    }


def geocode_tab_address(ctn_parquet: str) -> None:
    """
    Geocodes addresses from a CTN table parquet and saves the results.

    Args:
        ctn_parquet: parquet file name to be processed.
    """
    pth_geo = get_path("geo") / ctn_parquet

    if is_nonempty_file(pth_geo):
        logger.info(
            "Geocoded address file already exists; skipping: %s",
            pth_geo,
        )
        return

    df_tab = pd.read_parquet(get_path("tab") / ctn_parquet)

    row_lst = [
        [val for val in r if pd.notna(val)]
        for r in df_tab.values.tolist()
    ]
    df_addr = pd.DataFrame(row_lst)

    addresses = df_addr.loc[df_addr[0].str.contains(r"^\d", na=False), 1]

    records = [
        r for addr in addresses
        if (r := _get_geocode(addr)) is not None
    ]

    df = pd.DataFrame(records).assign(source=ctn_parquet)
    write_parquet_atomic(df, pth_geo)
