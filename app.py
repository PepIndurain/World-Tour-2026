import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CSS: CUSTOM STYLING (PURE BLACK, RED HEADER & FIXED HOF GRID) ---
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

    /* --- HALL OF FAME ALIGNMENT --- */
    .hof-header-grid {
        display: grid;
        grid-template-columns: 100px repeat(4, 1fr); /* Match exactly with hof-row */
        text-align: center;
        margin-bottom: 15px;
        background: #f8f9fa;
        padding: 15px 10px;
        border-radius: 10px;
        align-items: end;
    }
    .hof-header-item {
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.9rem;
    }

    .hof-row {
        display: grid;
        grid-template-columns: 100px repeat(4, 1fr); /* 100px for Group, then 4 equal columns */
        gap: 15px;
        background: #ffffff;
        border: 2px solid #000000;
        border-radius: 12px;
        margin-bottom: 12px;
        padding: 15px 10px;
        align-items: center;
        box-shadow: 4px 4px 0px #eee;
    }
    .group-label {
        font-size: 2.5rem; font-weight: 800; color: #C1272D; text-align: center;
        border-right: 2px solid #eee;
    }
    .jersey-box { 
        text-align: left; 
        padding-left: 10px; 
    }
    .rider-name { font-size: 1.2rem; font-weight: 700; color: #000000; display: block; line-height: 1.2; margin-bottom: 2px; }
    .team-name { font-size: 0.85rem; font-weight: 600; color: #555; text-transform: uppercase; }
    
    /* Tables Style */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.15rem !important; color: #000000 !important; font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION ---
MASTER_URL = "INSERISCI_QUI_IL_TUO_URL_MASTER" # Da riempire con il tuo URL Master

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
page = st.sidebar.radio("Navigate to:", ["Live Dashboard", "🏆 Hall of Fame", "📊 Master Standings"])

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

elif page == "🏆 Hall of Fame":
    st.markdown('<div class="main-header"><h1>🏆 Hall of Fame</h1><p>Final Tour Winners by Group</p></div>', unsafe_allow_html=True)
    sel_tour_hof = st.selectbox("Choose Tour to display FINAL Champions:", list(TOURS.keys()))
    
    if st.button("🔄 Refresh Winners"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data(ttl=600)
    def get_final_winners(tour_name):
        t_info = TOURS[tour_name]
        try:
            meta = requests.get(f"{t_info['url']}?code=26.{t_info['id']}.A.1").json()
            num_groups = meta.get("totalGroups", 1)
            last_stage = meta.get("totalStages", 1)
            results = []
            for lit in list(string.ascii_uppercase)[:num_groups]:
                res = requests.get(f"{t_info['url']}?code=26.{t_info['id']}.{lit}.{last_stage}").json()
                get_t = lambda k: {"name": res[k][0]["name"], "team": res[k][0].get("teamName", res[k][0].get("team", ""))} if res.get(k) else {"name": "No Winner", "team": "-"}
                results.append({"group": lit, "yellow": get_t("generalClassification"), "green": get_t("sprintClassification"), "polkadot": get_t("mountainClassification"), "white": get_t("teamTimeClassification")})
            return results
        except: return []

    with st.spinner("Analyzing Winners..."):
        final_winners = get_final_winners(sel_tour_hof)

    if final_winners:
        # --- FIXED HEADER WITH PERFECT ALIGNMENT ---
        st.markdown(f"""
            <div class="hof-header-grid">
                <div class="hof-header-item">Group</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('yellow')}" width="40"><br>GC</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('green')}" width="40"><br>Points</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('polkadot')}" width="40"><br>KOM</div>
                <div class="hof-header-item"><img src="{get_jersey_icon('white')}" width="40"><br>Team</div>
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
 # --- 📊 MASTER STANDINGS ---
    st.markdown('<div class="main-header"><h1>📊 Master Standings</h1><p>World Tour Global Rankings</p></div>', unsafe_allow_html=True)
    
    # Inserisci il NUOVO URL qui sotto
    # MASTER_URL = "https://script.google.com/macros/s/AKfycbyOTpSNzycmZFrlgJ0tlCkQkKsK1A0TwZlO5uHyybiKyd5qGdBNyAP3xd8VecMgjqrELA/exec"

    if st.button("🔄 Force Refresh Standings"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data(ttl=600)
    def fetch_master():
        try:
            r = requests.get(MASTER_URL, timeout=20)
            return r.json()
        except: return {"error": "Connection error to Master File."}

    master_data = fetch_master()

    if "error" in master_data: 
        st.error(master_data["error"])
    else:
        tr, tt = st.tabs(["👤 Overall Riders Standings", "👥 Overall Teams Standings"])
        
        with tr:
            df_r = pd.DataFrame(master_data.get("ridersMaster", []))
            if not df_r.empty:
                df_r['WTP'] = pd.to_numeric(df_r['WTP'], errors='coerce').round(2)
                st.dataframe(df_r[["Rank", "Player", "Type", "Rider Name", "WTP"]], use_container_width=True, hide_index=True)
            else:
                st.warning("No rider data found.")

        with tt:
            df_t = pd.DataFrame(master_data.get("teamsMaster", []))
            if not df_t.empty:
                df_t['WTP'] = pd.to_numeric(df_t['WTP'], errors='coerce').round(2)
                st.dataframe(df_t[["Rank", "Player", "Team Name", "WTP"]], use_container_width=True, hide_index=True)
            else:
                st.error("Team data not found. Make sure names are in Column Y starting from row 5.")
