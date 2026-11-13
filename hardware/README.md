# 🛠️ MeshCom E22 DevBoard & Hardware Lab

Progetto hardware e archivio PCB per nodi radioamatoriali **MeshCom / Meshtastic** ad alta potenza (fino a 1-2 Watt RF / 30-33 dBm), basato sull'architettura **Hydra devboard** ([github.com/fzellini/meshtastic-devboard](https://github.com/fzellini/meshtastic-devboard)) e ottimizzato per la massima affidabilità energetica e radiofrequenza.

---

## 📸 Galleria e Render 3D

| Vista Assonometrica 3D | Vista Top Circuitale |
| :---: | :---: |
| ![Render Assonometrico](Renders/render_isometric.png) | ![Render Top](Renders/render_top.png) |

---

## 📌 Specifiche Hardware — Release Corrente (Rev 1.0)

- **Microcontrollore**: ESP32 (ESP32-D0WD-V3, modulo ESP32-WROOM-32 / formato DevKitC v4 a 38 pin).
- **Modulo RF LoRa**: 
  - **Ebyte E22-400M30S** (Semtech SX1268, banda UHF 433 MHz, potenza fino a +30 dBm / 1W).
  - **Ebyte E22-900M30S** (Semtech SX1262, banda 868 MHz / 915 MHz, fino a +30 dBm / 1W o versione 33 dBm / 2W).
- **Alimentazione USB**:
  - Porta **USB Type-C** nativa con resistori di pull-down **5.1 kΩ su CC1 e CC2** per il corretto handshake con alimentatori intelligenti USB-PD e cavi C-to-C.
- **Stadio Regolazione Tensione (LDO)**:
  - Regolatore 3.3V a basso drop-out ad alta corrente (minimo **1.0A – 1.5A continui**) in package SOT-223 (es. AMS1117-3.3, AP2112K o RT9080) per sostenere senza flessioni i transienti di assorbimento in trasmissione LoRa (~650-750 mA di picco a 30 dBm).
  - Condensatori elettrolitici / ceramici a basso ESR a monte e a valle del regolatore.
- **Porta Espansione I2C (Display / Sensori)**:
  - Header maschio 4-pin con pinout standard maker: **`GND — VCC (3.3V) — SCL — SDA`** per display OLED 0.96"/1.3" (SSD1306/SH1106) e sensori ambientali BME280/BMP280/AHT20.
- **Interfaccia Utente & LED**:
  - Pulsante Utente/SafeBoot su **GPIO 0**.
  - LED di stato attività RF/Rete su **GPIO 2**.

---

## 🔌 Pinout & Mappatura Segnali (ESP32 ⟷ Ebyte E22)

| Segnale Hardware | Modulo Ebyte E22 | Pin ESP32 | Descrizione / Ruolo |
| :--- | :--- | :--- | :--- |
| **LoRa SCK** | Pin 14 (SCK) | **GPIO 5** | Clock seriale bus SPI |
| **LoRa MISO** | Pin 13 (MISO) | **GPIO 19** | Master In Slave Out SPI |
| **LoRa MOSI** | Pin 15 (MOSI) | **GPIO 27** | Master Out Slave In SPI |
| **LoRa CS (NSS)** | Pin 12 (NSS) | **GPIO 18** | Chip Select LoRa (attivo basso) |
| **LoRa RST** | Pin 11 (NRST) | **GPIO 23** | Reset hardware del chip SX126x |
| **LoRa BUSY** | Pin 16 (BUSY) | **GPIO 32** | Linea di attesa elaborazione comando |
| **LoRa DIO1** | Pin 10 (DIO1) | **GPIO 33** | Interrupt ricezione pacchetto (RX_DONE) |
| **E22 RXEN** | Pin 6 (RXEN) | **GPIO 14** | Commutazione switch RF in ricezione |
| **E22 TXEN** | Pin 7 (TXEN) | **GPIO 13** | Abilitazione finale amplificatore (PA) in trasmissione |
| **I2C SCL** | — | **GPIO 22** | Bus I2C Clock (Display OLED / Meteo) |
| **I2C SDA** | — | **GPIO 21** | Bus I2C Data (Display OLED / Meteo) |
| **USER / BOOT** | — | **GPIO 0** | Tasto funzione / SafeBoot / Download |
| **STATUS LED** | — | **GPIO 2** | LED segnalazione attività |

---

## 📂 Contenuto della Directory Hardware

```text
hardware/
├── KiCad/                               # Sorgenti CAD elettronico
│   ├── meshcom-e22-devboard.kicad_pro   # File progetto KiCad
│   ├── meshcom-e22-devboard.kicad_sch   # Schema elettrico completo
│   ├── meshcom-e22-devboard.kicad_pcb   # Layout circuitale e sbroglio tracce RF
│   └── meshcom-e22-devboard.kicad_prl   # Impostazioni locali KiCad
│
├── JLCPCB/                              # File pronti per la fabbricazione e montaggio SMD
│   ├── gerbers.zip                      # File Gerber per produzione PCB
│   ├── bom.csv                          # Bill of Materials con codici LCSC
│   ├── cpl.csv                          # Coordinate Pick-and-Place SMD
│   └── assembly.zip                     # Pacchetto compresso tutto-in-uno
│
└── Renders/                             # Visualizzazioni grafiche e 3D
    ├── render_top.png                   # Vista superiore PCB renderizzata
    ├── render_isometric.png             # Vista 3D prospettica
    └── pcb_layout.svg                   # Tracciato vettoriale delle piste
```

---

## 🏭 Produzione e Ordinazione su JLCPCB

1. **Caricamento Gerber**:
   - Collegati a [jlcpcb.com](https://jlcpcb.com) e carica il file `JLCPCB/gerbers.zip`.
   - Parametri consigliati:
     - **Layers**: 2 strati.
     - **Spessore PCB**: 1.6 mm.
     - **Finitura superficiale**: **ENIG (oro chimico)** raccomandata per preservare l'integrità del segnale RF e le saldature SMD del modulo Ebyte. In alternativa **HASL Lead-Free**.
     - **Colore Solder Mask**: Nero opaco, Blu radioamatore o Verde classico.
2. **Assemblaggio SMT (Opzionale per passivi e LDO)**:
   - Seleziona **SMT Assembly** e carica `JLCPCB/bom.csv` e `JLCPCB/cpl.csv`.
   - Verifica nell'anteprima 3D l'orientamento dei diodi, condensatori polarizzati e connettore USB-C prima di confermare.

---

## 🚀 Roadmap: Futuri Progetti Hardware & PCB

Per i futuri sviluppi della piattaforma MeshCom sono previste le seguenti evoluzioni hardware:

### 🌟 Rev 2.0 — "MeshCom Solar Repeater & High-Power Gateway"
- **MCU Upgrade**: Passaggio a **ESP32-S3-WROOM-1** (Dual-Core Xtensa LX7 a 240 MHz, USB nativo OTG/JTAG per debug avanzato, 8MB Flash + 2MB PSRAM).
- **Ricevitore GNSS/GPS Integrato**:
  - Chip u-blox **MAX-M10S** o **ATGM336H** con connettore u.FL per antenna GPS patch attiva/passiva.
  - Sincronizzazione oraria satellitare ad altissima precisione per nodi APRS fissi o mobili.
- **Gestione Alimentazione Solare & Batteria (BMS)**:
  - Controller di carica solare integrato con supporto **Li-Ion (3.7V - 18650/21700)** o **LiFePO4 (3.2V)** per installazioni ad alta quota con temperature estreme.
  - Circuito di **Power Path automatico** (priorità pannello solare/USB, zero interruzioni del nodo).
  - Circuito ADC di misura per monitorare in tempo reale via telemetria la tensione del pannello e lo stato di carica della batteria.
- **Sezione RF Ottimizzata**:
  - Filtro passa-basso RF (LPF a 5 o 7 poli) o filtro SAW per soppressione delle armoniche superiori secondo le normative IARU.
  - Connettore coassiale SMA femmina da pannello saldato direttamente a bordo PCB con piano di massa rinforzato.
- **Case Industriale IP67**:
  - Predisposizione fori di fissaggio per box stagno esterno da palo con staffa antivento.

### 🌟 Rev 2.5 — "MeshCom Micro-Tracker Tattico"
- Form-factor ultra-compatto tascabile.
- Display integrato **e-Paper (E-Ink) a bassissimo consumo** o display OLED frontale a filo case.
- Modulo nRF52840 o ESP32-C3 per consumi minimi in sleep (<15 µA) con autonomia di settimane su singola cella.
- Sensore ambientale integrato Bosch BME680 (temperatura, umidità, pressione e qualità dell'aria VOC).
