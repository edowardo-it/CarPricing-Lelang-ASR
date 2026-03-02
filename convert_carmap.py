import pandas as pd
from pathlib import Path

# ==============================
# CONFIGURATION
# ==============================

INPUT_FILE = "Final_OTR_Lelang.xlsx"   # ganti jika perlu
OUTPUT_FILE = "CarMap.csv"

# Mapping nama kolom Excel -> format final
COLUMN_MAPPING = {
    "Merk": "Merk",
    "Model": "ModelName",
    "Tipe": "Tipe",
    "Price": "saleprice",
    "Tahun": "Tahun",
    "Wilayah": "Wilayah",
    "kilometer": "kilometer2"
}

# ==============================
# PIPELINE
# ==============================

def load_excel(filepath: str) -> pd.DataFrame:
    """Load Excel file"""
    return pd.read_excel(filepath)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename & select required columns"""

    # Rename sesuai mapping
    df = df.rename(columns=COLUMN_MAPPING)

    # Pastikan hanya kolom yang diperlukan
    df = df[list(COLUMN_MAPPING.values())]

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean whitespace & data types"""

    # Trim string columns
    for col in ["Merk", "ModelName", "Tipe", "Wilayah", "Tahun", "kilometer2"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Ensure price numeric
    df["saleprice"] = pd.to_numeric(df["saleprice"], errors="coerce")

    # Drop row jika price kosong
    df = df.dropna(subset=["saleprice"])

    return df


def export_to_csv(df: pd.DataFrame, output_path: str):
    """Export to CSV tanpa index"""
    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8"
    )


def main():
    print("Loading Excel...")
    df = load_excel(INPUT_FILE)

    print("Normalizing columns...")
    df = normalize_columns(df)

    print("Cleaning data...")
    df = clean_data(df)

    print("Exporting to CSV...")
    export_to_csv(df, OUTPUT_FILE)

    print(f"Done. File saved as {OUTPUT_FILE}")


if __name__ == "__main__":
    main()