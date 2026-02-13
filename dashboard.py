import streamlit as st
import pandas as pd
from supabase_utils import supabase_select
import plotly.express as px

st.set_page_config(page_title="MJM Dashboard", layout="wide")

st.title("🏠 Panoramica generale")

# ============================
# FUNZIONE DI CARICAMENTO ROBUSTA
# ============================
def load_table(name):
    data = supabase_select(name)
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

# ============================
# CARICO I DATI
# ============================
mov = load_table("movimenti_cassa")   # contiene entrate e uscite
vendite = load_table("vendite")

# ============================
# CALCOLI PRINCIPALI
# ============================
saldo = mov["importo"].sum() if not mov.empty else 0
totale_vendite = vendite["prezzo"].sum() if not vendite.empty else 0
totale_guadagno = vendite["guadagno"].sum() if ("guadagno" in vendite.columns and not vendite.empty) else 0

# Spese = movimenti con tipo = "uscita"
if not mov.empty:
    spese = mov[mov["tipo"] == "uscita"]
    totale_spese = spese["importo"].sum()
else:
    totale_spese = 0

# ============================
# KPI
# ============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Saldo cassa", f"€ {saldo:,.2f}")
col2.metric("Totale vendite", f"€ {totale_vendite:,.2f}")
col3.metric("Guadagno totale", f"€ {totale_guadagno:,.2f}")
col4.metric("Totale spese", f"€ {totale_spese:,.2f}")

# ============================
# GRAFICO MOVIMENTI CASSA
# ============================
st.subheader("📈 Andamento movimenti di cassa")

if not mov.empty:
    mov["data"] = mov["data"].astype(str)
    mov = mov[mov["data"] != ""]
    mov = mov.dropna(subset=["data"])

    fig = px.line(
        mov,
        x="data",
        y="importo",
        title="Andamento movimenti cassa",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessun movimento registrato.")
