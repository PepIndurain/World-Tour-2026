import streamlit as st
import requests
import pandas as pd
import string

st.set_page_config(layout="wide", page_title="Cycling Pro Hub") 

# --- CSS AGGRESSIVO PER LEGGIBILITÀ E CONTRASTO ---
st.markdown("""
    <style>
    /* 1. Importazione font ad alta leggibilità */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* 2. Applicazione font e colore nero assoluto ovunque */
    html, body, [class*="st-"], div, p, span, label {
        font-family: 'Inter', sans-serif !important;
        color: #000000 !important;
        font-size: 1.02rem;
    }

    /* 3. Titoli giganti e neri */
    h1 { font-size: 3rem !important; font-weight: 800 !important; color: #000000 !important; }
    h2 { font-size: 2rem !important; font-weight: 700 !important; color: #000000 !important; }
    h3 { font-size: 1.5rem !important; font-weight: 700 !important; color: #000000 !important; }

    /* 4. Widget della Sidebar (Label e Testo) */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        color: #000000 !important;
    }
    
    /* 5. Selectbox e Input (testo interno più nero e visibile) */
    div[data-baseweb="select"] > div {
        font-weight: 600 !important;
        color: #000000 !important;
        border-color: #000000 !important;
    }
    
    /* 6. Tabelle (Header e Celle) */
    [data-testid="stDataFrame"] {
        border: 1px solid #000000;
    }
    
    /* 7. Tabs (Rendi i titoli dei tab neri e spessi) */
    button[data-baseweb="tab"] p {
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        color: #000000 !important;
    }

    /* 8. Alert e Spinner */
    .stAlert p, .stSpinner div {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAZIONE TOUR ---
TOURS = {
    "Basque Country (5)": {"url": "https://script.google.com/macros/s/AKfycbQ...", "id": "5"},
    "Catalunya (4)": {"url": "https://script.google.com/macros/s/AKfyc...", "id": "4"},
    "Vlaanderen (3)": {"url": "https://script.google.com/macros/s/AKfy...", "id": "3"},
    "Tirreno (2)": {"url": "https://script.google.com/macros/s/AKfy...", "id": "2"},
    "Paris-Nice (1)": {"url": "https://script.google.com/macros/s/AKfy...", "id": "1"}
}

# --- GITHUB IMAGES & MAPPING ---
GITHUB_USER = "PepIndurain"
REPO_NAME = "World-Tour-2026"
BASE_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/"

COLUMN_MAP = {
    "rank": "Rank", "trend": "Trend", "player": "Rider", "team": "Team",
    "jersey": "Jersey", "type": "Type", "name": "Rider Name",
    "bonusSeconds": "Bonus (s)", "stageTime": "Stage Time", "wtp": "WTP",
    "leaders": "Leaders", "stagePts": "Stage Pts", "tourPts": "Total Pts",
    "bonusWtp": "Bonus WTP", "currentWtp": "Current WTP", "stageTimes": "Stage Time",
    "tourTimes": "Total Time", "grid": "Start Pos", "teamName": "Team Name", "e2": "Energy"
}

# --- FUNZIONI DI SUPPORTO ---
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
    return ""

def style_cycling_rows(row):
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    if 'yellow' in j: return ['background-color: #FFF2CC'] * len(row)
    if 'green' in j: return ['background-color: #E2F0D9'] * len(row)
    if 'polkadot' in j: return ['background-color: #FBE2E2'] * len(row)
    if 'white' in j: return ['background-color: #F2F2F2'] * len(row)
    return [''] * len(row)

def fetch_data(url, code):
    try:
        response = requests.get(f"{url}?code={code}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def trigger_loading():
    st.session_state.is_loading = True

# --- SESSION STATE ---
if "prev_tour" not in st.session_state: st.session_state.prev_tour = None
if "current_group" not in st.session_state: st.session_state.current_group = "A"
if "current_stage" not in st.session_state: st.session_state.current_stage = "1"
if "total_groups" not in st.session_state: st.session_state.total_groups = 6
if "total_stages" not in st.session_state: st.session_state.total_stages = 3
if "json_data" not in st.session_state: st.session_state.json_data = {}
if "is_loading" not in st.session_state: st.session_state.is_loading = False

# --- SIDEBAR ---
st.sidebar.header("Settings")
selected_tour_name = st.sidebar.selectbox(
    "Select Tour", list(TOURS.keys()), 
    disabled=st.session_state.is_loading, on_change=trigger_loading
)
year_code = st.sidebar.text_input("Year (e.g., 26)", "26", disabled=st.session_state.is_loading)

tour_id = TOURS[selected_tour_name]["id"]
url_attuale = TOURS[selected_tour_name]["url"]

if st.session_state.prev_tour != selected_tour_name:
    st.session_state.prev_tour = selected_tour_name
    st.session_state.is_loading = True

group_options = list(string.ascii_uppercase)[:st.session_state.total_groups]
stage_options = [str(i) for i in range(1, st.session_state.total_stages + 1)]

selected_group = st.sidebar.selectbox(
    "Select Group", group_options, index=group_options.index(st.session_state.current_group) if st.session_state.current_group in group_options else 0,
    disabled=st.session_state.is_loading, on_change=trigger_loading
)
selected_stage = st.sidebar.selectbox(
    "Select Stage", stage_options, index=stage_options.index(st.session_state.current_stage) if st.session_state.current_stage in stage_options else 0,
    disabled=st.session_state.is_loading, on_change=trigger_loading
)

# --- LOGICA FETCH ---
if st.session_state.is_loading or (selected_group != st.session_state.current_group or selected_stage != st.session_state.current_stage):
    st.session_state.current_group = selected_group
    st.session_state.current_stage = selected_stage
    
    codice_call = f"{year_code}.{tour_id}.{selected_group}.{selected_stage}"
    msg = f"FETCHING: {selected_tour_name} | Group {selected_group} | Stage {selected_stage}"
    
    with st.spinner(msg):
        data = fetch_data(url_attuale, codice_call)
        st.session_state.json_data = data
        if "error" not in data:
            st.session_state.total_groups = data.get("totalGroups", 6)
            st.session_state.total_stages = data.get("totalStages", 10)
    
    st.session_state.is_loading = False
    st.rerun()

# --- MAIN CONTENT ---
st.title("🚴 World Tour Cycling Hub")
data = st.session_state.json_data

if "error" in data:
    st.error(f"Error: {data['error']}")
elif data:
    st.info(f"📍 MOSTRANDO: {selected_tour_name} - Gruppo {st.session_state.current_group} - Tappa {st.session_state.current_stage}")
    
    tabs = st.tabs(["🏁 Tappa", "🟡 GC", "🟢 Punti", "🔴 KOM", "🔵 TP", "👥 Team", "🚀 Griglia"])

    def render_table(key, tab_idx):
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
                st.dataframe(df.style.apply(style_cycling_rows, axis=1), 
                             use_container_width=True, hide_index=True,
                             column_config={"Jersey": st.column_config.ImageColumn("Jersey"), "jersey_raw": None})
            else:
                st.warning("Dati non disponibili")

    keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "tpClassification", "teamTimeClassification", "nextStageGrid"]
    for i, k in enumerate(keys): render_table(k, i)
