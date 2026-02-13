import streamlit as st
import pandas as pd
from supabase_utils import supabase_select

st.title("📈 Statistiche generali")

# Carico dati
vendite = pd.DataFrame(supabase_select("vendite"))
rate = pd.DataFrame(supabase_select("pagamenti_rate"))
spese = pd.DataFrame(supabase_select("spese"))
mov = pd.DataFrame(supabase_select("movimenti_cassa"))

# Sezioni vuote → messaggi
if vendite.empty:
    st.info("Nessuna vendita registrata.")
    st.stop()

# Calcoli principali
tot_vendite = vendite["prezzo"].sum()
tot_costo = vendite["costo"].sum()
tot_guadagno = vendite["guadagno"].sum()
tot_extra = vendite["extra"].sum()
tot_acconti = vendite["acconto"].sum()

if not rate.empty:
    tot_rate = rate["importo"].sum()
else:
    tot_rate = 0

if not spese.empty:
    tot_spese = spese["importo"].sum()
else:
    tot_spese = 0

if not mov.empty:
    saldo_cassa = mov["importo"].sum()
else:
    saldo_cassa = 0

# Mostra metriche
st.subheader("📊 Riepilogo generale")

col1, col2, col3 = st.columns(3)
col1.metric("Totale vendite", f"€ {tot_vendite:,.2f}")
col2.metric("Totale costi", f"€ {tot_costo:,.2f}")
col3.metric("Guadagno totale", f"€ {tot_guadagno:,.2f}")

col4, col5, col6 = st.columns(3)
col4.metric("Extra totale", f"€ {tot_extra:,.2f}")
col5.metric("Acconti incassati", f"€ {tot_acconti:,.2f}")
col6.metric("Rate incassate", f"€ {tot_rate:,.2f}")

col7, col8 = st.columns(2)
col7.metric("Spese totali", f"€ {tot_spese:,.2f}")
col8.metric("Saldo cassa", f"€ {saldo_cassa:,.2f}")

# Statistiche aggiuntive
st.subheader("📦 Statistiche vendite")

# Vendite per cliente
vend_per_cliente = vendite.groupby("cliente")["prezzo"].sum().reset_index()
vend_per_cliente = vend_per_cliente.sort_values("prezzo", ascending=False)

st.write("### 💼 Vendite per cliente")
st.dataframe(vend_per_cliente)

# Vendite per prodotto
vend_per_prodotto = vendite.groupby("prodotto")["prezzo"].sum().reset_index()
vend_per_prodotto = vend_per_prodotto.sort_values("prezzo", ascending=False)

st.write("### 📦 Vendite per prodotto")
st.dataframe(vend_per_prodotto)

# Guadagno per prodotto
guad_per_prodotto = vendite.groupby("prodotto")["guadagno"].sum().reset_index()
guad_per_prodotto = guad_per_prodotto.sort_values("guadagno", ascending=False)

st.write("### 💵 Guadagno per prodotto")
st.dataframe(guad_per_prodotto)

# Extra per mese (se data presente)
st.subheader("📅 Extra per mese")

if "data" in vendite.columns and vendite["data"].notna().any():
    vendite["mese"] = vendite["data"].str.slice(0, 7)
    extra_mese = vendite.groupby("mese")["extra"].sum().reset_index()
    st.dataframe(extra_mese)
else:
    st.info("Nessuna data disponibile per calcolare gli extra mensili.")
