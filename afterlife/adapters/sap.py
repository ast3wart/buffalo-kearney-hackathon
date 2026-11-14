"""SAP-extract adapter (v3 #15). Owner: 💲 Asher.

Some companies (Ironridge) arrive as raw SAP table extracts with technical field names
and SAP quirks. io.load() calls `to_contract()` on any table whose headers look like SAP,
so nothing downstream ever sees SAP names. No live connector: point us at an extract.

Quirks handled (planted by the generator so the adapter visibly earns its keep):
  - numeric MATNR / LIFNR zero-padded to 18 / 10 chars  -> leading zeros stripped
  - dates as YYYYMMDD (BEDAT)                             -> YYYY-MM-DD
  - PO number EBELN (10) + item EBELP (5, steps of 10)    -> po_line_id "EBELN-EBELP"
  - optional decimal comma in prices ("4,12")             -> 4.12
Field names follow EKKO/EKPO, LFA1, MARA/MAKT/MBEW, EINA. Both technical names and a few
common descriptive labels are accepted on input; the generator writes technical names only.
"""
import pandas as pd

# technical name -> our column, per contract table
MAPS: dict[str, dict[str, str]] = {
    "production_spend": {
        "MATNR": "part_no", "LIFNR": "supplier_id", "NAME1": "supplier_name", "IDNLF": "supplier_pn",
        "TXZ01": "description", "MENGE": "qty", "MEINS": "uom", "NETPR": "unit_price", "PEINH": "price_unit",
        "BEDAT": "po_date", "WERKS": "plant", "LAND1": "country",
    },
    "part_master": {"MATNR": "part_no", "MAKTX": "description", "MATKL": "category", "STPRS": "std_cost"},
    "info_records": {"MATNR": "part_no", "LIFNR": "supplier_id", "IDNLF": "supplier_pn"},
}
MAPS["service_spend"] = MAPS["production_spend"]  # + our own 'channel' column, kept as is

# descriptive labels some extracts use instead of technical names
LABELS = {"Material": "MATNR", "Vendor": "LIFNR", "Supplier": "LIFNR", "Short Text": "TXZ01",
          "Purchasing Document": "EBELN", "Item": "EBELP", "Net Price": "NETPR", "Price Unit": "PEINH",
          "Plant": "WERKS", "Document Date": "BEDAT", "Order Unit": "MEINS", "Quantity": "MENGE",
          "Vendor Material Number": "IDNLF", "Material Description": "MAKTX", "Material Group": "MATKL"}

SAP_MARKERS = {"MATNR", "LIFNR", "EBELN", "Material", "Vendor", "Purchasing Document"}


def looks_like_sap(df: pd.DataFrame) -> bool:
    return bool(SAP_MARKERS & set(df.columns))


def _strip_zeros(s: pd.Series) -> pd.Series:
    s = s.astype("string")
    return s.where(~s.str.fullmatch(r"\d+", na=False), s.str.lstrip("0"))


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype("string").str.replace(",", ".", regex=False), errors="coerce")


def _po_parts(ids: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Split any PO line id ('PO-450001-010', '4500000012-00010') into SAP EBELN (10) + EBELP (5)."""
    parts = ids.astype(str).str.extract(r"(\d+)\D*(\d+)?$")
    return parts[0].str.zfill(10), parts[1].fillna("10").str.zfill(5)


def canonical_po_id(ids: pd.Series) -> pd.Series:
    """The po_line_id a PO line has AFTER an SAP round trip ('PO-450001-010' -> '0000450001-00010').
    For SAP-format companies, every table that references a PO line (build_supply, truth_links,
    truth_spikes) must use this form, or joins break (found by Brandon in the CP1 review).
    Ids with no digits (e.g. '') are returned unchanged rather than becoming NaN.
    NOTE: non-numeric prefixes are dropped, so 'PO-450001-010' and 'TX2-450001-010' collide.
    Generators for SAP companies must mint distinct numeric PO numbers (callers check for collisions)."""
    ebeln, ebelp = _po_parts(ids)
    canon = ebeln + "-" + ebelp
    return canon.where(ebeln.notna(), ids.astype(str))


def to_contract(table: str, df: pd.DataFrame) -> pd.DataFrame:
    """Rename SAP fields to our contract columns and undo SAP formatting quirks."""
    df = df.rename(columns=LABELS)
    out = df.rename(columns=MAPS.get(table, {}))
    if "EBELN" in out.columns and "EBELP" in out.columns:
        # same normalization as canonical_po_id, so an extract that lost its zero padding
        # (e.g. re-saved through Excel: EBELN '450001') still joins
        ebeln = out["EBELN"].astype(str).str.extract(r"(\d+)")[0].str.zfill(10)
        ebelp = out["EBELP"].astype(str).str.extract(r"(\d+)")[0].fillna("10").str.zfill(5)
        out.insert(0, "po_line_id", ebeln + "-" + ebelp)
        out = out.drop(columns=["EBELN", "EBELP"])
    for col in ["part_no", "supplier_id"]:
        if col in out.columns:
            out[col] = _strip_zeros(out[col])
    for col in ["unit_price", "std_cost", "qty", "price_unit"]:
        if col in out.columns:
            out[col] = _num(out[col])
    if "po_date" in out.columns:
        d = out["po_date"].astype("string")
        out["po_date"] = d.where(~d.str.fullmatch(r"\d{8}", na=False), d.str[:4] + "-" + d.str[4:6] + "-" + d.str[6:])
    return out


def from_contract(table: str, df: pd.DataFrame, pad: bool = True) -> pd.DataFrame:
    """Inverse, used by the generator to WRITE a company as a raw SAP extract."""
    inv = {v: k for k, v in MAPS[table].items()}
    out = df.copy()
    if "po_line_id" in out.columns:
        ebeln, ebelp = _po_parts(out["po_line_id"])
        out.insert(0, "EBELN", ebeln)
        out.insert(1, "EBELP", ebelp)
        out = out.drop(columns=["po_line_id"])
    if pad:
        for col, width in [("part_no", 18), ("supplier_id", 10)]:
            if col in out.columns:
                s = out[col].astype("string")
                out[col] = s.where(~s.str.fullmatch(r"\d+", na=False), s.str.zfill(width))
    if "po_date" in out.columns:
        out["po_date"] = out["po_date"].astype(str).str.replace("-", "", regex=False)
    return out.rename(columns=inv)
