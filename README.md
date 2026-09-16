# 🎯 Bounty Sniper (Agente Autonomo CI/CD)

Un agente autonomo scritto in **Python** che scansiona GitHub alla ricerca di task Open Source ("Good First Issue"), le filtra e invia notifiche in tempo reale su Telegram.

A differenza dei classici bot che spammano notifiche duplicate o che richiedono un server sempre acceso, Bounty Sniper è progettato con un'architettura **Serverless ed Ephemeral**, supportata da un database persistente in cloud per tracciare lo stato delle notifiche.

## 🏗️ Architettura del Sistema

Il progetto è strutturato in 4 moduli logici:
1. **L'Occhio (API Integration):** Interroga in tempo reale le API REST di GitHub per estrarre le ultime issue basate su linguaggi specifici (es. Python).
2. **Il Cervello (Logica & Filtri):** Pulisce i dati grezzi, scartando i titoli troppo corti (anti-spam) e validando la struttura del JSON.
3. **Il Grilletto (Notifiche Alerting):** Si interfaccia con le API di Telegram per inviare messaggi formattati in HTML.
4. **La Memoria (Persistenza SQLite):** Gestisce un database relazionale (`memoria.db`) per evitare l'invio di task già processate.

## 🚀 Tecnologie Utilizzate

*   **Linguaggio:** Python 3.10 (con Type Hinting e Logging professionale)
*   **Database:** SQLite3
*   **Networking:** Libreria `requests` (HTTP REST)
*   **Sicurezza:** Gestione credenziali via OS Environment Variables (Secrets)
*   **CI/CD:** GitHub Actions (Automazione Cron + Sincronizzazione di stato)

## 🔐 Sicurezza & Deploy

Il bot è attualmente in produzione 24/7 in Cloud. 
Per garantire la massima sicurezza, i token bot di Telegram e gli ID utente non sono hardcodati nel codice, ma vengono iniettati a runtime tramite le **GitHub Secrets**. Ad ogni esecuzione, il workflow in Cloud estrae il codice, installa le dipendenze, esegue l'agente e aggiorna dinamicamente il database sul branch per mantenere la persistenza della memoria.