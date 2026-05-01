import streamlit as st
import requests
import pandas as pd
import string

st.set_page_config(layout="wide", page_title="Cycling Pro Hub")

# --- 1. CONFIGURAZIONE TOUR ---
TOURS = {
    "Itzulia Basque Country (5)": {
        "url": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec",
        "id": "5"
    },
    "Volta Ciclista a Catalunya (4)": {
        "url": "https://script.google.com/macros/s/AKfycbxXHl_6r4aSzKUo7ziahiDp08DiSKRCobOt3Ecu29n71-PnwI1ipRrbgH7GeeHw7NKV/exec",
        "id": "4"
    },
    "Ronde van Vlaanderen (3)": {
        "url": "https://script.google.com/macros/s/AKfycbbyiCdrp920TkVqvKYIYWR7ovllTbFgqxoYuyPc18yjrv-mK0-EfdPydzln2eiL0N1/exec",
        "id": "3"
    },   
    "Tirreno - Adriatico (2)": {
        "url": "https://script.google.com/macros/s/AKfycbwxNaL9swEDBUU3VqOQ4vDgj4BDCVd1-n0QVs4nUCKSzZTtxD54r6pVliV_uqNobzObaA/exec",
        "id": "2"
    },
    "Paris-Nice (1)": {
        "url": "https://script.google.com/macros/s/AKfycbyxixETwMCar087CvsXG6uTiYIUbm9TX9kFKCWzIHOCUURemBR2oVVCB15JU32dFwYY/exec",
        "id": "1"
    },
}

COLUMN_MAP = {
    "rank": "Rank", "trend": "Trend", "player": "Rider", "team": "Team",
    "jersey": "Jersey", "type": "Type", "name": "Rider Name",
    "bonusSeconds": "Bonus (s)", "stageTime": "Stage Time", "wtp": "WTP",
    "leaders": "Leaders", "stagePts": "Stage Pts", "tourPts": "Total Pts",
    "bonusWtp": "Bonus WTP", "currentWtp": "Current WTP", "stageTimes": "Stage Time",
    "tourTimes": "Total Time", "grid": "Start Pos", "teamName": "Team Name", "e2": "Energy"
}

BASE_IMAGE_URL = "https://raw.githubusercontent.com/PepIndurain/World-Tour-2026/main/"

# --- FUNZIONI DI SUPPORTO ---
def get_jersey_url(val):
    v = str(val).lower()
    if not v or v in ['none', 'nan', '']: return ""
    jerseys = {'yellow': 'yellow-jersey.png', 'green': 'green-jersey.png', 
               'polkadot': 'polkadot-jersey.png', 'white': 'white-jersey.png'}
    for k, img in jerseys.items():
        if k in v: return f"{BASE_IMAGE_URL}{img}"
    return ""

def get_leader_emojis(val):
    mapping = {'yellow': "🟡", 'green': "🟢", 'polkadot': "🔴", 'white': "⚪"}
    if isinstance(val, list):
        return " ".join([mapping.get(c.lower(), "") for c in val])
    return mapping.get(str(val).lower(), "")

def style_cycling_rows(row):
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    colors = {'yellow': '#FFF2CC', 'green': '#E2F0D9', 'polkadot': '#FBE2E2', 'white': '#F2F2F2'}
    for k, color in colors.items():
        if k in j: return [f'background-color: {color}'] * len(row)
    return [''] * len(row)

# --- LOGICA DI CARICAMENTO DATI ---
@st.cache_data(show_spinner=False)
def fetch_data(url, code):
    try:
        response = requests.get(f"{url}?code={code}", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- INTERFACCIA ---
st.title("🚴 World Tour Cycling Dashboard")

# Sidebar - Tournament Selection
st.sidebar.header("Settings")
selected_tour_name = st.sidebar.selectbox("Select Tour", list(TOURS.keys()), index=0)

# Inizializziamo parametri di default se non esistono
if "year" not in st.session_state: st.session_state.year = "26"
if "current_group_idx" not in st.session_state: st.session_state.current_group_idx = 0
if "current_stage_idx" not in st.session_state: st.session_state.current_stage_idx = 0

# Parametri Tour Corrente
tour_info = TOURS[selected_tour_name]
tour_url = tour_info["url"]
tour_id = tour_info["id"]
year_code = st.sidebar.text_input("Year", value=st.session_state.year)

# Mappatura Gruppi (A, B, C...)
alphabet = list(string.ascii_uppercase)

# --- PRIMA CHIAMATA (Per ottenere i metadati se non li abbiamo) ---
# Usiamo un codice temporaneo o quello in session_state per capire i limiti (totalGroups/totalStages)
temp_group = alphabet[st.session_state.current_group_idx]
temp_stage = st.session_state.current_stage_idx + 1
initial_code = f"{year_code}.{tour_id}.{temp_group}.{temp_stage}"

data = fetch_data(tour_url, initial_code)

if "error" in data:
    st.error(f"Errore nel caricamento: {data['error']}")
else:
    # --- POPOLAMENTO DINAMICO DEI MENU ---
    total_groups = data.get("totalGroups", 1)
    total_stages = data.get("totalStages", 1)
    
    st.sidebar.subheader("Race Selection")
    
    # Selettore Gruppo
    group_options = alphabet[:total_groups]
    selected_group = st.sidebar.selectbox(
        "Select Group", 
        group_options, 
        index=min(st.session_state.current_group_idx, total_groups-1)
    )
    
    # Selettore Tappa
    stage_options = [i for i in range(1, total_stages + 1)]
    selected_stage = st.sidebar.selectbox(
        "Select Stage", 
        stage_options, 
        index=min(st.session_state.current_stage_idx, total_stages-1)
    )

    # Aggiorniamo session_state per mantenere la memoria
    st.session_state.current_group_idx = group_options.index(selected_group)
    st.session_state.current_stage_idx = stage_options.index(selected_stage)
    
    # Costruiamo il codice finale dopo la selezione dell'utente
    final_code = f"{year_code}.{tour_id}.{selected_group}.{selected_stage}"
    
    # Se il codice finale è diverso da quello iniziale, rifacciamo la chiamata
    if final_code != initial_code:
        data = fetch_data(tour_url, final_code)

    # --- VISUALIZZAZIONE DATI ---
    st.sidebar.info(f"**Race Code:** `{final_code}`")
    st.info(f"📍 Location: **{data.get('currentCode', 'N/A')}**")

    tabs = st.tabs([
        "🏁 Stage Results", "🟡 General (GC)", "🟢 Points", 
        "🔴 Mountain", "🔵 TP Points", "👥 Teams", "🚀 Next Grid"
    ])

    keys = [
        ("stageResults", "Stage Classification"),
        ("generalClassification", "General Classification"),
        ("sprintClassification", "Points Classification"),
        ("mountainClassification", "Mountains Classification"),
        ("tpClassification", "TP Points Classification"),
        ("teamTimeClassification", "Team Classification"),
        ("nextStageGrid", "Next Stage Starting Grid")
    ]

    for i, (key, title) in enumerate(keys):
        with tabs[i]:
            df = pd.DataFrame(data.get(key, []))
            if not df.empty:
                df = df.fillna("")
                if 'jersey' in df.columns:
                    df['jersey_raw'] = df['jersey']
                    df['jersey'] = df['jersey_raw'].apply(get_jersey_url)
                if 'leaders' in df.columns:
                    df['leaders'] = df['leaders'].apply(get_leader_emojis)
                
                df = df.rename(columns=COLUMN_MAP)
                # Rimuoviamo colonne non necessarie alla vista ma usate per lo stile
                styled_df = df.style.apply(style_cycling_rows, axis=1)
                
                st.header(title)
                st.dataframe(
                    styled_df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Jersey": st.column_config.ImageColumn("Jersey", width="small"),
                        "jersey_raw": None # Nasconde la colonna di supporto
                    }
                )
            else:
                st.write("No data available for this category.")
