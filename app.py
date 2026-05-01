import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Board Game Hub")

# --- CONFIGURAZIONE ---
# Incolla qui il link CSV della tua scheda "MENU" che hai creato nel file Hub
# Per ora mettiamo il link che hai già creato per testare
MENU_CSV_URL = "INSERISCI_QUI_IL_LINK_DELLA_SCHEDA_MENU"

st.title("🚴 World Tour Cycling - Board Game Hub")

@st.cache_data(ttl=300)
def load_csv(url):
    return pd.read_csv(url, header=None)

try:
    # 1. Carichiamo il menu dei tour
    # Se non hai ancora la scheda menu, possiamo inserire i link a mano qui sotto per ora
    tours = {
        "Itzulia Basque Country": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTb2BJs9RzhCeQZZvkWqseehXP4Y3ZyomFRG8Pwat43pvQ7O624Q3qcbhMy9x2jzEUKD-sbFRskFrlD/pub?gid=0&single=true&output=csv",
        # "Volta Ciclista": "IL_TUO_LINK_CSV_VOLTA",
    }
    
    tour_scelto = st.sidebar.selectbox("Seleziona Competizione", list(tours.keys()))
    
    # 2. Carichiamo i dati del tour scelto
    df = load_csv(tours[tour_scelto])
    
    # Riga 3 (indice 2) contiene i nomi delle tappe
    tappe = df.iloc[2, 0:].dropna().tolist()
    
    tappa_scelta = st.sidebar.selectbox("Seleziona Tappa/Gara", tappe)
    
    col_index = tappe.index(tappa_scelta)
    dati_tappa = df.iloc[:, col_index]

    # Blocchi di visualizzazione (coordinate fisse della scheda RESULTS)
    blocchi = {
        "🏆 Classifica Generale": (4, 13),
        "⛰️ Montagna (Mountain)": (16, 20),
        "🏁 Punti (Sprint)": (22, 28),
        "⚔️ Combattività": (33, 40),
        "💨 Slipstream": (43, 50)
    }

    st.header(f"Risultati: {tour_scelto}")
    st.subheader(f"Dettaglio: {tappa_scelta}")

    # Layout orizzontale
    cols = st.columns(len(blocchi))

    for i, (nome_blocco, range_righe) in enumerate(blocchi.items()):
        with cols[i]:
            st.markdown(f"### {nome_blocco}")
            fetta = dati_tappa.iloc[range_righe[0]:range_righe[1]+1].dropna()
            for riga in fetta:
                st.info(riga)

except Exception as e:
    st.warning("Configurazione in corso... Assicurati di aver inserito i link CSV corretti.")
    st.info("Una volta pronti i link nel file Hub, il sito mostrerà tutte le classifiche.")
