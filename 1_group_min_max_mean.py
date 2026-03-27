import pandas as pd

INPUT_FILE = "Final_OTR_Lelang.xlsx"
OUTPUT_FILE = "Final_OTR_Lelang_grouped.xlsx"

GROUP_COLS = ["Merk", "ModelName", "Tipe", "Tahun", "KodeDaerah",
            "lokasi", "Transmisi", "kilometer2"]
PRICE_COL = "saleprice"

def main():
    # 1) Read excel
    df = pd.read_excel(INPUT_FILE)

    # 2) Validasi kolom wajib
    missing = [c for c in GROUP_COLS + [PRICE_COL] if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak ditemukan: {missing}")

    # 3) Trim kolom grouping (hindari mismatch karena spasi)
    for c in GROUP_COLS:
        # Tahun biasanya numeric, tapi aman kita strip jika ternyata string
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)

    # 4) Pastikan saleprice numeric (bersihkan ribuan)
    df[PRICE_COL] = (
        df[PRICE_COL]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(".", "", regex=False)  # jika format ribuan pakai titik
        .str.strip()
    )
    df[PRICE_COL] = pd.to_numeric(df[PRICE_COL], errors="coerce")

    # 5) Buang baris tanpa harga
    df = df.dropna(subset=[PRICE_COL])

    # 6) Grouping + aggregation + COUNT (jumlah unit/record per grup)
    grouped = (
        df.groupby(GROUP_COLS, dropna=False, as_index=False)
          .agg(
              Min=(PRICE_COL, "min"),
              Avg=(PRICE_COL, "mean"),
              Max=(PRICE_COL, "max"),
              Count=(PRICE_COL, "size"),   # <-- ini nilai count yang kamu butuhkan
          )
    )

    # 7) Rapikan avg (opsional)
    grouped["Avg"] = grouped["Avg"].round(2)

    # 8) Save hasil ke excel
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        grouped.to_excel(writer, index=False, sheet_name="grouped_stats")

    print(f"OK. Output tersimpan ke: {OUTPUT_FILE}")
    print(grouped.head(10))


if __name__ == "__main__":
    main()