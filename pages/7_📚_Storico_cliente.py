import streamlit as st
import pandas as pd
from supabase_utils import supabase_select

st.title("📚 Storico cliente")

# Carico dati
vendite = pd.DataFrame(supabase_select("vendite"))
rate = pd.DataFrame(supabase_select("pagamenti_rate"))
mov = pd.DataFrame(supabase_select("movimenti_cassa"))

if vendite.empty:
    st.info("Nessuna vendita registrata.")
    st.stop()

# Lista clienti
clienti = sorted(vendite["cliente"].dropna().unique().tolist())

cliente_sel = st.selectbox("Seleziona un cliente", clienti)

if not cliente_sel:
    st.stop()

st.subheader(f"📦 Vendite di {cliente_sel}")

vend_cliente = vendite[vendite["cliente"] == cliente_sel]

if vend_cliente.empty:
    st.info("Nessuna vendita trovata per questo cliente.")
else:
    st.dataframe(vend_cliente[[
        "id", "prodotto", "costo", "prezzo", "extra", "guadagno",
        "acconto", "data", "note"
    ]])

# Rate del cliente
st.subheader("💶 Rate pagate")

if not rate.empty:
    rate_cliente = rate[rate["cliente"] == cliente_sel]
else:
    rate_cliente = pd.DataFrame()

if rate_cliente.empty:
    st.info("Nessuna rata registrata per questo cliente.")
else:
    st.dataframe(rate_cliente[["id_vendita", "importo", "data"]])

# Calcolo residuo totale
st.subheader("📌 Situazione pagamenti")

residui = []

for _, v in vend_cliente.iterrows():
    id_v = v["id"]
    prezzo = v["prezzo"]
    acconto = v["acconto"]

    if not rate.empty:
        rate_v = rate[rate["id_vendita"] == id_v]["importo"].sum()
    else:
        rate_v = 0

    residuo = prezzo - acconto - rate_v
    residui.append(residuo)

tot_residuo = sum(residui)

st.metric("Residuo totale da incassare", f"€ {tot_residuo:,.2f}")

# Movimenti cassa collegati
st.subheader("💰 Movimenti di cassa collegati")

if mov.empty:
    st.info("Nessun movimento registrato.")
else:
    mov_cliente = mov[mov["note"].str.contains(cliente_sel, case=False, na=False)]
    if mov_cliente.empty:
        st.info("Nessun movimento collegato a questo cliente.")
    else:
        st.dataframe(mov_cliente[["data", "tipo", "importo", "note"]])

# Totale guadagno generato
st.subheader("💵 Guadagno totale generato")

guadagno_tot = vend_cliente["guadagno"].sum()
st.metric("Guadagno totale", f"€ {guadagno_tot:,.2f}")

# Decima relativa
st.subheader("🟩 Decima relativa")

decima_tot = guadagno_tot * 0.10
st.metric("Decima totale", f"€ {decima_tot:,.2f}")
