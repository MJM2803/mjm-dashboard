import streamlit as st
import pandas as pd
from supabase_utils import supabase_select, supabase_insert, supabase_update

st.title("💶 Rate")

# ============================
# CARICAMENTO DATI ROBUSTO
# ============================

raw_vendite = supabase_select("vendite")
raw_rate = supabase_select("pagamenti_rate")

vendite = pd.DataFrame(raw_vendite) if isinstance(raw_vendite, list) else pd.DataFrame()
rate = pd.DataFrame(raw_rate) if isinstance(raw_rate, list) else pd.DataFrame()

if vendite.empty:
    st.info("Nessuna vendita presente.")
    st.stop()

# ============================
# SELEZIONE VENDITA
# ============================

vendite["label"] = vendite.apply(
    lambda v: f"{v['id']} - {v['cliente']} - {v['prodotto']}", axis=1
)
mappa_vendite = {row["label"]: row["id"] for _, row in vendite.iterrows()}

st.subheader("➕ Inserisci nuova rata")

with st.form("nuova_rata"):
    scelta = st.selectbox("Seleziona vendita", list(mappa_vendite.keys()))
    cliente_rata = st.text_input("Cliente (opzionale, se diverso)")
    importo_rata = st.number_input("Importo rata", min_value=0.0)

    # Date picker
    data_rata_input = st.date_input("Data rata", format="DD/MM/YYYY")

    submit = st.form_submit_button("Salva rata")

if submit:
    id_vendita = mappa_vendite[scelta]
    vendita_sel = vendite[vendite["id"] == id_vendita].iloc[0]

    if not cliente_rata:
        cliente_rata = vendita_sel["cliente"]

    # ============================
    # CONVERSIONE DATA
    # ============================
    data_rata = data_rata_input.strftime("%Y-%m-%d")

    # ============================
    # INSERISCO RATA
    # ============================
    supabase_insert("pagamenti_rate", {
        "id_vendita": id_vendita,
        "cliente": cliente_rata,
        "importo": importo_rata,
        "data": data_rata
    })

    # ============================
    # MOVIMENTO DI CASSA
    # ============================
    supabase_insert("movimenti_cassa", {
        "data": data_rata,
        "tipo": "entrata",
        "soggetto": "rata",
        "importo": importo_rata,
        "note": f"Rata vendita {id_vendita} - {cliente_rata}"
    })

    # ============================
    # RICALCOLO RESIDUO
    # ============================
    raw_rate = supabase_select("pagamenti_rate")
    rate = pd.DataFrame(raw_rate) if isinstance(raw_rate, list) else pd.DataFrame()

    totale_rate = rate[rate["id_vendita"] == id_vendita]["importo"].sum() if not rate.empty else 0
    residuo = vendita_sel["prezzo"] - vendita_sel["acconto"] - totale_rate

    if residuo <= 0:
        supabase_update("vendite", id_vendita, {"data": data_rata})

    st.success("Rata salvata e movimento registrato.")

# ============================
# RIEPILOGO RATE
# ============================

st.subheader("📋 Riepilogo rate per vendita")

if rate.empty:
    st.info("Nessuna rata registrata.")
else:
    rate["id_vendita"] = pd.to_numeric(rate["id_vendita"], errors="coerce")
    vendite["id"] = pd.to_numeric(vendite["id"], errors="coerce")

    rate = rate.rename(columns={"cliente": "cliente_rata", "data": "data_rata"})
    vendite = vendite.rename(columns={"cliente": "cliente_vendita"})

    df = rate.merge(
        vendite,
        left_on="id_vendita",
        right_on="id",
        how="left"
    )

    colonne = []
    for c in ["id_vendita", "cliente_rata", "cliente_vendita", "prodotto", "importo", "data_rata"]:
        if c in df.columns:
            colonne.append(c)

    df_view = df[colonne]

    st.dataframe(df_view)
