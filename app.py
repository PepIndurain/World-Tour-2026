import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Hub")

TOURS = {
    "Itzulia Basque Country": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec",
}

# --- FUNZIONE MANUALE PER ASSEGNARE L'ICONA ---
def get_jersey_url(val):
    v = str(val).lower()
    if 'yellow' in v: return "https://img.icons8.com/color/48/cycling-jersey--v1.png"
    if 'green' in v: return "https://img.icons8.com/color/48/cycling-jersey--v2.png"
    if 'polkadot' in v: return "https://img.icons8.com/color/48/cycling-jersey--v3.png"
    if 'white' in v: return "https://img.icons8.com/color/48/cycling-jersey--v4.png"
    return None

def style_cycling_rows(row):
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    if 'yellow' in j: return ['background-color: #FFF2CC'] * len(row)
    if 'green' in j: return ['background-color: #E2F0D9'] * len(row)
    if 'polkadot' in j: return ['background-color: #FBE2E2'] * len(row)
    if 'white' in j: return ['background-color: #F2F2F2'] * len(row)
    return [''] * len(row)

st.title("🚴 World Tour Cycling Dashboard")

st.sidebar.header("Impostazioni")
nome_tour = st.sidebar.selectbox("Seleziona il Tour", list(TOURS.keys()))
codice_gara = st.sidebar.text_input("Codice Gara", "26.5.A.2")

if codice_gara:
    with st.spinner('Pescando i dati...'):
        try:
            response = requests.get(f"{TOURS[nome_tour]}?code={codice_gara}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                tabs = st.tabs(["🏁 Tappa", "🟡 Generale", "🟢 Sprint", "🔴 Montagna", "🔵 Punti TP", "👥 Team", "🚀 Griglia"])

                def render_table(key, title, tab_idx):
                    with tabs[tab_idx]:
                        df = pd.DataFrame(data.get(key, []))
                        if not df.empty:
                            # Creiamo la colonna con le immagini usando la funzione robusta
                            if 'jersey' in df.columns:
                                df['jersey_raw'] = df['jersey'] # salviamo per il colore
                                df['jersey'] = df['jersey'].apply(get_jersey_url)
                            
                            # Applichiamo lo stile
                            styled_df = df.style.apply(style_cycling_rows, axis=1)
                            
                            st.header(title)
                            st.dataframe(
                                styled_df, 
                                use_container_width=True, 
                                hide_index=True,
                                column_config={
                                    "jersey": st.column_config.ImageColumn("Maglia"),
                                    "jersey_raw": None # nascondi la colonna testo
                                }
                            )
                        else:
                            st.info(f"Nessun dato per {title}")

                render_table("stageResults", "Risultati Tappa", 0)
                render_table("generalClassification", "Classifica Generale", 1)
                render_table("sprintClassification", "Classifica Sprint", 2)
                render_table("mountainClassification", "Classifica Montagna", 3)
                render_table("tpClassification", "Classifica Punti TP", 4)
                render_table("teamTimeClassification", "Team Classification", 5)
                render_table("nextStageGrid", "Griglia Prossima Tappa", 6)

        except Exception as e:
            st.error(f"Errore: {e}")
