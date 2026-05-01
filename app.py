import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Pro Hub")

# --- 1. TOUR CONFIGURATION (ID and URLs) ---
# Qui ho inserito i tuoi URL e associato l'ID (5 per Itzulia, 4 per Volta)
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
        "url": "https://script.google.com/macros/s/AKfycbzbyiCdrp920TkVqvKYIYWR7ovllTbFgqxoYuyPc18yjrv-mK0-EfdPydzln2eiL0N1/exec",
        "id": "3"
    },   
}

# --- 2. GITHUB IMAGES CONFIGURATION ---
GITHUB_USER = "PepIndurain"
REPO_NAME = "World-Tour-2026"
BASE_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/"

# --- DICTIONARY FOR COLUMN TRANSLATION ---
COLUMN_MAP = {
    "rank": "Rank", "trend": "Trend", "player": "Rider", "team": "Team",
    "jersey": "Jersey", "type": "Type", "name": "Rider Name",
    "bonusSeconds": "Bonus (s)", "stageTime": "Stage Time", "wtp": "WTP",
    "leaders": "Leaders", "stagePts": "Stage Pts", "tourPts": "Total Pts",
    "bonusWtp": "Bonus WTP", "currentWtp": "Current WTP", "stageTimes": "Stage Time",
    "tourTimes": "Total Time", "grid": "Start Pos", "teamName": "Team Name", "e2": "Energy"
}

# --- SUPPORT FUNCTIONS ---
def get_jersey_url(val):
    v = str(val).lower()
    if not v or v in ['none', 'nan', '']: return ""
    if 'yellow' in v: return f"{BASE_IMAGE_URL}yellow-jersey.png"
    if 'green' in v: return f"{BASE_IMAGE_URL}green-jersey.png"
    if 'polkadot' in v: return f"{BASE_IMAGE_URL}polkadot-jersey.png"
    if 'white' in v: return f"{BASE_IMAGE_URL}white-jersey.png"
    return ""

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

# --- INTERFACE ---
st.title("🚴 World Tour Cycling Dashboard")

st.sidebar.header("Settings")

# 1. Selezione Tour
selected_tour_name = st.sidebar.selectbox("Select Tour", list(TOURS.keys()))

# 2. Selezione Parametri temporali e logistici
st.sidebar.subheader("Race Selection")
year_code = st.sidebar.text_input("Year (e.g., 26)", "26")
tour_id = TOURS[selected_tour_name]["id"] # Prende l'ID in automatico (4 o 5)
gruppo = st.sidebar.selectbox("Select Group", ["A", "B", "C", "D", "E", "F"])
tappa = st.sidebar.selectbox("Select Stage", [str(i) for i in range(1, 11)])

# Composizione automatica del codice: [Anno].[TourID].[Gruppo].[Tappa]
codice_finale = f"{year_code}.{tour_id}.{gruppo}.{tappa}"
st.sidebar.info(f"**Race Code:** `{codice_finale}`")

# Recuperiamo l'URL specifico per il Tour selezionato
URL_ATTUALE = TOURS[selected_tour_name]["url"]

with st.spinner(f'Loading {selected_tour_name}...'):
    try:
        response = requests.get(f"{URL_ATTUALE}?code={codice_finale}")
        data = response.json()

        if "error" in data:
            st.error(f"Data not available: {data['error']}")
        else:
            st.info(f"📍 Stage: {data.get('currentCode', '')}")
            
            tabs = st.tabs([
                "🏁 Stage Results", "🟡 General (GC)", "🟢 Points", 
                "🔴 Mountain", "🔵 TP Points", "👥 Teams", "🚀 Next Grid"
            ])

            def render_table(key, title, tab_idx):
                with tabs[tab_idx]:
                    df = pd.DataFrame(data.get(key, []))
                    if not df.empty:
                        df = df.fillna("")
                        if 'jersey' in df.columns:
                            df['jersey_raw'] = df['jersey']
                            df['jersey'] = df['jersey_raw'].apply(get_jersey_url)
                        if 'leaders' in df.columns:
                            df['leaders'] = df['leaders'].apply(get_leader_emojis)
                        
                        df = df.rename(columns=COLUMN_MAP)
                        styled_df = df.style.apply(style_cycling_rows, axis=1)
                        
                        st.header(title)
                        st.dataframe(
                            styled_df, use_container_width=True, hide_index=True,
                            column_config={"Jersey": st.column_config.ImageColumn("Jersey"), "jersey_raw": None}
                        )
            
            render_table("stageResults", "Stage Classification", 0)
            render_table("generalClassification", "General Classification (GC)", 1)
            render_table("sprintClassification", "Points Classification", 2)
            render_table("mountainClassification", "Mountains Classification (KOM)", 3)
            render_table("tpClassification", "TP Points Classification", 4)
            render_table("teamTimeClassification", "Team Classification", 5)
            render_table("nextStageGrid", "Next Stage Starting Grid", 6)

    except Exception as e:
        st.error(f"Connection Error: {e}")
