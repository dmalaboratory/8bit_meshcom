#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_spectrum_design.py
Upgrades the RF & Spettro tab in build_ultimate_dashboard.py and generates index.html
with a stunning, modern, tactical SDR RF Spectrum Analyzer, Waterfall Display,
real-time S-meter, and heard-station ranking table.
"""

import sys

BUILD_SCRIPT = "/home/user/.gemini/antigravity/scratch/meshcom-dashboard/build_ultimate_dashboard.py"

with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
    code = f.read()

# 1. NEW CSS FOR SDR SPECTRUM & WATERFALL
SPECTRUM_CSS = """
    /* =========================================================
       RF & SPETTRO TATTICO SDR MODERN DESIGN
       ========================================================= */
    .spectrum-hud-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 0.75rem;
    }
    .rf-hud-card {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      background: linear-gradient(180deg, rgba(17, 24, 39, 0.7) 0%, rgba(10, 15, 29, 0.8) 100%);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.85rem 1rem;
      position: relative;
      overflow: hidden;
    }
    .rf-hud-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
      opacity: 0.6;
    }
    .rf-hud-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .rf-hud-title {
      font-size: 0.68rem;
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--text-dim);
      letter-spacing: 0.05em;
    }
    .rf-badge {
      font-size: 0.65rem;
      font-family: var(--font-mono);
      font-weight: 700;
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: rgba(0, 0, 0, 0.35);
      color: var(--text-muted);
    }
    .rf-badge.active-green {
      color: var(--accent-green);
      border-color: rgba(16, 185, 129, 0.4);
      background: rgba(16, 185, 129, 0.12);
    }
    .rf-badge.active-cyan {
      color: var(--accent-cyan);
      border-color: rgba(6, 182, 212, 0.4);
      background: rgba(6, 182, 212, 0.12);
    }
    .rf-badge.active-amber {
      color: var(--accent-amber);
      border-color: rgba(245, 158, 11, 0.4);
      background: rgba(245, 158, 11, 0.12);
    }
    .rf-hud-main {
      display: flex;
      align-items: baseline;
      gap: 0.35rem;
      margin: 0.2rem 0;
    }
    .rf-val-num {
      font-size: 1.75rem;
      font-family: var(--font-mono);
      font-weight: 800;
      color: var(--text-main);
      line-height: 1;
      letter-spacing: -0.02em;
    }
    .rf-val-unit {
      font-size: 0.75rem;
      color: var(--text-dim);
      font-family: var(--font-mono);
      font-weight: 600;
    }
    .rf-smeter-pill {
      margin-left: auto;
      font-size: 0.72rem;
      font-family: var(--font-mono);
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 9999px;
      border: 1px solid rgba(6, 182, 212, 0.4);
      background: rgba(6, 182, 212, 0.12);
      color: var(--accent-cyan);
    }
    .rf-led-meter {
      display: flex;
      gap: 3px;
      height: 7px;
      margin-top: 0.2rem;
    }
    .led-bar-seg {
      flex: 1;
      border-radius: 1px;
      background: rgba(255, 255, 255, 0.08);
      transition: background 0.15s ease, box-shadow 0.15s ease;
    }
    .led-bar-seg.active-green {
      background: #10b981;
      box-shadow: 0 0 6px rgba(16, 185, 129, 0.6);
    }
    .led-bar-seg.active-cyan {
      background: #06b6d4;
      box-shadow: 0 0 6px rgba(6, 182, 212, 0.6);
    }
    .led-bar-seg.active-amber {
      background: #f59e0b;
      box-shadow: 0 0 6px rgba(245, 158, 11, 0.6);
    }
    .led-bar-seg.active-red {
      background: #ef4444;
      box-shadow: 0 0 6px rgba(239, 68, 68, 0.6);
    }
    .rf-progress-track {
      height: 5px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 9999px;
      overflow: hidden;
      margin-top: 0.35rem;
    }
    .rf-progress-fill {
      height: 100%;
      border-radius: 9999px;
      background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
      transition: width 0.3s ease;
    }
    .rf-hud-sub {
      font-size: 0.68rem;
      color: var(--text-dim);
      font-family: var(--font-sans);
    }

    /* SDR CONTAINER & VIEWPORT */
    .rf-sdr-container {
      padding: 0 !important;
      overflow: hidden;
      border: 1px solid var(--border-active);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.55);
      background: #03050d;
      border-radius: var(--radius-md);
    }
    .sdr-control-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.65rem 1rem;
      background: rgba(10, 16, 30, 0.85);
      border-bottom: 1px solid var(--border-subtle);
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .sdr-title-group {
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }
    .sdr-status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-green);
      box-shadow: 0 0 8px var(--accent-green);
      animation: pulseGreen 2s infinite;
    }
    .sdr-title {
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--text-main);
      font-family: var(--font-mono);
    }
    .sdr-center-chip {
      font-size: 0.68rem;
      font-family: var(--font-mono);
      color: var(--accent-cyan);
      background: rgba(6, 182, 212, 0.12);
      border: 1px solid rgba(6, 182, 212, 0.3);
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
    }
    .sdr-btn-group {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      flex-wrap: wrap;
    }
    .sdr-tool-btn {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      border-radius: var(--radius-sm);
      padding: 0.3rem 0.65rem;
      font-size: 0.72rem;
      font-family: var(--font-mono);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.3rem;
      transition: all 0.2s;
    }
    .sdr-tool-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.25);
    }
    .sdr-tool-btn.active {
      background: rgba(6, 182, 212, 0.18);
      color: var(--accent-cyan);
      border-color: var(--accent-cyan);
      box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
    }
    .sdr-select {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      border-radius: var(--radius-sm);
      padding: 0.3rem 0.5rem;
      font-size: 0.72rem;
      font-family: var(--font-mono);
      outline: none;
      cursor: pointer;
    }
    .sdr-viewport {
      position: relative;
      background: #030611;
      user-select: none;
      cursor: crosshair;
    }
    .sdr-fft-wrap {
      position: relative;
      height: 220px;
      width: 100%;
      background: #040816;
    }
    .sdr-fft-wrap canvas {
      width: 100%;
      height: 100%;
      display: block;
    }
    .sdr-carrier-tag {
      position: absolute;
      top: 8px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(6, 182, 212, 0.18);
      border: 1px solid var(--accent-cyan);
      color: #67e8f9;
      font-size: 0.68rem;
      font-family: var(--font-mono);
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 9999px;
      pointer-events: none;
      box-shadow: 0 0 12px rgba(6, 182, 212, 0.4);
    }
    .sdr-crosshair-hud {
      position: absolute;
      display: none;
      pointer-events: none;
      background: rgba(6, 11, 25, 0.94);
      border: 1px solid var(--accent-cyan);
      box-shadow: 0 4px 16px rgba(0,0,0,0.7);
      border-radius: 4px;
      padding: 0.3rem 0.6rem;
      font-family: var(--font-mono);
      font-size: 0.7rem;
      color: #fff;
      z-index: 10;
      white-space: nowrap;
    }
    .sdr-freq-axis {
      height: 24px;
      background: #02040a;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 1rem;
      font-size: 0.65rem;
      font-family: var(--font-mono);
      color: var(--text-dim);
    }
    .sdr-freq-axis span.active {
      color: var(--accent-cyan);
      font-weight: 700;
    }
    .sdr-waterfall-wrap {
      position: relative;
      height: 180px;
      width: 100%;
      background: #020409;
    }
    .sdr-waterfall-wrap canvas {
      width: 100%;
      height: 100%;
      display: block;
    }
    .sdr-waterfall-scale {
      position: absolute;
      right: 6px;
      top: 0;
      bottom: 0;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 6px 0;
      font-size: 0.62rem;
      font-family: var(--font-mono);
      color: rgba(255, 255, 255, 0.35);
      pointer-events: none;
    }
"""

# Insert CSS before </style>
if "/* SDR CONTAINER & VIEWPORT */" not in code:
    code = code.replace("  </style>", SPECTRUM_CSS + "\n  </style>")

# 2. RENAME TAB BUTTON
code = code.replace(
    '<button class="tab-btn" onclick="switchTab(\'spectrum\')">\n        📊 RF & Spettro RSSI',
    '<button class="tab-btn" onclick="switchTab(\'spectrum\')">\n        📡 RF & Spettro SDR'
)

# 3. REPLACE PANE-SPECTRUM HTML
OLD_SPECTRUM_PANE = """    <!-- PANE 7: RF & SPETTRO RSSI -->
    <section class="tab-pane" id="pane-spectrum">
      <div class="card">
        <h3 style="font-size:0.95rem; font-weight:700">Attività Canale LoRa & Storico Segnale RSSI</h3>
        <p style="font-size:0.75rem; color:var(--text-muted)">Distribuzione intensità segnale delle ultime trasmissioni radio ricevute</p>
      </div>

      <div class="card" style="padding:1.5rem">
        <div style="display:flex; justify-content:space-between; margin-bottom:1rem; font-family:var(--font-mono); font-size:0.8rem">
          <span>Segnale Debole (-125 dBm)</span>
          <span style="color:var(--accent-cyan)">Soglia Ottimale (-90 dBm)</span>
          <span style="color:var(--accent-green)">Segnale Forte (-60 dBm)</span>
        </div>
        <div id="rssiHistoryBars" style="display:flex; align-items:flex-end; gap:4px; height:180px; background:rgba(0,0,0,0.3); border-radius:var(--radius-sm); padding:0.5rem; border:1px solid var(--border-subtle)">
          <div style="margin:auto; color:var(--text-dim); font-size:0.8rem">In attesa di pacchetti radio con telemetria RSSI...</div>
        </div>
      </div>
    </section>"""

NEW_SPECTRUM_PANE = """    <!-- PANE 7: RF & SPETTRO TATTICO SDR -->
    <section class="tab-pane" id="pane-spectrum">
      <!-- 1. BARRA METRICHE CHIAVE RF -->
      <div class="spectrum-hud-grid">
        <!-- Card 1: RSSI Live & S-Meter -->
        <div class="card rf-hud-card">
          <div class="rf-hud-header">
            <span class="rf-hud-title">LIVE SIGNAL RSSI</span>
            <span class="rf-badge" id="rfSignalBadge">ATTESA RX</span>
          </div>
          <div class="rf-hud-main">
            <span class="rf-val-num" id="rfCurRssi">--</span>
            <span class="rf-val-unit">dBm</span>
            <span class="rf-smeter-pill" id="rfCurSmeter">S--</span>
          </div>
          <!-- 10-segment LED bar -->
          <div class="rf-led-meter" id="rfLedMeter">
            <div class="led-bar-seg" data-idx="0"></div>
            <div class="led-bar-seg" data-idx="1"></div>
            <div class="led-bar-seg" data-idx="2"></div>
            <div class="led-bar-seg" data-idx="3"></div>
            <div class="led-bar-seg" data-idx="4"></div>
            <div class="led-bar-seg" data-idx="5"></div>
            <div class="led-bar-seg" data-idx="6"></div>
            <div class="led-bar-seg" data-idx="7"></div>
            <div class="led-bar-seg" data-idx="8"></div>
            <div class="led-bar-seg" data-idx="9"></div>
          </div>
          <div class="rf-hud-sub">Demodulazione LoRa fino a -135 dBm</div>
        </div>

        <!-- Card 2: Margine SNR & Headroom -->
        <div class="card rf-hud-card">
          <div class="rf-hud-header">
            <span class="rf-hud-title">MARGINE SNR</span>
            <span class="rf-badge" id="rfSnrBadge" style="color:var(--accent-cyan); border-color:var(--border-active)">HEADROOM</span>
          </div>
          <div class="rf-hud-main">
            <span class="rf-val-num" id="rfCurSnr">--</span>
            <span class="rf-val-unit">dB</span>
          </div>
          <div class="rf-progress-track">
            <div class="rf-progress-fill" id="rfSnrFill" style="width: 50%;"></div>
          </div>
          <div class="rf-hud-sub">Soglia operativa SX1262: -20 dB a SF11</div>
        </div>

        <!-- Card 3: Canale & Parametri Radio -->
        <div class="card rf-hud-card">
          <div class="rf-hud-header">
            <span class="rf-hud-title">CANALE LORA MESH</span>
            <span class="rf-badge" style="color:var(--accent-green); border-color:rgba(16,185,129,0.3)">EU CH 1</span>
          </div>
          <div class="rf-hud-main">
            <span class="rf-val-num" style="color:var(--accent-cyan); font-size:1.45rem">433.175</span>
            <span class="rf-val-unit">MHz</span>
          </div>
          <div style="font-family:var(--font-mono); font-size:0.72rem; color:var(--text-muted); display:flex; gap:0.5rem; margin-top:0.4rem">
            <span>BW: <b>125 kHz</b></span>
            <span>SF: <b>11</b></span>
            <span>CR: <b>4/5</b></span>
            <span>TX: <b id="rfTxPwrDisp">20 dBm</b></span>
          </div>
          <div class="rf-hud-sub">Spettro ISM 433.050 - 433.300 MHz</div>
        </div>

        <!-- Card 4: Noise Floor & Qualità Link -->
        <div class="card rf-hud-card">
          <div class="rf-hud-header">
            <span class="rf-hud-title">NOISE FLOOR & LQI</span>
            <span class="rf-badge" style="color:var(--accent-purple); border-color:rgba(168,85,247,0.3)">THERMAL</span>
          </div>
          <div class="rf-hud-main">
            <span class="rf-val-num" id="rfNoiseFloor">-118</span>
            <span class="rf-val-unit">dBm</span>
            <span class="rf-smeter-pill" style="border-color:rgba(168,85,247,0.4); color:#c084fc">99% LQI</span>
          </div>
          <div class="rf-progress-track">
            <div class="rf-progress-fill" style="width:94%; background:linear-gradient(90deg, #10b981, #06b6d4)"></div>
          </div>
          <div class="rf-hud-sub" id="rfPacketsSeenSub">0 pacchetti LoRa analizzati</div>
        </div>
      </div>

      <!-- 2. PANNELLO PRINCIPALE SDR ANALYZER + WATERFALL -->
      <div class="card rf-sdr-container">
        <!-- SDR Control Header Bar -->
        <div class="sdr-control-bar">
          <div class="sdr-title-group">
            <div class="sdr-status-dot"></div>
            <span class="sdr-title">ANALIZZATORE DI SPETTRO RF & CASCATA SDR</span>
            <span class="sdr-center-chip">FO: 433.175 MHz • SPAN 250 kHz</span>
          </div>

          <div class="sdr-btn-group">
            <button class="sdr-tool-btn active" id="btnSdrSimBurst" onclick="triggerSimulatedRfBurst()" title="Simula burst RF LoRa in tempo reale">
              🧪 Simula Burst LoRa
            </button>
            <button class="sdr-tool-btn" id="btnToggleWaterfall" onclick="toggleWaterfallPause()">
              <span id="waterfallPlayIcon">⏸️</span> Pausa
            </button>
            <button class="sdr-tool-btn" onclick="resetPeakHold()">
              🔄 Reset Picchi
            </button>
            <select class="sdr-select" id="sdrPaletteSelect" onchange="changeSdrPalette(this.value)">
              <option value="tactical">Palette: SDR Tactical</option>
              <option value="thermal">Palette: Heatmap Termica</option>
              <option value="phosphor">Palette: Fosfori Verdi</option>
            </select>
          </div>
        </div>

        <!-- SDR Visualizer Viewport -->
        <div class="sdr-viewport" id="sdrViewport" onmousemove="onSdrMouseMove(event)" onmouseleave="onSdrMouseLeave()">
          <!-- FFT Realtime Scope Canvas -->
          <div class="sdr-fft-wrap">
            <canvas id="sdrFftCanvas" width="900" height="220"></canvas>
            <div class="sdr-carrier-tag">CH 1 • 433.175 MHz (125 kHz BW)</div>
            <div class="sdr-crosshair-hud" id="sdrCrosshairHud"></div>
          </div>

          <!-- Tactical Frequency Axis Bar -->
          <div class="sdr-freq-axis">
            <span>433.050 MHz</span>
            <span>433.100 MHz</span>
            <span class="active">433.175 MHz (CENTER)</span>
            <span>433.250 MHz</span>
            <span>433.300 MHz</span>
          </div>

          <!-- SDR Scrolling Waterfall Canvas -->
          <div class="sdr-waterfall-wrap">
            <canvas id="sdrWaterfallCanvas" width="900" height="180"></canvas>
            <div class="sdr-waterfall-scale">
              <span>0s</span>
              <span>15s</span>
              <span>30s</span>
              <span>45s</span>
              <span>60s</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. DETTAGLI SECONDARI: STORICO TEMPORALE RSSI & CLASSIFICA STAZIONI -->
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
        <!-- Card Sinistra: Trend Temporale RSSI Ultimi Pacchetti -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem">
            <div>
              <h3 style="font-size:0.92rem; font-weight:700">Trend Temporale RSSI</h3>
              <p style="font-size:0.72rem; color:var(--text-muted)">Storico dinamico ultimi pacchetti ricevuti</p>
            </div>
            <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent-cyan)" id="rssiAvgLabel">Media: -- dBm</span>
          </div>
          <div id="rssiTimelineWrap" style="position:relative; height:180px; width:100%;">
            <canvas id="rssiTrendCanvas" width="450" height="180" style="width:100%; height:100%;"></canvas>
          </div>
        </div>

        <!-- Card Destra: Classifica Segnale Stazioni Ascoltate -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem">
            <div>
              <h3 style="font-size:0.92rem; font-weight:700">Classifica RF Stazioni (MHeard)</h3>
              <p style="font-size:0.72rem; color:var(--text-muted)">Nodi ordinati per potenza di ricezione RF</p>
            </div>
            <span class="rf-badge" id="rfHeardCountBadge">0 Nodi</span>
          </div>
          <div style="overflow-y:auto; max-height:180px;">
            <table class="table" style="margin:0">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Nominativo</th>
                  <th>RSSI</th>
                  <th>S-Meter</th>
                  <th>SNR</th>
                  <th>Azione</th>
                </tr>
              </thead>
              <tbody id="rfRankingTableBody">
                <tr>
                  <td colspan="6" style="text-align:center; color:var(--text-dim); padding:2rem 0">
                    In attesa di stazioni RF con telemetria RSSI...
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>"""

if OLD_SPECTRUM_PANE in code:
    code = code.replace(OLD_SPECTRUM_PANE, NEW_SPECTRUM_PANE)
    print("Replaced pane-spectrum HTML successfully.")
else:
    print("Warning: OLD_SPECTRUM_PANE exact string not found! Checking fallback.")

# 4. UPDATE switchTab
OLD_SWITCH_TAB = """      if (paneId === 'map' && leafletMap) {
        setTimeout(() => leafletMap.invalidateSize(), 200);
      }"""

NEW_SWITCH_TAB = """      if (paneId === 'map' && leafletMap) {
        setTimeout(() => leafletMap.invalidateSize(), 200);
      }

      if (paneId === 'spectrum') {
        onSpectrumTabActivated();
      } else {
        onSpectrumTabDeactivated();
      }"""

if OLD_SWITCH_TAB in code and "onSpectrumTabActivated()" not in code:
    code = code.replace(OLD_SWITCH_TAB, NEW_SWITCH_TAB)
    print("Updated switchTab() function.")

# 5. REPLACE JS SECTION FOR SPECTRUM
OLD_SPECTRUM_JS = """    // ==========================================
    // SPETTRO & STORICO RSSI
    // ==========================================
    function recordRssi(call, rssiVal) {
      rssiHistory.push({ call, rssi: rssiVal, time: Date.now() });
      if (rssiHistory.length > 40) rssiHistory.shift();

      const container = document.getElementById("rssiHistoryBars");
      if (!container) return;
      container.innerHTML = "";

      rssiHistory.forEach(r => {
        const heightPct = Math.min(100, Math.max(10, ((r.rssi + 130) / 80) * 100));
        const bar = document.createElement("div");
        bar.style.flex = "1";
        bar.style.height = `${heightPct}%`;
        bar.style.borderRadius = "2px 2px 0 0";
        bar.style.background = r.rssi > -80 ? "var(--accent-green)" : (r.rssi > -105 ? "var(--accent-cyan)" : "var(--accent-red)");
        bar.title = `${r.call}: ${r.rssi} dBm`;
        container.appendChild(bar);
      });
    }"""

NEW_SPECTRUM_JS = """    // ==========================================
    // SDR REAL-TIME SPECTRUM & WATERFALL ENGINE
    // ==========================================
    const SDR_BINS = 128;
    let sdrFftData = new Float32Array(SDR_BINS);
    let sdrPeakHold = new Float32Array(SDR_BINS);
    for (let i = 0; i < SDR_BINS; i++) {
      sdrFftData[i] = -118;
      sdrPeakHold[i] = -118;
    }

    let sdrActiveBurst = null;
    let sdrIsPaused = false;
    let sdrPalette = 'tactical';
    let sdrAnimFrameId = null;
    let sdrLastFrameTime = 0;
    let sdrTotalPacketsAnalyzed = 0;

    function generateTacticalPalette() {
      const p = new Uint8ClampedArray(256 * 4);
      for (let i = 0; i < 256; i++) {
        let r, g, b;
        const norm = i / 255;
        if (norm < 0.15) {
          r = Math.floor((norm / 0.15) * 10);
          g = Math.floor((norm / 0.15) * 16);
          b = Math.floor((norm / 0.15) * 45);
        } else if (norm < 0.4) {
          const t = (norm - 0.15) / 0.25;
          r = Math.floor(10 + t * (6 - 10));
          g = Math.floor(16 + t * (182 - 16));
          b = Math.floor(45 + t * (212 - 45));
        } else if (norm < 0.65) {
          const t = (norm - 0.4) / 0.25;
          r = Math.floor(6 + t * (16 - 6));
          g = Math.floor(182 + t * (185 - 182));
          b = Math.floor(212 + t * (129 - 212));
        } else if (norm < 0.85) {
          const t = (norm - 0.65) / 0.2;
          r = Math.floor(16 + t * (245 - 16));
          g = Math.floor(185 + t * (158 - 185));
          b = Math.floor(129 + t * (11 - 129));
        } else {
          const t = (norm - 0.85) / 0.15;
          r = Math.floor(245 + t * (255 - 245));
          g = Math.floor(158 + t * (255 - 158));
          b = Math.floor(11 + t * (255 - 11));
        }
        const idx = i * 4;
        p[idx] = r;
        p[idx + 1] = g;
        p[idx + 2] = b;
        p[idx + 3] = 255;
      }
      return p;
    }

    function generateThermalPalette() {
      const p = new Uint8ClampedArray(256 * 4);
      for (let i = 0; i < 256; i++) {
        let r, g, b;
        const norm = i / 255;
        if (norm < 0.25) {
          const t = norm / 0.25;
          r = Math.floor(t * 80);
          g = 0;
          b = Math.floor(t * 120);
        } else if (norm < 0.5) {
          const t = (norm - 0.25) / 0.25;
          r = Math.floor(80 + t * (220 - 80));
          g = Math.floor(t * 30);
          b = Math.floor(120 * (1 - t));
        } else if (norm < 0.8) {
          const t = (norm - 0.5) / 0.3;
          r = Math.floor(220 + t * 35);
          g = Math.floor(30 + t * 200);
          b = 0;
        } else {
          const t = (norm - 0.8) / 0.2;
          r = 255;
          g = Math.floor(230 + t * 25);
          b = Math.floor(t * 255);
        }
        const idx = i * 4;
        p[idx] = r;
        p[idx + 1] = g;
        p[idx + 2] = b;
        p[idx + 3] = 255;
      }
      return p;
    }

    function generatePhosphorPalette() {
      const p = new Uint8ClampedArray(256 * 4);
      for (let i = 0; i < 256; i++) {
        const norm = i / 255;
        let r = Math.floor(norm > 0.8 ? ((norm - 0.8) / 0.2) * 180 : 0);
        let g = Math.floor(norm * 255);
        let b = Math.floor(norm > 0.8 ? ((norm - 0.8) / 0.2) * 180 : (norm * 50));
        const idx = i * 4;
        p[idx] = r;
        p[idx + 1] = g;
        p[idx + 2] = b;
        p[idx + 3] = 255;
      }
      return p;
    }

    const SDR_PALETTES = {
      tactical: generateTacticalPalette(),
      thermal: generateThermalPalette(),
      phosphor: generatePhosphorPalette()
    };

    function initSpectrumCanvases() {
      const fftCanvas = document.getElementById("sdrFftCanvas");
      const wfCanvas = document.getElementById("sdrWaterfallCanvas");
      if (!fftCanvas || !wfCanvas) return;

      const rect = fftCanvas.parentElement.getBoundingClientRect();
      const targetW = Math.max(400, Math.floor(rect.width));

      if (fftCanvas.width !== targetW) {
        fftCanvas.width = targetW;
        fftCanvas.height = 220;
      }
      if (wfCanvas.width !== targetW) {
        wfCanvas.width = targetW;
        wfCanvas.height = 180;
      }

      const wfCtx = wfCanvas.getContext("2d");
      wfCtx.fillStyle = "#020409";
      wfCtx.fillRect(0, 0, wfCanvas.width, wfCanvas.height);

      if (!sdrAnimFrameId) {
        sdrLastFrameTime = performance.now();
        sdrAnimFrameId = requestAnimationFrame(sdrRenderLoop);
      }

      updateRssiTrendChart();
      updateRfRankingTable();
    }

    function onSpectrumTabActivated() {
      initSpectrumCanvases();
    }

    function onSpectrumTabDeactivated() {
      if (sdrAnimFrameId) {
        cancelAnimationFrame(sdrAnimFrameId);
        sdrAnimFrameId = null;
      }
    }

    function sdrRenderLoop(timestamp) {
      const pane = document.getElementById("pane-spectrum");
      if (!pane || !pane.classList.contains("active")) {
        sdrAnimFrameId = null;
        return;
      }

      const dt = timestamp - sdrLastFrameTime;
      sdrLastFrameTime = timestamp;

      updateSdrFftBins(timestamp, dt);
      drawSdrFft();

      if (!sdrIsPaused) {
        drawSdrWaterfallRow();
      }

      sdrAnimFrameId = requestAnimationFrame(sdrRenderLoop);
    }

    function updateSdrFftBins(timestamp, dt) {
      const now = Date.now();
      const baseFloor = -118;

      for (let i = 0; i < SDR_BINS; i++) {
        const slowWave = Math.sin(i * 0.15 + timestamp * 0.002) * 1.8;
        const fastJitter = (Math.random() - 0.5) * 3.2;
        let val = baseFloor + slowWave + fastJitter;

        if (sdrActiveBurst) {
          const elapsed = now - sdrActiveBurst.startTime;
          if (elapsed < sdrActiveBurst.duration) {
            const centerBin = 64;
            const halfBw = 32;
            const distFromCenter = Math.abs(i - centerBin);

            if (distFromCenter <= halfBw) {
              const progress = elapsed / sdrActiveBurst.duration;
              let env = 1.0;
              if (progress < 0.1) env = progress / 0.1;
              else if (progress > 0.85) env = (1.0 - progress) / 0.15;

              const chirpTexture = Math.sin(i * 1.2 + timestamp * 0.02) * 2.5;
              const signalPower = sdrActiveBurst.power + chirpTexture;
              val = Math.max(val, signalPower * env);
            } else if (distFromCenter <= halfBw + 8) {
              const skirtRatio = (distFromCenter - halfBw) / 8;
              const skirtDrop = skirtRatio * 25;
              val = Math.max(val, sdrActiveBurst.power - skirtDrop);
            }
          } else {
            sdrActiveBurst = null;
          }
        }

        sdrFftData[i] = val;

        if (val > sdrPeakHold[i]) {
          sdrPeakHold[i] = val;
        } else {
          sdrPeakHold[i] = Math.max(baseFloor, sdrPeakHold[i] - 0.12);
        }
      }
    }

    function drawSdrFft() {
      const canvas = document.getElementById("sdrFftCanvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const W = canvas.width;
      const H = canvas.height;

      ctx.fillStyle = "#040816";
      ctx.fillRect(0, 0, W, H);

      const minDbm = -125;
      const maxDbm = -40;
      const dbmRange = maxDbm - minDbm;

      const dbmToY = (dbm) => {
        const clamped = Math.max(minDbm, Math.min(maxDbm, dbm));
        return H - ((clamped - minDbm) / dbmRange) * H;
      };

      // 1. Grid Lines and Labels
      ctx.lineWidth = 1;
      const gridLevels = [-40, -60, -80, -100, -120];
      gridLevels.forEach(lvl => {
        const y = Math.round(dbmToY(lvl));
        ctx.strokeStyle = (lvl === -100 || lvl === -60) ? "rgba(255, 255, 255, 0.12)" : "rgba(255, 255, 255, 0.05)";
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(45, y);
        ctx.lineTo(W - 45, y);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
        ctx.font = "9px 'JetBrains Mono', monospace";
        ctx.textAlign = "right";
        ctx.fillText(`${lvl} dBm`, 40, y + 3);

        let smeterText = "";
        if (lvl === -40) smeterText = "S9+30";
        else if (lvl === -60) smeterText = "S9+10";
        else if (lvl === -80) smeterText = "S8";
        else if (lvl === -100) smeterText = "S4";
        else if (lvl === -120) smeterText = "S1";

        if (smeterText) {
          ctx.fillStyle = "rgba(6, 182, 212, 0.6)";
          ctx.textAlign = "left";
          ctx.fillText(smeterText, W - 40, y + 3);
        }
      });

      // 2. Channel Bandwidth Highlight (125 kHz)
      const bwLeftX = Math.round((32 / SDR_BINS) * W);
      const bwRightX = Math.round((96 / SDR_BINS) * W);
      const centerX = Math.round((64 / SDR_BINS) * W);

      ctx.fillStyle = "rgba(6, 182, 212, 0.04)";
      ctx.fillRect(bwLeftX, 0, bwRightX - bwLeftX, H);

      ctx.strokeStyle = "rgba(6, 182, 212, 0.25)";
      ctx.setLineDash([2, 4]);
      ctx.beginPath();
      ctx.moveTo(bwLeftX, 0); ctx.lineTo(bwLeftX, H);
      ctx.moveTo(bwRightX, 0); ctx.lineTo(bwRightX, H);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.strokeStyle = "rgba(6, 182, 212, 0.65)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(centerX, 0); ctx.lineTo(centerX, H);
      ctx.stroke();

      // 3. Peak Hold (Amber)
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = "#f59e0b";
      ctx.beginPath();
      for (let i = 0; i < SDR_BINS; i++) {
        const x = (i / (SDR_BINS - 1)) * W;
        const y = dbmToY(sdrPeakHold[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // 4. Live FFT Area Gradient & Stroke
      const gradFill = ctx.createLinearGradient(0, 0, 0, H);
      gradFill.addColorStop(0, "rgba(6, 182, 212, 0.45)");
      gradFill.addColorStop(0.6, "rgba(16, 185, 129, 0.15)");
      gradFill.addColorStop(1, "rgba(6, 182, 212, 0.0)");

      ctx.beginPath();
      ctx.moveTo(0, H);
      for (let i = 0; i < SDR_BINS; i++) {
        const x = (i / (SDR_BINS - 1)) * W;
        const y = dbmToY(sdrFftData[i]);
        ctx.lineTo(x, y);
      }
      ctx.lineTo(W, H);
      ctx.closePath();
      ctx.fillStyle = gradFill;
      ctx.fill();

      ctx.lineWidth = 2;
      ctx.shadowColor = "rgba(6, 182, 212, 0.75)";
      ctx.shadowBlur = 8;
      ctx.strokeStyle = "#00f0ff";
      ctx.beginPath();
      for (let i = 0; i < SDR_BINS; i++) {
        const x = (i / (SDR_BINS - 1)) * W;
        const y = dbmToY(sdrFftData[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      // 5. Peak Tag
      let maxVal = -125;
      let maxIdx = 64;
      for (let i = 0; i < SDR_BINS; i++) {
        if (sdrFftData[i] > maxVal) {
          maxVal = sdrFftData[i];
          maxIdx = i;
        }
      }

      if (maxVal > -105) {
        const peakX = (maxIdx / (SDR_BINS - 1)) * W;
        const peakY = dbmToY(maxVal);
        const tagText = sdrActiveBurst ? `${sdrActiveBurst.call}: ${Math.round(maxVal)} dBm` : `${Math.round(maxVal)} dBm`;

        ctx.fillStyle = "#10b981";
        ctx.beginPath();
        ctx.moveTo(peakX, peakY - 4);
        ctx.lineTo(peakX - 5, peakY - 12);
        ctx.lineTo(peakX + 5, peakY - 12);
        ctx.closePath();
        ctx.fill();

        ctx.font = "bold 10px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.fillStyle = "#ffffff";
        ctx.fillText(tagText, peakX, Math.max(16, peakY - 15));
      }
    }

    function drawSdrWaterfallRow() {
      const canvas = document.getElementById("sdrWaterfallCanvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const W = canvas.width;
      const H = canvas.height;

      ctx.drawImage(canvas, 0, 0, W, H - 2, 0, 2, W, H - 2);

      const palette = SDR_PALETTES[sdrPalette] || SDR_PALETTES.tactical;
      const rowImg = ctx.createImageData(W, 2);
      const data = rowImg.data;

      for (let x = 0; x < W; x++) {
        const binFloat = (x / (W - 1)) * (SDR_BINS - 1);
        const bin0 = Math.floor(binFloat);
        const bin1 = Math.min(SDR_BINS - 1, bin0 + 1);
        const frac = binFloat - bin0;
        const valDbm = sdrFftData[bin0] * (1 - frac) + sdrFftData[bin1] * frac;

        const norm = Math.max(0, Math.min(1, (valDbm - (-120)) / 70));
        const colorIdx = Math.floor(norm * 255) * 4;

        const r = palette[colorIdx];
        const g = palette[colorIdx + 1];
        const b = palette[colorIdx + 2];

        for (let row = 0; row < 2; row++) {
          const pIdx = (row * W + x) * 4;
          data[pIdx] = r;
          data[pIdx + 1] = g;
          data[pIdx + 2] = b;
          data[pIdx + 3] = 255;
        }
      }

      ctx.putImageData(rowImg, 0, 0);
    }

    function toggleWaterfallPause() {
      sdrIsPaused = !sdrIsPaused;
      const btn = document.getElementById("btnToggleWaterfall");
      const icon = document.getElementById("waterfallPlayIcon");
      if (sdrIsPaused) {
        btn.classList.add("active");
        if (icon) icon.textContent = "▶️";
        btn.innerHTML = `<span id="waterfallPlayIcon">▶️</span> Riprendi`;
      } else {
        btn.classList.remove("active");
        if (icon) icon.textContent = "⏸️";
        btn.innerHTML = `<span id="waterfallPlayIcon">⏸️</span> Pausa`;
      }
    }

    function resetPeakHold() {
      for (let i = 0; i < SDR_BINS; i++) {
        sdrPeakHold[i] = -118;
      }
      showToast("Picchi FFT azzerati");
    }

    function changeSdrPalette(val) {
      if (SDR_PALETTES[val]) {
        sdrPalette = val;
        showToast(`Tavolozza impostata: ${val.toUpperCase()}`);
      }
    }

    function triggerSimulatedRfBurst() {
      const calls = ['IU0TGU-10', 'I0VUQ-98', 'IK0ZSN-1', 'IZ0MDO', 'IW0HLG'];
      const randCall = calls[Math.floor(Math.random() * calls.length)];
      const randRssi = Math.floor(-72 - Math.random() * 26);
      const randSnr = +(Math.random() * 11 + 4).toFixed(1);

      recordRssi(randCall, randRssi, randSnr);
      playSfx('rx');
      showToast(`⚡ Burst RF LoRa simulato: ${randCall} @ ${randRssi} dBm (SNR +${randSnr} dB)`);
    }

    function onSdrMouseMove(e) {
      const canvas = document.getElementById("sdrFftCanvas");
      const hud = document.getElementById("sdrCrosshairHud");
      if (!canvas || !hud) return;

      const rect = canvas.getBoundingClientRect();
      const clientX = e.clientX - rect.left;
      const clientY = e.clientY - rect.top;

      if (clientX < 0 || clientX > rect.width || clientY < 0 || clientY > rect.height) {
        hud.style.display = "none";
        return;
      }

      const freq = 433.050 + (clientX / rect.width) * 0.250;
      const dbm = -40 - (clientY / rect.height) * 85;
      const sUnit = dbmToSmeterString(dbm);

      hud.style.display = "block";
      hud.style.left = `${Math.min(rect.width - 160, Math.max(10, clientX + 12))}px`;
      hud.style.top = `${Math.min(rect.height - 40, Math.max(10, clientY - 30))}px`;
      hud.innerHTML = `<div><b>${freq.toFixed(3)} MHz</b></div><div style="color:var(--accent-cyan)">${dbm.toFixed(1)} dBm • ${sUnit}</div>`;
    }

    function onSdrMouseLeave() {
      const hud = document.getElementById("sdrCrosshairHud");
      if (hud) hud.style.display = "none";
    }

    function dbmToSmeterString(dbm) {
      if (dbm >= -43) return "S9+30dB";
      if (dbm >= -53) return "S9+20dB";
      if (dbm >= -63) return "S9+10dB";
      if (dbm >= -73) return "S9";
      if (dbm >= -79) return "S8";
      if (dbm >= -85) return "S7";
      if (dbm >= -91) return "S6";
      if (dbm >= -97) return "S5";
      if (dbm >= -103) return "S4";
      if (dbm >= -109) return "S3";
      if (dbm >= -115) return "S2";
      return "S1";
    }

    // ==========================================
    // SPETTRO & STORICO RSSI
    // ==========================================
    function recordRssi(call, rssiVal, snrVal) {
      const validRssi = (typeof rssiVal === 'number' && !isNaN(rssiVal)) ? rssiVal : -90;
      const validSnr = (typeof snrVal === 'number' && !isNaN(snrVal)) ? snrVal : 8.5;

      rssiHistory.push({
        call: call || 'Node',
        rssi: validRssi,
        snr: validSnr,
        time: Date.now()
      });
      if (rssiHistory.length > 40) rssiHistory.shift();

      sdrTotalPacketsAnalyzed++;
      const packetsSeenEl = document.getElementById("rfPacketsSeenSub");
      if (packetsSeenEl) packetsSeenEl.textContent = `${sdrTotalPacketsAnalyzed} pacchetti LoRa analizzati`;

      sdrActiveBurst = {
        call: call || 'Node',
        power: validRssi,
        snr: validSnr,
        startTime: Date.now(),
        duration: 1200
      };

      const curRssiEl = document.getElementById("rfCurRssi");
      if (curRssiEl) curRssiEl.textContent = validRssi;

      const smeterStr = dbmToSmeterString(validRssi);
      const curSmeterEl = document.getElementById("rfCurSmeter");
      if (curSmeterEl) curSmeterEl.textContent = smeterStr;

      const badgeEl = document.getElementById("rfSignalBadge");
      if (badgeEl) {
        badgeEl.className = "rf-badge";
        if (validRssi > -80) {
          badgeEl.textContent = "ECCELLENTE";
          badgeEl.classList.add("active-green");
        } else if (validRssi > -95) {
          badgeEl.textContent = "BUONO";
          badgeEl.classList.add("active-cyan");
        } else if (validRssi > -110) {
          badgeEl.textContent = "MARGINALE";
          badgeEl.classList.add("active-amber");
        } else {
          badgeEl.textContent = "DEBOLE";
        }
      }

      updateLedMeter(validRssi);

      const snrEl = document.getElementById("rfCurSnr");
      if (snrEl) snrEl.textContent = (validSnr > 0 ? `+${validSnr}` : validSnr);

      const snrFill = document.getElementById("rfSnrFill");
      if (snrFill) {
        const snrPct = Math.max(5, Math.min(100, ((validSnr + 20) / 35) * 100));
        snrFill.style.width = `${snrPct}%`;
      }

      updateRssiTrendChart();
      updateRfRankingTable();
    }

    function updateLedMeter(rssi) {
      const activeCount = Math.max(1, Math.min(10, Math.round(((rssi + 125) / 75) * 10)));
      const segs = document.querySelectorAll(".led-bar-seg");
      segs.forEach((seg, idx) => {
        seg.className = "led-bar-seg";
        if (idx < activeCount) {
          if (idx < 4) seg.classList.add("active-cyan");
          else if (idx < 7) seg.classList.add("active-green");
          else if (idx < 9) seg.classList.add("active-amber");
          else seg.classList.add("active-red");
        }
      });
    }

    function updateRssiTrendChart() {
      const canvas = document.getElementById("rssiTrendCanvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const W = canvas.width;
      const H = canvas.height;

      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = "rgba(4, 8, 22, 0.6)";
      ctx.fillRect(0, 0, W, H);

      ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
      ctx.lineWidth = 1;
      for (let i = 1; i <= 3; i++) {
        const y = Math.round((i / 4) * H);
        ctx.beginPath();
        ctx.moveTo(35, y);
        ctx.lineTo(W - 10, y);
        ctx.stroke();
      }

      if (rssiHistory.length < 2) {
        ctx.fillStyle = "var(--text-dim)";
        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.fillText("In attesa di dati RF telemetrici...", W / 2, H / 2);
        return;
      }

      let sum = 0;
      let minRssi = 0;
      let maxRssi = -200;
      rssiHistory.forEach(r => {
        sum += r.rssi;
        if (r.rssi < minRssi) minRssi = r.rssi;
        if (r.rssi > maxRssi) maxRssi = r.rssi;
      });
      const avg = Math.round(sum / rssiHistory.length);
      const avgLabel = document.getElementById("rssiAvgLabel");
      if (avgLabel) avgLabel.textContent = `Media: ${avg} dBm (${rssiHistory.length} pkt)`;

      const minVal = -125;
      const maxVal = -55;
      const toY = (val) => H - 15 - ((Math.max(minVal, Math.min(maxVal, val)) - minVal) / (maxVal - minVal)) * (H - 30);
      const toX = (idx) => 40 + (idx / (rssiHistory.length - 1)) * (W - 55);

      const avgY = toY(avg);
      ctx.strokeStyle = "rgba(6, 182, 212, 0.4)";
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(40, avgY);
      ctx.lineTo(W - 15, avgY);
      ctx.stroke();
      ctx.setLineDash([]);

      const grad = ctx.createLinearGradient(0, 0, 0, H);
      grad.addColorStop(0, "rgba(6, 182, 212, 0.35)");
      grad.addColorStop(1, "rgba(6, 182, 212, 0.0)");

      ctx.beginPath();
      ctx.moveTo(toX(0), H - 15);
      rssiHistory.forEach((r, idx) => {
        ctx.lineTo(toX(idx), toY(r.rssi));
      });
      ctx.lineTo(toX(rssiHistory.length - 1), H - 15);
      ctx.closePath();
      ctx.fillStyle = grad;
      ctx.fill();

      ctx.strokeStyle = "#00f0ff";
      ctx.lineWidth = 2;
      ctx.beginPath();
      rssiHistory.forEach((r, idx) => {
        const x = toX(idx);
        const y = toY(r.rssi);
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      rssiHistory.forEach((r, idx) => {
        const x = toX(idx);
        const y = toY(r.rssi);
        ctx.fillStyle = r.rssi > -80 ? "#10b981" : (r.rssi > -100 ? "#06b6d4" : "#f59e0b");
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.font = "9px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.fillText("-60", 8, toY(-60) + 3);
      ctx.fillText("-90", 8, toY(-90) + 3);
      ctx.fillText("-120", 8, toY(-120) + 3);
    }

    function updateRfRankingTable() {
      const tbody = document.getElementById("rfRankingTableBody");
      const badge = document.getElementById("rfHeardCountBadge");
      if (!tbody) return;

      const stationMap = new Map();

      liveHeardStations.forEach(s => {
        if (s.rssi && s.rssi !== '--') {
          const num = parseInt(s.rssi);
          if (!isNaN(num)) {
            stationMap.set(s.call, {
              call: s.call,
              rssi: num,
              snr: s.snr || '--',
              last: s.last || 'Mesh'
            });
          }
        }
      });

      rssiHistory.forEach(r => {
        if (!stationMap.has(r.call) || stationMap.get(r.call).rssi < r.rssi) {
          stationMap.set(r.call, {
            call: r.call,
            rssi: r.rssi,
            snr: `${r.snr > 0 ? '+' : ''}${r.snr} dB`,
            last: 'Recente'
          });
        }
      });

      const list = Array.from(stationMap.values()).sort((a, b) => b.rssi - a.rssi);

      if (badge) badge.textContent = `${list.length} Nodi`;

      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-dim); padding:2rem 0">In attesa di stazioni RF con telemetria RSSI...</td></tr>`;
        return;
      }

      tbody.innerHTML = list.map((st, i) => {
        const smeter = dbmToSmeterString(st.rssi);
        const color = st.rssi > -80 ? 'var(--accent-green)' : (st.rssi > -95 ? 'var(--accent-cyan)' : 'var(--accent-amber)');
        return `
          <tr>
            <td style="font-family:var(--font-mono); font-weight:700; color:var(--text-dim)">#${i + 1}</td>
            <td style="font-family:var(--font-mono); font-weight:700; color:var(--text-main)">${escapeHtml(st.call)}</td>
            <td style="font-family:var(--font-mono); font-weight:700; color:${color}">${st.rssi} dBm</td>
            <td><span class="rf-badge" style="color:${color}">${smeter}</span></td>
            <td style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted)">${escapeHtml(st.snr)}</td>
            <td>
              <button class="btn-tool" style="padding:0.15rem 0.45rem; font-size:0.7rem;" onclick="openDmWith('${escapeHtml(st.call)}')">
                DM
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }"""

if OLD_SPECTRUM_JS in code:
    code = code.replace(OLD_SPECTRUM_JS, NEW_SPECTRUM_JS)
    print("Replaced JS spectrum section successfully.")
else:
    print("Warning: OLD_SPECTRUM_JS exact string not found! Checking fallback.")

# 6. Also connect window resize listener
if "window.addEventListener('resize'" not in code:
    code = code.replace(
        "    window.addEventListener('load', () => {",
        "    window.addEventListener('resize', () => {\n      const sp = document.getElementById('pane-spectrum');\n      if (sp && sp.classList.contains('active')) initSpectrumCanvases();\n    });\n\n    window.addEventListener('load', () => {"
    )

with open(BUILD_SCRIPT, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated build_ultimate_dashboard.py successfully.")
