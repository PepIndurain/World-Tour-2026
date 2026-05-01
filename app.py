import streamlit as st
import requests
import pandas as pd

# Configurazione pagina
st.set_page_config(layout="wide", page_title="Cycling Hub")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec"

st.title("🚴 World Tour Cycling Dashboard")

# --- BARRA LATERALE PER IL CODICE ---
st.sidebar.header("Impostazioni")
code_input = st.sidebar.text_input("Codice Gara (es: 26.5.A.2)", "26.5.A.2")
btn_carica = st.sidebar.button("Aggiorna Dati")

if btn_carica or "data_cache" in st.session_state:
    with st.spinner('Caricamento in corso...'):
        try:
            # Se è la prima volta o è stato premuto il tasto, scarichiamo i dati
            if btn_carica or "data_cache" not in st.session_state:
                response = requests.get(f"{WEB_APP_URL}?code={code_input}")
                st.session_state.data_cache = response.json()
            
            data = st.session_state.data_cache

            if "error" in data:
                st.error(data["error"])
            else:
                st.info(f"📍 {data.get('currentCode', '')}")

                # --- MENU ORIZZONTALE SCORREVOLE (TABS) ---
                # Definiamo i titoli delle schede con le Emoji
                nomi_tab = [
                    "🏁 Tappa", "🟡 Generale", "🟢 Sprint", "🔴 Montagna", 
                    "🔵 Punti TP", "👥 Team Tempo", "👥 Team TP", "🚀 Griglia"
                ]
                
                # Creiamo i tab: Streamlit li mette in fila in alto
                tabs = st.tabs(nomi_tab)

                # --- TAB 1: RISULTATI TAPPA ---
                with tabs[0]:
                    st.header("🏁 Risultati della Tappa")
                    df = pd.DataFrame(data["stageResults"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                # --- TAB 2: CLASSIFICA GENERALE ---
                with tabs[1]:
                    st.header("🟡 Classifica Generale")
                    df = pd.DataFrame(data["generalClassification"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                # --- TAB 3: SPRINT ---
                with tabs[2]:
                    st.header("🟢 Classifica Sprint")
                    df = pd.DataFrame(data["sprintClassification"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                # --- TAB 4: MONTAGNA ---
                with tabs[3]:
                    st.header("🔴 Classifica Montagna")
                    df = pd.DataFrame(data["mountainClassification"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                # --- TAB 5: PUNTI TP ---
                with tabs[4]:
                    st.header("🔵 Classifica Punti TP")
                    df = pd.DataFrame(data["tpClassification"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                # --- TAB 6: TEAM TEMPO ---
                with tabs[5]:
                    st.header("👥 Team Time Classification")
                    df = pd.DataFrame(data["teamTimeClassification"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                # --- TAB 7: TEAM TP ---
                with tabs[6]:
                    st.header("👥 Team TP Classification")
                    df = pd.DataFrame(data["teamTPClassification"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                # --- TAB 8: GRIGLIA ---
                with tabs[7]:
                    st.header("🚀 Griglia Prossima Tappa")
                    df = pd.DataFrame(data["nextStageGrid"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Errore di connessione: {e}")
else:
    st.info("Inserisci il codice gara a sinistra per iniziare.")
