import streamlit as st
import pandas as pd
from supabase_utils import supabase_select

st.title("📚 Storico cliente")

# Carico dati in modo robusto
def load_table(name):
    data = supabase_select(name)
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

vendite = load_table("vendite")
rate = load_table("pagamenti_rate")
mov = load_table("movimenti_cassa")

if vendite.empty:
    st.info("Nessuna vendita registrata.")
    st.stop()

# Normalizzo tipi
vendite["id"] = pd.to_numeric(vendite["id"], errors="coerce")
rate["id_vendita"] = pd.to_numeric(rate["id_vendita"], errors="coerce")

# Lista clienti
clienti = sorted(vendite["cliente"].dropna().unique().tolist())
cliente_sel = st.selectbox("Seleziona un cliente", clienti)

if not cliente_sel:
    st.stop()

# ============================
# 📦 Vendite del cliente
# ============================
st.subheader(f"📦 Vendite di {cliente_sel}")

vend_cliente = vendite[vendite["cliente"] == cliente_sel]

if vend_cliente.empty:
    st.info("Nessuna vendita trovata per questo cliente.")
else:
    st.dataframe(vend_cliente[[
        "id", "prodotto", "costo", "prezzo", "extra", "guadagno",
        "acconto", "data", "note"
    ]])

# ============================
# 💶 Rate del cliente
# ============================
st.subheader("💶 Rate pagate")

rate_cliente = rate[rate["id_vendita"].isin(vend_cliente["id"])]

if rate_cliente.empty:
    st.info("Nessuna rata registrata per questo cliente.")
else:
    st.dataframe(rate_cliente[["id_vendita", "importo", "data"]])

# ============================
# 📌 Situazione pagamenti
# ============================
st.subheader("📌 Situazione pagamenti")

tot_residuo = 0

for _, v in vend_cliente.iterrows():
    id_v = v["id"]
    prezzo = v["prezzo"]
    acconto = v["acconto"]

    rate_v = rate[rate["id_vendita"] == id_v]["importo"].sum()
    residuo = prezzo - acconto - rate_v

    tot_residuo += residuo

st.metric("Residuo totale da incassare", f"€ {tot_residuo:,.2f}")

# ============================
# 💰 Movimenti cassa collegati
# ============================
st.subheader("💰 Movimenti di cassa collegati")

if mov.empty:
    st.info("Nessun movimento registrato.")
else:
    # Movimenti legati SOLO alle vendite del cliente
    id_vendite_cliente = vend_cliente["id"].astype(str).tolist()

    mov["id_vendita"] = mov["note"].str.extract(r'(\d+)')  # estrae ID vendita dalle note
    mov["id_vendita"] = pd.to_numeric(mov["id_vendita"], errors="coerce")

    mov_cliente = mov[mov["id_vendita"].isin(vend_cliente["id"])]

    if mov_cliente.empty:
        st.info("Nessun movimento collegato a questo cliente.")
    else:
        st.dataframe(mov_cliente[["data", "tipo", "importo", "note"]])

# ============================
# 💵 Guadagno totale
# ============================
st.subheader("💵 Guadagno totale generato")

guadagno_tot = vend_cliente["guadagno"].sum()
st.metric("Guadagno totale", f"€ {guadagno_tot:,.2f}")

# ============================
# 🟩 Decima
# ============================
st.subheader("🟩 Decima relativa")

decima_tot = guadagno_tot * 0.10
st.metric("Decima totale", f"€ {decima_tot:,.2f}")
