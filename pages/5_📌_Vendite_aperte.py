import streamlit as st
import pandas as pd
from supabase_utils import supabase_select

st.title("📌 Vendite aperte")

# Carico vendite e rate
vendite = pd.DataFrame(supabase_select("vendite"))
rate = pd.DataFrame(supabase_select("pagamenti_rate"))

if vendite.empty:
    st.info("Nessuna vendita registrata.")
    st.stop()

# ============================
# NORMALIZZAZIONE TIPI
# ============================
vendite["id"] = pd.to_numeric(vendite["id"], errors="coerce")

if not rate.empty:
    rate["id_vendita"] = pd.to_numeric(rate["id_vendita"], errors="coerce")
else:
    rate = pd.DataFrame(columns=["id_vendita", "importo"])

# ============================
# CALCOLO TOTALE RATE PER VENDITA
# ============================
if not rate.empty:
    rate_group = rate.groupby("id_vendita")["importo"].sum().reset_index()
else:
    rate_group = pd.DataFrame(columns=["id_vendita", "importo"])

# ============================
# MERGE SICURO
# ============================
df = vendite.merge(rate_group, left_on="id", right_on="id_vendita", how="left")
df["importo"] = df["importo"].fillna(0)

# ============================
# CALCOLO RESIDUO
# ============================
df["residuo"] = df["prezzo"] - df["acconto"] - df["importo"]

# ============================
# FILTRO VENDITE APERTE
# ============================
aperte = df[df["residuo"] > 0]

st.subheader("🔍 Filtri")

col1, col2 = st.columns(2)
f_cliente = col1.text_input("Filtra per cliente")
f_prodotto = col2.text_input("Filtra per prodotto")

df_view = aperte.copy()

if f_cliente:
    df_view = df_view[df_view["cliente"].str.contains(f_cliente, case=False, na=False)]

if f_prodotto:
    df_view = df_view[df_view["prodotto"].str.contains(f_prodotto, case=False, na=False)]

# ============================
# TABELLA RISULTATI
# ============================
st.subheader("📋 Vendite ancora aperte")

if df_view.empty:
    st.info("Nessuna vendita aperta trovata con questi filtri.")
else:
    st.dataframe(df_view[[
        "id", "cliente", "prodotto", "prezzo", "costo", "extra",
        "acconto", "importo", "residuo"
    ]])

# ============================
# TOTALE RESIDUO
# ============================
st.subheader("📊 Totale residuo")

tot_residuo = df_view["residuo"].sum()

st.metric("Residuo totale da incassare", f"€ {tot_residuo:,.2f}")
