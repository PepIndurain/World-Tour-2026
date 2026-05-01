import streamlit as st
import requests
import pandas as pd
import string

# Page Configuration
st.set_page_config(layout="wide", page_title="World Tour Dashboard") 

# --- 1. CONFIGURATION ---
# INCOLLA QUI L'URL CHE HAI OTTENUTO DAL FILE MASTER
MASTER_URL = "https://script.google.com/macros/s/AKfycbyOTpSNzycmZFrlgJ0tlCkQkKsK1A0TwZlO5uHyybiKyd5qGdBNyAP3xd8VecMgjqrELA/exec" 

TOURS = {
    "Itzulia Basque Country (5)": {"url": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec", "id": "5"},
    "Volta Ciclista a Catalunya (4)": {"url": "https://script.google.com/macros/s/AKfycbxXHl_6a4aSzKUo7ziahiDp08DiSKRCobOt3Ecu29n71-PnwI1ipRrbgH7GeeHw7NKV/exec", "id": "4"},
    "Ronde van Vlaanderen (3)": {"url": "https://script.google.com/macros/s/AKfycbzbyiCdrp920TkVqvKYIYWR7ovllTbFgqxoYuyPc18yjrv-mK0-EfdPydzln2eiL0N1/exec", "id": "3"},
    "Tirreno - Adriatico (2)": {"url": "https://script.google.com/macros/s/AKfycbwxNaL9swEDBUU3VqOQ4vDgj4BDCVd1-n0QVs4nUCKSzZTtxD54r6pVliV_uqNobzObaA/exec", "id": "2"},
    "Paris-Nice (1)": {"url": "https://script.google.com/macros/s/AKfycbyxixETwMCar087CvsXG6uTiYIUbm9TX9kFKCWzIHOCUURemBR2oVVCB15JU32dFwYY/exec", "id": "1"}
}

BASE_IMAGE_URL = "https://raw.githubusercontent.com/PepIndurain/World-Tour-2026/main/"

# --- 2. CSS: ULTRA BLACK & LARGE FONT ---
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

    /* Tables Style (Pure Black & Bold for PC) */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 1.15rem !important; color: #000000 !important; font-weight: 700 !important;
    }
    
    .hof-row {
        display: grid; grid-template-columns: 80px repeat(4, 1fr); gap: 10px;
        background: #ffffff; border: 2px solid #000000; border-radius: 10px;
        margin-bottom: 10px; padding: 15px 10px; align-items: center; box-shadow: 4px 4px 0px #eee;
    }
    .group-label { font-size: 2.2rem; font-weight: 800; color: #C1272D; text-align: center; border-right: 2px solid #eee; }
    .rider-name { font-size: 1.2rem; font-weight: 700; color: #000000; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_jersey_icon(color): return f"{BASE_IMAGE_URL}{color}-jersey.png"

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
                get_t = lambda k: {"name": res[k][0]["name"], "team": res[k][0].get("teamName", res[k][0].get("team", ""))} if res.get(k) else {"name": "N/A", "team": "-"}
                results.append({"group": lit, "yellow": get_t("generalClassification"), "green": get_t("sprintClassification"), "polkadot": get_t("mountainClassification"), "white": get_t("teamTimeClassification")})
            return results
        except: return []

    final_winners = get_final_winners(sel_tour_hof)
    if final_winners:
        st.markdown(f'<div class="hof-header-grid"><div>Group</div><div><img src="{get_jersey_icon("yellow")}" width="30"><br>GC</div><div><img src="{get_jersey_icon("green")}" width="30"><br>Pts</div><div><img src="{get_jersey_icon("polkadot")}" width="30"><br>KOM</div><div><img src="{get_jersey_icon("white")}" width="30"><br>Team</div></div>', unsafe_allow_html=True)
        for w in final_winners:
            row = f'<div class="hof-row"><div class="group-label">{w["group"]}</div>'
            for col in ["yellow", "green", "polkadot", "white"]: row += f'<div class="jersey-box"><span class="rider-name">{w[col]["name"]}</span><span class="team-name">{w[col]["team"]}</span></div>'
            st.markdown(row + "</div>", unsafe_allow_html=True)

else:
 # --- 📊 MASTER STANDINGS ---
    st.markdown('<div class="main-header"><h1>📊 Master Standings</h1><p>World Tour Global Rankings</p></div>', unsafe_allow_html=True)
    
    # Ricordati di aggiornare l'URL se ne hai generato uno nuovo
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
                df_r = df_r[["Rank", "Player", "Type", "Rider Name", "WTP"]]
                st.dataframe(df_r, use_container_width=True, hide_index=True)
            else:
                st.warning("Rider data is empty in the Google Script response.")

        with tt:
            # Recuperiamo i dati dei team
            raw_teams = master_data.get("teamsMaster", [])
            df_t = pd.DataFrame(raw_teams)
            
            if not df_t.empty:
                df_t['WTP'] = pd.to_numeric(df_t['WTP'], errors='coerce').round(2)
                # Verifichiamo che le colonne esistano prima di riordinare
                cols_to_show = ["Rank", "Player", "Team Name", "WTP"]
                df_t = df_t[[c for c in cols_to_show if c in df_t.columns]]
                st.dataframe(df_t, use_container_width=True, hide_index=True)
            else:
                # Se entriamo qui, lo script Google ha restituito una lista vuota per i team
                st.error("Team data was not found in the spreadsheet. Check if Column V (Teams) has data starting from row 5.")
                st.write("Debug info - Keys found in JSON:", list(master_data.keys()))
