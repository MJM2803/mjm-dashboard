import streamlit as st
import pandas as pd
from supabase_utils import supabase_insert, supabase_select

st.title("💸 Spese")

st.subheader("➕ Inserisci una nuova spesa")

with st.form("nuova_spesa"):
    data_spesa = st.text_input("Data spesa (es: 2026-01-01)")
    categoria = st.text_input("Categoria (es: manutenzione, benzina, ecc.)")
    descrizione = st.text_input("Descrizione")
    importo_spesa = st.number_input("Importo spesa", min_value=0.0)

    submit = st.form_submit_button("Salva spesa")

if submit:
    # Salvo SOLO in movimenti_cassa
    supabase_insert("movimenti_cassa", {
        "data": data_spesa,
        "tipo": "uscita",
        "soggetto": "spesa",
        "importo": importo_spesa,
        "note": f"{categoria} - {descrizione}"
    })

    st.success("Spesa salvata correttamente!")

st.subheader("📋 Storico spese")

# --- LEGGIAMO SOLO DA movimenti_cassa ---
raw = supabase_select("movimenti_cassa")
mov = pd.DataFrame(raw) if isinstance(raw, list) else pd.DataFrame()

if mov.empty:
    st.info("Nessuna spesa registrata.")
else:
    # Filtra solo le spese
    spese = mov[
        (mov["tipo"] == "uscita") &
        (mov["soggetto"].str.contains("spesa", case=False, na=False))
    ]

    if spese.empty:
        st.info("Nessuna spesa trovata.")
    else:
        spese = spese.sort_values("data", ascending=False)
        st.dataframe(spese[["data", "note", "importo"]])
