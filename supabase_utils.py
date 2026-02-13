import streamlit as st
import requests

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def supabase_select(table):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    r = requests.get(url, headers=HEADERS)
    try:
        return r.json()
    except:
        st.error(f"Errore Supabase: {r.text}")
        return []

def supabase_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data)
    try:
        return r.json()
    except:
        st.error(f"Errore Supabase: {r.text}")
        return None

def supabase_update(table, row_id, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}"
    r = requests.patch(url, headers=HEADERS, json=data)
    try:
        return r.json()
    except:
        st.error(f"Errore Supabase: {r.text}")
        return None
