import streamlit as st
import requests
import pandas as pd

# Impostiamo la pagina in modalità larga per favorire lo scorrimento orizzontale
st.set_page_config(layout="wide", page_title="Cycling Pro Hub")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzQ-ORFurfO95nLnljLP4Z5eMJQv5bzE8k5voX_CrKhpNTemYaeoD8UNftr2p1ClJWr/exec"

st.title("🚴 World Tour Cycling Dashboard")

# Barra laterale
st.sidebar.header("Navigazione Gara")
code_input = st.sidebar.text_input("Codice Gara (es: 26.5.A.2)", "26.5.A.2")
btn_carica = st.sidebar.button("Carica Dati")

if btn_carica:
    with st.spinner('Aggiornamento classifiche in corso...'):
        try:
            response = requests.get(f"{WEB_APP_URL}?code={code_input}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.success(f"Visualizzazione: {data.get('currentCode', '')}")
                
                # --- LAYOUT A COLONNE AFFIANCATE ---
                # Creiamo 8 colonne (una per ogni classifica disponibile nel tuo JSON)
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

                with c1:
                    st.subheader("🏁 Tappa")
                    df1 = pd.DataFrame(data["stageResults"])
                    if not df1.empty:
                        st.dataframe(df1[['rank', 'player', 'stageTime']], hide_index=True)

                with c2:
                    st.subheader("🟡 Generale")
                    df2 = pd.DataFrame(data["generalClassification"])
                    if not df2.empty:
                        st.dataframe(df2[['rank', 'player', 'tourPts']], hide_index=True)

                with c3:
                    st.subheader("🟢 Sprint")
                    df3 = pd.DataFrame(data["sprintClassification"])
                    if not df3.empty:
                        st.dataframe(df3[['rank', 'player', 'tourPts']], hide_index=True)

                with c4:
                    st.subheader("🔴 Montagna")
                    df4 = pd.DataFrame(data["mountainClassification"])
                    if not df4.empty:
                        st.dataframe(df4[['rank', 'player', 'tourPts']], hide_index=True)

                with c5:
                    st.subheader("🔵 Punti TP")
                    df5 = pd.DataFrame(data["tpClassification"])
                    if not df5.empty:
                        st.dataframe(df5[['rank', 'player', 'currentWtp']], hide_index=True)

                with c6:
                    st.subheader("👥 Team Tempo")
                    df6 = pd.DataFrame(data["teamTimeClassification"])
                    if not df6.empty:
                        st.dataframe(df6[['rank', 'team', 'tourTimes']], hide_index=True)

                with c7:
                    st.subheader("👥 Team TP")
                    df7 = pd.DataFrame(data["teamTPClassification"])
                    if not df7.empty:
                        st.dataframe(df7[['rank', 'team', 'currentWtp']], hide_index=True)

                with c8:
                    st.subheader("🚀 Griglia")
                    df8 = pd.DataFrame(data["nextStageGrid"])
                    if not df8.empty:
                        st.dataframe(df8[['grid', 'player', 'e2']], hide_index=True)

        except Exception as e:
            st.error(f"Errore: {e}")
else:
    st.info("Inserisci il codice gara e premi 'Carica Dati'")
