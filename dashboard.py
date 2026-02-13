import streamlit as st
import pandas as pd
import requests

# -----------------------------
# CONFIGURAZIONE SUPABASE
# -----------------------------
SUPABASE_URL = "https://qthmotrbsumohhzdcrbp.supabase.co"
SUPABASE_KEY = "sb_publishable_5ACoXLMtmKoayqLWSO-7og_KKTgX5Q9"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Funzioni helper
def supabase_select(table):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    r = requests.get(url, headers=HEADERS)
    return r.json()

def supabase_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data)
    return r.json()

def supabase_update(table, row_id, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}"
    r = requests.patch(url, headers=HEADERS, json=data)
    return r.json()

# -----------------------------
# UI
# -----------------------------
st.title("📊 Dashboard Vendite, Rate e Decime")

# -----------------------------
# SEZIONE 1: INSERIMENTO VENDITA
# -----------------------------
st.header("➕ Inserisci nuova vendita")

with st.form("nuova_vendita"):
    cliente = st.text_input("Cliente")
    prodotto = st.text_input("Prodotto")
    prezzo = st.number_input("Prezzo totale", min_value=0.0)
    acconto = st.number_input("Acconto", min_value=0.0)
    guadagno = st.number_input("Guadagno", min_value=0.0)
    data = st.text_input("Data")
    note = st.text_input("Note (es: decima_ok)")

    submit_vendita = st.form_submit_button("Salva vendita")

if submit_vendita:
    supabase_insert("vendite", {
        "cliente": cliente,
        "prodotto": prodotto,
        "prezzo_totale": prezzo,
        "acconto": acconto,
        "guadagno": guadagno,
        "data": data,
        "note": note
    })
    st.success("Vendita salvata!")

# -----------------------------
# SEZIONE 2: INSERIMENTO RATA
# -----------------------------
st.header("💶 Inserisci pagamento rata")

vendite = supabase_select("vendite")
lista_vendite = {f"{v['id']} - {v['cliente']}": v["id"] for v in vendite}

with st.form("nuova_rata"):
    id_vendita = st.selectbox("Seleziona vendita", lista_vendite.keys())
    cliente_rata = st.text_input("Cliente")
    importo_rata = st.number_input("Importo rata", min_value=0.0)
    data_rata = st.text_input("Data")

    submit_rata = st.form_submit_button("Salva rata")

if submit_rata:
    supabase_insert("pagamenti_rate", {
        "id_vendita": lista_vendite[id_vendita],
        "cliente": cliente_rata,
        "importo": importo_rata,
        "data": data_rata
    })
    st.success("Rata salvata!")

# -----------------------------
# SEZIONE 3: VENDITE ANCORA APERTE
# -----------------------------
st.header("📌 Vendite ancora aperte")

rate = supabase_select("pagamenti_rate")

df_vendite = pd.DataFrame(vendite)
df_rate = pd.DataFrame(rate)

if not df_rate.empty:
    df_rate_grouped = df_rate.groupby("id_vendita")["importo"].sum().reset_index()
else:
    df_rate_grouped = pd.DataFrame(columns=["id_vendita", "importo"])

df = df_vendite.merge(df_rate_grouped, left_on="id", right_on="id_vendita", how="left")
df["importo"] = df["importo"].fillna(0)
df["residuo"] = df["prezzo_totale"] - df["acconto"] - df["importo"]

df_aperte = df[df["residuo"] > 0]

st.dataframe(df_aperte[["id", "cliente", "prodotto", "prezzo_totale", "acconto", "importo", "residuo"]])

# -----------------------------
# SEZIONE 4: STATISTICHE
# -----------------------------
st.header("📈 Statistiche")

totale_rate = df_rate["importo"].sum() if not df_rate.empty else 0
totale_residuo = df_aperte["residuo"].sum()

st.metric("Totale rate ricevute", f"€ {totale_rate:,.2f}")
st.metric("Totale residuo", f"€ {totale_residuo:,.2f}")

# -----------------------------
# SEZIONE 5: GESTIONE DECIME
# -----------------------------
st.header("🟩 Gestione Decime")

df_vendite["decima"] = df_vendite["guadagno"] * 0.10

df_decime_ok = df_vendite[df_vendite["note"] == "decima_ok"]
df_decime_da_dare = df_vendite[(df_vendite["note"].isna()) | (df_vendite["note"] == "")]

st.subheader("Decime da dare")
st.dataframe(df_decime_da_dare[["id", "cliente", "guadagno", "decima"]])

with st.form("segna_decima"):
    id_decima = st.selectbox(
        "Seleziona vendita per segnare la decima come data",
        df_decime_da_dare["id"].tolist()
    )
    submit_decima = st.form_submit_button("Segna come data")

if submit_decima:
    supabase_update("vendite", id_decima, {"note": "decima_ok"})
    st.success("Decima segnata come data!")

st.subheader("Decime già date")
st.dataframe(df_decime_ok[["id", "cliente", "guadagno", "decima"]])

tot_decime_date = df_decime_ok["decima"].sum()
tot_decime_da_dare = df_decime_da_dare["decima"].sum()

st.metric("Totale decime date", f"€ {tot_decime_date:,.2f}")
st.metric("Totale decime da dare", f"€ {tot_decime_da_dare:,.2f}")
