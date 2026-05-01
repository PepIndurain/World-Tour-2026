import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CLEANER CSS: TARGETED BOLD FOR INPUTS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global text: Pure black, Inter font, weight 400 */
    html, body, p, div:not([data-testid="stIcon"]), label, h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        color: #000000 !important;
        font-weight: 400 !important;
    }

    /* Restore Streamlit Icons font */
    [data-testid="stIcon"] {
        font-family: inherit !important;
    }

    /* Titles: Semi-bold (600) */
    h1, h2, h3 { 
        font-weight: 600 !important; 
        letter-spacing: -0.02em;
    }

    /* --- SPECIFIC FOR INPUT FIELDS (Year, Tour, etc.) --- */
    /* Text inside Selectbox */
    div[data-baseweb="select"] > div {
        font-weight: 600 !important;
        color: #000000 !important;
    }
    
    /* Text inside Text Input (the "26" field) */
    .stTextInput input {
        font-weight: 600 !important;
        color: #000000 !important;
    }

    /* TABLES: Large font */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.15rem !important; 
        color: #000000 !important;
        font-weight: 400 !important;
    }

    /* Sidebar Labels */
    [data-testid="stWidgetLabel"] p {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Tab headers */
    button[data-baseweb="tab"] p {
        font-weight: 500 !important;
        font-size: 1rem !important;
    }

    button[aria-selected="true"] p {
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TOUR CONFIGURATION ---
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

COLUMN_MAP = {
    "rank": "Rank", "trend": "Trend", "player": "Rider", "team": "Team",
    "jersey": "Jersey", "type": "Type", "name": "Rider Name",
    "bonusSeconds": "Bonus (s)", "stageTime": "Stage Time", "wtp": "WTP",
    "leaders": "Leaders", "stagePts": "Stage Pts", "tourPts": "Total Pts",
    "bonusWtp": "Bonus WTP", "currentWtp": "Current WTP", "stageTimes": "Stage Time",
    "tourTimes": "Total Time", "grid": "Start Pos", "teamName": "Team Name", "e2": "Energy"
}

GITHUB_USER = "PepIndurain"
REPO_NAME = "World-Tour-2026"
BASE_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/"

# --- 3. SUPPORT FUNCTIONS ---
def fetch_data(url, code):
    try:
        response = requests.get(f"{url}?code={code}", timeout=15)
        response.raise_for_status()
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        else:
            return {"error": "Server error (Non-JSON)"}
    except Exception as e:
        return {"error": str(e)}

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

def trigger_loading():
    st.session_state.is_loading = True

# --- 4. SESSION STATE ---
if "prev_tour" not in st.session_state: st.session_state.prev_tour = None
if "current_group" not in st.session_state: st.session_state.current_group = "A"
if "current_stage" not in st.session_state: st.session_state.current_stage = "1"
if "total_groups" not in st.session_state: st.session_state.total_groups = 6
if "total_stages" not in st.session_state: st.session_state.total_stages = 3
if "json_data" not in st.session_state: st.session_state.json_data = {}
if "is_loading" not in st.session_state: st.session_state.is_loading = False

# --- 5. SIDEBAR ---
st.sidebar.header("Settings")
selected_tour_name = st.sidebar.selectbox(
    "Select Tour", list(TOURS.keys()), 
    disabled=st.session_state.is_loading, on_change=trigger_loading
)
year_code = st.sidebar.text_input("Year", "26", disabled=st.session_state.is_loading)

tour_id = TOURS[selected_tour_name]["id"]
url_attuale = TOURS[selected_tour_name]["url"]

if st.session_state.prev_tour != selected_tour_name:
    st.session_state.prev_tour = selected_tour_name
    st.session_state.is_loading = True

group_options = list(string.ascii_uppercase)[:st.session_state.total_groups]
stage_options = [str(i) for i in range(1, st.session_state.total_stages + 1)]

selected_group = st.sidebar.selectbox(
    "Select Group", group_options, 
    index=group_options.index(st.session_state.current_group) if st.session_state.current_group in group_options else 0,
    disabled=st.session_state.is_loading, on_change=trigger_loading
)
selected_stage = st.sidebar.selectbox(
    "Select Stage", stage_options, 
    index=stage_options.index(st.session_state.current_stage) if st.session_state.current_stage in stage_options else 0,
    disabled=st.session_state.is_loading, on_change=trigger_loading
)

# --- 6. DATA FETCHING LOGIC ---
if st.session_state.is_loading or (selected_group != st.session_state.current_group or selected_stage != st.session_state.current_stage):
    st.session_state.current_group = selected_group
    st.session_state.current_stage = selected_stage
    
    codice_call = f"{year_code}.{tour_id}.{selected_group}.{selected_stage}"
    msg_loading = f"Fetching: {selected_tour_name} | Group {selected_group} | Stage {selected_stage}..."
    
    with st.spinner(msg_loading):
        data = fetch_data(url_attuale, codice_call)
        st.session_state.json_data = data
        if data and "error" not in data:
            st.session_state.total_groups = data.get("totalGroups", 6)
            st.session_state.total_stages = data.get("totalStages", 10)
    
    st.session_state.is_loading = False
    st.rerun()

# --- 7. MAIN INTERFACE ---
st.title("World Tour Dashboard")
data = st.session_state.json_data

if "error" in data:
    st.error(f"⚠️ Error: {data['error']}")
elif data:
    st.success(f"📍 Displaying: {selected_tour_name} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
    
    tabs = st.tabs(["🏁 Stage Results", "🟡 GC", "🟢 Points", "🔴 KOM", "🔵 TP Points", "👥 Team GC", "🚀 Next Grid"])

    def render_table(key, tab_idx):
        with tabs[tab_idx]:
            raw_data = data.get(key, [])
            if raw_data:
                df = pd.DataFrame(raw_data).fillna("")
                if 'jersey' in df.columns:
                    df['jersey_raw'] = df['jersey']
                    df['jersey'] = df['jersey_raw'].apply(get_jersey_url)
                if 'leaders' in df.columns:
                    df['leaders'] = df['leaders'].apply(get_leader_emojis)
                
                df = df.rename(columns=COLUMN_MAP)
                
                st.dataframe(
                    df.style.apply(style_cycling_rows, axis=1), 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={"Jersey": st.column_config.ImageColumn("Jersey"), "jersey_raw": None}
                )
            else:
                st.warning("No data available.")

    classifiche = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "tpClassification", "teamTimeClassification", "nextStageGrid"]
    for i, chiave in enumerate(classifiche):
        render_table(chiave, i)
