import streamlit as st
import pandas as pd
from supabase_utils import supabase_select

st.title("💰 Movimenti di cassa")

mov = pd.DataFrame(supabase_select("movimenti_cassa"))

if mov.empty:
    st.info("Nessun movimento registrato.")
    st.stop()

# Pulizia dati
mov["data"] = mov["data"].replace("", None)

# Applico il segno corretto ai movimenti
mov["importo_signed"] = mov.apply(
    lambda row: -row["importo"] if row["tipo"] == "uscita" else row["importo"],
    axis=1
)

st.subheader("📋 Lista movimenti")

# Filtri
col1, col2, col3 = st.columns(3)

tipo_filtro = col1.selectbox("Filtra per tipo", ["Tutti", "entrata", "uscita"])
soggetto_filtro = col2.text_input("Filtra per soggetto")
mese_filtro = col3.text_input("Filtra per mese (es: 2025-02)")

df = mov.copy()

if tipo_filtro != "Tutti":
    df = df[df["tipo"] == tipo_filtro]

if soggetto_filtro:
    df = df[df["soggetto"].str.contains(soggetto_filtro, case=False, na=False)]

if mese_filtro:
    df = df[df["data"].str.startswith(mese_filtro, na=False)]

df = df.sort_values("data", ascending=False)

st.dataframe(df)

st.subheader("📊 Totali")

tot_entrate = df[df["tipo"] == "entrata"]["importo"].sum()
tot_uscite = df[df["tipo"] == "uscita"]["importo"].sum()

# Saldo corretto usando importo_signed
saldo = df["importo_signed"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Entrate", f"€ {tot_entrate:,.2f}")
col2.metric("Uscite", f"€ {abs(tot_uscite):,.2f}")
col3.metric("Saldo", f"€ {saldo:,.2f}")
