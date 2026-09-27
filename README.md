# SWYNEX Data Cleaning & Preparation

This project cleans an e-commerce transaction dataset with Python and Pandas for completed-sales analysis. The original CSV is kept as a read-only input and the cleaned result is written separately.

## Dataset and source

The dataset is the [Online Retail dataset from the UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail). It contains transactions for a UK-based online retailer between 1 December 2010 and 9 December 2011. UCI provides the source data as an Excel workbook; `data/raw_dataset.csv` is a value-preserving CSV export of that workbook with the same 541,909 rows and eight columns.

Columns: `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, and `Country`.

## Actual problems found

All counts below were produced by `cleaning.py` on `data/raw_dataset.csv`.

| Finding | Count | Treatment |
| --- | ---: | --- |
| Missing `CustomerID` values | 135,080 | Rows with any required missing value were removed because a customer and product description cannot be inferred reliably. |
| Missing `Description` values | 1,454 | Included in the same required-value rule. |
| Exact duplicate rows | 5,268 | Removed with `drop_duplicates()`. |
| Text cells with leading or trailing whitespace | 112,371 | Normalized with `str.strip()`; these occur in `Description`. |
| Cancellation invoice rows after deduplication and missing-value removal | 8,872 | Excluded from the completed-sales dataset. |
| Remaining rows with non-positive quantity or unit price | 40 | Excluded from the completed-sales dataset. |

The raw CSV reads `InvoiceDate` as text and `CustomerID` as a floating-point value because the latter contains missing values. The script parses `InvoiceDate` as a date-time value, validates customer IDs as whole numbers, stores identifiers as strings in the cleaned DataFrame, keeps `Quantity` as an integer, and keeps `UnitPrice` numeric. CSV files do not store type metadata, so the script performs these conversions each time it runs.

Cancellation and non-positive rows are not described as errors in the source data. They are transaction types that do not belong in a dataset limited to completed sales, which is the defined scope of `cleaned_dataset.csv`.

## Cleaning steps performed

1. Load `data/raw_dataset.csv` without writing to it.
2. Confirm the expected eight columns are present and calculate a SHA-256 checksum before cleaning.
3. Find and remove exact duplicate rows.
4. Strip leading and trailing whitespace from text fields, converting blank text to missing values.
5. Convert dates, quantities, prices, and customer IDs to appropriate analysis types.
6. Remove rows missing any required transaction field. No missing values are imputed.
7. Remove cancelled invoices and rows with a quantity or unit price less than or equal to zero for the completed-sales scope.
8. Save the result to `data/cleaned_dataset.csv` and confirm the raw file checksum did not change.

## Before and after size

| Stage | Rows | Columns |
| --- | ---: | ---: |
| Raw dataset | 541,909 | 8 |
| After exact duplicate removal | 536,641 | 8 |
| After required missing-value removal | 401,604 | 8 |
| After cancellation removal | 392,732 | 8 |
| Cleaned completed-sales dataset | 392,692 | 8 |

The final verification found zero missing values, zero exact duplicate rows, zero cancelled invoices, and zero non-positive quantity/price rows in the cleaned dataset.

## Tools used

- Python 3
- Pandas

## How to run

From this project folder, install Pandas if it is not already available:

```powershell
python -m pip install pandas
```

Then run:

```powershell
python cleaning.py
```

The script prints a data-cleaning summary and creates or replaces only `data/cleaned_dataset.csv`. It never writes to `data/raw_dataset.csv`.

## Project structure

```text
SWYNEX-Data-Cleaning-Preparation/
├── data/
│   ├── raw_dataset.csv
│   └── cleaned_dataset.csv
├── cleaning.py
└── README.md
```

No GitHub repository has been created or pushed for this project.
