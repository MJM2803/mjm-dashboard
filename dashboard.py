import streamlit as st
import pandas as pd
from supabase_utils import supabase_select
import plotly.express as px

st.set_page_config(page_title="MJM Dashboard", layout="wide")

st.title("🏠 Panoramica generale")

mov = pd.DataFrame(supabase_select("movimenti_cassa"))
vendite = pd.DataFrame(supabase_select("vendite"))
spese = pd.DataFrame(supabase_select("spese"))

col1, col2, col3, col4 = st.columns(4)

saldo = mov["importo"].sum() if not mov.empty else 0
totale_vendite = vendite["prezzo"].sum() if not vendite.empty else 0
totale_guadagno = vendite["guadagno"].sum() if not vendite.empty else 0
totale_spese = spese["importo"].sum() if not spese.empty else 0

col1.metric("Saldo cassa", f"€ {saldo:,.2f}")
col2.metric("Totale vendite", f"€ {totale_vendite:,.2f}")
col3.metric("Guadagno totale", f"€ {totale_guadagno:,.2f}")
col4.metric("Totale spese", f"€ {totale_spese:,.2f}")

if not mov.empty:
    mov["data"] = mov["data"].replace("", None)
    mov = mov.dropna(subset=["data"])
    fig = px.line(mov, x="data", y="importo", title="Andamento movimenti cassa")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessun movimento registrato.")
