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
if not mov.empty:
    mov["importo_signed"] = mov.apply(
        lambda row: -row["importo"] if row["tipo"] == "uscita" else row["importo"],
        axis=1
    )
    saldo = mov["importo_signed"].sum()
else:
    saldo = 0

totale_vendite = vendite["prezzo"].sum() if not vendite.empty else 0
totale_guadagno
