import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Pro Hub")

# --- INSERISCI QUI L'URL CHE HAI COPIATO (quello che finisce con /exec) ---
WEB_APP_URL = "AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr"

st.title("🚴 World Tour Cycling Dashboard")

# Barra laterale per inserire il codice gara
st.sidebar.header("Configurazione Gara")
code_input = st.sidebar.text_input("Inserisci Codice Gara (es: 26.5.C.3)", "26.5.C.3")

if st.sidebar.button("Aggiorna Classifiche"):
    # Chiamata al tuo script Google
    with st.spinner('Pescando i dati dal foglio ufficiale...'):
        try:
            # Inviamo il codice al tuo script via URL
            response = requests.get(f"{WEB_APP_URL}?code={code_input}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.success(f"Dati caricati per: {data['currentCode']}")
                
                # Creazione Tab per le varie classifiche
                t1, t2, t3, t4 = st.tabs(["🏆 Generale", "🏁 Sprint/Mountain", "👥 Team", "🚀 Next Stage"])

                with t1:
                    st.subheader("Classifica Generale")
                    df_gen = pd.DataFrame(data["generalClassification"])
                    st.table(df_gen[['rank', 'player', 'team', 'tourPts', 'bonusWtp']])

                with t2:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🔴 Montagna")
                        st.table(pd.DataFrame(data["mountainClassification"])[['rank', 'player', 'tourPts']])
                    with col2:
                        st.subheader("🟢 Sprint")
                        st.table(pd.DataFrame(data["sprintClassification"])[['rank', 'player', 'tourPts']])

                with t3:
                    st.subheader("Classifica Squadre (Time)")
                    st.table(pd.DataFrame(data["teamTimeClassification"])[['rank', 'team', 'tourTimes']])

                with t4:
                    st.subheader("Griglia di partenza prossima tappa")
                    st.table(pd.DataFrame(data["nextStageGrid"])[['grid', 'player', 'teamName', 'e2']])

        except Exception as e:
            st.error(f"Errore di connessione: {e}")
else:
    st.info("Inserisci il codice della gara a sinistra e clicca su 'Aggiorna Classifiche'")
