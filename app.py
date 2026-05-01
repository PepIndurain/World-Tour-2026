import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Hub")

TOURS = {
    "Itzulia Basque Country": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec",
}

# --- FUNZIONE PER COLORARE LE RIGHE ---
def style_cycling_rows(row):
    # Recuperiamo il valore della colonna 'jersey'
    color_val = str(row['jersey']).lower() if 'jersey' in row else ''
    
    # Definiamo i colori (Hex) simili al tuo Excel
    bg_color = ''
    if 'yellow' in color_val: bg_color = 'background-color: #fdf3c0' # Giallo tenue
    elif 'green' in color_val: bg_color = 'background-color: #d5f5e3' # Verde tenue
    elif 'polkadot' in color_val: bg_color = 'background-color: #f5d5d5' # Rosso/Pois tenue
    elif 'white' in color_val: bg_color = 'background-color: #f2f4f4' # Grigio/Bianco tenue
    
    return [bg_color] * len(row)

# --- FUNZIONE PER SOSTITUIRE TESTO CON EMOJI ---
def icon_jersey(val):
    val = str(val).lower()
    if 'yellow' in val: return "👕🟡"
    if 'green' in val: return "👕🟢"
    if 'polkadot' in val: return "👕🔴"
    if 'white' in val: return "👕⚪"
    return ""

st.title("🚴 World Tour Cycling Dashboard")

st.sidebar.header("Impostazioni")
nome_tour = st.sidebar.selectbox("Seleziona il Tour", list(TOURS.keys()))
codice_gara = st.sidebar.text_input("Codice Gara (es: 26.5.A.2)", "26.5.A.2")

if codice_gara:
    with st.spinner('Caricamento dati e applicazione maglie...'):
        try:
            response = requests.get(f"{TOURS[nome_tour]}?code={codice_gara}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.success(f"Visualizzazione: {data.get('currentCode', '')}")

                nomi_tab = ["🏁 Tappa", "🟡 Generale", "🟢 Sprint", "🔴 Montagna", "🔵 Punti TP", "👥 Team", "🚀 Griglia"]
                tabs = st.tabs(nomi_tab)

                def render_styled_table(key, title):
                    df = pd.DataFrame(data.get(key, []))
                    if not df.empty:
                        # 1. Trasformiamo i nomi dei colori in icone nella colonna 'jersey'
                        if 'jersey' in df.columns:
                            df['jersey'] = df['jersey'].apply(icon_jersey)
                        
                        # 2. Applichiamo lo stile alle righe
                        styled_df = df.style.apply(style_cycling_rows, axis=1)
                        
                        st.header(title)
                        st.dataframe(styled_df, use_container_width=True, hide_index=True)
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
