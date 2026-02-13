import streamlit as st
import pandas as pd
from supabase_utils import supabase_select

st.title("📈 Statistiche")

# ============================
# FUNZIONE DI CARICAMENTO ROBUSTA
# ============================
def load_table(name):
    data = supabase_select(name)
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

# ============================
# CARICAMENTO TABELLE
# ============================
vendite = load_table("vendite")
rate = load_table("pagamenti_rate")
movimenti = load_table("movimenti_cassa")

# ============================
# NORMALIZZAZIONE TIPI
# ============================
if not movimenti.empty:
    movimenti["importo"] = pd.to_numeric(movimenti["importo"], errors="coerce")
    movimenti["tipo"] = movimenti["tipo"].astype(str)
    movimenti["soggetto"] = movimenti["soggetto"].astype(str)

# ============================
# CALCOLO SPESE (uscite)
# ============================
if not movimenti.empty:
    spese = movimenti[movimenti["tipo"] == "uscita"]
else:
    spese = pd.DataFrame(columns=["data", "importo", "soggetto"])

tot_spese = spese["importo"].sum() if not spese.empty else 0

# ============================
# CALCOLO ENTRATE (rate + acconti)
# ============================
entrate = movimenti[movimenti["tipo"] == "entrata"] if not movimenti.empty else pd.DataFrame()
tot_entrate = entrate["importo"].sum() if not entrate.empty else 0

# ============================
# CALCOLO PROFITTO
# ============================
profitto = tot_entrate - tot_spese

# ============================
# DASHBOARD KPI
# ============================
col1, col2, col3 = st.columns(3)

col1.metric("Totale entrate", f"€ {tot_entrate:,.2f}")
col2.metric("Totale spese", f"€ {tot_spese:,.2f}")
col3.metric("Profitto netto", f"€ {profitto:,.2f}")

# ============================
# DETTAGLIO SPESE
# ============================
st.subheader("💸 Dettaglio spese")

if spese.empty:
    st.info("Nessuna spesa registrata.")
else:
    st.dataframe(spese[["data", "soggetto", "importo", "note"]])

# ============================
# DETTAGLIO ENTRATE
# ============================
st.subheader("💰 Dettaglio entrate")

if entrate.empty:
    st.info("Nessuna entrata registrata.")
else:
    st.dataframe(entrate[["data", "soggetto", "importo", "note"]])
