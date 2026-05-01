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

    /* Tables: Pure Black and Bold */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th, [role="gridcell"] {
        font-size: 1.2rem !important; color: #000000 !important; font-weight: 600 !important;
    }
    
    /* Hall of Fame Cards */
    .hof-card {
        background: #ffffff; border: 3px solid #000000; border-radius: 15px; padding: 20px;
        text-align: center; box-shadow: 8px 8px 0px #C1272D; margin-bottom: 25px;
        min-height: 350px; display: flex; flex-direction: column; justify-content: center;
    }
    .hof-tour-name { font-size: 1.1rem; font-weight: 800; color: #C1272D; text-transform: uppercase; margin-bottom: 10px; }
    .hof-winner-name { font-size: 1.6rem; font-weight: 800; color: #000000; margin: 15px 0; border-top: 1px solid #eee; padding-top: 10px; }
    .hof-team { font-size: 1rem; font-weight: 600; color: #555; }
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
@st.cache_data(ttl=600) # Cache per 10 minuti per non rallentare l'app
def fetch_winner(tour_name, tour_url, tour_id, year="26"):
    try:
        # Per trovare il vincitore finale, proviamo a recuperare l'ultima tappa possibile
        # Nota: Qui scarichiamo i dati della tappa corrente per ottenere il leader GC attuale
        response = requests.get(f"{tour_url}?code={year}.{tour_id}.A.1", timeout=10)
        data = response.json()
        if "generalClassification" in data and len(data["generalClassification"]) > 0:
            winner = data["generalClassification"][0] # Il primo in classifica GC
            return {
                "tour": tour_name,
                "winner": winner.get("name", "N/A"),
                "team": winner.get("teamName", winner.get("team", "N/A")),
                "time": winner.get("tourTimes", "")
            }
    except:
        return None
    return None

def get_jersey_url(val):
    v = str(val).lower()
    if 'yellow' in v: return f"{BASE_IMAGE_URL}yellow-jersey.png"
    if 'green' in v: return f"{BASE_IMAGE_URL}green-jersey.png"
    if 'polkadot' in v: return f"{BASE_IMAGE_URL}polkadot-jersey.png"
    if 'white' in v: return f"{BASE_IMAGE_URL}white-jersey.png"
    return ""

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
    # --- DASHBOARD LOGIC (Il tuo codice precedente) ---
    st.sidebar.divider()
    st.sidebar.header("Race Settings")
    selected_tour = st.sidebar.selectbox("Select Tour", list(TOURS.keys()))
    year_code = st.sidebar.text_input("Year", "26")
    
    if "prev_tour" not in st.session_state or st.session_state.prev_tour != selected_tour:
        st.session_state.prev_tour = selected_tour
        st.session_state.current_group, st.session_state.current_stage = "A", "1"
        st.session_state.is_loading = True

    # Dinamici
    total_groups = st.session_state.get("total_groups", 6)
    total_stages = st.session_state.get("total_stages", 10)
    group_opts = list(string.ascii_uppercase)[:total_groups]
    stage_opts = [str(i) for i in range(1, total_stages + 1)]

    sel_group = st.sidebar.selectbox("Group", group_opts, index=group_opts.index(st.session_state.current_group) if st.session_state.current_group in group_opts else 0)
    sel_stage = st.sidebar.selectbox("Stage", stage_opts, index=stage_opts.index(st.session_state.current_stage) if st.session_state.current_stage in stage_opts else 0)

    if st.session_state.get("is_loading") or sel_group != st.session_state.current_group or sel_stage != st.session_state.current_stage:
        st.session_state.current_group, st.session_state.current_stage = sel_group, sel_stage
        with st.spinner("Loading Race Data..."):
            code = f"{year_code}.{TOURS[selected_tour]['id']}.{sel_group}.{sel_stage}"
            data = requests.get(f"{TOURS[selected_tour]['url']}?code={code}").json()
            st.session_state.json_data = data
            if "totalGroups" in data:
                st.session_state.total_groups = data["totalGroups"]
                st.session_state.total_stages = data["totalStages"]
        st.session_state.is_loading = False
        st.rerun()

    st.markdown('<div class="main-header"><h1>World Tour Dashboard</h1><p>Pro Cycling Race Results</p></div>', unsafe_allow_html=True)
    data = st.session_state.get("json_data", {})
    if data:
        st.success(f"📍 {selected_tour} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
        tabs = st.tabs(["🏁 Stage", "🟡 GC", "🟢 Points", "🔴 KOM", "👥 Team", "🚀 Next"])
        keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "teamTimeClassification", "nextStageGrid"]
        for i, k in enumerate(keys):
            with tabs[i]:
                df = pd.DataFrame(data.get(k, [])).fillna("")
                if not df.empty:
                    if 'jersey' in df.columns:
                        df['jersey_raw'] = df['jersey']
                        df['jersey'] = df['jersey_raw'].apply(get_jersey_url)
                    st.dataframe(df.style.apply(style_cycling_rows, axis=1), use_container_width=True, hide_index=True, column_config={"Jersey": st.column_config.ImageColumn()})

else:
    # --- HALL OF FAME (AUTOMATICA) ---
    st.markdown('<div class="main-header"><h1>🏆 Hall of Fame</h1><p>The 5 Great Classics Leaders</p></div>', unsafe_allow_html=True)
    
    with st.spinner("Analyzing Tour History..."):
        winners = []
        for name, info in TOURS.items():
            res = fetch_winner(name, info["url"], info["id"])
            if res: winners.append(res)
    
    if winners:
        cols = st.columns(len(winners))
        for idx, w in enumerate(winners):
            with cols[idx]:
                st.markdown(f"""
                    <div class="hof-card">
                        <div class="hof-tour-name">{w['tour']}</div>
                        <img src="{BASE_IMAGE_URL}yellow-jersey.png" width="80" style="margin: auto;">
                        <div class="hof-winner-name">{w['winner']}</div>
                        <div class="hof-team">{w['team']}</div>
                        <div style="margin-top:15px; font-size:0.9rem; color:#C1272D; font-weight:800;">
                            ⏱️ {w['time']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.write("### 📜 Summary Roll of Honor")
        st.table(pd.DataFrame(winners))
    else:
        st.warning("No winner data found. Make sure the races have started!")
