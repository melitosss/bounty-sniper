import requests
import sqlite3
import os # Nuova libreria di sistema per leggere le variabili segrete

# --- CONFIGURAZIONE SICURA ---
# Leggiamo i token direttamente dalla cassaforte di GitHub (Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- FASE 4: LA MEMORIA (Nuovo Modulo) ---
def inizializza_database():
    """Crea il taccuino (file .db) e la tabella se non esistono."""
    connessione = sqlite3.connect("memoria.db")
    cursore = connessione.cursor()
    # Creiamo una tabella con una sola colonna: l'ID univoco di GitHub
    cursore.execute('''CREATE TABLE IF NOT EXISTS taglie_notificate (id_github TEXT PRIMARY KEY)''')
    connessione.commit()
    connessione.close()

def taglia_gia_vista(id_github):
    """Controlla se abbiamo già mandato questa taglia in passato."""
    connessione = sqlite3.connect("memoria.db")
    cursore = connessione.cursor()
    cursore.execute("SELECT id_github FROM taglie_notificate WHERE id_github = ?", (str(id_github),))
    risultato = cursore.fetchone()
    connessione.close()
    return risultato is not None # Restituisce True se c'è, False se è nuova

def segna_come_inviata(id_github):
    """Scrive l'ID nel taccuino dopo aver inviato il messaggio."""
    connessione = sqlite3.connect("memoria.db")
    cursore = connessione.cursor()
    cursore.execute("INSERT INTO taglie_notificate (id_github) VALUES (?)", (str(id_github),))
    connessione.commit()
    connessione.close()

# --- FASE 3: IL GRILLETTO ---
def invia_notifica(messaggio):
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dati = {"chat_id": TELEGRAM_CHAT_ID, "text": messaggio, "parse_mode": "HTML"}
    try:
        requests.post(url_telegram, data=dati)
    except Exception as e:
        print(f"Errore Telegram: {e}")

# --- FASE 1 & 2: OCCHIO E CERVELLO ---
def cerca_problemi(linguaggio):
    bersaglio = f'https://api.github.com/search/issues?q=label:"good first issue"+language:{linguaggio}+state:open&sort=updated&order=desc'
    try:
        risposta = requests.get(bersaglio)
        if risposta.status_code == 200:
            return risposta.json().get("items", []) 
        return []
    except:
        return []

def analizza_taglie(lista_problemi):
    taglie_valide = []
    for problema in lista_problemi:
        titolo = problema.get("title", "").lower()
        if len(titolo) > 10: 
            taglie_valide.append(problema)
    return taglie_valide


if __name__ == "__main__":
    print("🤖 Cecchino avviato. Inizializzazione memoria...")
    inizializza_database() # Prepariamo il database
    
    lista_grezza = cerca_problemi("python")
    taglie_pulite = analizza_taglie(lista_grezza)
    
    # Ora filtriamo ulteriormente tenendo SOLO le taglie che non abbiamo mai visto
    taglie_nuove = []
    for taglia in taglie_pulite:
        id_univoco = taglia.get("id")
        if not taglia_gia_vista(id_univoco):
            taglie_nuove.append(taglia)
            
    if taglie_nuove:
        testo_notifica = f"🎯 <b>Trovate {len(taglie_nuove)} NUOVE task in Python!</b>\n\n"
        
        # 1. Costruiamo il messaggio e mandiamo su Telegram SOLO le prime 3
        for i in range(min(3, len(taglie_nuove))):
            titolo = taglie_nuove[i].get("title")
            link = taglie_nuove[i].get("html_url")
            testo_notifica += f"🔹 <b>{titolo}</b>\n🔗 {link}\n\n"
            
        invia_notifica(testo_notifica)
        
        # 2. LA CORREZIONE: Segniamo TUTTE le nuove task nel taccuino, così non ce le riproporrà mai più
        for taglia in taglie_nuove:
            id_univoco = taglia.get("id")
            segna_come_inviata(id_univoco)
            
        print(f"✅ Inviato riassunto su Telegram. Salvate {len(taglie_nuove)} task nel database per non scordarle.")
    else:
        print("📭 Nessuna nuova task trovata rispetto all'ultimo controllo. Riposo.")