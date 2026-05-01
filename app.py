import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CSS: RED HEADER & ULTRA-BLACK TABLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, p, div, label { font-family: 'Inter', sans-serif !important; color: #000000 !important; }
    [data-testid="stIcon"] { font-family: inherit !important; }

    .main-header {
        background: linear-gradient(95deg, #FF4B4B 0%, #C1272D 100%);
        padding: 35px; border-radius: 15px; text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(193, 39, 45, 0.3);
    }
    .main-header h1 { color: #FFFFFF !important; font-weight: 800 !important; font-size: 3.2rem !important; margin: 0 !important; text-transform: uppercase; }
    .main-header p { color: rgba(255, 255, 255, 0.95) !important; font-weight: 500 !important; margin-top: 10px !important; font-size: 1.2rem !important; }

    /* Tables & Inputs: Pure Black and Bold */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th, [role="gridcell"] {
        font-size: 1.2rem !important; color: #000000 !important; font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div, .stTextInput input { font-weight: 700 !important; color: #000000 !important; }
    
    /* Hall of Fame Cards */
    .hof-card {
        background: #fdfdfd; border: 2px solid #000000; border-radius: 10px; padding: 20px;
        text-align: center; box-shadow: 5px 5px 0px #C1272D; margin-bottom: 20px;
    }
    .hof-year { font-size: 1.5rem; font-weight: 800; color: #C1272D; }
    .hof-winner { font-size: 1.3rem; font-weight: 700; color: #000000; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA CONFIGURATION ---
TOURS = {
    "Itzulia Basque Country (5)": {"url": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec", "id": "5"},
    "Volta Ciclista a Catalunya (4)": {"url": "https://script.google.com/macros/s/AKfycbxXHl_6r4aSzKUo7ziahiDp08DiSKRCobOt3Ecu29n71-PnwI1ipRrbgH7GeeHw7NKV/exec", "id": "4"},
    "Ronde van Vlaanderen (3)": {"url": "https://script.google.com/macros/s/AKfycbzbyiCdrp920TkVqvKYIYWR7ovllTbFgqxoYuyPc18yjrv-mK0-EfdPydzln2eiL0N1/exec", "id": "3"},
    "Tirreno - Adriatico (2)": {"url": "https://script.google.com/macros/s/AKfycbwxNaL9swEDBUU3VqOQ4vDgj4BDCVd1-n0QVs4nUCKSzZTtxD54r6pVliV_uqNobzObaA/exec", "id": "2"},
    "Paris-Nice (1)": {"url": "https://script.google.com/macros/s/AKfycbyxixETwMCar087CvsXG6uTiYIUbm9TX9kFKCWzIHOCUURemBR2oVVCB15JU32dFwYY/exec", "id": "1"}
}

# Esempio Dati Hall of Fame (Puoi aggiungere i vincitori reali qui)
HOF_DATA = [
    {"year": "2025", "tour": "Paris-Nice", "winner": "Tadej Pogačar", "team": "UAE Team Emirates", "icon": "🟡"},
    {"year": "2025", "tour": "Tirreno-Adriatico", "winner": "Jonas Vingegaard", "team": "Visma-Lease a Bike", "icon": "🔱"},
    {"year": "2024", "tour": "Tour de France", "winner": "Tadej Pogačar", "team": "UAE Team Emirates", "icon": "🟡"},
]

GITHUB_USER = "PepIndurain"
REPO_NAME = "World-Tour-2026"
BASE_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/"

# --- 3. SUPPORT FUNCTIONS ---
def fetch_data(url, code):
    try:
        response = requests.get(f"{url}?code={code}", timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e: return {"error": str(e)}

def get_jersey_url(val):
    v = str(val).lower()
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
    text_style = 'color: #000000; font-weight: 700;'
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    bg = ""
    if 'yellow' in j: bg = "#FFF2CC"
    elif 'green' in j: bg = "#E2F0D9"
    elif 'polkadot' in j: bg = "#FBE2E2"
    elif 'white' in j: bg = "#F2F2F2"
    
    if bg: return [f'background-color: {bg}; {text_style}'] * len(row)
    return [text_style] * len(row)

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("🏁 Navigation")
page = st.sidebar.radio("Go to", ["Live Dashboard", "🏆 Hall of Fame"])

if page == "Live Dashboard":
    # --- LIVE DASHBOARD LOGIC ---
    if "is_loading" not in st.session_state: st.session_state.is_loading = False
    
    st.sidebar.header("Settings")
    selected_tour_name = st.sidebar.selectbox("Select Tour", list(TOURS.keys()), disabled=st.session_state.is_loading)
    year_code = st.sidebar.text_input("Year", "26", disabled=st.session_state.is_loading)

    if "prev_tour" not in st.session_state or st.session_state.prev_tour != selected_tour_name:
        st.session_state.prev_tour = selected_tour_name
        st.session_state.current_group = "A"
        st.session_state.current_stage = "1"
        st.session_state.is_loading = True

    # Parametri dinamici
    total_groups = st.session_state.get("total_groups", 6)
    total_stages = st.session_state.get("total_stages", 10)
    group_options = list(string.ascii_uppercase)[:total_groups]
    stage_options = [str(i) for i in range(1, total_stages + 1)]

    selected_group = st.sidebar.selectbox("Select Group", group_options, index=group_options.index(st.session_state.current_group) if st.session_state.current_group in group_options else 0)
    selected_stage = st.sidebar.selectbox("Select Stage", stage_options, index=stage_options.index(st.session_state.current_stage) if st.session_state.current_stage in stage_options else 0)

    if st.session_state.is_loading or selected_group != st.session_state.current_group or selected_stage != st.session_state.current_stage:
        st.session_state.current_group = selected_group
        st.session_state.current_stage = selected_stage
        code = f"{year_code}.{TOURS[selected_tour_name]['id']}.{selected_group}.{selected_stage}"
        with st.spinner("Fetching Data..."):
            data = fetch_data(TOURS[selected_tour_name]["url"], code)
            st.session_state.json_data = data
            if data and "error" not in data:
                st.session_state.total_groups = data.get("totalGroups", 6)
                st.session_state.total_stages = data.get("totalStages", 10)
        st.session_state.is_loading = False
        st.rerun()

    # --- DISPLAY LIVE ---
    st.markdown('<div class="main-header"><h1>World Tour Dashboard</h1><p>Pro Cycling Race Management & Results</p></div>', unsafe_allow_html=True)
    data = st.session_state.get("json_data", {})
    
    if "error" in data: st.error(f"Error: {data['error']}")
    elif data:
        st.success(f"📍 Displaying: {selected_tour_name} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
        tabs = st.tabs(["🏁 Stage", "🟡 GC", "🟢 Points", "🔴 KOM", "🔵 TP", "👥 Team", "🚀 Next Grid"])
        
        keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "tpClassification", "teamTimeClassification", "nextStageGrid"]
        map_cols = {"rank": "Rank", "player": "Rider", "team": "Team", "name": "Rider Name", "leaders": "Leaders", "jersey": "Jersey", "teamName": "Team Name"}

        for i, key in enumerate(keys):
            with tabs[i]:
                df = pd.DataFrame(data.get(key, [])).fillna("")
                if not df.empty:
                    if 'jersey' in df.columns:
                        df['jersey_raw'] = df['jersey']
                        df['jersey'] = df['jersey_raw'].apply(get_jersey_url)
                    if 'leaders' in df.columns: df['leaders'] = df['leaders'].apply(get_leader_emojis)
                    df = df.rename(columns=map_cols)
                    st.dataframe(df.style.apply(style_cycling_rows, axis=1), use_container_width=True, hide_index=True, column_config={"Jersey": st.column_config.ImageColumn("Jersey"), "jersey_raw": None})

else:
    # --- HALL OF FAME PAGE ---
    st.markdown('<div class="main-header"><h1>🏆 Hall of Fame</h1><p>The Eternal Wall of Cycling Champions</p></div>', unsafe_allow_html=True)
    
    st.write("### 🥇 Historical Winners")
    
    # Grid of winners
    cols = st.columns(3)
    for idx, entry in enumerate(HOF_DATA):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="hof-card">
                    <div class="hof-year">{entry['year']}</div>
                    <div style="font-size: 2rem;">{entry['icon']}</div>
                    <div class="hof-winner">{entry['winner']}</div>
                    <p><b>Tour:</b> {entry['tour']}<br>
                    <b>Team:</b> {entry['team']}</p>
                </div>
            """, unsafe_allow_html=True)
            
    st.divider()
    st.write("### 📜 Roll of Honor")
    df_hof = pd.DataFrame(HOF_DATA)
    st.dataframe(df_hof, use_container_width=True, hide_index=True)
