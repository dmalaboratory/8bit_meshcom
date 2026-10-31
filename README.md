# 📡 MeshCom Tactical Pro Web Dashboard

[![MeshCom](https://img.shields.io/badge/MeshCom-v4.33b%20%2F%20v4.35-blue.svg)](https://meshcom.net)
[![LoRa](https://img.shields.io/badge/LoRa-433%20%2F%20868%20%2F%20915%20MHz-red.svg)]()
[![Web Bluetooth](https://img.shields.io/badge/Web%20Bluetooth-NUS-cyan.svg)]()
[![Wi-Fi REST](https://img.shields.io/badge/Wi--Fi-REST%20API-emerald.svg)]()
[![PWA Ready](https://img.shields.io/badge/PWA-Offline%20Ready-green.svg)]()

Dashboard Web tattica di nuova generazione con design **Dark Glassmorphism**, supporto **Web Bluetooth (BLE)** e **Wi-Fi REST/LAN** per nodi radioamatoriali **MeshCom 4.x / 5.x** (ESP32, ESP32-S3, Heltec V1/V2/V3, LilyGO T-Beam, T-Deck, RAK WisBlock, T-Echo, RP2040, ecc.).

Sostituisce e potenzia le interfacce standard offrendo una suite operativa completa per il traffico radio LoRa, la telemetria, il tracciamento APRS satellitare e l'analisi RF spettrale SDR.

---

## 📸 Anteprime Interfaccia

### 1. Spettro RF SDR & Cascata (Waterfall) in Ricezione Live
![Stato Connesso Reale](screenshot_connected_real.png)

### 2. Standby Pulito a Riposo (Zero Dati Simulati quando Disconnesso)
![Stato Disconnesso Standby](screenshot_disconnected_clean.png)

### 3. Connessione Dual-Mode: Bluetooth Low Energy + Wi-Fi / LAN REST
![Connessione Dual-Mode](screenshot_connection_dual.png)

---

## ⚡ Caratteristiche Principali

1. **🛡️ Zero Finzioni & Standby Pulito**:
   - Quando nessun dispositivo è collegato, la dashboard non mostra finte frequenze, finti callsign né barre casuali: rimane in elegante standby tattico con avvisi chiari.
   - Tutti i parametri (nominativo, frequenza, potenza TX, sensori meteo e coordinate GPS) vengono popolati **esclusivamente dai dati reali** trasmessi dal nodo.

2. **🌍 Compatibilità Hardware & Frequenze Universale**:
   - **Auto-Detection Microcontrollore**: Riconosce automaticamente **ESP32**, **ESP32-S3** (Heltec V3, T-Beam Supreme, T-Deck), **nRF52840** (RAK4631, T-Echo) e **RP2040**.
   - **Tutte le Bande Mondiali**: Si adatta istantaneamente a frequenze **433 MHz** (EU), **868 MHz** (EU), **915 MHz** (US/AU) o frequenze personalizzate, riallineando dinamicamente la frequenza centrale e le scale graduate dello spettro.

3. **🔌 Connessione Hardware Ibrida (BLE + Wi-Fi)**:
   - **Bluetooth Low Energy (BLE)**: Scansione tramite Nordic UART Service (NUS) compatibile con tutti i moduli portatili.
   - **Wi-Fi / Rete LAN**: Connessione diretta tramite IP locale a nodi fissi, gateway o SoftAP (default `192.168.4.1`) con polling delle API REST native.
   - Terminale integrato per comandi CLI diretti (`--info`, `--wx`, `--pos`, `--nodeset`, `--wifiset`, `--mheard`, `--batt`, `--help`).

4. **💬 Chat & Gestione Canali**:
   - Ricezione e trasmissione su canali LoRa Broadcast (`*`), Nazionali (`222` / `22251`), Emergenza (`999`) e messaggi diretti (DM).
   - **Zero caratteri corrotti**: Decodifica binaria nativa del protocollo APRS con rimozione dei byte di coda e gestione frame ACK (`0x41`) con conferme grafiche (`✓✓`).

5. **📡 Analizzatore di Spettro RF SDR & Cascata (Waterfall)**:
   - Traccia FFT dinamica a 60 FPS con bagliore neon ciano e inviluppo ambra dei picchi (*Peak-Hold*) per visualizzare la sagoma del chirp LoRa (125 kHz BW).
   - Cascata SDR scorrevole con palette selezionabili (*Tactical SDR*, *Heatmap Termica*, *Fosfori Verdi*).
   - Metriche RF: lettura RSSI, **S-Meter radioamatoriale standard IARU**, margine SNR e Noise Floor.
   - Trend temporale degli ultimi 40 pacchetti e classifica nodi ordinata per intensità con tasto rapido `DM`.

6. **🗺️ Mappa APRS Satellitare HD Offline**:
   - Tracciamento stazioni e beacon GPS vettoriali in tempo reale.
   - Layer cartografici ad alta risoluzione **100% gratuiti e senza API key**: *Esri World Imagery (Satellite HD)*, *OpenStreetMap* e *OpenTopoMap*.

7. **🌤️ Telemetria Sensori & Meteo WX**:
   - Monitoraggio sensori ambientali reali (temperatura, umidità, pressione barometrica, quota altimetrica) ed energetici (tensione e percentuale batteria).

8. **🌐 Matrice Vicini (MeshCom 5)**:
   - Matrice dei nodi adiacenti con statistiche di qualità del collegamento radio (LQI).

---

## 🚀 Come Eseguire il Progetto

### Opzione 1: GitHub Pages (Consigliato per mobilità su qualsiasi PC o Smartphone)
La dashboard è un'applicazione Web autonoma. Se attivata su **GitHub Pages**:
1. Nel tuo repository su GitHub, vai in **Settings** > **Pages**.
2. Sotto **Build and deployment**, seleziona il branch `main` e la cartella `/ (root)`, poi clicca **Save**.
3. In meno di un minuto avrai un link protetto **HTTPS** (es. `https://<tuo-utente>.github.io/<tuo-repo>/`).
4. Aprendo quel link da qualsiasi computer o smartphone Android (con Chrome o Edge), potrai connetterti al nodo via Bluetooth istantaneamente senza dover installare nulla!

### Opzione 2: Esecuzione in Locale
Puoi clonare il repository su qualsiasi computer (Linux, macOS, Windows):

```bash
# 1. Clona il repository
git clone https://github.com/dmalaboratory/8bit_meshcom.git
cd 8bit_meshcom

# 2. Avvia la dashboard locale
python3 start_dashboard.py
```

Apri quindi il browser su **`http://localhost:8080`**.

---

## 🌐 Compatibilità Bluetooth (Web Bluetooth)

- **Desktop**: Google Chrome, Microsoft Edge, Opera, Brave (abilitando Bluetooth).
- **Android**: Google Chrome, Microsoft Edge, Samsung Internet.
- **Linux**: Richiede Bluetooth attivo e BlueZ (in esecuzione di default su tutte le distribuzioni moderne).
- **iOS (iPhone/iPad)**: Safari non supporta Web Bluetooth di default; utilizzare browser compatibili come **Bluefy** o **WebBLE**.

---

## 📄 Licenza
Rilasciato per la community radioamatoriale mondiale. 73 de IU0TGU!
