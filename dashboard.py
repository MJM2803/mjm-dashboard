import streamlit as st
import pandas as pd
import requests

# -----------------------------
# CONFIGURAZIONE SUPABASE
# -----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# -----------------------------
# FUNZIONI SUPABASE
# -----------------------------
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
st.title("📊 MJM Dashboard — Vendite, Rate, Spese, Decime & Cassa")

# -----------------------------
# SEZIONE 1: INSERIMENTO VENDITA
# -----------------------------
st.header("➕ Inserisci nuova vendita")

with st.form("nuova_vendita"):
    cliente = st.text_input("Cliente")
    prodotto = st.text_input("Prodotto")
    costo = st.number_input("Costo", min_value=0.0)
    prezzo = st.number_input("Prezzo", min_value=0.0)
    extra = st.number_input("Extra (accantonamento informativo)", min_value=0.0)
    acconto = st.number_input("Acconto", min_value=0.0)
    data_vendita = ""  # si aggiorna solo quando finisce di pagare
    note = st.text_input("Note (es: decima_ok)")

    # Calcolo automatico guadagno
    guadagno = prezzo - costo
    st.info(f"Guadagno calcolato automaticamente: € {guadagno:.2f}")

    submit_vendita = st.form_submit_button("Salva vendita")

if submit_vendita:
    supabase_insert("vendite", {
        "cliente": cliente,
        "prodotto": prodotto,
        "costo": costo,
        "prezzo": prezzo,
        "extra": extra,
        "guadagno": guadagno,
        "acconto": acconto,
        "data": data_vendita,
        "note": note
    })

    # Movimento automatico per acconto
    if acconto > 0:
        supabase_insert("movimenti_cassa", {
            "data": "",
            "tipo": "entrata",
            "soggetto": "acconto",
            "importo": acconto,
            "note": f"Acconto vendita {cliente}"
        })

    st.success("Vendita salvata e movimento di cassa registrato!")

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

    # Movimento automatico
    supabase_insert("movimenti_cassa", {
        "data": data_rata,
        "tipo": "entrata",
        "soggetto": "rata",
        "importo": importo_rata,
        "note": f"Rata vendita {lista_vendite[id_vendita]} - {cliente_rata}"
    })

    # Controllo se la vendita è stata completamente pagata
    rate = supabase_select("pagamenti_rate")
    df_rate = pd.DataFrame(rate)
    df_rate_vendita = df_rate[df_rate["id_vendita"] == lista_vendite[id_vendita]]

    totale_rate = df_rate_vendita["importo"].sum()

    vendita_sel = [v for v in vendite if v["id"] == lista_vendite[id_vendita]][0]
    residuo = vendita_sel["prezzo"] - vendita_sel["acconto"] - totale_rate

    if residuo <= 0:
        supabase_update("vendite", lista_vendite[id_vendita], {"data": data_rata})

    st.success("Rata salvata e movimento di cassa registrato!")

# -----------------------------
# SEZIONE 3: INSERIMENTO SPESE
# -----------------------------
st.header("💸 Inserisci una spesa")

with st.form("nuova_spesa"):
    data_spesa = st.text_input("Data spesa")
    categoria = st.text_input("Categoria")
    descrizione = st.text_input("Descrizione")
    importo_spesa = st.number_input("Importo spesa", min_value=0.0)

    submit_spesa = st.form_submit_button("Salva spesa")

if submit_spesa:
    supabase_insert("spese", {
        "data": data_spesa,
        "categoria": categoria,
        "descrizione": descrizione,
        "importo": importo_spesa
    })

    # Movimento automatico
    supabase_insert("movimenti_cassa", {
        "data": data_spesa,
        "tipo": "uscita",
        "soggetto": "spesa",
        "importo": -abs(importo_spesa),
        "note": descrizione
    })

    st.success("Spesa salvata e movimento di cassa registrato!")

# -----------------------------
# SEZIONE 4: VENDITE ANCORA APERTE
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
df["residuo"] = df["prezzo"] - df["acconto"] - df["importo"]

df_aperte = df[df["residuo"] > 0]

st.dataframe(df_aperte[["id", "cliente", "prodotto", "prezzo", "costo", "extra", "acconto", "importo", "residuo"]])

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

    vendita_sel = df_vendite[df_vendite["id"] == id_decima].iloc[0]
    decima_importo = vendita_sel["guadagno"] * 0.10

    # Movimento automatico
    supabase_insert("movimenti_cassa", {
        "data": vendita_sel["data"],
        "tipo": "uscita",
        "soggetto": "decima",
        "importo": -abs(decima_importo),
        "note": f"Decima vendita {id_decima}"
    })

    st.success("Decima segnata e movimento di cassa registrato!")

st.subheader("Decime già date")
st.dataframe(df_decime_ok[["id", "cliente", "guadagno", "decima"]])

# -----------------------------
# SEZIONE 6: MOVIMENTI DI CASSA
# -----------------------------
st.header("💰 Movimenti di cassa")

movimenti = supabase_select("movimenti_cassa")
df_mov = pd.DataFrame(movimenti)

if not df_mov.empty:
    st.dataframe(df_mov[["id", "data", "tipo", "soggetto", "importo", "note"]])
else:
    st.info("Nessun movimento registrato.")

# -----------------------------
# SEZIONE 7: STATISTICHE
# -----------------------------
st.header("📈 Statistiche")

totale_rate = df_rate["importo"].sum() if not df_rate.empty else 0
totale_residuo = df_aperte["residuo"].sum()
totale_spese = df_mov[df_mov["importo"] < 0]["importo"].sum() * -1 if not df_mov.empty else 0
saldo_cassa = df_mov["importo"].sum() if not df_mov.empty else 0

st.metric("Totale rate ricevute", f"€ {totale_rate:,.2f}")
st.metric("Totale residuo vendite", f"€ {totale_residuo:,.2f}")
st.metric("Totale spese", f"€ {totale_spese:,.2f}")
st.metric("Saldo cassa", f"€ {saldo_cassa:,.2f}")
