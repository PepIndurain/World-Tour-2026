import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Hub")

# --- 1. CONFIGURAZIONE DEI TOUR (Aggiungi qui i tuoi file futuri) ---
# Ogni volta che hai un nuovo Tour, aggiungi una riga qui sotto.
TOURS = {
    "Itzulia Basque Country": "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec",
    "Volta Ciclista (Esempio)": "URL_DI_UN_ALTRO_SCRIPT_SE_ESISTE",
}

st.title("🚴 World Tour Cycling Dashboard")

# --- 2. BARRA LATERALE ---
st.sidebar.header("Impostazioni")

# Menu a tendina per il nome del file (Tour)
nome_tour = st.sidebar.selectbox("Seleziona il Tour", list(TOURS.keys()))

# Input per il codice gara (Premendo INVIO si aggiorna da solo)
codice_gara = st.sidebar.text_input("Codice Gara (es: 26.5.A.2)", "26.5.A.2")

# Usiamo l'URL corrispondente al tour scelto
URL_ATTUALE = TOURS[nome_tour]

# --- 3. CARICAMENTO DATI (Reattivo all'INVIO) ---
# Non usiamo più il tasto "Aggiorna": Streamlit ricarica quando cambi testo e premi Invio
if codice_gara:
    with st.spinner(f'Caricamento dati da {nome_tour}...'):
        try:
            # Chiamata al Google Script
            response = requests.get(f"{URL_ATTUALE}?code={codice_gara}")
            data = response.json()

            if "error" in data:
                st.error(f"Nota: {data['error']}")
            else:
                st.success(f"Visualizzazione: {data.get('currentCode', '')}")

                # --- 4. VISUALIZZAZIONE TAB (Menu scorrevole) ---
                nomi_tab = [
                    "🏁 Tappa", "🟡 Generale", "🟢 Sprint", "🔴 Montagna", 
                    "🔵 Punti TP", "👥 Team Tempo", "👥 Team TP", "🚀 Griglia"
                ]
                
                tabs = st.tabs(nomi_tab)

                # Funzione per mostrare le tabelle
                def mostra_tabella(chiave_json, titolo):
                    df = pd.DataFrame(data.get(chiave_json, []))
                    if not df.empty:
                        st.header(titolo)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info(f"Nessun dato per {titolo}")

                with tabs[0]: mostra_tabella("stageResults", "Risultati Tappa")
                with tabs[1]: mostra_tabella("generalClassification", "Classifica Generale")
                with tabs[2]: mostra_tabella("sprintClassification", "Classifica Sprint")
                with tabs[3]: mostra_tabella("mountainClassification", "Classifica Montagna")
                with tabs[4]: mostra_tabella("tpClassification", "Classifica Punti TP")
                with tabs[5]: mostra_tabella("teamTimeClassification", "Team Time Classification")
                with tabs[6]: mostra_tabella("teamTPClassification", "Team TP Classification")
                with tabs[7]: mostra_tabella("nextStageGrid", "Griglia Prossima Tappa")

        except Exception as e:
            st.error("Inserisci un codice valido o controlla la connessione al file.")
