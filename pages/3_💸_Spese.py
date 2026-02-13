import streamlit as st
from supabase_utils import supabase_insert, supabase_select
import pandas as pd

st.title("💸 Spese")

st.subheader("➕ Inserisci una nuova spesa")

with st.form("nuova_spesa"):
    data_spesa = st.text_input("Data spesa (es: 2025-02-13)")
    categoria = st.text_input("Categoria (es: manutenzione, benzina, ecc.)")
    descrizione = st.text_input("Descrizione")
    importo_spesa = st.number_input("Importo spesa", min_value=0.0)

    submit = st.form_submit_button("Salva spesa")

if submit:
    # Salvo nella tabella spese
    supabase_insert("spese", {
        "data": data_spesa,
        "categoria": categoria,
        "descrizione": descrizione,
        "importo": importo_spesa
    })

    # Movimento di cassa automatico
    supabase_insert("movimenti_cassa", {
        "data": data_spesa,
        "tipo": "uscita",
        "soggetto": "spesa",
        "importo": -abs(importo_spesa),
        "note": descrizione
    })

    st.success("Spesa salvata e movimento di cassa registrato!")

st.subheader("📋 Storico spese")

# --- FIX ROBUSTO ---
raw_spese = supabase_select("spese")
spese = pd.DataFrame(raw_spese) if isinstance(raw_spese, list) else pd.DataFrame()

if spese.empty:
    st.info("Nessuna spesa registrata.")
else:
    spese = spese.sort_values("data", ascending=False)
    st.dataframe(spese)
