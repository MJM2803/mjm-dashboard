import streamlit as st
import pandas as pd
from supabase_utils import supabase_select
import plotly.express as px

st.set_page_config(page_title="MJM Dashboard", layout="wide")

st.title("🏠 Panoramica generale")

# ============================
# FUNZIONE DI CARICAMENTO
# ============================
def load_table(name):
    data = supabase_select(name)
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

# ============================
# CARICO I DATI
# ============================
mov = load_table("movimenti_cassa")
vendite = load_table("vendite")

# ============================
# CALCOLI PRINCIPALI
# ============================
saldo = 0
totale_vendite = 0
totale_guadagno = 0
totale_spese = 0

# --- Movimenti cassa ---
if not mov.empty:
    mov["importo_signed"] = mov.apply(
        lambda row: -row["importo"] if row["tipo"] == "uscita" else row["importo"],
        axis=1
    )
    saldo = mov["importo_signed"].sum()

    spese = mov[mov["tipo"] == "uscita"]
    totale_spese = spese["importo"].sum()

# --- Vendite ---
if not vendite.empty:
    totale_vendite = vendite["prezzo"].sum()
    if "guadagno" in vendite.columns:
        totale_guadagno = vendite["guadagno"].sum()

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

    # Conversione automatica della data (funziona con YYYY/MM/DD)
    mov["data"] = pd.to_datetime(mov["data"], errors="coerce")

    # Rimuovo eventuali date non valide
    mov = mov.dropna(subset=["data"])

    # Ordino per data
    mov = mov.sort_values("data")

    fig = px.line(
        mov,
        x="data",
        y="importo_signed",
        title="Andamento movimenti cassa",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Nessun movimento registrato.")
