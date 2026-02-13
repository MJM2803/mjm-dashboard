import streamlit as st
import pandas as pd
from supabase_utils import supabase_select, supabase_update, supabase_insert

st.title("🟩 Gestione Decime")

# Carico vendite
vendite = pd.DataFrame(supabase_select("vendite"))

if vendite.empty:
    st.info("Nessuna vendita registrata.")
    st.stop()

# Calcolo decima
vendite["decima"] = vendite["guadagno"] * 0.10

# Vendite con decima già data
decime_ok = vendite[vendite["note"] == "decima_ok"]

# Vendite con decima da dare
decime_da_dare = vendite[(vendite["note"].isna()) | (vendite["note"] == "")]

st.subheader("🟡 Decime da dare")

if decime_da_dare.empty:
    st.success("Tutte le decime sono state date.")
else:
    st.dataframe(decime_da_dare[["id", "cliente", "prodotto", "guadagno", "decima"]])

    with st.form("segna_decima"):
        id_decima = st.selectbox(
            "Seleziona vendita per segnare la decima come data",
            decime_da_dare["id"].tolist()
        )
        submit = st.form_submit_button("Segna come data")

    if submit:
        vendita_sel = vendite[vendite["id"] == id_decima].iloc[0]
        decima_importo = vendita_sel["decima"]

        # Aggiorno la vendita
        supabase_update("vendite", id_decima, {"note": "decima_ok"})

        # Movimento cassa automatico
        supabase_insert("movimenti_cassa", {
            "data": vendita_sel["data"] if vendita_sel["data"] else "",
            "tipo": "uscita",
            "soggetto": "decima",
            "importo": -abs(decima_importo),
            "note": f"Decima vendita {id_decima}"
        })

        st.success("Decima segnata come data e movimento di cassa registrato!")

st.subheader("🟢 Decime già date")

if decime_ok.empty:
    st.info("Nessuna decima ancora data.")
else:
    st.dataframe(decime_ok[["id", "cliente", "prodotto", "guadagno", "decima"]])
