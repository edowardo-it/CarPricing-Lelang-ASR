import streamlit as st
import pandas as pd

st.set_page_config(page_title="Harga Lelang Kendaraan", layout="wide")

# Per kendaraan (1 baris unik per kombinasi ini)
GROUP_COLS = ["Tipe", "Tahun", "Wilayah", "kilometer2"]

# ==============================
# HELPERS
# ==============================
def format_rupiah_ringkas(x) -> str:
    """
    198000000 -> 198jt
    1250000000 -> 1.25M
    950000 -> 950rb
    """
    if pd.isna(x):
        return "-"
    try:
        x = float(x)
    except Exception:
        return "-"

    sign = "-" if x < 0 else ""
    x = abs(x)

    if x >= 1_000_000_000:
        v = x / 1_000_000_000
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return f"{sign}{s}M"
    if x >= 1_000_000:
        v = x / 1_000_000
        s = f"{v:.0f}" if v.is_integer() else f"{v:.2f}".rstrip("0").rstrip(".")
        return f"{sign}{s}jt"
    if x >= 1_000:
        v = x / 1_000
        s = f"{v:.0f}" if v.is_integer() else f"{v:.2f}".rstrip("0").rstrip(".")
        return f"{sign}{s}rb"
    return f"{sign}{int(x)}"


# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    required_base = set(GROUP_COLS + ["min_price", "avg_price", "max_price"])
    missing = [c for c in required_base if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak ditemukan di CSV: {missing}")

    # Numeric prices
    for c in ["min_price", "avg_price", "max_price"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Count (opsional)
    if "count" in df.columns:
        df["count"] = pd.to_numeric(df["count"], errors="coerce").astype("Int64")

    # Tahun numeric
    df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce").astype("Int64")

    # Trim string
    for c in ["Merk", "ModelName", "Tipe", "Wilayah", "kilometer2"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    # Drop rows invalid
    drop_cols = ["min_price", "avg_price", "max_price", "Tahun"]
    if "count" in df.columns:
        drop_cols.append("count")
    df = df.dropna(subset=drop_cols)

    return df


df = load_data("CarMap.csv")

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filter")

merk_list = sorted(df["Merk"].dropna().unique().tolist())
selected_merk = st.sidebar.selectbox("Merk", options=merk_list)
df1 = df[df["Merk"] == selected_merk]

model_list = sorted(df1["ModelName"].dropna().unique().tolist())
selected_model = st.sidebar.selectbox("ModelName", options=model_list)
df2 = df1[df1["ModelName"] == selected_model]

tipe_list = sorted(df2["Tipe"].dropna().unique().tolist())
selected_tipe = st.sidebar.multiselect(
    "Tipe",
    options=tipe_list,
    default=tipe_list[:1] if tipe_list else []
)
df3 = df2[df2["Tipe"].isin(selected_tipe)] if selected_tipe else df2

tahun_list = sorted(df3["Tahun"].dropna().astype(int).unique().tolist())
selected_tahun = st.sidebar.selectbox("Tahun", options=["ALL"] + tahun_list)
df4 = df3 if selected_tahun == "ALL" else df3[df3["Tahun"] == int(selected_tahun)]

wilayah_list = sorted(df4["Wilayah"].dropna().unique().tolist())
selected_wilayah = st.sidebar.selectbox("Wilayah", options=["ALL"] + wilayah_list)
df5 = df4 if selected_wilayah == "ALL" else df4[df4["Wilayah"] == selected_wilayah]

km_list = sorted(df5["kilometer2"].dropna().unique().tolist())
selected_km = st.sidebar.selectbox("Kilometer", options=["ALL"] + km_list)
df_filtered = df5 if selected_km == "ALL" else df5[df5["kilometer2"] == selected_km]

# ==============================
# DEDUPE + COUNT
# ==============================
if "count" in df_filtered.columns:
    df_grouped = (
        df_filtered
        .groupby(GROUP_COLS, dropna=False, as_index=False)
        .agg(
            Min=("min_price", "min"),
            Avg=("avg_price", "mean"),
            Max=("max_price", "max"),
            TotalUnitTerjual=("count", "sum"),
        )
    )
else:
    df_grouped = (
        df_filtered
        .groupby(GROUP_COLS, dropna=False, as_index=False)
        .agg(
            Min=("min_price", "min"),
            Avg=("avg_price", "mean"),
            Max=("max_price", "max"),
            TotalUnitTerjual=("avg_price", "size"),
        )
    )

# NOTE: Biarkan numeric tetap numeric untuk perhitungan/sorting,
# tapi buat kolom display ringkas untuk ditampilkan.
df_grouped["Min_fmt"] = df_grouped["Min"].apply(format_rupiah_ringkas)
df_grouped["Avg_fmt"] = df_grouped["Avg"].apply(format_rupiah_ringkas)
df_grouped["Max_fmt"] = df_grouped["Max"].apply(format_rupiah_ringkas)

# ==============================
# MAIN VIEW
# ==============================
st.title("Harga Lelang Kendaraan")
st.markdown(f"**Merk = {selected_merk}**")
st.markdown(f"**Model = {selected_model}**")

# Siapkan tabel display: tampilkan yang ringkas, tapi tetap bisa simpan numeric kalau mau
df_show = df_grouped.rename(columns={"kilometer2": "Kilometer"})

# Kolom yang ditampilkan (ringkas)
df_show = df_show[["Tipe", "Tahun", "Wilayah", "Kilometer", "Min_fmt", "Avg_fmt", "Max_fmt", "TotalUnitTerjual"]]
df_show = df_show.rename(columns={"Min_fmt": "Min", "Avg_fmt": "Avg", "Max_fmt": "Max"})

df_show = df_show.sort_values(["Tipe", "Tahun", "Wilayah", "Kilometer"], ascending=True)

st.dataframe(df_show.reset_index(drop=True), use_container_width=True)
