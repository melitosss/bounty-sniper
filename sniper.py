import requests
import sqlite3
import os
import logging # 1. Nuova libreria di sistema per i log professionali

# --- CONFIGURAZIONE LOG E SICUREZZA ---
# Diciamo al sistema di registrare l'ora esatta e il livello di importanza di ogni messaggio
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- FASE 4: LA MEMORIA ---
# Nota il "-> None": indica che la funzione esegue un'azione ma non restituisce dati (Type Hinting)
def inizializza_database() -> None: 
    connessione = sqlite3.connect("memoria.db")
    cursore = connessione.cursor()
    cursore.execute('''CREATE TABLE IF NOT EXISTS taglie_notificate (id_github TEXT PRIMARY KEY)''')
    connessione.commit()
    connessione.close()

# Nota "id_github: str" e "-> bool": chiarisce che entra una stringa e deve uscire un Vero/Falso
def taglia_gia_vista(id_github: str) -> bool:
    connessione = sqlite3.connect("memoria.db")
    cursore = connessione.cursor()
    cursore.execute("SELECT id_github FROM taglie_notificate WHERE id_github = ?", (str(id_github),))
    risultato = cursore.fetchone()
    connessione.close()
    return risultato is not None

def segna_come_inviata(id_github: str) -> None:
    connessione = sqlite3.connect("memoria.db")
    cursore = connessione.cursor()
    cursore.execute("INSERT INTO taglie_notificate (id_github) VALUES (?)", (str(id_github),))
    connessione.commit()
    connessione.close()

# --- FASE 3: IL GRILLETTO ---
def invia_notifica(messaggio: str) -> None:
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dati = {"chat_id": TELEGRAM_CHAT_ID, "text": messaggio, "parse_mode": "HTML"}
    try:
        requests.post(url_telegram, data=dati)
    except Exception as e:
        # Se cade la connessione, registriamo un ERRORE, non una semplice info
        logging.error(f"Errore Telegram: {e}") 

# --- FASE 1 & 2: OCCHIO E CERVELLO ---
def cerca_problemi(linguaggio: str) -> list:
    bersaglio = f'https://api.github.com/search/issues?q=label:"good first issue"+language:{linguaggio}+state:open&sort=updated&order=desc'
    try:
        risposta = requests.get(bersaglio)
        if risposta.status_code == 200:
            return risposta.json().get("items", []) 
        return []
    except Exception as e:
        logging.error(f"Errore GitHub API: {e}")
        return []

def analizza_taglie(lista_problemi: list) -> list:
    taglie_valide = []
    for problema in lista_problemi:
        titolo = problema.get("title", "").lower()
        if len(titolo) > 10: 
            taglie_valide.append(problema)
    return taglie_valide


if __name__ == "__main__":
    # Addio print! Ora usiamo logging.info
    logging.info("Cecchino avviato. Inizializzazione memoria...")
    inizializza_database()
    
    lista_grezza = cerca_problemi("python")
    taglie_pulite = analizza_taglie(lista_grezza)
    
    taglie_nuove = []
    for taglia in taglie_pulite:
        id_univoco = str(taglia.get("id"))
        if not taglia_gia_vista(id_univoco):
            taglie_nuove.append(taglia)
            
    if taglie_nuove:
        testo_notifica = f"🎯 <b>Trovate {len(taglie_nuove)} NUOVE task in Python!</b>\n\n"
        
        for i in range(min(3, len(taglie_nuove))):
            id_univoco = taglie_nuove[i].get("id")
            titolo = taglie_nuove[i].get("title")
            link = taglie_nuove[i].get("html_url")
            testo_notifica += f"🔹 <b>{titolo}</b>\n🔗 {link}\n\n"
            
        invia_notifica(testo_notifica)
        
        for taglia in taglie_nuove:
            id_univoco = str(taglia.get("id"))
            segna_come_inviata(id_univoco)
            
        logging.info(f"Inviate notifiche. Salvate {len(taglie_nuove)} task nel database.")
    else:
        logging.info("Nessuna nuova task trovata. Riposo.")