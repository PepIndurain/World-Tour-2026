import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CSS: CUSTOM STYLING (PURE BLACK, RED HEADER & AUTO-SCALING HOF) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Global text */
    html, body, p, div, label { 
        font-family: 'Inter', sans-serif !important; 
        color: #000000 !important; 
    }
    
    /* Header Rosso */
    .main-header {
        background: linear-gradient(95deg, #FF4B4B 0%, #C1272D 100%);
        padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(193, 39, 45, 0.2);
    }
    .main-header h1 { color: #FFFFFF !important; font-weight: 800 !important; font-size: 2.8rem !important; margin: 0 !important; text-transform: uppercase; }

    /* Cursore a manina */
    div[data-baseweb="select"], div[data-baseweb="select"] > div, li[role="option"], 
    [data-testid="stSidebar"] label, [data-testid="stWidgetLabel"], button[data-baseweb="tab"] {
        cursor: pointer !important;
    }

    /* Stile Tabelle Live & Master */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.15rem !important; color: #000000 !important; font-weight: 700 !important;
    }

    /* --- HALL OF FAME: FULLY RESPONSIVE NO-SCROLL --- */
    .hof-container {
        width: 100%;
        margin-top: 10px;
    }
    
    .hof-header-grid {
        display: grid; 
        grid-template-columns: 50px repeat(4, 1fr); /* Colonna gruppo stretta */
        text-align: center; 
        background: #f1f3f5;
        padding: 10px 5px; 
        border-radius: 10px 10px 0 0;
        align-items: end;
        border-bottom: 2px solid #000000;
    }
    .hof-header-item { font-weight: 800; text-transform: uppercase; font-size: 0.8rem; color: #000000; }
    .header-jersey { width: 35px; margin-bottom: 5px; }

    .hof-row {
        display: grid; 
        grid-template-columns: 50px repeat(4, 1fr); 
        background: #ffffff;
        padding: 12px 5px;
        align-items: center;
        border-bottom: 1px solid #dee2e6;
    }

    .group-label { font-size: 1.8rem; font-weight: 800; color: #C1272D; text-align: center; }
    
    .jersey-box { 
        text-align: left; 
        padding: 0 8px;
        border-left: 1px solid #f0f0f0;
        word-wrap: break-word; /* Forza il testo ad andare a capo */
        overflow-wrap: break-word;
    }
    .rider-name { font-size: 1rem; font-weight: 700; color: #000000; display: block; line-height: 1.1; }
    .team-name { font-size: 0.75rem; font-weight: 600; color: #666; text-transform: uppercase; }

    /* --- MEDIA QUERY PER SMARTPHONE: RIDUZIONE CARATTERI --- */
    @media (max-width: 768px) {
        .hof-header-item { font-size: 0.6rem !important; }
        .header-jersey { width: 25px !important; }
        .group-label { font-size: 1.3rem !important; }
        .rider-name { font-size: 0.75rem !important; }
        .team-name { font-size: 0.6rem !important; }
        .jersey-box { padding: 0 4px !important; }
        .hof-row { padding: 8px 2px !important; }
    }

    /* Fix Icons */
    [data-testid="stIcon"] { font-family: inherit !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION & MAPPING ---
MASTER_URL = "https://script.google.com/macros/s/AKfycbyOTpSNzycmZFrlgJ0tlCkQkKsK1A0TwZlO5uHyybiKyd5qGdBNyAP3xd8VecMgjqrELA/exec"

BASE_COLUMN_MAP = {
    "rank": "Rank", "trend": "Trend", "player": "Rider", "team": "Team",
    "jersey": "Jersey", "type": "Type", "name": "Rider Name",
    "leaders": "Leaders", "bonusWtp": "Bonus WTP", "teamName": "Team Name",
    "currentWtp": "Current WTP", "e2": "Energy", "stageTime": "Stage Time", 
    "wtp": "WTP", "bonusSeconds": "Bonus (s)", "stageTimes": "Stage Time", "tourTimes": "Total Time"
}

TOURS = {
    "Itzulia Basque Country (5)": {"url": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec", "id": "5"},
    "Volta Ciclista a Catalunya (4)": {"url": "https://script.google.com/macros/s/AKfycbxXHl_6r4aSzKUo7ziahiDp08DiSKRCobOt3Ecu29n71-PnwI1ipRrbgH7GeeHw7NKV/exec", "id": "4"},
    "Ronde van Vlaanderen (3)": {"url": "https://script.google.com/macros/s/AKfycbzbyiCdrp920TkVqvKYIYWR7ovllTbFgqxoYuyPc18yjrv-mK0-EfdPydzln2eiL0N1/exec", "id": "3"},
    "Tirreno - Adriatico (2)": {"url": "https://script.google.com/macros/s/AKfycbwxNaL9swEDBUU3VqOQ4vDgj4BDCVd1-n0QVs4nUCKSzZTtxD54r6pVliV_uqNobzObaA/exec", "id": "2"},
    "Paris-Nice (1)": {"url": "https://script.google.com/macros/s/AKfycbyxixETwMCar087CvsXG6uTiYIUbm9TX9kFKCWzIHOCUURemBR2oVVCB15JU32dFwYY/exec", "id": "1"}
}

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
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else (str(row.get('Jersey', '')).lower() if 'Jersey' in row else '')
    bg = ""
    if 'yellow' in j: bg = "#FFF2CC"
    elif 'green' in j: bg = "#E2F0D9"
    elif 'polkadot' in j: bg = "#FBE2E2"
    elif 'white' in j: bg = "#F2F2F2"
    return [f'background-color: {bg}; {text_style}' if bg else text_style] * len(row)

def trigger_loading():
    st.session_state.is_loading = True

# --- 4. SESSION STATE ---
if "is_loading" not in st.session_state: st.session_state.is_loading = False
if "current_group" not in st.session_state: st.session_state.current_group = "A"
if "current_stage" not in st.session_state: st.session_state.current_stage = "1"
if "json_data" not in st.session_state: st.session_state.json_data = {}

# --- 5. NAVIGATION ---
st.sidebar.title("🏁 World Tour Menu")
page = st.sidebar.radio("Navigate to:", ["Live Dashboard", "🏆 Hall of Fame", "📊 Master Standings"], disabled=st.session_state.is_loading)

if page == "Live Dashboard":
    st.sidebar.header("Race Settings")
    selected_tour = st.sidebar.selectbox("Select Tour", list(TOURS.keys()), disabled=st.session_state.is_loading, on_change=trigger_loading)
    
    if "prev_tour" not in st.session_state or st.session_state.prev_tour != selected_tour:
        st.session_state.prev_tour = selected_tour
        st.session_state.current_group, st.session_state.current_stage = "A", "1"
        st.session_state.is_loading = True

    total_g, total_s = st.session_state.get("total_groups", 6), st.session_state.get("total_stages", 10)
    g_list, s_list = list(string.ascii_uppercase)[:total_g], [str(i) for i in range(1, total_s + 1)]

    sel_group = st.sidebar.selectbox("Group", g_list, index=g_list.index(st.session_state.current_group) if st.session_state.current_group in g_list else 0, disabled=st.session_state.is_loading, on_change=trigger_loading)
    sel_stage = st.sidebar.selectbox("Stage", s_list, index=s_list.index(st.session_state.current_stage) if st.session_state.current_stage in s_list else 0, disabled=st.session_state.is_loading, on_change=trigger_loading)

    if st.session_state.is_loading:
        st.session_state.current_group, st.session_state.current_stage = sel_group, sel_stage
        with st.spinner("Fetching Data..."):
            try:
                url = f"{TOURS[selected_tour]['url']}?code=26.{TOURS[selected_tour]['id']}.{sel_group}.{sel_stage}"
                res = requests.get(url, timeout=15).json()
                st.session_state.json_data = res
                st.session_state.total_groups, st.session_state.total_stages = res.get("totalGroups", 6), res.get("totalStages", 10)
            except: st.error("Connection Error")
        st.session_state.is_loading = False
        st.rerun()

    st.markdown('<div class="main-header"><h1>World Tour Dashboard</h1></div>', unsafe_allow_html=True)
    d = st.session_state.get("json_data", {})
    if d:
        st.success(f"📍 {selected_tour} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
        tabs = st.tabs(["🏁 Stage", "🟡 GC", "🟢 Points", "🔴 KOM", "🔵 TP", "👥 Team GC", "🏆 Team TP", "🚀 Next Stage Grid"])
        keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "tpClassification", "teamTimeClassification", "teamTPClassification", "nextStageGrid"]
        for i, k in enumerate(keys):
            with tabs[i]:
                df = pd.DataFrame(d.get(k, [])).fillna("")
                if not df.empty:
                    if 'leaders' in df.columns: df['leaders'] = df['leaders'].apply(get_leader_emojis)
                    if 'jersey' in df.columns:
                        df['jersey_raw'] = df['jersey']
                        df['jersey'] = df['jersey_raw'].apply(get_jersey_icon)
                    cur_map = BASE_COLUMN_MAP.copy()
                    if k == "generalClassification": cur_map["stagePts"], cur_map["tourPts"] = "Stage GC Time", "Tour Time"
                    elif k in ["sprintClassification", "mountainClassification"]: cur_map["stagePts"], cur_map["tourPts"] = "Stage Pts", "Total Pts"
                    elif k == "nextStageGrid": cur_map["grid"] = "Next Stage Grid"
                    df = df.rename(columns=cur_map)
                    st.dataframe(df.style.apply(style_rows, axis=1), use_container_width=True, hide_index=True, column_config={"Jersey": st.column_config.ImageColumn("Jersey"), "jersey_raw": None})

elif page == "🏆 Hall of Fame":
    st.markdown('<div class="main-header"><h1>🏆 Hall of Fame</h1><p>Final Tour Winners by Group</p></div>', unsafe_allow_html=True)
    sel_hof = st.selectbox("Choose Tour:", list(TOURS.keys()))
    
    @st.cache_data(ttl=600)
    def get_hof(t_name):
        t = TOURS[t_name]
        try:
            m = requests.get(f"{t['url']}?code=26.{t['id']}.A.1", timeout=15).json()
            res = []
            for lit in list(string.ascii_uppercase)[:m.get("totalGroups", 1)]:
                r = requests.get(f"{t['url']}?code=26.{t['id']}.{lit}.{m.get('totalStages', 1)}", timeout=15).json()
                def gt(k): return {"name": r[k][0]["name"], "team": r[k][0].get("teamName", r[k][0].get("team", ""))} if r.get(k) and len(r[k])>0 else {"name": "N/A", "team": "-"}
                res.append({"group": lit, "yellow": gt("generalClassification"), "green": gt("sprintClassification"), "polkadot": gt("mountainClassification"), "white": gt("teamTimeClassification")})
            return res
        except: return []

    winners = get_hof(sel_hof)
    if winners:
        st.markdown('<div class="hof-container">', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="hof-header-grid">
                <div class="hof-header-item">Group</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('yellow')}" class="header-jersey"><br>GC Leader</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('green')}" class="header-jersey"><br>Points</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('polkadot')}" class="header-jersey"><br>KOM</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('white')}" class="header-jersey"><br>Best Team</div>
            </div>
        """, unsafe_allow_html=True)
        for w in winners:
            html = f'<div class="hof-row"><div class="group-label">{w["group"]}</div>'
            for k in ["yellow", "green", "polkadot", "white"]:
                html += f"""<div class="jersey-box">
                    <span class="rider-name">{w[k]['name']}</span>
                    <span class="team-name">{w[k]['team']}</span>
                </div>"""
            st.markdown(html + "</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="main-header"><h1>📊 Overall Standings</h1></div>', unsafe_allow_html=True)
    if st.button("🔄 Refresh Master"): st.cache_data.clear()
    m_data = requests.get(MASTER_URL).json()
    tr, tt = st.tabs(["👤 Riders", "👥 Teams"])
    with tr:
        df_r = pd.DataFrame(m_data.get("ridersMaster", []))
        if not df_r.empty:
            df_r['WTP'] = pd.to_numeric(df_r['WTP'], errors='coerce').round(2)
            st.dataframe(df_r[["Rank", "Player", "Type", "Rider Name", "WTP"]], use_container_width=True, hide_index=True)
    with tt:
        df_t = pd.DataFrame(m_data.get("teamsMaster", []))
        if not df_t.empty:
            df_t['WTP'] = pd.to_numeric(df_t['WTP'], errors='coerce').round(2)
            st.dataframe(df_t[["Rank", "Player", "Team Name", "WTP"]], use_container_width=True, hide_index=True)
