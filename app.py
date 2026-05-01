import streamlit as st
import requests
import pandas as pd
import string

st.set_page_config(layout="wide", page_title="Cycling Pro Hub") 

# --- 0. CUSTOM CSS PER TESTO PIÙ NERO E DEFINITO ---
st.markdown("""
    <style>
    /* Testo generale e etichette dei widget */
    html, body, [data-testid="stWidgetLabel"] p, .st-ae {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Titoli */
    h1, h2, h3 {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Testo all'interno dei widget (selectbox, input) */
    .stSelectbox div[data-baseweb="select"] > div {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Testo della Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fb;
    }
    [data-testid="stSidebar"] .st-expanderHeader, [data-testid="stSidebar"] label p {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Celle delle tabelle/DataFrame */
    [data-testid="stTable"] td, [data-testid="stDataFrame"] td {
        color: #000000 !important;
    }
    
    /* Testo informativo (st.info, st.success) */
    .stAlert p {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. TOUR CONFIGURATION ---
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
    "Tirreno - Adriatico (2)": {
        "url": "https://script.google.com/macros/s/AKfycbwxNaL9swEDBUU3VqOQ4vDgj4BDCVd1-n0QVs4nUCKSzZTtxD54r6pVliV_uqNobzObaA/exec",
        "id": "2"
    },
    "Paris-Nice (1)": {
        "url": "https://script.google.com/macros/s/AKfycbyxixETwMCar087CvsXG6uTiYIUbm9TX9kFKCWzIHOCUURemBR2oVVCB15JU32dFwYY/exec",
        "id": "1"
    },
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

# --- SESSION STATE INITIALIZATION ---
if "prev_tour" not in st.session_state: st.session_state.prev_tour = None
if "current_group" not in st.session_state: st.session_state.current_group = "A"
if "current_stage" not in st.session_state: st.session_state.current_stage = "1"
if "total_groups" not in st.session_state: st.session_state.total_groups = 6
if "total_stages" not in st.session_state: st.session_state.total_stages = 3
if "json_data" not in st.session_state: st.session_state.json_data = {}
if "is_loading" not in st.session_state: st.session_state.is_loading = False

# --- INTERFACE ---
st.title("🚴 World Tour Cycling Dashboard")
st.sidebar.header("Settings")

# Selezione Tour
selected_tour_name = st.sidebar.selectbox(
    "Select Tour", 
    list(TOURS.keys()), 
    disabled=st.session_state.is_loading,
    on_change=trigger_loading
)
year_code = st.sidebar.text_input("Year (e.g., 26)", "26", disabled=st.session_state.is_loading)

tour_id = TOURS[selected_tour_name]["id"]
url_attuale = TOURS[selected_tour_name]["url"]

if st.session_state.prev_tour != selected_tour_name:
    st.session_state.prev_tour = selected_tour_name
    st.session_state.current_group = "A"
    st.session_state.current_stage = "1"
    st.session_state.is_loading = True

group_options = list(string.ascii_uppercase)[:st.session_state.total_groups]
stage_options = [str(i) for i in range(1, st.session_state.total_stages + 1)]

if st.session_state.current_group not in group_options: st.session_state.current_group = group_options[0]
if st.session_state.current_stage not in stage_options: st.session_state.current_stage = stage_options[0]

st.sidebar.subheader("Race Selection")

selected_group = st.sidebar.selectbox(
    "Select Group", 
    group_options, 
    index=group_options.index(st.session_state.current_group),
    disabled=st.session_state.is_loading,
    on_change=trigger_loading,
    key="group_box"
)

selected_stage = st.sidebar.selectbox(
    "Select Stage", 
    stage_options, 
    index=stage_options.index(st.session_state.current_stage),
    disabled=st.session_state.is_loading,
    on_change=trigger_loading,
    key="stage_box"
)

if selected_group != st.session_state.current_group or selected_stage != st.session_state.current_stage:
    st.session_state.is_loading = True

# --- LOGICA DI FETCHING ---
if st.session_state.is_loading:
    st.session_state.current_group = selected_group
    st.session_state.current_stage = selected_stage
    
    codice_call = f"{year_code}.{tour_id}.{selected_group}.{selected_stage}"
    
    # Messaggio descrittivo durante il caricamento
    msg = f"Fetching: {selected_tour_name} - Group {selected_group}, Stage {selected_stage}..."
    
    with st.spinner(msg):
        data = fetch_data(url_attuale, codice_call)
        st.session_state.json_data = data
        if "error" not in data:
            st.session_state.total_groups = data.get("totalGroups", 6)
            st.session_state.total_stages = data.get("totalStages", 10)
    
    st.session_state.is_loading = False
    st.rerun()

# --- RENDER DEI DATI ---
data = st.session_state.json_data

if "error" in data:
    st.error(f"Data not available: {data['error']}")
elif not data:
    st.warning("No data loaded. Please try again.")
else:
    st.success(f"📍 {selected_tour_name} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
    
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
            else:
                st.warning(f"No data available for {title}")
    
    render_table("stageResults", "Stage Classification", 0)
    render_table("generalClassification", "General Classification (GC)", 1)
    render_table("sprintClassification", "Points Classification", 2)
    render_table("mountainClassification", "Mountains Classification (KOM)", 3)
    render_table("tpClassification", "TP Points Classification", 4)
    render_table("teamTimeClassification", "Team Classification", 5)
    render_table("nextStageGrid", "Next Stage Starting Grid", 6)
