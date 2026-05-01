import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Cycling Board Game Hub")

# --- INSERISCI QUI IL TUO LINK CSV ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTb2BJs9RzhCeQZZvkWqseehXP4Y3ZyomFRG8Pwat43pvQ7O624Q3qcbhMy9x2jzEUKD-sbFRskFrlD/pub?gid=0&single=true&output=csv"

def clean_row(val):
    """Spezza le righe complesse in colonne pulite"""
    s = str(val).strip()
    if not s or s == 'nan' or '---' in s:
        return None
    
    # Caso Classifica Generale: "2. [WT]@User: Colore --> 13:40"
    if "-->" in s:
        try:
            pos_part = s.split(".")[0] if "." in s else ""
            rest = s.split(".")[1] if "." in s else s
            rider_part = rest.split("-->")[0].strip()
            time_part = rest.split("-->")[1].strip()
            return {"Pos": pos_part, "Giocatore/Team": rider_part, "Tempo/Distacco": time_part}
        except:
            return {"Dato": s}

    # Caso Punti/Montagna: "NOME_GIOCATORE - 5 CPts" o "NOME - 3"
    if " - " in s:
        parts = s.split(" - ")
        return {"Giocatore": parts[0].strip(), "Punti/Info": parts[1].strip()}
    
    return {"Dato": s}

st.title("🚴 World Tour Cycling - Risultati Live")

try:
    # Carichiamo i dati
    df_raw = pd.read_csv(CSV_URL, header=None)
    
    # --- FIX SELETTORE TAPPE ---
    # Cerchiamo i nomi delle tappe nella riga 3 (indice 2), saltando celle vuote o trattini
    riga_tappe = df_raw.iloc[2, :].tolist()
    opzioni_tappa = [str(x) for x in riga_tappe if str(x) not in ['nan', 'None', '----------', 'STAGE']]
    
    st.sidebar.header("Impostazioni")
    if opzioni_tappa:
        tappa_scelta = st.sidebar.selectbox("Seleziona la Tappa", opzioni_tappa)
        
        # Troviamo la colonna giusta (cerchiamo il valore esatto nella riga 3)
        idx_colonna = riga_tappe.index(tappa_scelta)
        dati_gara = df_raw.iloc[:, idx_colonna]

        # --- DEFINIZIONE BLOCCHI (Coordinate righe) ---
        blocchi = [
            {"titolo": "🏆 Generale", "range": (4, 14)},
            {"titolo": "⛰️ Montagna", "range": (16, 21)},
            {"titolo": "🏁 Punti", "range": (23, 29)},
            {"titolo": "⚔️ Combattività", "range": (33, 40)},
            {"titolo": "💨 Scia", "range": (43, 50)}
        ]

        # Visualizzazione
        st.header(f"Risultati: {tappa_scelta}")
        
        # Creiamo le colonne visive
        cols = st.columns(len(blocchi))

        for i, b in enumerate(blocchi):
            with cols[i]:
                st.subheader(b["titolo"])
                # Estraiamo le righe grezze
                rows_raw = dati_gara.iloc[b["range"][0]:b["range"][1]].tolist()
                
                # Elaboriamo ogni riga
                tabella_pulita = []
                for r in rows_raw:
                    dati_processati = clean_row(r)
                    if dati_processati:
                        tabella_pulita.append(dati_processati)
                
                if tabella_pulita:
                    # Trasformiamo in tabella visiva
                    df_view = pd.DataFrame(tabella_pulita)
                    st.dataframe(df_view, use_container_width=True, hide_index=True)
                else:
                    st.write("Dati non ancora disponibili")
    else:
        st.error("Non ho trovato i nomi delle tappe nel file. Controlla la riga 3 del foglio RESULTS.")

except Exception as e:
    st.error(f"Errore tecnico: {e}")
