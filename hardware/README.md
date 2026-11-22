# 🛠️ MeshCom E22 DevBoard v2.0 — Guida Hardware & PCB
### *Solar Repeater & High-Power RF Gateway (1W / 2W SX1268 / SX1262)*

Progetto hardware e archivio PCB per nodi radioamatoriali e gateway **MeshCom / Meshtastic** ad alta potenza (fino a **+30 dBm / 1 Watt** e **+33 dBm / 2 Watt RF**), basato sull'architettura **Hydra devboard** ([github.com/fzellini/meshtastic-devboard](https://github.com/fzellini/meshtastic-devboard)) e potenziato con gestione solare MPPT, protezione batteria BMS, stadio boost sincrono ad alta corrente, modulo GNSS/GPS hardware e bus sensori ambientali.

---

## 📌 Novità Architetturali della Release v2.0

La release **v2.0** introduce un'architettura completa per postazioni fisse da ripetitore solare, gateway e nodi mobili tattici, preservando rigorosamente le dimensioni standard economiche di **100.0 mm × 80.0 mm** (budget tier JLCPCB a 2 strati):

1. **Stadio di Potenza FP6277 (5.5A Switch, 5V / 2.5A Continui)**:
   - Sostituisce il vecchio convertitore asincrono MT3608 con il convertitore boost sincrono monolitico **FP6277** (SOP-8-EP) ad altissima efficienza (>93%).
   - Dimensionato per gestire i picchi transitori di trasmissione del finale RF da **+33 dBm (~2 Watt)**, con assorbimenti impulsivi fino a **1.6A – 1.8A su linea 5V** e picchi di scarica da cella LiPo fino a **3.2A**.
   - Induttore di potenza schermato 4.7 µH 4.5A (6045), filtraggio combinato con 2×22 µF 16V 1206 ceramici X5R e condensatore elettrolitico bulk a basso ESR da 470 µF 16V. Tracce ad alta corrente allargate a **0.8 mm** (capacità continua >2.5A, picco >4.5A).

2. **Caricatore Solare MPPT a Bordo (CN3791)**:
   - Controller buck step-down con inseguimento del punto di massima potenza solare (MPPT) per pannelli fotovoltaici con tensione nominale da **6V a 28V**.
   - Morsettiera industriale a vite da 5.08 mm (**J_SOLAR**, Phoenix Contact MKDS).
   - LED di stato a bordo: **LED_CHG** (Rosso - In Carica) e **LED_DONE** (Verde - Batteria Carica).

3. **Circuito Power-Path Automatico (Zero-Switching Glitch)**:
   - Commutazione istantanea e senza interruzioni tra alimentazione solare/USB-C e batteria LiPo mediante P-MOSFET **AO3401A** (30V, 4.2A) e diodo Schottky **SS34** (40V, 3A).
   - In presenza di sorgente esterna (USB-C o Pannello Solare), il carico del sistema (ESP32 + modulo LoRa ad alta potenza) viene alimentato direttamente dalla fonte esterna senza cicli parassiti di carica/scarica sulla batteria.

4. **Protezione Batteria LiPo 1S Integrata (BMS Hardware)**:
   - Connettore polarizzato **JST-PH 2.0 mm 2-pin** (**J_BATT**).
   - Circuito di protezione cella dedicato con IC **DW01A** e doppio N-MOSFET di potenza **FS8205A** (TSSOP-8, 20V 6A, $R_{DS(on)} < 25\text{ m}\Omega$).
   - Protezioni attive:
     - Sovraccarica: cutoff a **4.25V ± 0.05V**
     - Sovrascarica: cutoff a **2.40V ± 0.10V**
     - Sovracorrente / cortocircuito: soglia di intervento rapido a **6.0A**.

5. **Monitor Telemetrico Batteria via ADC**:
   - Partitore resistivo di precisione 1% (100 kΩ / 100 kΩ) con condensatore ceramico di filtraggio rumore da 100 nF su **GPIO 35** (`BATT_SENSE`).
   - Tensione massima letta dall'ADC: $V_{ADC} = 4.20\text{V} / 2 = 2.10\text{V}$, perfettamente lineare e all'interno della dinamica ottimale dell'ADC dell'ESP32.

6. **Interfaccia GNSS / GPS Hardware su UART2**:
   - Header dedicato 5-pin passo 2.54 mm (**J_GPS**) per moduli u-blox NEO-6M/NEO-8M o Quectel/ATGM336H.
   - Segnali: `+3V3`, `GPS_RXD` (ESP32 GPIO17 TX2), `GPS_TXD` (ESP32 GPIO16 RX2), `GPS_PPS` (ESP32 GPIO4) e `GND`.
   - Linea **PPS (Pulse Per Second)** connessa a interrupt hardware per la sincronizzazione temporale al millisecondo nei pacchetti APRS e time-slot MeshCom.

7. **Espansione Sensori Ambientali (Qwiic / STEMMA QT + 1-Wire + I2C)**:
   - Connettore orizzontale micro-JST **STEMMA QT / Qwiic JST-SH 1.0 mm 4-pin** (**J_QWIIC**) per il collegamento a caldo di sensori Adafruit/SparkFun senza saldature.
   - Connettore dedicato per sensore di temperatura esterno Dallas **DS18B20** a 3-pin (**J_DS18**) con resistore di pull-up integrato da 4.7 kΩ su **GPIO 25**.
   - Header I2C standard compatibili con display OLED SSD1306/SH1106 (**J_OLED**), sensore barometrico BME280/BMP280 (**J_BME**) e sensore voltmetrico/amperometrico bidirezionale INA219 (**J_INA**).
   - Resistori di pull-up I2C a bordo da **2.2 kΩ** su SDA (GPIO 21) e SCL (GPIO 22).

---

## 🔌 Mappatura Pinout Completa (ESP32 DevKitC v4 38-Pin)

| Segnale Hardware | Modulo Ebyte E22 | Connettori / Periferiche | Pin ESP32 | Ruolo nel Firmware MeshCom / Meshtastic |
| :--- | :--- | :--- | :--- | :--- |
| **LoRa SCK** | Pin 18 (SCK) | — | **GPIO 18** | Clock SPI hardware per transceiver SX126x |
| **LoRa MISO** | Pin 16 (MISO) | — | **GPIO 19** | Master In Slave Out bus SPI |
| **LoRa MOSI** | Pin 17 (MOSI) | — | **GPIO 23** | Master Out Slave In bus SPI |
| **LoRa NSS / CS** | Pin 19 (NSS) | — | **GPIO 5** | Chip Select LoRa (attivo basso) |
| **LoRa NRST** | Pin 15 (NRST) | — | **GPIO 33** | Reset hardware chip Semtech |
| **LoRa BUSY** | Pin 14 (BUSY) | — | **GPIO 27** | Segnale occupato transceiver RF |
| **LoRa DIO1** | Pin 13 (DIO1) | — | **GPIO 32** | Interrupt ricezione pacchetto (RX_DONE) |
| **E22 RXEN** | Pin 6 (RXEN) | — | **GPIO 14** | Switch RF: abilitazione percorso LNA in RX |
| **E22 TXEN** | Pin 7 (TXEN) | — | **GPIO 13** | Switch RF: abilitazione finale di potenza (PA) |
| **GPS TXD (Data Out)**| — | `J_GPS` Pin 3 (TXD) | **GPIO 16** | UART2 RX ESP32 (Ricezione frasi NMEA) |
| **GPS RXD (Data In)** | — | `J_GPS` Pin 2 (RXD) | **GPIO 17** | UART2 TX ESP32 (Configurazione GNSS) |
| **GPS PPS** | — | `J_GPS` Pin 4 (PPS) | **GPIO 4** | Time-pulse 1 Hz sincronizzazione oraria |
| **1-Wire Data** | — | `J_DS18` Pin 2 (DAT) | **GPIO 25** | Bus digitale sensore temperatura Dallas DS18B20 |
| **Battery ADC Sense** | — | Partitore R_BAT1/R_BAT2 | **GPIO 35** | Lettura analogica tensione cella LiPo (x2) |
| **I2C SCL** | — | OLED, BME280, INA, QWIIC | **GPIO 22** | Bus I2C Clock (pull-up 2.2kΩ a bordo) |
| **I2C SDA** | — | OLED, BME280, INA, QWIIC | **GPIO 21** | Bus I2C Data (pull-up 2.2kΩ a bordo) |
| **USER / BOOT** | — | Modulo ESP32 DevKitC | **GPIO 0** | Tasto funzione utente / Download firmware |
| **LED Attività** | — | Modulo ESP32 DevKitC | **GPIO 2** | Segnalazione lampeggio pacchetti RF |

---

## ⚡ Gestione Alimentazione: Moduli da 30 dBm (1W) vs 33 dBm (2W)

### Calcolo Energetico e Dimensionamento:

1. **Modulo Ebyte E22-400M30S / E22-900M30S (1 Watt RF / +30 dBm)**:
   - Tensione nominale stadio RF: **5.0V**
   - Corrente di picco in trasmissione (+30 dBm): **~650 mA – 750 mA**
   - Assorbimento di potenza di picco: **~3.5W – 3.8W**
   - Corrente richiesta alla cella LiPo (a 3.7V nominali, rendimento 93%): **~1.1A**

2. **Modulo Ebyte E22-400M33S / E22-900M33S (2 Watt RF / +33 dBm)**:
   - Tensione nominale stadio RF: **5.0V**
   - Con efficienza dello stadio amplificatore PA (Power Amplifier) pari a circa 40-45%, la potenza assorbita in trasmissione raggiunge **~8W – 9W**.
   - Corrente di picco in trasmissione (+33 dBm): **~1.6A – 1.8A continui su linea 5V**.
   - Corrente istantanea richiesta alla batteria LiPo (a 3.3V di fine scarica, rendimento 92%): **~3.0A – 3.2A**.

### Accorgimenti Hardware Adottati:
- Lo stadio **FP6277** eroga fino a **2.5A continui e 5.5A di picco switch**, saturando ampiamente i requisiti del modulo da 33 dBm senza cali di tensione (voltage sag).
- L'induttore schermato **4.7 µH con corrente di saturazione di 4.5A** evita il surriscaldamento e previene il collasso dell'induttanza durante i burst LoRa.
- **Dissipazione Termica**: Per impieghi del modulo da 33 dBm con ciclo di lavoro (duty cycle) elevato (es. ripetitore o gateway con beacon frequenti), si raccomanda di applicare un pad termico siliconico da 1.0 mm sul fondo metallico del modulo LoRa a contatto con il piano di massa in rame della scheda.

---

## 📁 Struttura dei File del Progetto

```text
HARDWARE/
├── KiCad/
│   ├── meshcom-e22-devboard.kicad_pro   # File di progetto KiCad v10
│   ├── meshcom-e22-devboard.kicad_sch   # Schema elettrico gerarchico v2.0
│   ├── meshcom-e22-devboard.kicad_pcb   # Layout circuitale sbrogliato (0 errori DRC)
│   ├── meshcom-e22-devboard.kicad_prl   # Impostazioni locali dell'area di lavoro
│   └── meshcom-e22-devboard-drc.rpt     # Rapporto ufficiale DRC (0 violazioni, 0 unconnected)
│
├── JLCPCB/
│   ├── gerbers.zip                      # File Gerber ed Excellon Drills pronti per produzione
│   ├── bom.csv                          # Distinta componenti completa con codici LCSC
│   ├── cpl.csv                          # Coordinate Pick-and-Place (CPL / Centroid)
│   ├── jlcpcb_bom_smd_only.csv          # Distinta componenti solo montaggio SMD
│   ├── jlcpcb_cpl_smd_only.csv          # Coordinate CPL solo montaggio SMD
│   └── assembly.zip                     # Archivio completo per preventivo immediato SMT
│
└── Renders/                             # Visualizzazioni grafiche e 3D
    ├── render_top.png                   # Vista superiore
    └── render_isometric.png             # Vista assonometrica 3D
```

---

## 🛒 Distinta Base Componenti Principali (BOM con Codici LCSC)

Tutti i componenti passivi e attivi sono stati selezionati tra le parti standard ad alta disponibilità del catalogo JLCPCB / LCSC:

| Riferimento | Descrizione Componente | Footprint | Codice LCSC | Tipo Montaggio |
| :--- | :--- | :--- | :--- | :--- |
| **U_BOOST** | FP6277 Convertitore Boost Sincrono 5V 2.5A | SOIC-8-EP | **C2895690** | SMD (Top) |
| **U_MPPT** | CN3791 Caricatore Solare MPPT 6-28V | SSOP-10 | **C2939886** | SMD (Top) |
| **U_BMS** | DW01A Circuito Protezione Batteria LiPo 1S | SOT-23-6 | **C39702** | SMD (Top) |
| **Q_BMS** | FS8205A Doppio N-MOSFET 20V 6A | TSSOP-8 | **C47738** | SMD (Top) |
| **Q_PWR** | AO3401A P-MOSFET Power-Path 30V 4.2A | SOT-23 | **C15127** | SMD (Top) |
| **D_USB, D_MPPT** | SS34 Diodo Schottky 40V 3A | SMA (DO-214AC) | **C1586** | SMD (Top) |
| **L_BOOST** | Induttore Schermato 4.7 µH 4.5A (6045) | SMD 6.3×6.3 mm | **C517036** | SMD (Top) |
| **L_MPPT** | Induttore Schermato 10 µH 3.0A (6045) | SMD 6.3×6.3 mm | **C517038** | SMD (Top) |
| **C_BST_IN, C_BST_OUT, C_BAT_CHG** | Condensatore Ceramico 22 µF 16V X5R | SMD 1206 | **C12882** | SMD (Top) |
| **C_SOL** | Condensatore Ceramico 10 µF 50V X7R | SMD 1206 | **C96979** | SMD (Top) |
| **C2, C3, C_BAT** | Condensatore Ceramico 100 nF 50V X7R | SMD 0805 | **C49678** | SMD (Top) |
| **C1** | Condensatore Elettrolitico Bulk 470 µF 16V | Radiale D6.3 mm P2.5 mm | **C331295** | Through-Hole |
| **R1, R2** | Resistore Precisione 5.1 kΩ 1% | SMD 0805 | **C27834** | SMD (Top) |
| **R3, R4** | Resistore Precisione 2.2 kΩ 1% (Pull-Up I2C) | SMD 0805 | **C17520** | SMD (Top) |
| **R_BAT1, R_BAT2** | Resistore Precisione 100 kΩ 1% (Partitore ADC) | SMD 0805 | **C17407** | SMD (Top) |
| **R_OW** | Resistore Precisione 4.7 kΩ 1% (Pull-Up 1-Wire) | SMD 0805 | **C17673** | SMD (Top) |
| **LED_CHG** | LED SMD 0805 Rosso (Stato Carica) | SMD 0805 | **C2286** | SMD (Top) |
| **LED_DONE** | LED SMD 0805 Verde (Fine Carica) | SMD 0805 | **C2290** | SMD (Top) |
| **J_USB** | Connettore USB Type-C 16-pin (TYPE-C-31-M-12) | USB-C SMD/Hybrid | **C165948** | SMD / Through-Hole |
| **J_QWIIC** | Connettore I2C STEMMA QT / Qwiic (SM04B) | JST-SH 1.0 mm 4P Orizzontale | **C160404** | SMD (Top) |
| **J_BATT** | Connettore Batteria LiPo JST-PH 2.0 mm 2P | JST-PH Orizzontale | **C131337** | Through-Hole |
| **J_SOLAR** | Morsettiera Solare a Vite 2P Passo 5.08 mm | Phoenix Contact MKDS | **C8379** | Through-Hole |
| **J_SMA** | Connettore SMA EdgeMount 50Ω per PCB | SMA EdgeMount Amphenol | **C494294** | EdgeMount SMD |
| **J_GPS** | Strip Maschio 1×05 Passo 2.54 mm Verticale | Pin Header 2.54 mm | **C2897385** | Through-Hole |
| **J_DS18** | Strip Maschio 1×03 Passo 2.54 mm Verticale | Pin Header 2.54 mm | **C2897383** | Through-Hole |
| **J_ESP_L, J_ESP_R** | Strip Femmina 1×19 Passo 2.54 mm Verticale | Pin Header 2.54 mm | **C225578** | Through-Hole |
| **J_OLED** | Strip Femmina 1×04 Passo 2.54 mm Verticale | Pin Header 2.54 mm | **C224375** | Through-Hole |
| **J_BME** | Strip Maschio 1×04 Passo 2.54 mm Verticale | Pin Header 2.54 mm | **C2897384** | Through-Hole |
| **J_INA** | Strip Maschio 1×06 Passo 2.54 mm Verticale | Pin Header 2.54 mm | **C2897386** | Through-Hole |
| **U2** | Modulo LoRa Ebyte E22-400M30S o E22-900M30S | E22 Castellated SMD | *(DNP / Salda Utente)* | SMD |

---

## 🏭 Istruzioni di Ordinazione e Produzione su JLCPCB

1. **Caricamento File di Fabbricazione**:
   - Accedi a [jlcpcb.com](https://jlcpcb.com) e carica il file `JLCPCB/gerbers.zip`.
   - Parametri consigliati:
     - **Dimensioni PCB**: **100.0 mm × 80.0 mm** (calcolate in automatico)
     - **Strati (Layers)**: **2 strati**
     - **Spessore PCB**: **1.6 mm**
     - **Finitura superficiale**: **ENIG (Oro Chimico)** raccomandata per la stabilità delle microstrisce RF a 50Ω e l'affidabilità delle piazzole castellate dell'E22. In alternativa, **HASL Lead-Free**.
     - **Colore Solder Mask**: Nero opaco (Matte Black), Blu o Verde classico.
     - **Rame**: 1 oz (35 µm).

2. **Assemblaggio SMT (Montaggio Automatico)**:
   - Seleziona **SMT Assembly** -> **Top Side**.
   - Carica `JLCPCB/bom.csv` (o `jlcpcb_bom_smd_only.csv`) per la distinta componenti.
   - Carica `JLCPCB/cpl.csv` (o `jlcpcb_cpl_smd_only.csv`) per le coordinate di piazzamento.
   - Nella finestra di anteprima 3D interattiva di JLCPCB, verifica l'orientamento dei componenti (pin 1 e polarità diodi). Le rotazioni sono già state allineate agli standard IPC/JLCPCB.
   - Il modulo Ebyte E22 (**U2**) è contrassegnato come **DNP (Do Not Populate)** per consentire la saldatura manuale del modulo prescelto (433 MHz vs 868/915 MHz, 30 dBm vs 33 dBm).

---

## 🔬 Collaudo e Verifica Elettrica (DRC Benchmark)

- **KiCad Design Rules Check (DRC)**:
  - Violazioni di isolamento (Clearance): **0**
  - Tracce non connesse (Unconnected pads): **0**
  - Errori di footprint o pad: **0**
  - Isolamento tra piste di potenza e piani di massa: **≥ 0.35 mm** (superiore agli standard industriali di sicurezza).
  - Piani di massa superiore (`F.Cu`) e inferiore (`B.Cu`) completamente interconnessi con via stitching termici dedicati sotto il modulo RF e lo stadio di potenza boost.
