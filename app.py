import streamlit as st
import pandas as pd
import re

st.set_page_config(layout="wide", page_title="Cycling Board Game Hub")

# --- CONFIGURAZIONE ---
# Metti qui il tuo link CSV (quello della scheda ITZULIA o del MENU)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTb2BJs9RzhCeQZZvkWqseehXP4Y3ZyomFRG8Pwat43pvQ7O624Q3qcbhMy9x2jzEUKD-sbFRskFrlD/pub?gid=0&single=true&output=csv"

def parse_line(line):
    """Funzione per pulire le righe di testo e dividerle in colonne"""
    if not line or pd.isna(line) or '---' in str(line):
        return None
    
    line = str(line).strip()
    
    # Prova a dividere per Classifica Generale (es: 2. [WT]@User --> 13:40)
    if '-->' in line:
        parts = re.split(r'\. | --> ', line)
        if len(parts) >= 2:
            pos = parts[0]
            # Pulizia nome (toglie [WT] e simili)
            name = parts[1].split(':')[-1].strip()
            val = parts[-1].strip()
            return {"Pos": pos, "Ciclista": name, "Tempo/Distacco": val}

    # Prova a dividere per Classifiche a Punti (es: B_WHITE - 2 FPts)
    if ' - ' in line:
        parts = line.split(' - ')
        return {"Ciclista": parts[0], "Punti": parts[1]}
    
    return {"Dato": line}

st.title("🚴 World Tour Cycling - Classifiche")

try:
    # Caricamento dati
    df_raw = pd.read_csv(CSV_URL, header=None)
    
    # Menu Tappe
    tappe = df_raw.iloc[2, 0:].dropna().tolist()
    st.sidebar.header("Navigazione")
    tappa_scelta = st.sidebar.selectbox("Seleziona Tappa", tappe)
    
    col_index = tappe.index(tappa_scelta)
    dati_colonna = df_raw.iloc[:, col_index]

    # Definizione blocchi
    blocchi = [
        {"nome": "🏆 Classifica Generale", "range": (4, 13)},
        {"nome": "⛰️ Montagna", "range": (16, 20)},
        {"nome": "🏁 Punti (Sprint)", "range": (22, 28)},
        {"nome": "⚔️ Combattività", "range": (33, 40)},
        {"nome": "💨 Scia (Slipstream)", "range": (43, 50)}
    ]

    # Visualizzazione in colonne larghe
    st.write(f"## {tappa_scelta}")
    
    # Creiamo una riga di colonne per le tabelle
    cols = st.columns(len(blocchi))

    for i, blocco in enumerate(blocchi):
        with cols[i]:
            st.subheader(blocco["nome"])
            
            # Estraiamo e puliamo i dati
            raw_lines = dati_colonna.iloc[blocco["range"][0]:blocco["range"][1]+1].dropna()
            parsed_data = [parse_line(l) for l in raw_lines if parse_line(l) is not None]
            
            if parsed_data:
                # Trasformiamo in una tabella vera (DataFrame)
                df_tabella = pd.DataFrame(parsed_data)
                # La mostriamo senza l'indice brutto a sinistra
                st.table(df_tabella)
            else:
                st.write("Nessun dato")

except Exception as e:
    st.error("Errore nel caricamento dei dati.")
    st.write(e)
