import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Pro Hub")

# --- 1. CONFIGURAZIONE DEI TOUR (Aggiungi qui i link degli altri file) ---
TOURS = {
    "Itzulia Basque Country": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec",
    "Volta Ciclista (Esempio)": "INSERISCI_QUI_URL_VOLTA_QUANDO_PRONTO",
}

# --- 2. CONFIGURAZIONE IMMAGINI GITHUB ---
GITHUB_USER = "PepIndurain"
REPO_NAME = "World-Tour-2026"
BASE_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/"

# --- FUNZIONI DI SUPPORTO ---
def get_jersey_url(val):
    v = str(val).lower()
    if 'yellow' in v: return f"{BASE_IMAGE_URL}yellow-jersey.png"
    if 'green' in v: return f"{BASE_IMAGE_URL}green-jersey.png"
    if 'polkadot' in v: return f"{BASE_IMAGE_URL}polkadot-jersey.png"
    if 'white' in v: return f"{BASE_IMAGE_URL}white-jersey.png"
    return None

def get_leader_emojis(val):
    if isinstance(val, list):
        emojis = []
        for color in val:
            c = str(color).lower()
            if 'yellow' in c: emojis.append("🟡")
            elif 'green' in c: emojis.append("🟢")
            elif 'polkadot' in c: emojis.append("🔴")
            elif 'white' in c: emojis.append("⚪")
        return " ".join(emojis)
    else:
        c = str(val).lower()
        if 'yellow' in c: return "🟡"
        if 'green' in c: return "🟢"
        if 'polkadot' in c: return "🔴"
        if 'white' in c: return "⚪"
    return ""

def style_cycling_rows(row):
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    if 'yellow' in j: return ['background-color: #FFF2CC'] * len(row)
    if 'green' in j: return ['background-color: #E2F0D9'] * len(row)
    if 'polkadot' in j: return ['background-color: #FBE2E2'] * len(row)
    if 'white' in j: return ['background-color: #F2F2F2'] * len(row)
    return [''] * len(row)

# --- INTERFACCIA ---
st.title("🚴 World Tour Cycling Dashboard")

st.sidebar.header("Impostazioni")
# Ripristino del menu dei Tour
nome_tour = st.sidebar.selectbox("Seleziona il Tour", list(TOURS.keys()))
# Input del codice
codice_gara = st.sidebar.text_input("Codice Gara (es: 26.5.A.2)", "26.5.A.2")

URL_ATTUALE = TOURS[nome_tour]

if codice_gara:
    with st.spinner(f'Caricamento dati da {nome_tour}...'):
        try:
            response = requests.get(f"{URL_ATTUALE}?code={codice_gara}")
            dat
