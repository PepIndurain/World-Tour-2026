import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Pro Hub")

# --- 1. CONFIGURAZIONE DEI TOUR ---
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
nome_tour = st.sidebar.selectbox("Seleziona il Tour", list(TOURS.keys()))
codice_gara = st.sidebar.text_input("Codice Gara (es: 26.5.A.2)", "26.5.A.2")

URL_ATTUALE = TOURS[nome_tour]

if codice_gara:
    with st.spinner(f'Caricamento dati da {nome_tour}...'):
        try:
            response = requests.get(f"{URL_ATTUALE}?code={codice_gara}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.info(f"📍 {data.get('currentCode', '')}")
                
                tabs = st.tabs(["🏁 Tappa", "🟡 Generale", "🟢 Sprint", "🔴 Montagna", "🔵 Punti TP", "👥 Team", "🚀 Griglia"])

                def render_table(key, title, tab_idx):
                    with tabs[tab_idx]:
                        df = pd.DataFrame(data.get(key, []))
                        if not df.empty:
                            if 'jersey' in df.columns:
                                df['jersey_raw'] = df['jersey']
                                df['jersey'] = df['jersey_raw'].apply(get_jersey_url)
                            
                            if 'leaders' in df.columns:
                                df['leaders'] = df['leaders'].apply(get_leader_emojis)
                            
                            styled_df = df.style.apply(style_cycling_rows, axis=1)
                            
                            st.header(title)
                            st.dataframe(
                                styled_df, 
                                use_container_width=True, 
                                hide_index=True,
                                column_config={
                                    "jersey": st.column_config.ImageColumn("Maglia"),
                                    "jersey_raw": None 
                                }
                            )
                
                render_table("stageResults", "Risultati Tappa", 0)
                render_table("generalClassification", "Classifica Generale", 1)
                render_table("sprintClassification", "Classifica Sprint", 2)
                render_table("mountainClassification", "Classifica Montagna", 3)
                render_table("tpClassification", "Classifica Punti TP", 4)
                render_table("teamTimeClassification", "Team Classification", 5)
                render_table("nextStageGrid", "Griglia Prossima Tappa", 6)

        except Exception as e:
            st.error(f"Errore di connessione: {e}")
