import streamlit as st
import pandas as pd

st.set_page_config(page_title="Harga Lelang Kendaraan", layout="wide")

#GROUP_COLS = ["Merk", "ModelName", "Tipe", "Tahun", "Wilayah", "kilometer2"]
GROUP_COLS = ["Tipe", "Tahun", "Wilayah", "kilometer2"]

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Ensure saleprice numeric
    df["saleprice"] = pd.to_numeric(df["saleprice"], errors="coerce")

    # Tahun numeric (biar sorting rapi)
    df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce").astype("Int64")

    # Trim object cols (aman utk filtering/grouping)
    for c in ["Tipe", "Wilayah", "kilometer2"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    # Drop rows tanpa group cols / saleprice
    df = df.dropna(subset=["saleprice", "Tipe", "Tahun", "Wilayah", "kilometer2"])

    return df

df = load_data("CarMap.csv")

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filter")

# Merk
merk_list = sorted(df["Merk"].unique().tolist())
selected_merk = st.sidebar.selectbox("Merk", options=merk_list)
df1 = df[df["Merk"] == selected_merk]

# ModelName
model_list = sorted(df1["ModelName"].unique().tolist())
selected_model = st.sidebar.selectbox("ModelName", options=model_list)
df2 = df1[df1["ModelName"] == selected_model]

# Tipe (multi)
tipe_list = sorted(df2["Tipe"].unique().tolist())
selected_tipe = st.sidebar.multiselect(
    "Tipe",
    options=tipe_list,
    default=tipe_list[:1] if tipe_list else []
)
df3 = df2[df2["Tipe"].isin(selected_tipe)] if selected_tipe else df2

# Tahun
tahun_list = sorted(df3["Tahun"].dropna().astype(int).unique().tolist())
selected_tahun = st.sidebar.selectbox("Tahun", options=["ALL"] + tahun_list)
df4 = df3 if selected_tahun == "ALL" else df3[df3["Tahun"] == int(selected_tahun)]

# Wilayah
wilayah_list = sorted(df4["Wilayah"].unique().tolist())
selected_wilayah = st.sidebar.selectbox("Wilayah", options=["ALL"] + wilayah_list)
df5 = df4 if selected_wilayah == "ALL" else df4[df4["Wilayah"] == selected_wilayah]

# Kilometer2
km_list = sorted(df5["kilometer2"].unique().tolist())
selected_km = st.sidebar.selectbox("Kilometer", options=["ALL"] + km_list)
df_filtered = df5 if selected_km == "ALL" else df5[df5["kilometer2"] == selected_km]

# ==============================
# GROUPING / DISTINCT + AVG SALEPRICE
# ==============================
df_grouped = (
    df_filtered
    .groupby(GROUP_COLS, dropna=False, as_index=False)
    .agg(
        saleprice=("saleprice", "mean"),
        TotalUnitTerjual=("saleprice", "size")  # opsional: biar tahu jumlah data per group
    )
)

# Biar rapi tampilannya (average dibulatkan)
df_grouped["saleprice"] = df_grouped["saleprice"].round(0).astype("Int64")


# ==============================
# MAIN VIEW
# ==============================
st.title("Harga Lelang Kendaraan")


st.markdown(
    f"**Merk = {selected_merk}**  "
)

st.markdown(
    f"**Model = {selected_model}**  "
)

# Rename colsname
RENAME_COLS = {
    "Merk": "Merk",
    "ModelName": "Model",
    "Tipe": "Tipe",
    "Tahun": "Tahun",
    "Wilayah": "Wilayah",
    "kilometer2": "Kilometer",
    "saleprice": "HargaLelangRata-rata",
    "sample_count": "TotalUnitTerjual",   # kalau kamu pakai sample_count
}

df_show = df_grouped.rename(columns=RENAME_COLS)

st.dataframe(df_show.reset_index(drop=True), use_container_width=True)

#st.markdown(
#    f"**Brand = {selected_merk}**  "
#    f"**ModelName = {selected_model}**  "
#    f"**Tipe = {selected_tipe if selected_tipe else 'ALL'}**  "
#    f"**Tahun = {selected_tahun}**  "
#    f"**Wilayah = {selected_wilayah}**  "
#    f"**Kilometer = {selected_km}**"
#)
