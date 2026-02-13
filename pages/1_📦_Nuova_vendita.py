import streamlit as st
from supabase_utils import supabase_insert
import pandas as pd

st.title("📦 Nuova vendita")

with st.form("nuova_vendita"):
    cliente = st.text_input("Cliente")
    prodotto = st.text_input("Prodotto")
    costo = st.number_input("Costo", min_value=0.0)
    prezzo = st.number_input("Prezzo", min_value=0.0)
    extra = st.number_input("Extra (informativo)", min_value=0.0)
    acconto = st.number_input("Acconto", min_value=0.0)
    note = st.text_input("Note")

    guadagno = prezzo - costo
    st.info(f"Guadagno calcolato automaticamente: € {guadagno:.2f}")

    submit = st.form_submit_button("Salva vendita")

if submit:
    supabase_insert("vendite", {
        "cliente": cliente,
        "prodotto": prodotto,
        "costo": costo,
        "prezzo": prezzo,
        "extra": extra,
        "guadagno": guadagno,
        "acconto": acconto,
        "data": None,
        "note": note
    })

    if acconto > 0:
        supabase_insert("movimenti_cassa", {
            "data": "",
            "tipo": "entrata",
            "soggetto": "acconto",
            "importo": acconto,
            "note": f"Acconto vendita {cliente}"
        })

    st.success("Vendita salvata!")
