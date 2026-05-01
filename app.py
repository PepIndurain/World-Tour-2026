import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Hub")

TOURS = {
    "Itzulia Basque Country": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec",
}

# --- MAPPATURA IMMAGINI MAGLIETTE ---
# Qui colleghiamo il testo dello script a delle icone reali
JERSEY_ICONS = {
    "yellow": "https://cdn-icons-png.flaticon.com/512/3159/3159614.png", # Gialla
    "green": "https://cdn-icons-png.flaticon.com/512/3159/3159611.png",  # Verde
    "polkadot": "https://cdn-icons-png.flaticon.com/512/3159/3159642.png", # Pois (Rossa)
    "white": "https://cdn-icons-png.flaticon.com/512/3159/3159615.png",  # Bianca
}

def style_cycling_rows(row):
    # Logica per il colore della riga (tenue per leggibilità)
    j = str(row['jersey_raw']).lower() if 'jersey_raw' in row else ''
    if 'yellow' in j: return ['background-color: #fdf3c0'] * len(row)
    if 'green' in j: return ['background-color: #d5f5e3'] * len(row)
    if 'polkadot' in j: return ['background-color: #f5d5d5'] * len(row)
    if 'white' in j: return ['background-color: #f2f4f4'] * len(row)
    return [''] * len(row)

st.title("🚴 World Tour Cycling Dashboard")

st.sidebar.header("Impostazioni")
nome_tour = st.sidebar.selectbox("Seleziona il Tour", list(TOURS.keys()))
codice_gara = st.sidebar.text_input("Codice Gara", "26.5.A.2")

if codice_gara:
    with st.spinner('Caricamento maglie e classifiche...'):
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
                        # Salviamo il testo originale per il colore, poi trasformiamo 'jersey' in link immagine
                        if 'jersey' in df.columns:
                            df['jersey_raw'] = df['jersey']
                            df['jersey'] = df['jersey'].str.lower().map(JERSEY_ICONS).fillna("")
                        
                        # Applichiamo lo stile colore
                        styled_df = df.style.apply(style_cycling_rows, axis=1)
                        
                        st.header(title)
                        # Usiamo column_config per mostrare l'immagine vera
                        st.dataframe(
                            styled_df, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "jersey": st.column_config.ImageColumn("Maglia"),
                                "jersey_raw": None # Nascondiamo la colonna di servizio
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
