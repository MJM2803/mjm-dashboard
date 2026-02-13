import streamlit as st
import pandas as pd
from supabase_utils import supabase_select, supabase_insert, supabase_update

st.title("💶 Rate")

# Carico vendite e rate
raw_vendite = supabase_select("vendite")
raw_rate = supabase_select("pagamenti_rate")

vendite = pd.DataFrame(raw_vendite) if isinstance(raw_vendite, list) else pd.DataFrame()
rate = pd.DataFrame(raw_rate) if isinstance(raw_rate, list) else pd.DataFrame()

if vendite.empty:
    st.info("Nessuna vendita presente.")
    st.stop()

# Mappa vendite per selezione
vendite["label"] = vendite.apply(
    lambda v: f"{v['id']} - {v['cliente']} - {v['prodotto']}", axis=1
)
mappa_vendite = {row["label"]: row["id"] for _, row in vendite.iterrows()}

st.subheader("➕ Inserisci nuova rata")

with st.form("nuova_rata"):
    scelta = st.selectbox("Seleziona vendita", list(mappa_vendite.keys()))
    cliente_rata = st.text_input("Cliente (opzionale, se diverso)")
    importo_rata = st.number_input("Importo rata", min_value=0.0)
    data_rata = st.text_input("Data rata (es: 2026-02-13)")

    submit = st.form_submit_button("Salva rata")

if submit:
    id_vendita = mappa_vendite[scelta]
    vendita_sel = vendite[vendite["id"] == id_vendita].iloc[0]

    if not cliente_rata:
        cliente_rata = vendita_sel["cliente"]

    # Inserisco rata
    supabase_insert("pagamenti_rate", {
        "id_vendita": id_vendita,
        "cliente": cliente_rata,
        "importo": importo_rata,
        "data": data_rata
    })

    # Movimento di cassa automatico
    supabase_insert("movimenti_cassa", {
        "data": data_rata,
        "tipo": "entrata",
        "soggetto": "rata",
        "importo": importo_rata,
        "note": f"Rata vendita {id_vendita} - {cliente_rata}"
    })

    # Ricalcolo totale rate
    raw_rate = supabase_select("pagamenti_rate")
    rate = pd.DataFrame(raw_rate) if isinstance(raw_rate, list) else pd.DataFrame()

    if not rate.empty:
        rate_vendita = rate[rate["id_vendita"] == id_vendita]["importo"].sum()
    else:
        rate_vendita = 0

    residuo = vendita_sel["prezzo"] - vendita_sel["acconto"] - rate_vendita

    # Se residuo = 0 → chiudo vendita
    if residuo <= 0:
        supabase_update("vendite", id_vendita, {"data": data_rata})

    st.success("Rata salvata, movimento registrato e residuo aggiornato.")

# ============================
# RIEPILOGO RATE
# ============================

st.subheader("📋 Riepilogo rate per vendita")

# Fix tipi per merge
if not rate.empty:
    rate["id_vendita"] = pd.to_numeric(rate["id_vendita"], errors="coerce")
if not vendite.empty:
    vendite["id"] = pd.to_numeric(vendite["id"], errors="coerce")

if rate.empty:
    st.info("Nessuna rata registrata.")
else:
    df = rate.merge(
        vendite,
        left_on="id_vendita",
        right_on="id",
        how="left",
        suffixes=("_rata", "_vendita")
    )

    df_view = df[[
        "id_vendita",
        "cliente_rata",
        "cliente_vendita",
        "prodotto",
        "importo",
        "data_rata"
    ]].copy()

    df_view.rename(columns={
        "id_vendita": "ID vendita",
        "cliente_rata": "Cliente rata",
        "cliente_vendita": "Cliente vendita",
        "prodotto": "Prodotto",
        "importo": "Importo rata",
        "data_rata": "Data rata"
    }, inplace=True)

    st.dataframe(df_view)
