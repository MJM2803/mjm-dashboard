import streamlit as st
import pandas as pd
import plotly.express as px
from supabase_utils import supabase_select

st.title("📊 Analisi vendite")

# ============================
# FUNZIONE DI CARICAMENTO ROBUSTA
# ============================
def load_table(name):
    data = supabase_select(name)
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

# ============================
# CARICO I DATI
# ============================
vendite = load_table("vendite")
rate = load_table("pagamenti_rate")
mov = load_table("movimenti_cassa")  # contiene ENTRATE e USCITE

if vendite.empty:
    st.info("Nessuna vendita registrata.")
    st.stop()

# ============================
# NORMALIZZAZIONE DATE
# ============================
# Vendite: data in formato dd/mm/YYYY
if "data" in vendite.columns:
    vendite["data"] = vendite["data"].replace("", None)
    vendite["data"] = pd.to_datetime(vendite["data"], format="%d/%m/%Y", errors="coerce")

# Movimenti cassa
if not mov.empty:
    mov["data"] = pd.to_datetime(mov["data"], format="%d/%m/%Y", errors="coerce")
    mov["mese"] = mov["data"].dt.strftime("%Y-%m")
    mov["importo"] = pd.to_numeric(mov["importo"], errors="coerce")

# ============================
# 📅 ENTRATE MENSILI
# ============================
st.subheader("📅 Entrate mensili")

if not mov.empty:
    entrate = mov[mov["tipo"] == "entrata"].groupby("mese")["importo"].sum().reset_index()

    if not entrate.empty:
        fig = px.bar(entrate, x="mese", y="importo", title="Entrate mensili", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessuna entrata registrata.")
else:
    st.info("Nessun movimento di cassa registrato.")

# ============================
# 📉 USCITE MENSILI
# ============================
st.subheader("📉 Uscite mensili")

if not mov.empty:
    uscite = mov[mov["tipo"] == "uscita"].copy()
    uscite_mese = uscite.groupby("mese")["importo"].sum().reset_index()

    if not uscite_mese.empty:
        fig = px.bar(uscite_mese, x="mese", y="importo", title="Uscite mensili", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessuna uscita registrata.")
else:
    st.info("Nessun movimento di cassa registrato.")

# ============================
# 💰 SALDO MENSILE
# ============================
st.subheader("💰 Saldo mensile")

if not mov.empty:
    saldo_mese = mov.groupby("mese")["importo"].sum().reset_index()

    fig = px.line(saldo_mese, x="mese", y="importo", markers=True, title="Saldo mensile")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessun movimento di cassa registrato.")

# ============================
# 📦 VENDITE PER PRODOTTO
# ============================
st.subheader("📦 Vendite per prodotto")

vend_prod = vendite.groupby("prodotto")["prezzo"].sum().reset_index()

if not vend_prod.empty:
    fig = px.bar(vend_prod, x="prodotto", y="prezzo", title="Totale vendite per prodotto", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessuna vendita registrata.")

# ============================
# 💵 GUADAGNO PER PRODOTTO
# ============================
st.subheader("💵 Guadagno per prodotto")

if "guadagno" in vendite.columns:
    guad_prod = vendite.groupby("prodotto")["guadagno"].sum().reset_index()

    if not guad_prod.empty:
        fig = px.bar(guad_prod, x="prodotto", y="guadagno", title="Guadagno per prodotto", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessun guadagno registrato.")
else:
    st.info("La colonna 'guadagno' non è presente nella tabella vendite.")

# ============================
# 👥 VENDITE PER CLIENTE
# ============================
st.subheader("👥 Vendite per cliente")

vend_cliente = vendite.groupby("cliente")["prezzo"].sum().reset_index()

if not vend_cliente.empty:
    fig = px.bar(vend_cliente, x="cliente", y="prezzo", title="Totale vendite per cliente", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessuna vendita registrata.")

# ============================
# 🟩 EXTRA PER MESE
# ============================
st.subheader("🟩 Extra per mese")

if vendite["data"].notna().any():
    vendite["mese"] = vendite["data"].dt.strftime("%Y-%m")
    extra_mese = vendite.groupby("mese")["extra"].sum().reset_index()

    fig = px.line(extra_mese, x="mese", y="extra", markers=True, title="Extra per mese")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessuna data disponibile per calcolare gli extra mensili.")
