"""Clean the UCI Online Retail dataset for completed-sales analysis.

The raw CSV is read only. This script creates data/cleaned_dataset.csv and
prints a reproducible summary of the checks and removals it performs.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
RAW_DATA_PATH = PROJECT_DIR / "data" / "raw_dataset.csv"
CLEANED_DATA_PATH = PROJECT_DIR / "data" / "cleaned_dataset.csv"

EXPECTED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]
REQUIRED_COLUMNS = EXPECTED_COLUMNS.copy()


def file_checksum(file_path: Path) -> str:
    """Return a SHA-256 checksum without loading the full file into memory."""
    digest = sha256()
    with file_path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_missing_values(dataframe: pd.DataFrame) -> str:
    """Format only columns that actually contain missing values."""
    missing_counts = dataframe.isna().sum()
    present_counts = missing_counts[missing_counts.gt(0)]
    if present_counts.empty:
        return "none"
    return ", ".join(f"{column}={count}" for column, count in present_counts.items())


def ensure_expected_columns(dataframe: pd.DataFrame) -> None:
    missing_columns = sorted(set(EXPECTED_COLUMNS).difference(dataframe.columns))
    if missing_columns:
        raise ValueError(
            "The raw dataset is missing expected column(s): "
            + ", ".join(missing_columns)
        )


def clean_dataset(raw_dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Return cleaned completed-sales rows and measured cleaning statistics."""
    dataframe = raw_dataframe.drop_duplicates().copy()
    statistics = {
        "duplicate_rows_removed": len(raw_dataframe) - len(dataframe),
        "text_cells_with_whitespace_normalized": 0,
    }

    # IDs and labels are text fields. Strip surrounding whitespace and preserve blanks as missing.
    for column in ["InvoiceNo", "StockCode", "Description", "Country"]:
        text_values = dataframe[column].astype("string")
        trimmed_values = text_values.str.strip()
        statistics["text_cells_with_whitespace_normalized"] += int(
            (text_values.notna() & text_values.ne(trimmed_values)).sum()
        )
        dataframe[column] = trimmed_values.replace("", pd.NA)

    dataframe["InvoiceDate"] = pd.to_datetime(dataframe["InvoiceDate"], errors="coerce")
    dataframe["Quantity"] = pd.to_numeric(dataframe["Quantity"], errors="coerce")
    dataframe["UnitPrice"] = pd.to_numeric(dataframe["UnitPrice"], errors="coerce")

    customer_numbers = pd.to_numeric(dataframe["CustomerID"], errors="coerce")
    valid_customer_ids = customer_numbers.notna() & customer_numbers.mod(1).eq(0)
    dataframe["CustomerID"] = customer_numbers.where(valid_customer_ids).astype("Int64").astype("string")

    statistics["rows_with_missing_required_values"] = int(
        dataframe[REQUIRED_COLUMNS].isna().any(axis=1).sum()
    )
    dataframe = dataframe.dropna(subset=REQUIRED_COLUMNS).copy()

    cancelled_invoices = dataframe["InvoiceNo"].str.upper().str.startswith("C", na=False)
    statistics["cancelled_invoice_rows_removed"] = int(cancelled_invoices.sum())
    dataframe = dataframe.loc[~cancelled_invoices].copy()

    nonpositive_sales_values = (dataframe["Quantity"] <= 0) | (dataframe["UnitPrice"] <= 0)
    statistics["nonpositive_quantity_or_price_rows_removed"] = int(
        nonpositive_sales_values.sum()
    )
    dataframe = dataframe.loc[~nonpositive_sales_values].copy()

    dataframe["Quantity"] = dataframe["Quantity"].astype("Int64")
    dataframe["UnitPrice"] = dataframe["UnitPrice"].astype(float)

    return dataframe, statistics


def main() -> None:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_DATA_PATH}")

    raw_checksum_before = file_checksum(RAW_DATA_PATH)
    raw_dataframe = pd.read_csv(RAW_DATA_PATH)
    ensure_expected_columns(raw_dataframe)

    cleaned_dataframe, statistics = clean_dataset(raw_dataframe)
    cleaned_dataframe.to_csv(
        CLEANED_DATA_PATH,
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )

    raw_checksum_after = file_checksum(RAW_DATA_PATH)
    if raw_checksum_before != raw_checksum_after:
        raise RuntimeError("The raw dataset changed while the script was running.")

    print("Data-cleaning summary")
    print(f"Raw dataset size: {raw_dataframe.shape[0]} rows x {raw_dataframe.shape[1]} columns")
    print(f"Raw missing values: {format_missing_values(raw_dataframe)}")
    print(f"Exact duplicate rows removed: {statistics['duplicate_rows_removed']}")
    print(
        "Text cells with leading or trailing whitespace normalized: "
        f"{statistics['text_cells_with_whitespace_normalized']}"
    )
    print(
        "Rows removed for missing required values: "
        f"{statistics['rows_with_missing_required_values']}"
    )
    print(
        "Cancelled invoice rows removed: "
        f"{statistics['cancelled_invoice_rows_removed']}"
    )
    print(
        "Rows removed for non-positive quantity or unit price: "
        f"{statistics['nonpositive_quantity_or_price_rows_removed']}"
    )
    print(
        "Cleaned dataset size: "
        f"{cleaned_dataframe.shape[0]} rows x {cleaned_dataframe.shape[1]} columns"
    )
    print("Raw dataset checksum unchanged: yes")


if __name__ == "__main__":
    main()
