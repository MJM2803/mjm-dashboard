import streamlit as st
import pandas as pd
import plotly.express as px
from supabase_utils import supabase_select

st.title("📊 Analisi vendite")

# Carico dati
vendite = pd.DataFrame(supabase_select("vendite"))
rate = pd.DataFrame(supabase_select("pagamenti_rate"))
spese = pd.DataFrame(supabase_select("spese"))
mov = pd.DataFrame(supabase_select("movimenti_cassa"))

if vendite.empty:
    st.info("Nessuna vendita registrata.")
    st.stop()

# Pulizia date
if "data" in vendite.columns:
    vendite["data"] = vendite["data"].replace("", None)

# ============================
# 📅 Entrate mensili
# ============================

st.subheader("📅 Entrate mensili")

if not mov.empty:
    mov["mese"] = mov["data"].str.slice(0, 7)
    entrate = mov[mov["tipo"] == "entrata"].groupby("mese")["importo"].sum().reset_index()

    if not entrate.empty:
        fig = px.bar(entrate, x="mese", y="importo", title="Entrate mensili", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessuna entrata registrata.")
else:
    st.info("Nessun movimento di cassa registrato.")

# ============================
# 📉 Uscite mensili
# ============================

st.subheader("📉 Uscite mensili")

if not mov.empty:
    uscite = mov[mov["tipo"] == "uscita"].copy()
    uscite["mese"] = uscite["data"].str.slice(0, 7)
    uscite_mese = uscite.groupby("mese")["importo"].sum().reset_index()

    if not uscite_mese.empty:
        fig = px.bar(uscite_mese, x="mese", y="importo", title="Uscite mensili", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessuna uscita registrata.")
else:
    st.info("Nessun movimento di cassa registrato.")

# ============================
# 💰 Saldo mensile
# ============================

st.subheader("💰 Saldo mensile")

if not mov.empty:
    mov["mese"] = mov["data"].str.slice(0, 7)
    saldo_mese = mov.groupby("mese")["importo"].sum().reset_index()

    fig = px.line(saldo_mese, x="mese", y="importo", markers=True, title="Saldo mensile")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessun movimento di cassa registrato.")

# ============================
# 📦 Vendite per prodotto
# ============================

st.subheader("📦 Vendite per prodotto")

vend_prod = vendite.groupby("prodotto")["prezzo"].sum().reset_index()

if not vend_prod.empty:
    fig = px.bar(vend_prod, x="prodotto", y="prezzo", title="Totale vendite per prodotto", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessuna vendita registrata.")

# ============================
# 💵 Guadagno per prodotto
# ============================

st.subheader("💵 Guadagno per prodotto")

guad_prod = vendite.groupby("prodotto")["guadagno"].sum().reset_index()

if not guad_prod.empty:
    fig = px.bar(guad_prod, x="prodotto", y="guadagno", title="Guadagno per prodotto", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessun guadagno registrato.")

# ============================
# 👥 Vendite per cliente
# ============================

st.subheader("👥 Vendite per cliente")

vend_cliente = vendite.groupby("cliente")["prezzo"].sum().reset_index()

if not vend_cliente.empty:
    fig = px.bar(vend_cliente, x="cliente", y="prezzo", title="Totale vendite per cliente", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessuna vendita registrata.")

# ============================
# 🟩 Extra per mese
# ============================

st.subheader("🟩 Extra per mese")

if vendite["data"].notna().any():
    vendite["mese"] = vendite["data"].str.slice(0, 7)
    extra_mese = vendite.groupby("mese")["extra"].sum().reset_index()

    fig = px.line(extra_mese, x="mese", y="extra", markers=True, title="Extra per mese")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nessuna data disponibile per calcolare gli extra mensili.")
