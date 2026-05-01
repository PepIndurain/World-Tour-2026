import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CSS: RED HEADER & IMPROVED HOF CARDS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, p, div, label { font-family: 'Inter', sans-serif !important; color: #000000 !important; }
    
    .main-header {
        background: linear-gradient(95deg, #FF4B4B 0%, #C1272D 100%);
        padding: 35px; border-radius: 15px; text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(193, 39, 45, 0.3);
    }
    .main-header h1 { color: #FFFFFF !important; font-weight: 800 !important; font-size: 3.2rem !important; margin: 0 !important; text-transform: uppercase; }

    /* Hall of Fame Multi-Jersey Cards */
    .hof-card {
        background: #ffffff; border: 2px solid #000000; border-radius: 15px; padding: 15px;
        text-align: center; box-shadow: 6px 6px 0px #C1272D; margin-bottom: 20px;
        min-height: 480px;
    }
    .hof-tour-title { 
        font-size: 1.1rem; font-weight: 800; color: #FFFFFF; background: #C1272D;
        margin: -15px -15px 15px -15px; padding: 12px; border-radius: 12px 12px 0 0;
        text-transform: uppercase;
    }
    .leader-row {
        display: flex; align-items: center; text-align: left;
        padding: 10px 0; border-bottom: 1px solid #eee;
    }
    .leader-row:last-child { border-bottom: none; }
    .leader-info { margin-left: 10px; }
    .leader-name { font-size: 1.05rem; font-weight: 800; color: #000000; display: block; }
    .leader-team { font-size: 0.8rem; color: #555; font-weight: 600; }
    
    /* Tables Style */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.1rem !important; color: #000000 !important; font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION ---
TOURS = {
    "Itzulia Basque Country (5)": {"url": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec", "id": "5"},
    "Volta Ciclista a Catalunya (4)": {"url": "https://script.google.com/macros/s/AKfycbxXHl_6a4aSzKUo7ziahiDp08DiSKRCobOt3Ecu29n71-PnwI1ipRrbgH7GeeHw7NKV/exec", "id": "4"},
    "Ronde van Vlaanderen (3)": {"url": "https://script.google.com/macros/s/AKfycbzbyiCdrp920TkVqvKYIYWR7ovllTbFgqxoYuyPc18yjrv-mK0-EfdPydzln2eiL0N1/exec", "id": "3"},
    "Tirreno - Adriatico (2)": {"url": "https://script.google.com/macros/s/AKfycbwxNaL9swEDBUU3VqOQ4vDgj4BDCVd1-n0QVs4nUCKSzZTtxD54r6pVliV_uqNobzObaA/exec", "id": "2"},
    "Paris-Nice (1)": {"url": "https://script.google.com/macros/s/AKfycbyxixETwMCar087CvsXG6uTiYIUbm9TX9kFKCWzIHOCUURemBR2oVVCB15JU32dFwYY/exec", "id": "1"}
}

GITHUB_USER = "PepIndurain"
REPO_NAME = "World-Tour-2026"
BASE_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/"

# --- 3. FUNCTIONS ---
@st.cache_data(ttl=600)
def fetch_all_leaders(tour_name, tour_url, tour_id):
    try:
        response = requests.get(f"{tour_url}?code=26.{tour_id}.A.1", timeout=20)
        data = response.json()
        
        def get_first(key):
            if key in data and len(data[key]) > 0:
                item = data[key][0]
                return {"name": item.get("name", "N/A"), "team": item.get("teamName", item.get("team", "N/A"))}
            return {"name": "No Data", "team": "-"}

        return {
            "tour": tour_name,
            "yellow": get_first("generalClassification"),
            "green": get_first("sprintClassification"),
            "polkadot": get_first("mountainClassification"),
            "white": get_first("tpClassification"), # Usiamo TP Points come maglia bianca/giovani
            "found": True
        }
    except:
        return {"tour": tour_name, "found": False}

def get_jersey_url(color):
    return f"{BASE_IMAGE_URL}{color}-jersey.png"

def style_cycling_rows(row):
    text_style = 'color: #000000; font-weight: 700;'
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    bg = ""
    if 'yellow' in j: bg = "#FFF2CC"
    elif 'green' in j: bg = "#E2F0D9"
    elif 'polkadot' in j: bg = "#FBE2E2"
    elif 'white' in j: bg = "#F2F2F2"
    return [f'background-color: {bg}; {text_style}' if bg else text_style] * len(row)

# --- 4. NAVIGATION ---
st.sidebar.title("🏁 World Tour Menu")
page = st.sidebar.radio("Navigate to:", ["Live Dashboard", "🏆 Hall of Fame"])

if page == "Live Dashboard":
    # --- DASHBOARD CODE (Keep as is) ---
    st.sidebar.header("Race Settings")
    selected_tour = st.sidebar.selectbox("Select Tour", list(TOURS.keys()))
    if "prev_tour" not in st.session_state or st.session_state.prev_tour != selected_tour:
        st.session_state.prev_tour = selected_tour
        st.session_state.current_group, st.session_state.current_stage = "A", "1"
        st.session_state.is_loading = True

    group_opts = list(string.ascii_uppercase)[:st.session_state.get("total_groups", 6)]
    stage_opts = [str(i) for i in range(1, st.session_state.get("total_stages", 10) + 1)]
    
    sel_group = st.sidebar.selectbox("Group", group_opts, index=group_opts.index(st.session_state.current_group) if st.session_state.current_group in group_opts else 0)
    sel_stage = st.sidebar.selectbox("Stage", stage_opts, index=stage_opts.index(st.session_state.current_stage) if st.session_state.current_stage in stage_opts else 0)

    if st.session_state.get("is_loading") or sel_group != st.session_state.current_group or sel_stage != st.session_state.current_stage:
        st.session_state.current_group, st.session_state.current_stage = sel_group, sel_stage
        with st.spinner("Loading..."):
            code = f"26.{TOURS[selected_tour]['id']}.{sel_group}.{sel_stage}"
            data = requests.get(f"{TOURS[selected_tour]['url']}?code={code}").json()
            st.session_state.json_data = data
            st.session_state.total_groups = data.get("totalGroups", 6)
            st.session_state.total_stages = data.get("totalStages", 10)
        st.session_state.is_loading = False
        st.rerun()

    st.markdown('<div class="main-header"><h1>World Tour Dashboard</h1></div>', unsafe_allow_html=True)
    data = st.session_state.get("json_data", {})
    if data:
        tabs = st.tabs(["🏁 Stage", "🟡 GC", "🟢 Points", "🔴 KOM", "👥 Team", "🚀 Next"])
        keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "teamTimeClassification", "nextStageGrid"]
        for i, k in enumerate(keys):
            with tabs[i]:
                df = pd.DataFrame(data.get(k, [])).fillna("")
                if not df.empty:
                    if 'jersey' in df.columns:
                        df['jersey_raw'] = df['jersey']
                        df['jersey'] = df['jersey_raw'].apply(lambda x: get_jersey_url(x.split('-')[0]) if x else "")
                    st.dataframe(df.style.apply(style_cycling_rows, axis=1), use_container_width=True, hide_index=True, column_config={"Jersey": st.column_config.ImageColumn()})

else:
    # --- ENHANCED HALL OF FAME ---
    st.markdown('<div class="main-header"><h1>🏆 Hall of Fame</h1><p>The 4 Leaders of Every Classic</p></div>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    winners = []
    with st.spinner("Fetching all jerseys..."):
        for name, info in TOURS.items():
            winners.append(fetch_all_leaders(name, info["url"], info["id"]))

    cols = st.columns(5)
    jerseys = [
        ("yellow", "General (GC)"),
        ("green", "Points"),
        ("polkadot", "Mountains"),
        ("white", "TP Points")
    ]

    for idx, w in enumerate(winners):
        with cols[idx]:
            if w["found"]:
                html = f'<div class="hof-card"><div class="hof-tour-title">{w["tour"]}</div>'
                for j_color, j_label in jerseys:
                    html += f"""
                    <div class="leader-row">
                        <img src="{get_jersey_url(j_color)}" width="45">
                        <div class="leader-info">
                            <span class="leader-name">{w[j_color]['name']}</span>
                            <span class="leader-team">{w[j_color]['team']}</span>
                        </div>
                    </div>"""
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="hof-card"><div class="hof-tour-title">{w["tour"]}</div><p>Connection Error</p></div>', unsafe_allow_html=True)
