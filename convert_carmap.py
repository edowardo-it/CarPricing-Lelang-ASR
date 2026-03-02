import pandas as pd

# ==============================
# CONFIGURATION
# ==============================

INPUT_FILE = "Final_OTR_Lelang_grouped.xlsx"   # ganti jika perlu
OUTPUT_FILE = "CarMap.csv"

# Mapping nama kolom Excel -> format final
# Tambahkan "Count" -> "count" (pastikan di Excel memang ada kolom Count)
COLUMN_MAPPING = {
    "Merk": "Merk",
    "ModelName": "ModelName",
    "Tipe": "Tipe",
    "Min": "min_price",
    "Avg": "avg_price",
    "Max": "max_price",
    "Count": "count",          # <-- kolom baru
    "Tahun": "Tahun",
    "Wilayah": "Wilayah",
    "kilometer2": "kilometer2"
}

# ==============================
# PIPELINE
# ==============================

def load_excel(filepath: str) -> pd.DataFrame:
    """Load Excel file"""
    return pd.read_excel(filepath)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename & select required columns"""

    # Validasi kolom yang dibutuhkan ada di file
    required_excel_cols = list(COLUMN_MAPPING.keys())
    missing = [c for c in required_excel_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Kolom berikut tidak ditemukan di Excel: {missing}\n"
            f"Kolom yang tersedia: {df.columns.tolist()}"
        )

    # Rename sesuai mapping
    df = df.rename(columns=COLUMN_MAPPING)

    # Pastikan hanya kolom yang diperlukan
    df = df[list(COLUMN_MAPPING.values())]

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean whitespace & data types"""

    # Trim string columns
    for col in ["Merk", "ModelName", "Tipe", "Wilayah", "kilometer2"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Tahun numeric (lebih aman untuk filtering/sorting)
    df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce").astype("Int64")

    # Ensure price numeric
    for c in ["min_price", "avg_price", "max_price"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Count numeric integer
    df["count"] = pd.to_numeric(df["count"], errors="coerce").astype("Int64")

    # Drop row jika price kosong / Tahun kosong
    df = df.dropna(subset=["min_price", "avg_price", "max_price", "Tahun"])

    # Jika count kosong, isi 1 (opsional; ubah sesuai kebutuhan)
    df["count"] = df["count"].fillna(1).astype("Int64")

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