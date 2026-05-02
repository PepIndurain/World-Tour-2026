import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CSS: CUSTOM STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, p, div, label { font-family: 'Inter', sans-serif !important; color: #000000 !important; }
    
    .main-header {
        background: linear-gradient(95deg, #FF4B4B 0%, #C1272D 100%);
        padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(193, 39, 45, 0.2);
    }
    .main-header h1 { color: #FFFFFF !important; font-weight: 800 !important; font-size: 2.8rem !important; margin: 0 !important; text-transform: uppercase; }

    /* Tables Style (Pure Black and Bold) */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.15rem !important; color: #000000 !important; font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION & COLUMN MAPPING ---
BASE_COLUMN_MAP = {
    "rank": "Rank", "trend": "Trend", "player": "Rider", "team": "Team",
    "jersey": "Jersey", "type": "Type", "name": "Rider Name",
    "leaders": "Leaders", "bonusWtp": "Bonus WTP", "teamName": "Team Name",
    "currentWtp": "Current WTP", "e2": "Energy"
}

TOURS = {
    "Itzulia Basque Country (5)": {"url": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec", "id": "5"},
    "Volta Ciclista a Catalunya (4)": {"url": "https://script.google.com/macros/s/AKfycbxXHl_6r4aSzKUo7ziahiDp08DiSKRCobOt3Ecu29n71-PnwI1ipRrbgH7GeeHw7NKV/exec", "id": "4"},
    "Ronde van Vlaanderen (3)": {"url": "https://script.google.com/macros/s/AKfycbzbyiCdrp920TkVqvKYIYWR7ovllTbFgqxoYuyPc18yjrv-mK0-EfdPydzln2eiL0N1/exec", "id": "3"},
    "Tirreno - Adriatico (2)": {"url": "https://script.google.com/macros/s/AKfycbwxNaL9swEDBUU3VqOQ4vDgj4BDCVd1-n0QVs4nUCKSzZTtxD54r6pVliV_uqNobzObaA/exec", "id": "2"},
    "Paris-Nice (1)": {"url": "https://script.google.com/macros/s/AKfycbyxixETwMCar087CvsXG6uTiYIUbm9TX9kFKCWzIHOCUURemBR2oVVCB15JU32dFwYY/exec", "id": "1"}
}

MASTER_URL = "https://script.google.com/macros/s/AKfycbyOTpSNzycmZFrlgJ0tlCkQkKsK1A0TwZlO5uHyybiKyd5qGdBNyAP3xd8VecMgjqrELA/exec"
BASE_IMAGE_URL = "https://raw.githubusercontent.com/PepIndurain/World-Tour-2026/main/"

# --- 3. HELPER FUNCTIONS ---
def get_jersey_icon(color):
    if not color or str(color).lower() in ["none", ""]: return ""
    return f"{BASE_IMAGE_URL}{color.split('-')[0].lower()}-jersey.png"

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

def style_rows(row):
    text_style = 'color: #000000; font-weight: 700;'
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else str(row.get('Jersey', '')).lower()
    bg = ""
    if 'yellow' in j: bg = "#FFF2CC"
    elif 'green' in j: bg = "#E2F0D9"
    elif 'polkadot' in j: bg = "#FBE2E2"
    elif 'white' in j: bg = "#F2F2F2"
    return [f'background-color: {bg}; {text_style}' if bg else text_style] * len(row)

# --- 4. NAVIGATION ---
st.sidebar.title("🏁 World Tour Menu")
page = st.sidebar.radio("Navigate to:", ["Live Dashboard", "🏆 Hall of Fame", "📊 Master Standings"])

if page == "Live Dashboard":
    st.sidebar.header("Race Settings")
    selected_tour = st.sidebar.selectbox("Select Tour", list(TOURS.keys()))
    if "prev_tour" not in st.session_state or st.session_state.prev_tour != selected_tour:
        st.session_state.prev_tour = selected_tour
        st.session_state.current_group, st.session_state.current_stage = "A", "1"
        st.session_state.is_loading = True
    
    total_g, total_s = st.session_state.get("total_groups", 6), st.session_state.get("total_stages", 10)
    sel_group = st.sidebar.selectbox("Group", list(string.ascii_uppercase)[:total_g], index=list(string.ascii_uppercase).index(st.session_state.current_group) if st.session_state.current_group in list(string.ascii_uppercase) else 0)
    sel_stage = st.sidebar.selectbox("Stage", [str(i) for i in range(1, total_s + 1)], index=int(st.session_state.current_stage)-1 if int(st.session_state.current_stage) <= total_s else 0)

    if st.session_state.is_loading or sel_group != st.session_state.current_group or sel_stage != st.session_state.current_stage:
        st.session_state.current_group, st.session_state.current_stage = sel_group, sel_stage
        with st.spinner("Fetching Data..."):
            url = f"{TOURS[selected_tour]['url']}?code=26.{TOURS[selected_tour]['id']}.{sel_group}.{sel_stage}"
            data = requests.get(url).json()
            st.session_state.json_data, st.session_state.total_groups, st.session_state.total_stages = data, data.get("totalGroups", 6), data.get("totalStages", 10)
        st.session_state.is_loading = False
        st.rerun()

    st.markdown('<div class="main-header"><h1>World Tour Dashboard</h1></div>', unsafe_allow_html=True)
    d = st.session_state.get("json_data", {})
    if d:
        st.success(f"📍 {selected_tour} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
        
        # AGGIUNTO IL TAB "🏆 Team TP"
        tabs = st.tabs(["🏁 Stage", "🟡 GC", "🟢 Points", "🔴 KOM", "🔵 TP", "👥 Team GC", "🏆 Team TP", "🚀 Next Stage Grid"])
        
        # AGGIUNTA LA CHIAVE "teamTpClassification"
        keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "tpClassification", "teamTimeClassification", "teamTpClassification", "nextStageGrid"]
        
        for i, k in enumerate(keys):
            with tabs[i]:
                df = pd.DataFrame(d.get(k, [])).fillna("")
                if not df.empty:
                    if 'leaders' in df.columns: df['leaders'] = df['leaders'].apply(get_leader_emojis)
                    if 'jersey' in df.columns:
                        df['jersey_raw'] = df['jersey']
                        df['jersey'] = df['jersey_raw'].apply(get_jersey_icon)
                    
                    # Mapping dinamico
                    current_map = BASE_COLUMN_MAP.copy()
                    if k == "generalClassification":
                        current_map["stagePts"] = "Stage GC Time"
                        current_map["tourPts"] = "Tour Time"
                    elif k in ["sprintClassification", "mountainClassification"]:
                        current_map["stagePts"] = "Stage Pts"
                        current_map["tourPts"] = "Total Pts"
                    elif k == "nextStageGrid":
                        current_map["grid"] = "Next Stage Grid"
                    
                    df = df.rename(columns=current_map)
                    st.dataframe(df.style.apply(style_rows, axis=1), use_container_width=True, hide_index=True, column_config={"Jersey": st.column_config.ImageColumn("Jersey"), "jersey_raw": None})
                else:
                    st.warning(f"No data available for {k}")

elif page == "🏆 Hall of Fame":
    # (Codice Hall of Fame invariato...)
    pass

else:
    # (Codice Master Standings invariato...)
    pass
