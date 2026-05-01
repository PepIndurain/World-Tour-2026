import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Pro Hub")

# URL COMPLETO (Sostituisci questo)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec"

st.title("🚴 World Tour Cycling Dashboard")

st.sidebar.header("Navigazione Gara")
code_input = st.sidebar.text_input("Codice Gara (es: 26.5.C.3)", "26.5.C.3")

if st.sidebar.button("Carica Dati"):
    with st.spinner('Accesso al database ufficiale in corso...'):
        try:
            # Chiamata API
            response = requests.get(f"{WEB_APP_URL}?code={code_input}")
            data = response.json()

            if "error" in data:
                st.error(f"Errore dal foglio: {data['error']}")
            else:
                st.success(f"Visualizzazione: {data.get('currentCode', 'Dati caricati')}")
                
                # Creazione Tab
                t1, t2, t3, t4 = st.tabs(["🏆 Classifiche Individuali", "🏁 Risultati Tappa", "👥 Team", "🚀 Next Stage"])

                with t1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🟡 Generale")
                        st.dataframe(pd.DataFrame(data["generalClassification"]), use_container_width=True, hide_index=True)
                    with col2:
                        st.subheader("🔴 Montagna")
                        st.dataframe(pd.DataFrame(data["mountainClassification"]), use_container_width=True, hide_index=True)

                with t2:
                    st.subheader("🏁 Risultati di Tappa")
                    st.dataframe(pd.DataFrame(data["stageResults"]), use_container_width=True, hide_index=True)
                    st.subheader("🟢 Sprint")
                    st.dataframe(pd.DataFrame(data["sprintClassification"]), use_container_width=True, hide_index=True)

                with t3:
                    st.subheader("👥 Classifica Squadre")
                    st.dataframe(pd.DataFrame(data["teamTimeClassification"]), use_container_width=True, hide_index=True)

                with t4:
                    st.subheader("🚀 Griglia Prossima Tappa")
                    st.dataframe(pd.DataFrame(data["nextStageGrid"]), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Errore di connessione. Verifica che il Web App sia attivo. Dettaglio: {e}")
else:
    st.info("Inserisci il codice e clicca su Carica Dati. Il foglio Excel lavorerà per te!")
