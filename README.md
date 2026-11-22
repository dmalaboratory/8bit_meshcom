# 📡 8BitWave MeshCom v2.0
### *Autonomous Tactical LoRa Ham Radio Node & Mobile Suite*
**Designed and Developed by IU0TGU**

[![MeshCom](https://img.shields.io/badge/MeshCom-4.0%20Core-blue.svg)](https://icssw.org)
[![Callsign](https://img.shields.io/badge/Callsign-IU0TGU-orange.svg)]()
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)
[![Android App](https://img.shields.io/badge/Android%20App-1.2%20MB-emerald.svg)](8BitWave-MeshCom.apk)
[![WebGUI](https://img.shields.io/badge/WebGUI-Embedded%20ESP32-red.svg)]()
[![Hardware](https://img.shields.io/badge/Hardware-KiCad%20v8%20%7C%20JLCPCB-purple.svg)](hardware/)

---

## ⚡ Panoramica del Progetto

**8BitWave MeshCom v2.0** è una piattaforma completa per comunicazioni tattiche radioamatoriali off-grid e gateway **MeshCom 4.0**. Integra una **WebGUI retro-cyberpunk a 8-bit** responsive ospitata direttamente nella memoria flash dell'ESP32 (`http://192.168.4.1`), un'**applicazione Android nativa companion** (`8BitWave-MeshCom.apk`), una **suite di strumenti radioamatoriali avanzati** (SDR Waterfall, calcolo Fresnel 3D, RDF Direction Finding, tracciatore satelliti, tasto telegrafico CW) e il progetto hardware completo **PCB v2.0 Solar Repeater (1W/2W)** pronto per la produzione con JLCPCB.

```
                           ┌──────────────────────────┐
                           │    🛰️ SATELLITI & APRS    │
                           │     (ISS / SO-50 / LORa) │
                           └─────────────┬────────────┘
                                         ▼
┌──────────────────────┐         ┌──────────────┐         ┌──────────────────────┐
│  📱 App Android      │  BLE /  │  📡 NODO     │  LoRa   │  🌐 Rete MeshCom     │
│  8BitWave-MeshCom    │◄───────►│  ESP32 / S3  │◄───────►│  Nodi & Gateway      │
│  (1.2 MB Standalone) │  Wi-Fi  │  (Flash 0x0) │ 433/868 │  Ripetitori Nazionali│
└──────────────────────┘         └──────┬───────┘         └──────────────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │  💻 WebGUI Tattica 8-Bit    │
                         │  Mappa Satellite HD Hybrid  │
                         │  SDR Waterfall & RF Tools   │
                         └─────────────────────────────┘
```

---

## 📥 Download Rapidi (Binari & Pacchetti)

Tutti i file sono pronti all'uso, compilati e collaudati:

| Pacchetto | Descrizione | File / Download | Dimensione |
| :--- | :--- | :--- | :--- |
| 📱 **App Android** | Applicazione companion con scansione AP & BLE | [`8BitWave-MeshCom.apk`](8BitWave-MeshCom.apk) | `1.2 MB` |
| ⚡ **ESP32 + Ebyte E22** | Immagine FULL Unificata pronta al flash (`0x0`) | [`8BitWave-MeshCom-FULL-0x0.bin`](8BitWave-MeshCom-FULL-0x0.bin) | `2.9 MB` |
| ⚡ **ESP32 + Ebyte E22** | Partizione applicativa firmware standard | [`firmware.bin`](firmware.bin) | `2.1 MB` |
| 📟 **Heltec WiFi LoRa 32 V3** | Immagine FULL Unificata pronta al flash (`0x0`) | [`Heltec V3 FULL-0x0.bin`](firmwares/Heltec/heltec_wifi_lora_32_V3/8BitWave-MeshCom-heltec_wifi_lora_32_V3-FULL-0x0.bin) | `2.8 MB` |
| 📟 **Heltec WiFi LoRa 32 V3** | Partizione applicativa firmware Heltec V3 | [`Heltec V3 firmware.bin`](firmwares/Heltec/heltec_wifi_lora_32_V3/8BitWave-MeshCom-heltec_wifi_lora_32_V3-firmware.bin) | `2.0 MB` |
| 🧭 **LilyGO TTGO T-Beam** | Immagine FULL Unificata pronta al flash (`0x0`) | [`T-Beam FULL-0x0.bin`](firmwares/LilyGO/ttgo_tbeam/8BitWave-MeshCom-ttgo_tbeam-FULL-0x0.bin) | `3.0 MB` |
| 🧭 **LilyGO TTGO T-Beam** | Partizione applicativa firmware T-Beam | [`T-Beam firmware.bin`](firmwares/LilyGO/ttgo_tbeam/8BitWave-MeshCom-ttgo_tbeam-firmware.bin) | `2.2 MB` |
| 🛠️ **Hardware KiCad v8** | Progetto completo Schemi + PCB DevBoard v2.0 | [`meshcom-e22-kicad-v2.0.zip`](hardware/KiCad/meshcom-e22-kicad-project-v2.0.zip) | `4.2 MB` |
| 🏭 **JLCPCB SMT Package** | Gerber, Distinta componenti BOM e CPL assemblaggio | [`hardware/JLCPCB/`](hardware/JLCPCB/) | `Cartella` |

---

## ✨ Funzionalità Esclusive

### 🗺️ Mappa Satellite HD Ibrida (Zero API Keys)
- Layer predefinito ad alta risoluzione: **Esri World Imagery** combinato con **Esri World Boundaries and Places**.
- Nessuna chiave API richiesta: funziona immediatamente e gratuitamente.
- Mostra in tempo reale tutti i nodi ascoltati (`MHeard`), con icone dedicate, popup telemetrici (tensione batteria, altitudine, RSSI/SNR) e tracciamento rotte APRS.

### 💬 Chat Tattica & Gruppi Personalizzati Illimitati
- Canali predefiniti: `TUTTI (Broadcast)`, `EMERGENZA 112`, `ITALIA HAM`, `DX LORa`.
- **Nuovo Gestore Gruppi Personalizzati**: creazione immediata con ID esadecimale (00-FF), etichetta personalizzata, colore badge dedicato e possibilità di rimozione.
- Trasmissione immediata ai nodi nel raggio e routing mesh automatico.

### 📶 SDR Waterfall & Spettrogramma RF Live
- Monitor spettrale grafico in tempo reale del traffico RF sulla frequenza di canale (433.175 MHz / 868 MHz).
- Spettrogramma a cascata (Waterfall) dinamico a colori termici, calcolo FFT a 64 bin, Noise Floor, RSSI istantaneo e visualizzazione Bit Error Rate.

### 🧮 Suite Strumenti Radioamatoriali (by IU0TGU)
1. **Calcolo Ellissoide di Fresnel 3D & Link Budget**:
   - Tracciamento visivo del 1° e 2° ellissoide di Fresnel su canvas interattivo.
   - Calcolo istantaneo del raggio massimo della prima zona $R_1$, Free Space Path Loss (FSPL) in dB e stima del Fade Margin in base a guadagno antenne e potenza di trasmissione.
2. **Radio Direction Finding (RDF) & Triangolazione**:
   - Inserimento stazioni di ascolto con coordinate geografiche e azimuth stimato.
   - Diagramma polare interattivo e calcolo geometrico del punto di convergenza/intersezione con marker proiettato direttamente sulla mappa.
3. **Tracciatore Satelliti Radioamatoriali**:
   - Radar azimutale/elevazione (Sky Polar Chart) e mappa di ground track orbitale per satelliti FM/APRS (ISS ZARYA, SO-50, AO-91).
   - Predizione passaggi, elevazione massima (AOS/LOS/MEL) e calcolo del Doppler shift su downlink LoRa/VHF.
4. **Tasto Telegrafico CW Virtuale**:
   - Oscillatore audio integrato con generatore di tono continuo (Web Audio API).
   - Velocità regolabile da 10 a 35 WPM, frequenza sidetone regolabile da 400 a 1000 Hz, traduttore bidirezionale Testo ↔ Codice Morse.
5. **Topologia Mesh 3D Dinamica**:
   - Grafico interattivo a forze di tutti i nodi e collegamenti della rete, con colorazione dinamica in base all'SNR e numero di salti (hop count).

### 📱 100% Mobile Responsive
- Interfaccia progettata per smartphone e tablet da 320px a 4K.
- Tabelle telemetriche e MHeard con scrolling fluido touch senza alcun overflow orizzontale.
- Cassetto di navigazione a scomparsa laterale con accesso istantaneo a tutti i menu tattici.

---

## ⚡ Guida Rapida al Flashing

### Metodo 1: Web Flasher da Browser (Consigliato)
Nessuna installazione richiesta, compatibile con Google Chrome e Microsoft Edge:
1. Collega la scheda via cavo USB al PC.
2. Apri il Web Flasher ufficiale: **[https://esptool.oevsv.at/](https://esptool.oevsv.at/)**
3. Clicca su **Connect** e seleziona la porta seriale USB.
4. Scegli il file unificato **`FULL-0x0.bin`** (offset `0x0000`).
5. Clicca su **Program** e attendi il completamento.

### Metodo 2: Riga di Comando con `esptool.py`

#### Per ESP32 Classico (Ebyte E22 DevKitC / T-Beam V1.1 / LoRa32):
```bash
# Sostituisci /dev/ttyUSB0 con la tua porta (es. COM3 su Windows)
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
    write_flash -fm dout 0x0 8BitWave-MeshCom-FULL-0x0.bin
```

#### Per ESP32-S3 (Heltec WiFi LoRa 32 V3 / T-Beam Supreme / T-Deck):
```bash
esptool.py --chip esp32s3 --port /dev/ttyACM0 --baud 921600 \
    write_flash 0x0 firmwares/Heltec/heltec_wifi_lora_32_V3/8BitWave-MeshCom-heltec_wifi_lora_32_V3-FULL-0x0.bin
```

> [!TIP]
> Se durante la connessione compaiono puntini continui (`Connecting......`), tieni premuto il tasto **BOOT** (GPIO 0) sulla scheda finché non inizia la scrittura, poi rilascialo.

---

## 📱 App Android Companion

L'applicazione nativa **`8BitWave-MeshCom.apk`** (1.2 MB) offre:
- **Schermata di Avvio Pulita**: Connessione istantanea in un tocco al nodo via **Wi-Fi AP (`192.168.4.1`)** o **Rete Locale LAN (`192.168.1.x`)**.
- **Scansione Bluetooth LE**: Accoppiamento diretto con i nodi MeshCom dotati di BLE.
- **Visualizzazione Ottimizzata**: WebView accelerata con rendering nativo, perfetta visualizzazione di mappe e grafici spettrometrici verticali.

---

## 📋 Matrice di Compatibilità Hardware

Tutte le immagini firmware possono essere compilate in un comando con lo script incluso:
```bash
# Esempio: compila e unifica l'immagine per Heltec V3
python3 build_all_devices.py --target heltec_wifi_lora_32_V3

# Visualizza tutti i 26+ target disponibili
python3 build_all_devices.py --list
```

### Sintesi Dispositivi Supportati:

| Produttore | Modello Dispositivo | MCU | Chip LoRa | Display / Note | Binario Pronto |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Heltec** | WiFi LoRa 32 V3 / V3.2 | ESP32-S3 | SX1262 | OLED 0.96" | ✅ Incluso |
| **Heltec** | WiFi LoRa 32 V4 | ESP32-S3 | SX1262 | OLED 0.96", PMU | ⏳ Script |
| **Heltec** | WiFi LoRa 32 V2 | ESP32 | SX1276/78 | OLED 0.96" | ⏳ Script |
| **Heltec** | Wireless Stick V3 | ESP32-S3 | SX1262 | Mini OLED 0.49" | ⏳ Script |
| **Heltec** | Wireless Tracker | ESP32-S3 | SX1262 | TFT Colori + GPS | ⏳ Script |
| **Heltec** | Wireless Paper / Vision Master | ESP32-S3 | SX1262 | E-Paper 2.13"/2.9" | ⏳ Script |
| **LilyGO** | TTGO T-Beam V1.1 / V1.2 | ESP32 | SX1276/78 | GPS + 18650 | ✅ Incluso |
| **LilyGO** | TTGO T-Beam SX1262 / SX1268 | ESP32 | SX1262/68 | GPS + 18650 | ⏳ Script |
| **LilyGO** | T-Beam Supreme / 1W | ESP32-S3 | SX1262 1W | Quectel L76K + PMU | ⏳ Script |
| **LilyGO** | T-Deck / Plus / Pro | ESP32-S3 | SX1262 | Tastiera QWERTY, IPS | ⏳ Script |
| **LilyGO** | T-ETH-Elite 1262 | ESP32-S3 | SX1262 | Porta Ethernet RJ45 | ⏳ Script |
| **Ebyte DIY** | ESP32 DevKitC + E22-400M30S | ESP32 | SX1268 1W | +30 dBm (1.000 mW) | ✅ Incluso |
| **Ebyte DIY** | ESP32 DevKitC + E22-900M30S | ESP32 | SX1262 1W | +30 dBm 868/915MHz | ⏳ Script |
| **Ebyte DIY** | ESP32-S3 DevKitC-1 N16R8 | ESP32-S3 | SX1262/68 | 16MB Flash, 8MB PSRAM| ⏳ Script |
| **LoRa-APRS** | Schede Tracker E22 / RA-01 | ESP32 | SX1268/78 | Dedicato LoRa-APRS | ⏳ Script |

---

## 🛠️ Scheda Hardware v2.0 (KiCad & JLCPCB)

Nella directory [`hardware/`](hardware/) è disponibile il progetto completo per la realizzazione della devboard ad alta potenza per ripetitori solari:

- **Dimensioni standard**: 100.0 mm × 80.0 mm (budget tier JLCPCB 2-layer).
- **Stadio di Potenza Boost FP6277**: Convertitore sincrono 5.5A switch, 5V / 2.5A continui, dimensionato per picchi RF a piena potenza (+30 dBm / +33 dBm).
- **Inseguitore Solare MPPT CN3791**: Per pannelli fotovoltaici 6V - 28V con LED di stato CHG e DONE.
- **Protezione BMS LiPo 1S**: Chip DW01A + doppio MOSFET FS8205A (cutoff sovrascarica 2.4V, soglia cortocircuito 6A).
- **Interfaccia GNSS / GPS UART**: Header dedicato per moduli u-blox NEO-6M/8M con linea PPS su interrupt.
- **Espansione Sensori**: Connettore STEMMA QT / Qwiic (I2C), morsetto DS18B20 1-Wire, header I2C per OLED, BME280 e voltmetro/amperometro INA219.

---

## 🗂️ Struttura della Repository

```
8bit_meshcom/
├── 8BitWave-MeshCom.apk         # 📱 App Android nativa standalone (1.2 MB)
├── 8BitWave-MeshCom-FULL-0x0.bin# ⚡ Immagine firmware unificata ESP32 E22 DevKitC (0x0)
├── firmware.bin                 # ⚡ Partizione applicazione standard ESP32 E22 DevKitC
├── index.html                   # 💻 Tactical WebGUI 8-Bit (Satellite HD, SDR, Ham Tools)
├── build_all_devices.py         # 🔨 Script compilatore per tutti i 26+ target hardware
├── dev_server.py                # 🧪 Server di sviluppo locale con telemetria simulata
├── firmwares/                   # 📦 Archivio firmware organizzato per produttore
│   ├── Ebyte_DIY/               # Immagini per DevKitC e moduli E22 1W
│   │   └── E22-DevKitC/
│   └── Heltec/                  # Immagini per moduli Heltec Automation
│       └── heltec_wifi_lora_32_V3/
├── hardware/                    # 🛠️ Progetto Hardware KiCad v8 & JLCPCB
│   ├── KiCad/                   # Schemi elettrici e PCB layout (.kicad_sch, .kicad_pcb)
│   ├── JLCPCB/                  # Gerber, distinta base (BOM) e coordinate CPL per SMT
│   ├── Exports/                 # Esportazioni PDF, DXF e 3D STEP
│   └── README.md                # Documentazione dettagliata hardware v2.0
├── flash_official.sh            # 🚀 Script bash di flashing rapido
├── sync_to_esp32.sh             # 🔄 Script di sincronizzazione WebGUI -> Firmware
└── README.md                    # 📖 Questo documento
```

---

## 👥 Autore & Riconoscimenti

- **Sviluppo & Architettura**: **IU0TGU** (8BitWave Project)
- **Protocollo & Firmware Base**: Basato su **MeshCom 4.0** del team **ÖVSV / ICSSW** ([icssw.org](https://icssw.org) / [esptool.oevsv.at](https://esptool.oevsv.at))
- **Mappe**: Esri ArcGIS Living Atlas (World Imagery & Boundaries)
- **Licenza**: Distribuito sotto licenza open-source GNU GPL-3.0.
