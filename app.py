import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CSS: CUSTOM STYLING (ULTRA BLACK & RED HEADER) ---
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

    /* Hall of Fame Table Style */
    .hof-row {
        display: grid;
        grid-template-columns: 80px repeat(4, 1fr);
        gap: 10px;
        background: #ffffff;
        border: 2px solid #000000;
        border-radius: 10px;
        margin-bottom: 10px;
        padding: 15px 10px;
        align-items: center;
        box-shadow: 4px 4px 0px #eee;
    }
    .group-label {
        font-size: 2.2rem; font-weight: 800; color: #C1272D; text-align: center;
        border-right: 2px solid #eee;
    }
    .jersey-box { text-align: left; padding-left: 15px; }
    .rider-name { font-size: 1.2rem; font-weight: 700; color: #000000; display: block; line-height: 1.1; margin-bottom: 3px; }
    .team-name { font-size: 0.9rem; font-weight: 500; color: #555; text-transform: uppercase; }
    
    /* Headers for HOF */
    .hof-header-grid {
        display: grid;
        grid-template-columns: 80px repeat(4, 1fr);
        text-align: center; font-weight: 800; margin-bottom: 15px; text-transform: uppercase;
        background: #f8f9fa; padding: 10px; border-radius: 10px;
    }

    /* Dataframe Cells: Pure Black and Bold for PC */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.15rem !important; color: #000000 !important; font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION ---
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
    return f"{BASE_IMAGE_URL}{color}-jersey.png"

def style_rows(row):
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
    st.sidebar.header("Race Settings")
    selected_tour = st.sidebar.selectbox("Select Tour", list(TOURS.keys()))
    
    if "prev_tour" not in st.session_state or st.session_state.prev_tour != selected_tour:
        st.session_state.prev_tour = selected_tour
        st.session_state.current_group, st.session_state.current_stage = "A", "1"
        st.session_state.is_loading = True

    total_g = st.session_state.get("total_groups", 6)
    total_s = st.session_state.get("total_stages", 10)
    
    sel_group = st.sidebar.selectbox("Group", list(string.ascii_uppercase)[:total_g], index=list(string.ascii_uppercase).index(st.session_state.current_group) if st.session_state.current_group in list(string.ascii_uppercase) else 0)
    sel_stage = st.sidebar.selectbox("Stage", [str(i) for i in range(1, total_s + 1)], index=int(st.session_state.current_stage)-1 if int(st.session_state.current_stage) <= total_s else 0)

    if st.session_state.is_loading or sel_group != st.session_state.current_group or sel_stage != st.session_state.current_stage:
        st.session_state.current_group, st.session_state.current_stage = sel_group, sel_stage
        with st.spinner("Fetching Data..."):
            url = f"{TOURS[selected_tour]['url']}?code=26.{TOURS[selected_tour]['id']}.{sel_group}.{sel_stage}"
            data = requests.get(url).json()
            st.session_state.json_data = data
            st.session_state.total_groups = data.get("totalGroups", 6)
            st.session_state.total_stages = data.get("totalStages", 10)
        st.session_state.is_loading = False
        st.rerun()

    st.markdown('<div class="main-header"><h1>World Tour Dashboard</h1></div>', unsafe_allow_html=True)
    d = st.session_state.get("json_data", {})
    if d:
        st.success(f"📍 {selected_tour} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
        tabs = st.tabs(["🏁 Stage", "🟡 GC", "🟢 Points", "🔴 KOM", "👥 Team", "🚀 Next"])
        keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "teamTimeClassification", "nextStageGrid"]
        for i, k in enumerate(keys):
            with tabs[i]:
                df = pd.DataFrame(d.get(k, [])).fillna("")
                if not df.empty:
                    if 'jersey' in df.columns:
                        df['jersey_raw'] = df['jersey']
                        df['jersey'] = df['jersey_raw'].apply(lambda x: get_jersey_icon(x.split('-')[0]) if x else "")
                    st.dataframe(df.style.apply(style_rows, axis=1), use_container_width=True, hide_index=True, column_config={"Jersey": st.column_config.ImageColumn()})

else:
    # --- FINAL WINNERS HALL OF FAME ---
    st.markdown('<div class="main-header"><h1>🏆 Hall of Fame</h1><p>Final Tour Winners by Group</p></div>', unsafe_allow_html=True)
    
    sel_tour_hof = st.selectbox("Choose Tour to display FINAL Champions:", list(TOURS.keys()))
    
    if st.button("🔄 Refresh Winners"):
        st.cache_data.clear()

    @st.cache_data(ttl=600)
    def get_final_winners(tour_name):
        t_info = TOURS[tour_name]
        try:
            meta_req = requests.get(f"{t_info['url']}?code=26.{t_info['id']}.A.1").json()
            num_groups = meta_req.get("totalGroups", 1)
            last_stage = meta_req.get("totalStages", 1)
            
            all_final_results = []
            letters = list(string.ascii_uppercase)[:num_groups]
            
            for lit in letters:
                try:
                    res = requests.get(f"{t_info['url']}?code=26.{t_info['id']}.{lit}.{last_stage}", timeout=15).json()
                    
                    def get_top(key):
                        lst = res.get(key, [])
                        return {"name": lst[0]["name"], "team": lst[0].get("teamName", lst[0].get("team", ""))} if lst else {"name": "N/A", "team": "-"}

                    all_final_results.append({
                        "group": lit, "stage": last_stage,
                        "yellow": get_top("generalClassification"), 
                        "green": get_top("sprintClassification"),
                        "polkadot": get_top("mountainClassification"), 
                        "white": get_top("teamTimeClassification") # CORREZIONE: Maglia Bianca = Teams Time Classification (M81)
                    })
                except: continue
            return all_final_results
        except: return []

    with st.spinner(f"Retrieving final winners for {sel_tour_hof}..."):
        final_winners = get_final_winners(sel_tour_hof)

    if final_winners:
        st.info(f"🏆 Showing results from the final stage (Stage {final_winners[0]['stage']})")
        st.markdown(f"""
            <div class="hof-header-grid">
                <div>Group</div>
                <div><img src="{get_jersey_icon('yellow')}" width="30"><br>Final GC</div>
                <div><img src="{get_jersey_icon('green')}" width="30"><br>Final Points</div>
                <div><img src="{get_jersey_icon('polkadot')}" width="30"><br>Final KOM</div>
                <div><img src="{get_jersey_icon('white')}" width="30"><br>Best Team</div>
            </div>
        """, unsafe_allow_html=True)

        for w in final_winners:
            row_html = f'<div class="hof-row"><div class="group-label">{w["group"]}</div>'
            for col in ["yellow", "green", "polkadot", "white"]:
                row_html += f"""
                <div class="jersey-box">
                    <span class="rider-name">{w[col]['name']}</span>
                    <span class="team-name">{w[col]['team']}</span>
                </div>"""
            row_html += "</div>"
            st.markdown(row_html, unsafe_allow_html=True)
    else:
        st.error("Data not available for the final stage.")import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CSS: CUSTOM STYLING (PURE BLACK & RED HEADER) ---
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

    /* Hall of Fame Table Style */
    .hof-row {
        display: grid;
        grid-template-columns: 80px repeat(4, 1fr);
        gap: 10px;
        background: #ffffff;
        border: 2px solid #000000;
        border-radius: 10px;
        margin-bottom: 10px;
        padding: 15px 10px;
        align-items: center;
        box-shadow: 4px 4px 0px #eee;
    }
    .group-label {
        font-size: 2.2rem; font-weight: 800; color: #C1272D; text-align: center;
        border-right: 2px solid #eee;
    }
    .jersey-box { text-align: left; padding-left: 15px; }
    .rider-name { font-size: 1.2rem; font-weight: 700; color: #000000; display: block; line-height: 1.1; margin-bottom: 3px; }
    .team-name { font-size: 0.9rem; font-weight: 500; color: #555; text-transform: uppercase; }
    
    /* Headers for HOF */
    .hof-header-grid {
        display: grid;
        grid-template-columns: 80px repeat(4, 1fr);
        text-align: center; font-weight: 800; margin-bottom: 15px; text-transform: uppercase;
        background: #f8f9fa; padding: 10px; border-radius: 10px;
    }

    /* Tables Style (Pure Black and Bold) */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.15rem !important; color: #000000 !important; font-weight: 700 !important;
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

BASE_IMAGE_URL = "https://raw.githubusercontent.com/PepIndurain/World-Tour-2026/main/"

# --- 3. HELPER FUNCTIONS ---
def get_jersey_icon(color):
    return f"{BASE_IMAGE_URL}{color}-jersey.png"

def style_rows(row):
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
    st.sidebar.header("Race Settings")
    selected_tour = st.sidebar.selectbox("Select Tour", list(TOURS.keys()))
    
    if "prev_tour" not in st.session_state or st.session_state.prev_tour != selected_tour:
        st.session_state.prev_tour = selected_tour
        st.session_state.current_group, st.session_state.current_stage = "A", "1"
        st.session_state.is_loading = True

    total_g = st.session_state.get("total_groups", 6)
    total_s = st.session_state.get("total_stages", 10)
    
    sel_group = st.sidebar.selectbox("Group", list(string.ascii_uppercase)[:total_g], index=list(string.ascii_uppercase).index(st.session_state.current_group) if st.session_state.current_group in list(string.ascii_uppercase) else 0)
    sel_stage = st.sidebar.selectbox("Stage", [str(i) for i in range(1, total_s + 1)], index=int(st.session_state.current_stage)-1 if int(st.session_state.current_stage) <= total_s else 0)

    if st.session_state.is_loading or sel_group != st.session_state.current_group or sel_stage != st.session_state.current_stage:
        st.session_state.current_group, st.session_state.current_stage = sel_group, sel_stage
        with st.spinner("Fetching Data..."):
            url = f"{TOURS[selected_tour]['url']}?code=26.{TOURS[selected_tour]['id']}.{sel_group}.{sel_stage}"
            data = requests.get(url).json()
            st.session_state.json_data = data
            st.session_state.total_groups = data.get("totalGroups", 6)
            st.session_state.total_stages = data.get("totalStages", 10)
        st.session_state.is_loading = False
        st.rerun()

    st.markdown('<div class="main-header"><h1>World Tour Dashboard</h1></div>', unsafe_allow_html=True)
    d = st.session_state.get("json_data", {})
    if d:
        st.success(f"📍 {selected_tour} | Group {st.session_state.current_group} | Stage {st.session_state.current_stage}")
        tabs = st.tabs(["🏁 Stage", "🟡 GC", "🟢 Points", "🔴 KOM", "👥 Team", "🚀 Next"])
        keys = ["stageResults", "generalClassification", "sprintClassification", "mountainClassification", "teamTimeClassification", "nextStageGrid"]
        for i, k in enumerate(keys):
            with tabs[i]:
                df = pd.DataFrame(d.get(k, [])).fillna("")
                if not df.empty:
                    if 'jersey' in df.columns:
                        df['jersey_raw'] = df['jersey']
                        df['jersey'] = df['jersey_raw'].apply(lambda x: get_jersey_icon(x.split('-')[0]) if x else "")
                    st.dataframe(df.style.apply(style_rows, axis=1), use_container_width=True, hide_index=True, column_config={"Jersey": st.column_config.ImageColumn()})

else:
    # --- FINAL WINNERS HALL OF FAME ---
    st.markdown('<div class="main-header"><h1>🏆 Hall of Fame</h1><p>Final Tour Winners by Group</p></div>', unsafe_allow_html=True)
    
    sel_tour_hof = st.selectbox("Choose Tour to display FINAL Champions:", list(TOURS.keys()))
    
    if st.button("🔄 Refresh Winners"):
        st.cache_data.clear()

    @st.cache_data(ttl=600)
    def get_final_winners(tour_name):
        t_info = TOURS[tour_name]
        try:
            meta_req = requests.get(f"{t_info['url']}?code=26.{t_info['id']}.A.1").json()
            num_groups = meta_req.get("totalGroups", 1)
            last_stage = meta_req.get("totalStages", 1)
            
            all_final_results = []
            letters = list(string.ascii_uppercase)[:num_groups]
            
            for lit in letters:
                try:
                    res = requests.get(f"{t_info['url']}?code=26.{t_info['id']}.{lit}.{last_stage}", timeout=15).json()
                    
                    def get_top(key):
                        lst = res.get(key, [])
                        return {"name": lst[0]["name"], "team": lst[0].get("teamName", lst[0].get("team", ""))} if lst else {"name": "N/A", "team": "-"}

                    all_final_results.append({
                        "group": lit, "stage": last_stage,
                        "yellow": get_top("generalClassification"), 
                        "green": get_top("sprintClassification"),
                        "polkadot": get_top("mountainClassification"), 
                        "white": get_top("teamstimeClassification") # CORREZIONE: Maglia Bianca = Best Team (M81)
                    })
                except: continue
            return all_final_results
        except: return []

    with st.spinner(f"Retrieving final winners for {sel_tour_hof}..."):
        final_winners = get_final_winners(sel_tour_hof)

    if final_winners:
        st.info(f"🏆 Showing results from the final stage (Stage {final_winners[0]['stage']})")
        st.markdown(f"""
            <div class="hof-header-grid">
                <div>Group</div>
                <div><img src="{get_jersey_icon('yellow')}" width="30"><br>Final GC</div>
                <div><img src="{get_jersey_icon('green')}" width="30"><br>Final Points</div>
                <div><img src="{get_jersey_icon('polkadot')}" width="30"><br>Final KOM</div>
                <div><img src="{get_jersey_icon('white')}" width="30"><br>Best Team</div>
            </div>
        """, unsafe_allow_html=True)

        for w in final_winners:
            row_html = f'<div class="hof-row"><div class="group-label">{w["group"]}</div>'
            for col in ["yellow", "green", "polkadot", "white"]:
                row_html += f"""
                <div class="jersey-box">
                    <span class="rider-name">{w[col]['name']}</span>
                    <span class="team-name">{w[col]['team']}</span>
                </div>"""
            row_html += "</div>"
            st.markdown(row_html, unsafe_allow_html=True)
    else:
        st.error("Data not available for the final stage.")
