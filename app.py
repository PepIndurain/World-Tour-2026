import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Hub")

TOURS = {
    "Itzulia Basque Country": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec",
}

# --- NUOVE ICONE STABILI (Sperando non diventino skateboard!) ---
JERSEY_ICONS = {
    "yellow": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Jersey_yellow.svg/100px-Jersey_yellow.svg.png",
    "green": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Jersey_green.svg/100px-Jersey_green.svg.png",
    "polkadot": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Jersey_polkadot.svg/100px-Jersey_polkadot.svg.png",
    "white": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Jersey_white.svg/100px-Jersey_white.svg.png",
}

def style_cycling_rows(row):
    # Colori più simili al tuo screenshot originale
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    if 'yellow' in j: return ['background-color: #FFF2CC'] * len(row) # Giallo Itzulia
    if 'green' in j: return ['background-color: #E2F0D9'] * len(row) # Verde Sprint
    if 'polkadot' in j: return ['background-color: #FBE2E2'] * len(row) # Rosa/Pois
    if 'white' in j: return ['background-color: #F2F2F2'] * len(row) # Grigio Team
    return [''] * len(row)

st.title("🚴 World Tour Cycling Dashboard")

st.sidebar.header("Impostazioni")
nome_tour = st.sidebar.selectbox("Seleziona il Tour", list(TOURS.keys()))
codice_gara = st.sidebar.text_input("Codice Gara (es: 26.5.A.2)", "26.5.A.2")

if codice_gara:
    with st.spinner('Caricamento maglie reali...'):
        try:
            response = requests.get(f"{TOURS[nome_tour]}?code={codice_gara}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                nomi_tab = ["🏁 Tappa", "🟡 Generale", "🟢 Sprint", "🔴 Montagna", "🔵 Punti TP", "👥 Team", "🚀 Griglia"]
                tabs = st.tabs(nomi_tab)

                def render_styled_table(key, title):
                    df = pd.DataFrame(data.get(key, []))
                    if not df.empty:
                        # Gestione colonna maglia
                        if 'jersey' in df.columns:
                            df['jersey_raw'] = df['jersey']
                            # Mappa il testo al link dell'immagine
                            df['jersey'] = df['jersey'].str.lower().map(JERSEY_ICONS).fillna("")
                        
                        styled_df = df.style.apply(style_cycling_rows, axis=1)
                        
                        st.header(title)
                        st.dataframe(
                            styled_df, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "jersey": st.column_config.ImageColumn("Maglia", width="small"),
                                "jersey_raw": None 
                            }
                        )
                    else:
                        st.info(f"Nessun dato per {title}")

                with tabs[0]: render_styled_table("stageResults", "Risultati Tappa")
                with tabs[1]: render_styled_table("generalClassification", "Classifica Generale")
                with tabs[2]: render_styled_table("sprintClassification", "Classifica Sprint")
                with tabs[3]: render_styled_table("mountainClassification", "Classifica Montagna")
                with tabs[4]: render_styled_table("tpClassification", "Classifica Punti TP")
                with tabs[5]: render_styled_table("teamTimeClassification", "Team Classification")
                with tabs[6]: render_styled_table("nextStageGrid", "Griglia Prossima Tappa")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
