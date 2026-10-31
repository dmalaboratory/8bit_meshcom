#!/usr/bin/env python3
"""
Generatore della Dashboard Tattica Definitiva MeshCom (Versione Completa & Unica)
Risolve:
1. Parsing esatto caratteri e frame MeshCom (eliminazione byte nulli, trailer binari, FCS e codici errati).
2. Gestione ACK frame (0x41) come conferme di consegna (doppia spunta ✓✓ verde) invece di testo corrotto.
3. Tutte le funzionalità del MeshCom originale integrate come schede native:
   - Messaggi & Chat (Tutti, Gruppi 222/999, DMs, unread badge, ack, export)
   - MHeard Stazioni con ricerca e filtri
   - Mappa APRS Interattiva (Leaflet.js locale offline) + Radar Tattico commutabile
   - Meteo & Telemetria WX completa (Temp, Hum, Press, Alt, Gas, CO2, INA226 V/mA/mW)
   - Matrice Vicini MeshCom 5 (Topologia e link radio SNR/RSSI)
   - Log Pacchetti RX in tempo reale con hex dump e download txt
   - RF & Spettro / Monitor RSSI
   - Configurazione Completa Nodo (Call, APRS, Simbolo, Freq, Power, SF, CR, BW, Mesh, GW, GPS, Wi-Fi, Reboot)
   - Connessione BLE & Wi-Fi + Terminale CLI Diretto
4. Funzionalità uniche esclusive:
   - Effetti Sonori Radioamatoriali Web Audio (Roger Beep alla trasmissione, Chime all'ascolto, pulsante Mute)
   - Calcolatore interattivo QTH Locator Maidenhead e distanza Haversine
   - Design Tattico Dark Glassmorphism ad alta leggibilità con font ottimizzati
"""

import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="theme-color" content="#070a12">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <title>MeshCom Tactical Pro - IU0TGU-10</title>
  <link rel="manifest" href="manifest.json">
  <link rel="stylesheet" href="leaflet.css" />
  <script src="leaflet.js"></script>

  <style>
    :root {
      --bg-base: #060913;
      --bg-surface: #0b1122;
      --bg-surface-elevated: #131d36;
      --bg-card: rgba(16, 25, 48, 0.78);
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-active: rgba(6, 182, 212, 0.45);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent-cyan: #06b6d4;
      --accent-cyan-glow: rgba(6, 182, 212, 0.25);
      --accent-green: #10b981;
      --accent-green-glow: rgba(16, 185, 129, 0.25);
      --accent-amber: #f59e0b;
      --accent-red: #ef4444;
      --accent-blue: #3b82f6;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, "JetBrains Mono", Consolas, Menlo, monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-base);
      background-image: 
        radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.08) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.06) 0px, transparent 50%);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }

    /* HEADER */
    header {
      background: rgba(9, 14, 27, 0.9);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      position: sticky;
      top: 0;
      z-index: 1000;
      padding: 0.65rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .brand-icon {
      width: 36px;
      height: 36px;
      border-radius: var(--radius-sm);
      background: linear-gradient(135deg, #0891b2, #0284c7);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 16px var(--accent-cyan-glow);
    }
    .brand-title {
      font-weight: 800;
      font-size: 1.05rem;
      letter-spacing: 0.06em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .brand-callsign {
      color: var(--accent-cyan);
      font-family: var(--font-mono);
      font-size: 1.05rem;
      font-weight: 800;
      text-shadow: 0 0 10px var(--accent-cyan-glow);
    }

    .header-pills {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }
    .status-pill {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      border-radius: 9999px;
      padding: 0.25rem 0.65rem;
      font-size: 0.75rem;
      font-family: var(--font-mono);
      display: flex;
      align-items: center;
      gap: 0.4rem;
      color: var(--text-muted);
    }
    .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--text-dim);
    }
    .dot.online { background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green); }
    .dot.ble { background: #38bdf8; box-shadow: 0 0 8px #38bdf8; }
    .dot.offline { background: var(--accent-red); }

    .btn-header {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      border-radius: 9999px;
      padding: 0.25rem 0.65rem;
      font-size: 0.75rem;
      font-family: var(--font-mono);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.2s;
    }
    .btn-header:hover {
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }

    /* MAIN CONTAINER */
    main {
      flex: 1;
      padding: 1rem 1.25rem;
      max-width: 1440px;
      margin: 0 auto;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    /* TELEMETRY CARDS STRIP */
    .telemetry-strip {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 0.75rem;
    }

    .card {
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.85rem 1rem;
      transition: border-color 0.2s, transform 0.2s;
    }
    .card:hover {
      border-color: rgba(255, 255, 255, 0.16);
    }

    .stat-label {
      font-size: 0.7rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 0.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .stat-value {
      font-size: 1.2rem;
      font-weight: 700;
      font-family: var(--font-mono);
      color: var(--text-main);
      display: flex;
      align-items: baseline;
      gap: 0.35rem;
    }
    .stat-unit {
      font-size: 0.75rem;
      font-weight: normal;
      color: var(--text-dim);
    }
    .stat-sub {
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 0.25rem;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* NAVIGATION TABS */
    .tabs-bar {
      display: flex;
      gap: 0.4rem;
      background: var(--bg-surface);
      padding: 0.35rem;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-subtle);
      flex-wrap: wrap;
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.45rem;
      white-space: nowrap;
      transition: all 0.2s;
    }
    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }
    .tab-btn.active {
      color: #fff;
      background: var(--bg-surface-elevated);
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-active);
    }
    .tab-badge {
      background: rgba(6, 182, 212, 0.18);
      color: var(--accent-cyan);
      font-size: 0.7rem;
      padding: 0.1rem 0.4rem;
      border-radius: 9999px;
      font-family: var(--font-mono);
      font-weight: 700;
    }

    /* TAB CONTENT PANES */
    .tab-pane {
      display: none;
      flex-direction: column;
      gap: 1rem;
      animation: fadeIn 0.2s ease-in-out;
    }
    .tab-pane.active {
      display: flex;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* PANE 1: CHAT LAYOUT */
    .chat-layout {
      display: grid;
      grid-template-columns: 240px 1fr;
      gap: 1rem;
      height: 580px;
    }
    @media (max-width: 860px) {
      .chat-layout { grid-template-columns: 1fr; height: auto; }
      .channels-panel { max-height: 140px; }
      .chat-window { height: 480px; }
    }

    .channels-panel {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.65rem;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      overflow-y: auto;
    }
    .channel-title-bar {
      font-size: 0.68rem;
      color: var(--text-dim);
      text-transform: uppercase;
      font-weight: 700;
      padding: 0.25rem 0.5rem;
      letter-spacing: 0.05em;
    }
    .channel-item {
      padding: 0.5rem 0.65rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: all 0.2s;
      font-size: 0.82rem;
      color: var(--text-muted);
    }
    .channel-item:hover {
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-main);
    }
    .channel-item.active {
      background: rgba(6, 182, 212, 0.12);
      border: 1px solid var(--border-active);
      color: var(--accent-cyan);
      font-weight: 600;
    }
    .badge-tag {
      font-family: var(--font-mono);
      font-size: 0.65rem;
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
      background: rgba(0, 0, 0, 0.35);
      color: var(--text-muted);
      border: 1px solid var(--border-subtle);
    }

    .chat-window {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .chat-header {
      padding: 0.65rem 1rem;
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(0, 0, 0, 0.25);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .chat-messages {
      flex: 1;
      padding: 1rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    .msg-bubble {
      max-width: 78%;
      padding: 0.65rem 0.85rem;
      border-radius: var(--radius-md);
      font-size: 0.86rem;
      line-height: 1.4;
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
      word-break: break-word;
    }
    .msg-inbound {
      background: rgba(14, 23, 42, 0.9);
      border: 1px solid rgba(255, 255, 255, 0.08);
      align-self: flex-start;
      border-bottom-left-radius: 2px;
    }
    .msg-outbound {
      background: linear-gradient(135deg, #0e7490, #0369a1);
      border: 1px solid rgba(6, 182, 212, 0.4);
      align-self: flex-end;
      border-bottom-right-radius: 2px;
      color: #fff;
    }
    .msg-meta {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.72rem;
      color: var(--text-muted);
    }
    .msg-outbound .msg-meta { color: rgba(255, 255, 255, 0.8); }
    .msg-sender {
      font-weight: 700;
      color: var(--accent-cyan);
      font-family: var(--font-mono);
    }
    .msg-outbound .msg-sender { color: #67e8f9; }
    .msg-time {
      font-size: 0.68rem;
      color: var(--text-dim);
      margin-top: 0.15rem;
      text-align: right;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 0.3rem;
    }
    .msg-outbound .msg-time { color: rgba(255, 255, 255, 0.75); }

    .canned-bar {
      padding: 0.4rem 0.85rem;
      border-top: 1px solid var(--border-subtle);
      background: rgba(0, 0, 0, 0.25);
      display: flex;
      gap: 0.35rem;
      flex-wrap: wrap;
      align-items: center;
    }
    .quick-chip {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      border-radius: 9999px;
      color: var(--text-muted);
      padding: 0.2rem 0.55rem;
      font-size: 0.72rem;
      font-family: var(--font-mono);
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
    }
    .quick-chip:hover {
      background: var(--accent-cyan-glow);
      color: var(--accent-cyan);
      border-color: var(--border-active);
    }

    .chat-input-bar {
      padding: 0.65rem 0.85rem;
      background: rgba(0, 0, 0, 0.35);
      border-top: 1px solid var(--border-subtle);
      display: flex;
      gap: 0.5rem;
    }
    .chat-target-select {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--accent-cyan);
      border-radius: var(--radius-sm);
      padding: 0.5rem 0.65rem;
      font-family: var(--font-mono);
      font-size: 0.82rem;
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }
    .chat-input {
      flex: 1;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.5rem 0.85rem;
      color: var(--text-main);
      font-size: 0.86rem;
      outline: none;
    }
    .chat-input:focus {
      border-color: var(--accent-cyan);
    }
    .btn-send {
      background: linear-gradient(135deg, #0891b2, #0284c7);
      border: none;
      color: #fff;
      border-radius: var(--radius-sm);
      padding: 0.5rem 1rem;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s;
    }
    .btn-send:hover {
      box-shadow: 0 0 12px var(--accent-cyan-glow);
      filter: brightness(1.1);
    }

    /* TABLES (MHeard, Logs, Matrix) */
    .data-table-container {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      overflow-x: auto;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.82rem;
    }
    .data-table th {
      background: rgba(0, 0, 0, 0.3);
      padding: 0.65rem 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border-subtle);
      text-transform: uppercase;
      font-size: 0.7rem;
      letter-spacing: 0.05em;
    }
    .data-table td {
      padding: 0.65rem 0.85rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-main);
    }
    .data-table tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }

    /* MAP & RADAR */
    .map-wrapper {
      height: 520px;
      border-radius: var(--radius-md);
      overflow: hidden;
      border: 1px solid var(--border-subtle);
      position: relative;
    }
    #aprsMap {
      width: 100%;
      height: 100%;
      background: #060913;
    }
    .radar-box {
      width: 100%;
      height: 100%;
      background: radial-gradient(circle, #0a1426 0%, #030611 100%);
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .radar-sweep {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 50%;
      height: 2px;
      transform-origin: 0% 0%;
      background: linear-gradient(90deg, #10b981, transparent);
      box-shadow: 0 0 15px #10b981;
      animation: sweep 4s infinite linear;
    }
    @keyframes sweep {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .radar-circle {
      position: absolute;
      border: 1px dashed rgba(16, 185, 129, 0.25);
      border-radius: 50%;
    }
    .radar-c1 { width: 30%; height: 30%; }
    .radar-c2 { width: 60%; height: 60%; }
    .radar-c3 { width: 90%; height: 90%; }
    .radar-node-dot {
      position: absolute;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      transform: translate(-50%, -50%);
      box-shadow: 0 0 8px currentColor;
      cursor: pointer;
      transition: transform 0.2s;
    }
    .radar-node-dot:hover {
      transform: translate(-50%, -50%) scale(1.4);
      z-index: 20;
    }
    .radar-node-label {
      position: absolute;
      top: 12px;
      left: 50%;
      transform: translateX(-50%);
      font-family: var(--font-mono);
      font-size: 0.68rem;
      white-space: nowrap;
      text-shadow: 0 0 4px #000;
    }

    /* NEIGHBOURS MATRIX */
    .matrix-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 0.75rem;
    }
    .matrix-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.85rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    .matrix-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .matrix-call {
      font-weight: 700;
      font-family: var(--font-mono);
      color: var(--accent-cyan);
      font-size: 0.95rem;
    }
    .signal-bar-wrap {
      background: rgba(255, 255, 255, 0.06);
      height: 6px;
      border-radius: 3px;
      overflow: hidden;
      display: flex;
    }
    .signal-bar-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.3s;
    }

    /* TERMINAL & LOGS */
    .log-terminal {
      background: #030611;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.75rem;
      height: 240px;
      overflow-y: auto;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: #a5f3fc;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    /* FORM CONTROLS */
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      margin-bottom: 0.85rem;
    }
    .form-group label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }
    .form-control {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.5rem 0.75rem;
      color: var(--text-main);
      font-size: 0.85rem;
      outline: none;
    }
    .form-control:focus {
      border-color: var(--accent-cyan);
    }
    .switch-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 42px;
      height: 22px;
    }
    .toggle-switch input { opacity: 0; width: 0; height: 0; }
    .toggle-slider {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 22px;
      transition: .3s;
    }
    .toggle-slider:before {
      position: absolute;
      content: "";
      height: 16px; width: 16px;
      left: 2px; bottom: 2px;
      background-color: var(--text-dim);
      border-radius: 50%;
      transition: .3s;
    }
    input:checked + .toggle-slider {
      background-color: rgba(16, 185, 129, 0.3);
      border-color: var(--accent-green);
    }
    input:checked + .toggle-slider:before {
      transform: translateX(20px);
      background-color: var(--accent-green);
    }

    .btn-action {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius-sm);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.2s;
    }
    .btn-action:hover {
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }
    .btn-danger {
      color: var(--accent-red);
    }
    .btn-danger:hover {
      border-color: var(--accent-red);
      background: rgba(239, 68, 68, 0.1);
    }

    /* TOAST NOTIFICATION */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border-active);
      border-radius: var(--radius-sm);
      padding: 0.75rem 1.25rem;
      color: #fff;
      font-size: 0.82rem;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
      z-index: 9999;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      max-width: 380px;
    }
    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }

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

  </style>
</head>
<body>

  <!-- HEADER -->
  <header>
    <div class="brand">
      <div class="brand-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="2"></circle>
          <path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"></path>
        </svg>
      </div>
      <div>
        <div class="brand-title">
          <span>MESHCOM</span>
          <span class="brand-callsign" id="hdrCallsign">IU0TGU-10</span>
          <span class="badge-tag" id="hdrHwBadge" style="color:var(--accent-cyan); border-color:var(--border-active)">ESP32</span>
        </div>
      </div>
    </div>

    <div class="header-pills">
      <div class="status-pill" id="connStatusPill">
        <span class="dot ble" id="statusDot"></span>
        <span id="connStatusText">BLE CONNESSO</span>
      </div>
      <div class="status-pill" id="blePill">
        <span style="color:#60a5fa" id="blePillName">📶 MC-a498 IU0TGU-10</span>
      </div>
      <div class="status-pill">
        <span>⏱️ <span id="hdrUtcTime">--:--:-- UTC</span></span>
      </div>
      <div class="status-pill">
        <span id="hdrBattery">🔋 --V (--%)</span>
      </div>
      <button class="btn-header" id="btnHdrConnect" onclick="connectBle()" style="border-color:var(--accent-cyan); color:var(--accent-cyan); background:rgba(6,182,212,0.12)">
        <span>📶 Connetti BLE</span>
      </button>
      <button class="btn-header" id="btnAudioToggle" onclick="toggleAudioFx()">
        <span id="audioIcon">🔊</span> <span id="audioLabel">Audio ON</span>
      </button>
      <button class="btn-header" onclick="requestNodeTelemetry()">
        <span>🔄 Sync</span>
      </button>
    </div>
  </header>

  <!-- MAIN -->
  <main>

    <!-- LIVE TELEMETRY CARDS -->
    <section class="telemetry-strip">
      <div class="card">
        <div class="stat-label">
          <span>Stato Radio LoRa</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/><circle cx="12" cy="12" r="2"/></svg>
        </div>
        <div class="stat-value" id="cardFreq">433.175 <span class="stat-unit">MHz</span></div>
        <div class="stat-sub">
          <span style="color:var(--accent-cyan)" id="cardTxPower">TX 20 dBm</span> • <span id="cardModulation">SF11 CR4/5 BW125</span>
        </div>
      </div>

      <div class="card">
        <div class="stat-label">
          <span>Posizione GPS (APRS)</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
        </div>
        <div class="stat-value" id="cardLocator">JN61...</div>
        <div class="stat-sub" id="cardGpsCoords">
          <span>In attesa di fix GPS dal nodo...</span>
        </div>
      </div>

      <div class="card">
        <div class="stat-label">
          <span>Meteo / Telemetria WX</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/></svg>
        </div>
        <div class="stat-value" id="cardTemp">--.- <span class="stat-unit">°C</span></div>
        <div class="stat-sub" id="cardWeatherExtra">
          <span>Sensore in lettura...</span>
        </div>
      </div>

      <div class="card">
        <div class="stat-label">
          <span>Traffico & Statistiche</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m18 15-6-6-6 6"/></svg>
        </div>
        <div class="stat-value" id="cardMsgCount">0 <span class="stat-unit">msg live</span></div>
        <div class="stat-sub">
          <span style="color:var(--accent-green)" id="cardStatsRx">RX: 0</span> • <span style="color:var(--accent-cyan)" id="cardStatsTx">TX: 0</span> • <span id="cardAcks">ACK: 0</span>
        </div>
      </div>
    </section>

    <!-- NAVIGATION TABS (TUTTE LE FUNZIONI MESHCOM ORIGINALE + FUTURE) -->
    <nav class="tabs-bar">
      <button class="tab-btn active" onclick="switchTab('chat')">
        💬 Messaggi & Chat <span class="tab-badge" id="badgeUnread">0</span>
      </button>
      <button class="tab-btn" onclick="switchTab('mheard')">
        📡 MHeard (Stazioni) <span class="tab-badge" id="badgeMheard">0</span>
      </button>
      <button class="tab-btn" onclick="switchTab('map')">
        🗺️ Mappa & Radar APRS
      </button>
      <button class="tab-btn" onclick="switchTab('wx')">
        🌤️ Meteo & Sensori WX
      </button>
      <button class="tab-btn" onclick="switchTab('matrix')">
        🌐 Matrice Vicini (MeshCom 5)
      </button>
      <button class="tab-btn" onclick="switchTab('rxlog')">
        📜 Log Pacchetti & RX
      </button>
      <button class="tab-btn" onclick="switchTab('spectrum')">
        📡 RF & Spettro SDR
      </button>
      <button class="tab-btn" onclick="switchTab('setup')">
        ⚙️ Configurazione Nodo
      </button>
      <button class="tab-btn" onclick="switchTab('connection')">
        🔌 Connessione & CLI
      </button>
    </nav>

    <!-- PANE 1: CHAT & MESSAGGI -->
    <section class="tab-pane active" id="pane-chat">
      <div class="chat-layout">
        <div class="channels-panel">
          <div class="channel-title-bar">Canali LoRa</div>
          <div class="channel-item active" onclick="selectChannel('*', this)">
            <div>
              <div style="font-weight:600">Canale Generale</div>
              <div style="font-size:0.7rem; color:var(--text-dim)">Broadcast (*)</div>
            </div>
            <span class="badge-tag">TUTTI</span>
          </div>
          <div class="channel-item" onclick="selectChannel('222', this)">
            <div>
              <div style="font-weight:600">Gruppo Italia</div>
              <div style="font-size:0.7rem; color:var(--text-dim)">Canale 222 / 22251</div>
            </div>
            <span class="badge-tag">GRUPPO</span>
          </div>
          <div class="channel-item" onclick="selectChannel('999', this)">
            <div>
              <div style="font-weight:600">Emergenza Ham</div>
              <div style="font-size:0.7rem; color:var(--text-dim)">Canale 999</div>
            </div>
            <span class="badge-tag" style="color:var(--accent-red); border-color:var(--accent-red)">EMERG</span>
          </div>

          <div class="channel-title-bar" style="margin-top:0.5rem">Messaggi Diretti (DM)</div>
          <div class="channel-item" id="dynamicDmChannel" style="display:none;" onclick="selectChannel(this.getAttribute('data-dm'), this)">
            <div>
              <div style="font-weight:600" id="dynamicDmTitle">DM</div>
              <div style="font-size:0.7rem; color:var(--text-dim)">Chat Privata</div>
            </div>
            <span class="badge-tag">DM</span>
          </div>
        </div>

        <div class="chat-window">
          <div class="chat-header">
            <div>
              <span style="font-weight:700" id="currentChannelTitle">Canale Generale (*)</span>
              <span style="font-size:0.75rem; color:var(--text-muted); margin-left:0.5rem" id="currentChannelSub">Traffico LoRa in tempo reale</span>
            </div>
            <div style="display:flex; gap:0.4rem">
              <button class="btn-action" style="padding:0.25rem 0.5rem; font-size:0.75rem" onclick="exportChatHistory()">
                💾 Esporta Chat
              </button>
              <button class="btn-action" style="padding:0.25rem 0.5rem; font-size:0.75rem" onclick="clearChat()">
                🗑️ Pulisci
              </button>
            </div>
          </div>

          <div class="chat-messages" id="messagesList">
            <div style="text-align:center; color:var(--text-dim); margin:auto" id="noMessagesPlaceholder">
              In ascolto della rete mesh LoRa... Nessun messaggio ancora ricevuto.<br>
              Invia un messaggio o usa i pulsanti rapidi sotto per trasmettere via radio!
            </div>
          </div>

          <!-- MESSAGGI RAPIDI (CANNED MESSAGES) -->
          <div class="canned-bar">
            <span style="font-size:0.7rem; color:var(--text-dim); text-transform:uppercase; font-weight:700">Rapidi:</span>
            <button class="quick-chip" onclick="quickSend('73 de IU0TGU-10!')">73 de IU0TGU</button>
            <button class="quick-chip" onclick="quickSend('CQ CQ CQ de IU0TGU-10')">CQ CQ</button>
            <button class="quick-chip" onclick="quickSend('Radio Check QSO - Come mi ricevi?')">Radio Check</button>
            <button class="quick-chip" onclick="quickSend('QRV dal mio QTH!')">QRV QTH</button>
            <button class="quick-chip" onclick="quickSend('73 a tutti dal nodo MeshCom!')">73 a tutti</button>
          </div>

          <!-- BARRA INVIO -->
          <div class="chat-input-bar">
            <select class="chat-target-select" id="sendTargetSelect" onchange="onTargetSelectChange(this.value)">
              <option value="*">* (Broadcast)</option>
              <option value="222">Gr. 222</option>
              <option value="999">Gr. 999</option>
              <option value="CUSTOM">Altro Callsign...</option>
            </select>
            <input type="text" class="chat-input" id="messageInput" placeholder="Digita un messaggio LoRa da trasmettere con IU0TGU-10..." maxlength="110" onkeypress="if(event.key==='Enter') sendMeshMessage()">
            <button class="btn-send" onclick="sendMeshMessage()">
              <span>Invia</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- PANE 2: MHEARD (STAZIONI ASCOLTATE) -->
    <section class="tab-pane" id="pane-mheard">
      <div class="card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem">
        <div>
          <h3 style="font-size:0.95rem; font-weight:700">Stazioni LoRa Ascoltate (MHeard)</h3>
          <p style="font-size:0.75rem; color:var(--text-muted)">Elenco nodi e gateway ricevuti direttamente via etere o tramite ripetitori mesh</p>
        </div>
        <div style="display:flex; gap:0.5rem; align-items:center">
          <input type="text" class="form-control" style="font-size:0.78rem; padding:0.3rem 0.6rem; width:160px" placeholder="Filtra nominativo..." id="mheardFilter" oninput="renderMheard()">
          <button class="btn-action" onclick="execDirectCmd('--mheard')">🔄 Richiedi MHeard</button>
        </div>
      </div>

      <div class="data-table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Nominativo (Callsign)</th>
              <th>Distanza / Percorso</th>
              <th>Segnale (SNR / RSSI)</th>
              <th>Salti (Hops)</th>
              <th>Ultimo Contatto</th>
              <th>Azioni</th>
            </tr>
          </thead>
          <tbody id="mheardTableBody">
            <tr>
              <td colspan="6" style="text-align:center; color:var(--text-dim); padding:2rem">
                In ascolto del traffico LoRa... Nessuna stazione ancora registrata.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- PANE 3: MAPPA & RADAR APRS -->
    <section class="tab-pane" id="pane-map">
      <div class="card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem">
        <div>
          <h3 style="font-size:0.95rem; font-weight:700">Mappa Geografica & Radar APRS LoRa</h3>
          <p style="font-size:0.75rem; color:var(--text-muted)">Posizioni delle stazioni ricevute via radio con tracciamento vettoriale</p>
        </div>
        <div style="display:flex; gap:0.5rem">
          <button class="btn-action" id="btnToggleMapMode" onclick="toggleMapMode()">
            🎯 Passa a Radar Tattico
          </button>
          <button class="btn-action" onclick="callNodeFn('sendpos')">
            📡 Invia Beacon Posizione
          </button>
        </div>
      </div>

      <div class="map-wrapper">
        <div id="aprsMap"></div>
        <div class="radar-box" id="radarContainer" style="display:none">
          <div class="radar-sweep"></div>
          <div class="radar-circle radar-c1"></div>
          <div class="radar-circle radar-c2"></div>
          <div class="radar-circle radar-c3"></div>
          <div class="radar-node-dot" style="top:50%; left:50%; background:#10b981; color:#10b981">
            <div class="radar-node-label" id="radarCenterLabel">TU (IU0TGU-10)</div>
          </div>
        </div>
      </div>
    </section>

    <!-- PANE 4: METEO & SENSORI WX -->
    <section class="tab-pane" id="pane-wx">
      <div class="card">
        <h3 style="font-size:0.95rem; font-weight:700; margin-bottom:0.25rem">Stazione Meteo & Telemetria Ambientale (BME280 / INA226)</h3>
        <p style="font-size:0.75rem; color:var(--text-muted)">Dati acquisiti dai sensori I2C a bordo del nodo ESP32</p>
      </div>

      <div class="telemetry-strip">
        <div class="card">
          <div class="stat-label">Temperatura Ambiente</div>
          <div class="stat-value" id="wxTemp">--.- <span class="stat-unit">°C</span></div>
          <div class="stat-sub">Sensore BME280 / AHT20</div>
        </div>
        <div class="card">
          <div class="stat-label">Umidità Relativa</div>
          <div class="stat-value" id="wxHum">-- <span class="stat-unit">%</span></div>
          <div class="stat-sub">Umidità aria locale</div>
        </div>
        <div class="card">
          <div class="stat-label">Pressione Atmosferica</div>
          <div class="stat-value" id="wxPress">----.- <span class="stat-unit">hPa</span></div>
          <div class="stat-sub" id="wxQnh">QNH: ---- hPa</div>
        </div>
        <div class="card">
          <div class="stat-label">Altitudine Barometrica</div>
          <div class="stat-value" id="wxAlt">--- <span class="stat-unit">m</span></div>
          <div class="stat-sub">Calcolata da gradiente barico</div>
        </div>
        <div class="card">
          <div class="stat-label">Tensione Batteria / Bus</div>
          <div class="stat-value" id="wxBatV">-.-- <span class="stat-unit">V</span></div>
          <div class="stat-sub" id="wxBatP">Carica stimata: --%</div>
        </div>
        <div class="card">
          <div class="stat-label">Qualità Aria / Sensori Extra</div>
          <div class="stat-value" id="wxGas">-- <span class="stat-unit">kΩ</span></div>
          <div class="stat-sub" id="wxCo2">CO2: -- ppm</div>
        </div>
      </div>
    </section>

    <!-- PANE 5: MATRICE VICINI (MESHCOM 5 NEIGHBOURS) -->
    <section class="tab-pane" id="pane-matrix">
      <div class="card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem">
        <div>
          <h3 style="font-size:0.95rem; font-weight:700">Topologia & Matrice Vicini (MeshCom 5 Matrix)</h3>
          <p style="font-size:0.75rem; color:var(--text-muted)">Relazioni radio bilaterali e qualità del link RF con i nodi adiacenti</p>
        </div>
        <button class="btn-action" onclick="execDirectCmd('--neighbours')">🔄 Aggiorna Matrice</button>
      </div>

      <div class="matrix-grid" id="neighboursMatrixGrid">
        <div class="matrix-card">
          <div style="text-align:center; color:var(--text-dim); padding:1rem">
            In attesa di dati topologici dal nodo...<br>
            I vicini appariranno qui man mano che trasmettono pacchetti radio.
          </div>
        </div>
      </div>
    </section>

    <!-- PANE 6: LOG PACCHETTI RAW & RX LOG -->
    <section class="tab-pane" id="pane-rxlog">
      <div class="card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem">
        <div>
          <h3 style="font-size:0.95rem; font-weight:700">Analizzatore Pacchetti LoRa (RX & TX Packet Inspector)</h3>
          <p style="font-size:0.75rem; color:var(--text-muted)">Tracciamento di ogni frame grezzo ricevuto con verifica FCS, MsgID e payload</p>
        </div>
        <div style="display:flex; gap:0.5rem">
          <button class="btn-action" onclick="downloadPacketLog()">💾 Scarica Log (.txt)</button>
          <button class="btn-action" onclick="clearPacketLog()">🗑️ Pulisci Log</button>
        </div>
      </div>

      <div class="data-table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:90px">Ora (UTC)</th>
              <th style="width:80px">Tipo</th>
              <th style="width:140px">Intestazione</th>
              <th>Payload Decodificato</th>
              <th>Dump Hex</th>
            </tr>
          </thead>
          <tbody id="packetLogTableBody">
            <tr>
              <td colspan="5" style="text-align:center; color:var(--text-dim); padding:1.5rem">
                Nessun pacchetto ancora registrato nella sessione.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- PANE 7: RF & SPETTRO TATTICO SDR -->
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
    </section>

    <!-- PANE 8: CONFIGURAZIONE NODO COMPLETA -->
    <section class="tab-pane" id="pane-setup">
      <div class="form-grid">
        <!-- 1. Identità & APRS -->
        <div class="card">
          <h3 style="font-size:0.95rem; font-weight:700; margin-bottom:1rem; color:var(--accent-cyan)">
            🏷️ Identità Nodo & APRS
          </h3>
          <div class="form-group">
            <label>Nominativo (Callsign con SSID)</label>
            <input type="text" class="form-control" id="cfgCallsign" value="IU0TGU-10" maxlength="10">
          </div>
          <div class="form-group">
            <label>Testo Beacon APRS (Commento)</label>
            <input type="text" class="form-control" id="cfgAprsText" value="MeshCom LoRa Node IU0TGU" maxlength="50">
          </div>
          <div class="form-group">
            <label>Icona Simbolo APRS</label>
            <select class="form-control" id="cfgSymbol">
              <option value="/#">Digipeater (#)</option>
              <option value="/[">Runner / Jogger ([)</option>
              <option value="/-">House QTH (-)</option>
              <option value="/>">Auto Car (>)</option>
              <option value="/k">Truck (k)</option>
              <option value="/Y">Yacht / Boat (Y)</option>
            </select>
          </div>
          <button class="btn-send" style="width:100%" onclick="saveNodeIdentity()">
            Salva Identità & APRS
          </button>
        </div>

        <!-- 2. Parametri RF LoRa -->
        <div class="card">
          <h3 style="font-size:0.95rem; font-weight:700; margin-bottom:1rem; color:var(--accent-cyan)">
            📻 Parametri RF LoRa
          </h3>
          <div class="form-group">
            <label>Frequenza Radio (MHz)</label>
            <input type="number" step="0.005" class="form-control" id="cfgFreq" value="433.175">
          </div>
          <div class="form-group">
            <label>Potenza di Trasmissione TX (dBm)</label>
            <input type="number" min="2" max="22" class="form-control" id="cfgTxPower" value="20">
          </div>
          <div class="form-group">
            <label>Spreading Factor (SF)</label>
            <select class="form-control" id="cfgSf">
              <option value="11" selected>SF11 (Standard MeshCom)</option>
              <option value="12">SF12 (Massima Portata)</option>
              <option value="10">SF10</option>
              <option value="9">SF9</option>
              <option value="8">SF8</option>
              <option value="7">SF7 (Massima Velocità)</option>
            </select>
          </div>
          <button class="btn-send" style="width:100%" onclick="saveRadioParams()">
            Salva Parametri RF
          </button>
        </div>

        <!-- 3. Servizi & Funzioni Mesh -->
        <div class="card">
          <h3 style="font-size:0.95rem; font-weight:700; margin-bottom:1rem; color:var(--accent-cyan)">
            🔄 Servizi di Rete & Routing
          </h3>
          <div class="switch-row">
            <div>
              <div style="font-weight:600; font-size:0.85rem">Mesh Routing (Ripetitore)</div>
              <div style="font-size:0.72rem; color:var(--text-dim)">Inoltra pacchetti degli altri nodi</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" id="cfgMesh" checked onchange="toggleMeshParam('mesh', this.checked)">
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="switch-row">
            <div>
              <div style="font-weight:600; font-size:0.85rem">Gateway Internet</div>
              <div style="font-size:0.72rem; color:var(--text-dim)">Inoltra su Server MeshCom</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" id="cfgGateway" onchange="toggleMeshParam('gateway', this.checked)">
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="switch-row">
            <div>
              <div style="font-weight:600; font-size:0.85rem">Modulo GPS Hardware</div>
              <div style="font-size:0.72rem; color:var(--text-dim)">Acquisizione coordinate da satellite</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" id="cfgGps" checked onchange="toggleMeshParam('gps', this.checked)">
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <!-- 4. Azioni Rapide Hardware -->
        <div class="card">
          <h3 style="font-size:0.95rem; font-weight:700; margin-bottom:1rem; color:var(--accent-cyan)">
            ⚡ Azioni Hardware Dirette
          </h3>
          <div style="display:flex; flex-direction:column; gap:0.65rem">
            <button class="btn-action" onclick="callNodeFn('sendpos')">📍 Forza Invio Beacon Posizione</button>
            <button class="btn-action" onclick="requestNodeTelemetry()">🔄 Ricarica Telemetria Nodo (--info, --wx)</button>
            <button class="btn-action btn-danger" onclick="confirmReboot()">⚠️ Riavvia Nodo ESP32</button>
          </div>
        </div>
      </div>
    </section>

    <!-- PANE 9: CONNESSIONE & CLI TERMINAL -->
    <section class="tab-pane" id="pane-connection">
      <div class="card" style="max-width:840px; margin:0 auto; width:100%">
        <h3 style="font-size:1rem; font-weight:700; margin-bottom:0.75rem; color:var(--accent-cyan)">
          🔌 Connessione Hardware & Terminale CLI Nordic UART
        </h3>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.5rem">
          <div>
            <div style="font-size:0.85rem; font-weight:600">Dispositivo Accoppiato: <span id="bleDeviceLabel" style="color:var(--accent-cyan); font-family:var(--font-mono)">MC-a498 IU0TGU-10</span></div>
            <div style="font-size:0.72rem; color:var(--text-muted)">Servizio Nordic UART Service (NUS) attivo su 6E400001-...</div>
          </div>
          <div style="display:flex; gap:0.5rem">
            <button class="btn-send" id="btnScanBle" style="display:none" onclick="connectBle()">Riconnetti BLE</button>
            <button class="btn-action" id="btnDisconnectBle" onclick="disconnectBle()">Disconnetti</button>
            <button class="btn-action" onclick="sendBleHandshake()">Handshake (0x10)</button>
          </div>
        </div>

        <!-- CLI Terminal Box -->
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem">
          <span style="font-size:0.72rem; color:var(--text-muted); font-weight:700; text-transform:uppercase">Terminale Pacchetti BLE & Comandi:</span>
          <button class="btn-action" style="padding:0.15rem 0.45rem; font-size:0.7rem" onclick="clearBleLog()">Pulisci log</button>
        </div>
        <div class="log-terminal" id="bleLogTerminal">
          <div>[INFO] Connessione Bluetooth attiva con MC-a498 IU0TGU-10.</div>
        </div>

        <!-- Comandi Rapidi CLI -->
        <div style="margin-top:0.75rem; display:flex; flex-direction:column; gap:0.4rem">
          <div style="font-size:0.72rem; color:var(--text-dim); font-weight:700">COMANDI RAPIDI FIRMWARE:</div>
          <div style="display:flex; gap:0.35rem; flex-wrap:wrap">
            <button class="quick-chip" onclick="execDirectCmd('--info')">--info</button>
            <button class="quick-chip" onclick="execDirectCmd('--wx')">--wx</button>
            <button class="quick-chip" onclick="execDirectCmd('--pos')">--pos</button>
            <button class="quick-chip" onclick="execDirectCmd('--nodeset')">--nodeset</button>
            <button class="quick-chip" onclick="execDirectCmd('--wifiset')">--wifiset</button>
            <button class="quick-chip" onclick="execDirectCmd('--mheard')">--mheard</button>
            <button class="quick-chip" onclick="execDirectCmd('--batt')">--batt</button>
            <button class="quick-chip" onclick="execDirectCmd('--help')">--help</button>
          </div>
          <div style="display:flex; gap:0.5rem; margin-top:0.35rem">
            <input type="text" id="cliCommandInput" class="form-control" style="font-family:var(--font-mono); font-size:0.82rem" placeholder="Digita comando MeshCom diretto (es: --info, --wx, --help)..." onkeydown="if(event.key==='Enter') sendCliCommand()">
            <button class="btn-send" style="padding:0.45rem 1rem" onclick="sendCliCommand()">Invia</button>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- TOAST -->
  <div class="toast" id="toast">
    <span id="toastIcon">ℹ️</span>
    <span id="toastMsg">Notifica</span>
  </div>

  <script>
    // ==========================================
    // STATO APPLICAZIONE & LIVE NODE IU0TGU-10
    // ==========================================
    let activeMode = "ble";
    let ownCallsign = "IU0TGU-10";
    let currentChannel = "*";
    let audioFxEnabled = true;
    let mapMode = "map"; // "map" o "radar"

    // Bluetooth NUS UUIDs
    const NUS_SERVICE_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
    const NUS_RX_CHAR_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'; // Write -> Node
    const NUS_TX_CHAR_UUID = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'; // Notify -> Client

    let bleDevice = null;
    let bleServer = null;
    let rxCharacteristic = null;
    let txCharacteristic = null;

    // Archivi Dati Live
    let liveMessages = [];
    let liveHeardStations = [];
    let packetLogs = [];
    let rssiHistory = [];

    // Statistiche Traffico
    let rxStatsTotal = 0;
    let txStatsTotal = 0;
    let ackStatsTotal = 0;

    // Coordinate Proprie (Default QTH Roma JN61)
    let ownLat = 41.9028;
    let ownLon = 12.4964;

    // Istanza Mappa Leaflet
    let leafletMap = null;
    let mapMarkers = {};

    // Inizializzazione al caricamento
    window.addEventListener("DOMContentLoaded", () => {
      updateUtcClock();
      setInterval(updateUtcClock, 1000);

      initLeafletMap();

      // Query periodica telemetria ogni 30s
      setInterval(() => {
        if (activeMode === "ble" && rxCharacteristic) {
          sendBleTextMessage("--info", "*");
          setTimeout(() => sendBleTextMessage("--wx", "*"), 400);
        }
      }, 30000);

      // Query iniziale
      setTimeout(() => {
        requestNodeTelemetry();
      }, 1200);
    });

    // Orologio UTC
    function updateUtcClock() {
      const now = new Date();
      const utcString = now.toUTCString().split(" ")[4] + " UTC";
      document.getElementById("hdrUtcTime").textContent = utcString;
    }

    // ==========================================
    // GESTIONE SCHEDE (TABS)
    // ==========================================
    function switchTab(paneId) {
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));

      const pane = document.getElementById(`pane-${paneId}`);
      if (pane) pane.classList.add("active");

      const tabs = ['chat', 'mheard', 'map', 'wx', 'matrix', 'rxlog', 'spectrum', 'setup', 'connection'];
      const idx = tabs.indexOf(paneId);
      if (idx >= 0) {
        const btns = document.querySelectorAll(".tab-btn");
        if (btns[idx]) btns[idx].classList.add("active");
      }

      if (paneId === 'map' && leafletMap) {
        setTimeout(() => leafletMap.invalidateSize(), 200);
      }

      if (paneId === 'spectrum') {
        onSpectrumTabActivated();
      } else {
        onSpectrumTabDeactivated();
      }
    }

    // ==========================================
    // AUDIO FX REALISTICI (WEB AUDIO API)
    // ==========================================
    let audioCtx = null;

    function getAudioContext() {
      if (!audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContext();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      return audioCtx;
    }

    function toggleAudioFx() {
      audioFxEnabled = !audioFxEnabled;
      document.getElementById("audioIcon").textContent = audioFxEnabled ? "🔊" : "🔇";
      document.getElementById("audioLabel").textContent = audioFxEnabled ? "Audio ON" : "Muto";
      showToast(audioFxEnabled ? "Effetti sonori abilitati" : "Audio silenziato");
    }

    // Roger Beep alla trasmissione
    function playRogerBeep() {
      if (!audioFxEnabled) return;
      try {
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(1200, ctx.currentTime);
        osc.frequency.setValueAtTime(800, ctx.currentTime + 0.05);

        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start();
        osc.stop(ctx.currentTime + 0.12);
      } catch (e) {}
    }

    // Chime squelch alla ricezione pacchetto
    function playRxChime() {
      if (!audioFxEnabled) return;
      try {
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "triangle";
        osc.frequency.setValueAtTime(659.25, ctx.currentTime); // E5
        osc.frequency.setValueAtTime(880, ctx.currentTime + 0.06); // A5

        gain.gain.setValueAtTime(0.06, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start();
        osc.stop(ctx.currentTime + 0.15);
      } catch (e) {}
    }

    // ==========================================
    // PARSING ESATTO FRAME NORDIC UART BLE
    // ==========================================
    function handleBleNotification(event) {
      const dataView = event.target.value;
      if (!dataView || dataView.byteLength === 0) return;

      const raw = new Uint8Array(dataView.buffer, dataView.byteOffset, dataView.byteLength);
      const type = raw[0];
      const payload = raw.subarray(1);

      rxStatsTotal++;
      updatePacketStats();

      const hexDump = Array.from(raw.slice(0, 18)).map(b => b.toString(16).padStart(2, '0')).join(' ');

      // 1. FRAME JSON ('D' / 0x44)
      if (type === 0x44) {
        try {
          const dec = new TextDecoder('utf-8');
          let end = payload.indexOf(0x00);
          if (end === -1) end = payload.length;
          const jsonStr = dec.decode(payload.subarray(0, end));
          addPacketLog('JSON', 'Frame 0x44', jsonStr, hexDump);
          parseNodeJson(jsonStr);
        } catch (e) {
          console.warn('JSON error:', e);
        }
        return;
      }

      // 2. FRAME ACK ('A' / 0x41) - Quittanza consegna
      if (type === 0x41) {
        if (payload.length >= 5) {
          const ackMsgId = payload[0] | (payload[1] << 8) | (payload[2] << 16) | (payload[3] << 24);
          const status = payload[4]; // 0=Heard, 1=GW, 2=Peer, 3=Failed, 4=Held
          let call = '';
          if (payload.length >= 6) {
            const callLen = payload[5];
            if (callLen > 0 && payload.length >= 6 + callLen) {
              call = new TextDecoder('ascii').decode(payload.subarray(6, 6 + callLen));
            }
          }
          addPacketLog('ACK', `0x41 ID:0x${ackMsgId.toString(16).toUpperCase()}`, `Status:${status} Call:${call}`, hexDump);
          handleMessageAck(ackMsgId, status, call);
        }
        return;
      }

      // 3. FRAME MHEARD LIST (0x91)
      if (type === 0x91) {
        const dec = new TextDecoder('utf-8');
        let end = payload.indexOf(0x00);
        if (end === -1) end = payload.length;
        const mhStr = dec.decode(payload.subarray(0, end));
        addPacketLog('MHEARD', 'Frame 0x91', mhStr, hexDump);
        parseMheardRaw(mhStr);
        return;
      }

      // 4. FRAME TESTO / APRS / RISPOSTE CLI (0x40 '@' o altro)
      parseIncomingBleFrame(payload, hexDump);
    }

    function parseIncomingBleFrame(payload, hexDump) {
      if (!payload || payload.length === 0) return;

      const dec = new TextDecoder('utf-8');
      const pType = payload[0];

      // APRS Standard Frame: [0]=type (':', '!', '@'), [1..4]=msg_id, [5]=hops, [6..]=SRC>DST:MSG
      if ((pType === 0x3A || pType === 0x21 || pType === 0x40) && payload.length >= 7) {
        const msgId = payload[1] | (payload[2] << 8) | (payload[3] << 16) | (payload[4] << 24);
        const hops = payload[5] & 0x0F;

        // TAGLIO METADATI BINARI DI CODA: trova il primo 0x00
        let nullIdx = payload.indexOf(0x00, 6);
        if (nullIdx === -1) nullIdx = payload.length;

        const asciiStr = dec.decode(payload.subarray(6, nullIdx)).trim();
        addPacketLog('APRS', `Tipo ${String.fromCharCode(pType)} ID:0x${msgId.toString(16).toUpperCase()}`, asciiStr, hexDump);

        if (pType === 0x3A) {
          parseAprsTextMessage(asciiStr, hops, msgId);
          return;
        } else if (pType === 0x21) {
          parseAprsPosBeacon(asciiStr, hops);
          return;
        }
      }

      // Fallback: Risposta CLI o testo grezzo
      let endIdx = payload.indexOf(0x00);
      if (endIdx === -1) endIdx = payload.length;
      let rawText = dec.decode(payload.subarray(0, endIdx)).trim();

      if (rawText.startsWith('response:')) {
        const clean = rawText.replace(/^response:/, '').trim();
        logBle(`[NODO RISPOSTA] ${clean}`);
        addPacketLog('CLI', 'Risposta Comando', clean, hexDump);
        showToast(`Nodo: ${clean}`);
        return;
      }

      // Filtra caratteri di controllo non stampabili
      rawText = rawText.replace(/[\\x00-\\x1F\\x7F-\\x9F]/g, '').trim();
      if (rawText.length > 0) {
        addPacketLog('TEXT', 'Testo Diretto', rawText, hexDump);
        parseAprsTextMessage(rawText, 0, 0);
      }
    }

    function parseAprsTextMessage(str, hops, msgId) {
      let sender = 'MESH';
      let via = [];
      let destination = '*';
      let content = str;

      if (str.includes('>')) {
        const [pathPart, rest] = str.split('>', 2);
        const calls = pathPart.split(',').map(c => c.trim()).filter(Boolean);
        sender = calls[0] || 'MESH';
        if (calls.length > 1) via = calls.slice(1);

        if (rest) {
          const sepIdx = rest.search(/[:;!#]/);
          if (sepIdx !== -1) {
            destination = rest.slice(0, sepIdx).trim();
            content = rest.slice(sepIdx + 1).trim();
          } else {
            destination = rest.trim();
            content = '';
          }
        }
      } else if (str.startsWith('@') || str.startsWith(':')) {
        const parts = str.substring(1).split(':');
        if (parts.length >= 2) {
          sender = parts[0].trim();
          content = parts.slice(1).join(':').trim();
        }
      }

      // Pulizia definitiva caratteri spuri
      content = content.replace(/[\\x00-\\x1F\\x7F-\\x9F]/g, '').trim();
      if (!content) return;

      const now = new Date();
      const timeStr = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0');

      playRxChime();

      addMessage({
        id: msgId || Date.now(),
        src: sender,
        dst: destination,
        via: via,
        hops: hops || 0,
        text: content,
        time: timeStr,
        self: (sender === ownCallsign),
        delivered: false
      });

      addOrUpdateMheard({
        call: sender,
        dist: via.length > 0 ? `Via ${via.join(',')}` : 'Diretto',
        distKm: null,
        snr: '--',
        rssi: '--',
        hops: hops || 0,
        last: timeStr,
        type: 'LoRa Station'
      });

      showToast(`💬 Messaggio da ${sender}`);
    }

    function parseAprsPosBeacon(str, hops) {
      // Esempio: "IU0XYZ>APLT00:!4153.20N/01228.40E#..."
      if (!str.includes('>') || !str.includes('!')) return;
      const parts = str.split('>');
      const sender = parts[0].trim();
      const posPart = str.split('!')[1] || '';

      // Regex coordinate APRS standard DDMM.MMN/DDDMM.MME
      const match = posPart.match(/(\\d{2})(\\d{2}\\.\\d{2})([NS])[\\/\\\\](\\d{3})(\\d{2}\\.\\d{2})([EW])/);
      if (match) {
        const lat = (parseInt(match[1]) + parseFloat(match[2]) / 60) * (match[3] === 'S' ? -1 : 1);
        const lon = (parseInt(match[4]) + parseFloat(match[5]) / 60) * (match[6] === 'W' ? -1 : 1);
        const distKm = calculateDistance(ownLat, ownLon, lat, lon);

        addOrUpdateMheard({
          call: sender,
          lat: lat,
          lon: lon,
          dist: `${distKm.toFixed(1)} km`,
          distKm: distKm,
          snr: '--',
          rssi: '--',
          hops: hops || 0,
          last: new Date().toLocaleTimeString(),
          type: 'APRS Beacon'
        });

        plotStationOnMap(sender, lat, lon, `${distKm.toFixed(1)} km`);
      }
    }

    function handleMessageAck(msgId, status, callsign) {
      ackStatsTotal++;
      updatePacketStats();

      const msg = liveMessages.find(m => m.id === msgId || m.self);
      if (msg) {
        msg.delivered = true;
        msg.ackStatus = status;
        msg.ackCall = callsign;
        renderMessages();
      }
      const labels = {
        0: "Ascoltato dal nodo (Heard)",
        1: `Confermato da Gateway ${callsign || 'MeshCom'}`,
        2: `Consegnato al destinatario ${callsign || ''}`,
        3: "Nack (Tentativi esauriti)",
        4: `In attesa su Store Node ${callsign || ''}`
      };
      const desc = labels[status] || `ACK status ${status}`;
      showToast(`✓✓ ${desc}`);
      logBle(`[ACK CONFERMATO] ID:0x${msgId.toString(16).toUpperCase()} -> ${desc}`);
    }

    // ==========================================
    // PARSING JSON MESHCOM COMPLETO
    // ==========================================
    function parseNodeJson(jsonStr) {
      try {
        const j = JSON.parse(jsonStr);

        // Frame I (Info generale hardware / batteria / callsign proprio nodo)
        if (j.TYP === "I") {
          if (j.CALL) {
            ownCallsign = j.CALL;
            document.getElementById("hdrCallsign").textContent = j.CALL;
            document.getElementById("cfgCallsign").value = j.CALL;
            document.getElementById("radarCenterLabel").textContent = `TU (${j.CALL})`;
          }
          if (j.FREQ || j.MQRG) {
            const f = j.MQRG || j.FREQ;
            document.getElementById("cardFreq").innerHTML = `${parseFloat(f).toFixed(3)} <span class="stat-unit">MHz</span>`;
            document.getElementById("cfgFreq").value = parseFloat(f).toFixed(3);
          }
          if (j.TXPWR !== undefined || j.TXP !== undefined) {
            const p = j.TXP !== undefined ? j.TXP : j.TXPWR;
            document.getElementById("cardTxPower").textContent = `TX ${p} dBm`;
            document.getElementById("cfgTxPower").value = p;
          }
          if (j.BATV !== undefined || j.BATP !== undefined) {
            const v = j.BATV ? parseFloat(j.BATV).toFixed(2) : '--';
            const p = j.BATP !== undefined ? j.BATP : '--';
            document.getElementById("hdrBattery").textContent = `🔋 ${v}V (${p}%)`;
            document.getElementById("wxBatV").innerHTML = `${v} <span class="stat-unit">V</span>`;
            document.getElementById("wxBatP").textContent = `Carica stimata: ${p}%`;
          }
          if (j.FWVER || j.HWID) {
            const hw = j.HWID ? `${j.HWID}` : 'ESP32';
            const fw = j.FWVER ? ` ${j.FWVER}` : '';
            document.getElementById("hdrHwBadge").textContent = `${hw}${fw}`;
          }
        }

        // Frame SN (Node Settings / LoRa RF)
        if (j.TYP === "SN" || j.MQRG !== undefined) {
          if (j.MQRG) {
            document.getElementById("cardFreq").innerHTML = `${parseFloat(j.MQRG).toFixed(3)} <span class="stat-unit">MHz</span>`;
            document.getElementById("cfgFreq").value = parseFloat(j.MQRG).toFixed(3);
          }
          if (j.TXP !== undefined) {
            document.getElementById("cardTxPower").textContent = `TX ${j.TXP} dBm`;
            document.getElementById("cfgTxPower").value = j.TXP;
          }
          if (j.MSF) {
            document.getElementById("cardModulation").textContent = `SF${j.MSF} CR${j.MCR||'4/5'} BW${j.MBW||125}`;
            document.getElementById("cfgSf").value = j.MSF;
          }
          if (j.MSH !== undefined) document.getElementById("cfgMesh").checked = (j.MSH === 1 || j.MSH === true);
          if (j.GW !== undefined) document.getElementById("cfgGateway").checked = (j.GW === 1 || j.GW === true);
          if (j.GPS !== undefined) document.getElementById("cfgGps").checked = (j.GPS === 1 || j.GPS === true);
        }

        // Frame W (Meteo sensori BME280/INA)
        if (j.TYP === "W") {
          if (j.TEMP !== undefined && j.TEMP !== null) {
            const t = parseFloat(j.TEMP).toFixed(1);
            document.getElementById("cardTemp").innerHTML = `${t} <span class="stat-unit">°C</span>`;
            document.getElementById("wxTemp").innerHTML = `${t} <span class="stat-unit">°C</span>`;
          }
          const hum = (j.HUM != null) ? `${j.HUM}%` : 'N/D';
          const pressVal = (j.PRES != null && j.PRES !== 0) ? j.PRES : ((j.PRESS != null && j.PRESS !== 0) ? j.PRESS : null);
          const pressStr = pressVal ? `${parseFloat(pressVal).toFixed(1)} hPa` : 'N/D';
          document.getElementById("cardWeatherExtra").innerHTML = `<span>Umidità: ${hum}</span> • <span>${pressStr}</span>`;
          document.getElementById("wxHum").innerHTML = `${hum}`;
          document.getElementById("wxPress").innerHTML = `${pressStr}`;
          if (j.QNH != null) document.getElementById("wxQnh").textContent = `QNH: ${parseFloat(j.QNH).toFixed(1)} hPa`;
          if (j.ALT != null) document.getElementById("wxAlt").innerHTML = `${j.ALT} <span class="stat-unit">m</span>`;
          if (j.GAS != null) document.getElementById("wxGas").innerHTML = `${(j.GAS / 1000).toFixed(1)} <span class="stat-unit">kΩ</span>`;
          if (j.CO2 != null) document.getElementById("wxCo2").textContent = `CO2: ${j.CO2} ppm`;
        }

        // Frame G (GPS)
        if (j.TYP === "G" || j.LAT !== undefined) {
          const lat = parseFloat(j.LAT);
          const lon = parseFloat(j.LON);
          if (!isNaN(lat) && !isNaN(lon) && (lat !== 0 || lon !== 0)) {
            ownLat = lat;
            ownLon = lon;
            const loc = calculateMaidenhead(lat, lon);
            document.getElementById("cardLocator").textContent = loc;
            const satStr = j.SAT !== undefined ? ` (${j.SAT} sat)` : '';
            document.getElementById("cardGpsCoords").innerHTML = `<span>${lat.toFixed(4)}°, ${lon.toFixed(4)}°</span> • <span style="color:var(--accent-green)">Fix GPS${satStr}</span>`;

            updateOwnMapPosition(lat, lon);
          }
        }

        // Frame MH (Stazione ascoltata live)
        if (j.TYP === "MH" && j.CALL) {
          const distKm = (j.DIST !== undefined && j.DIST >= 0) ? parseFloat(j.DIST) : null;
          addOrUpdateMheard({
            call: j.CALL,
            dist: (distKm !== null) ? `${distKm.toFixed(1)} km` : 'Mesh',
            distKm: distKm,
            snr: j.SNR !== undefined ? `${j.SNR > 0 ? '+' : ''}${j.SNR} dB` : '--',
            rssi: j.RSSI !== undefined ? `${j.RSSI} dBm` : '--',
            hops: j.HW || 0,
            last: j.TIME || 'Adesso',
            type: j.ROLE || 'Mesh Node'
          });

          if (j.RSSI !== undefined) {
            recordRssi(j.CALL, parseInt(j.RSSI));
          }
        }

        // Frame SA (APRS)
        if (j.TYP === "SA") {
          if (j.ATXT) document.getElementById("cfgAprsText").value = j.ATXT;
          if (j.SYMID) document.getElementById("cfgSymbol").value = j.SYMID;
        }

      } catch (err) {
        console.warn("JSON parse err:", err);
      }
    }

    // ==========================================
    // CHAT ENGINE
    // ==========================================
    function selectChannel(channel, element) {
      currentChannel = channel;
      document.querySelectorAll(".channel-item").forEach(item => item.classList.remove("active"));
      if (element) element.classList.add("active");

      document.getElementById("currentChannelTitle").textContent = 
        channel === '*' ? 'Canale Generale (*)' : (channel === '222' ? 'Gruppo Italia (222)' : `Canale ${channel}`);

      const sel = document.getElementById("sendTargetSelect");
      if (channel === '*' || channel === '222' || channel === '999') {
        sel.value = channel;
      } else {
        ensureSelectOption(sel, channel, `DM: ${channel}`);
        sel.value = channel;
      }

      renderMessages();
    }

    function onTargetSelectChange(val) {
      if (val === "CUSTOM") {
        const customCall = prompt("Inserisci il nominativo destinatario (es. IU0XYZ):");
        if (customCall) {
          const clean = customCall.toUpperCase().trim();
          const sel = document.getElementById("sendTargetSelect");
          ensureSelectOption(sel, clean, `DM: ${clean}`);
          sel.value = clean;
          openDmWith(clean);
        } else {
          document.getElementById("sendTargetSelect").value = "*";
        }
      }
    }

    function ensureSelectOption(sel, value, label) {
      let opt = Array.from(sel.options).find(o => o.value === value);
      if (!opt) {
        opt = document.createElement("option");
        opt.value = value;
        opt.textContent = label;
        sel.appendChild(opt);
      }
    }

    function openDmWith(callsign) {
      const dmItem = document.getElementById("dynamicDmChannel");
      dmItem.style.display = "flex";
      dmItem.setAttribute("data-dm", callsign);
      document.getElementById("dynamicDmTitle").textContent = callsign;
      selectChannel(callsign, dmItem);
      switchTab('chat');
      showToast(`Aperta chat diretta con ${callsign}`);
    }

    function addMessage(msg) {
      liveMessages.push(msg);
      document.getElementById("cardMsgCount").innerHTML = `${liveMessages.length} <span class="stat-unit">msg live</span>`;
      document.getElementById("badgeUnread").textContent = liveMessages.length;
      renderMessages();
    }

    function renderMessages() {
      const container = document.getElementById("messagesList");
      container.innerHTML = "";

      const filtered = liveMessages.filter(m => {
        if (currentChannel === "*") return true;
        return m.dst === currentChannel || m.src === currentChannel || (currentChannel === '222' && m.dst.startsWith('222'));
      });

      if (filtered.length === 0) {
        container.innerHTML = `<div style="text-align:center; color:var(--text-dim); margin:auto">Nessun messaggio in questo canale. Invia un messaggio per trasmettere via LoRa!</div>`;
        return;
      }

      filtered.forEach(msg => {
        const bubble = document.createElement("div");
        bubble.className = `msg-bubble ${msg.self ? 'msg-outbound' : 'msg-inbound'}`;

        const viaStr = (msg.via && msg.via.length > 0) ? ` via ${msg.via.join(',')}` : '';
        const statusBadge = msg.self ? 
          (msg.delivered ? '<span class="badge-tag" style="color:var(--accent-green); border-color:var(--accent-green)">✓✓ Consegnato</span>' : '<span class="badge-tag">✓ Trasmesso</span>') :
          `<span class="badge-tag">RX LoRa${msg.hops ? ' • '+msg.hops+'h' : ''}</span>`;

        bubble.innerHTML = `
          <div class="msg-meta">
            <span class="msg-sender">${escapeHtml(msg.src)}</span>
            <span>➜ ${escapeHtml(msg.dst)}${escapeHtml(viaStr)}</span>
            <div style="margin-left:auto">${statusBadge}</div>
          </div>
          <div style="font-size:0.9rem">${escapeHtml(msg.text)}</div>
          <div class="msg-time">${msg.time}</div>
        `;
        container.appendChild(bubble);
      });

      container.scrollTop = container.scrollHeight;
    }

    function quickSend(txt) {
      const inp = document.getElementById("messageInput");
      inp.value = txt;
      sendMeshMessage();
    }

    function sendMeshMessage() {
      const input = document.getElementById("messageInput");
      const target = document.getElementById("sendTargetSelect").value;
      const text = input.value.trim();

      if (!text) return;

      const now = new Date();
      const timeStr = String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0');

      playRogerBeep();

      txStatsTotal++;
      updatePacketStats();

      sendBleTextMessage(text, target)
        .then(() => {
          addMessage({
            id: Date.now(),
            src: ownCallsign,
            dst: target,
            text: text,
            time: timeStr,
            self: true,
            delivered: false
          });
          input.value = "";
          showToast("Messaggio inviato al ricetrasmettitore LoRa!");
        })
        .catch(err => {
          showToast("Errore invio BLE: " + err.message);
        });
    }

    function clearChat() {
      if (confirm("Vuoi cancellare i messaggi visualizzati?")) {
        liveMessages = [];
        renderMessages();
      }
    }

    function exportChatHistory() {
      const blob = new Blob([JSON.stringify(liveMessages, null, 2)], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `meshcom_chat_${new Date().toISOString().slice(0,10)}.json`;
      a.click();
    }

    // ==========================================
    // MHEARD & MATRICE VICINI
    // ==========================================
    function addOrUpdateMheard(st) {
      const idx = liveHeardStations.findIndex(s => s.call === st.call);
      if (idx >= 0) {
        liveHeardStations[idx] = { ...liveHeardStations[idx], ...st };
      } else {
        liveHeardStations.push(st);
      }
      document.getElementById("badgeMheard").textContent = liveHeardStations.length;
      renderMheard();
      renderMatrix();
      renderRadar();
    }

    function renderMheard() {
      const tbody = document.getElementById("mheardTableBody");
      const filter = (document.getElementById("mheardFilter")?.value || "").toUpperCase().trim();
      tbody.innerHTML = "";

      const filtered = liveHeardStations.filter(s => !filter || s.call.includes(filter));

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-dim); padding:1.5rem">Nessuna stazione corrisponde ai criteri.</td></tr>`;
        return;
      }

      filtered.forEach(st => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <div style="font-weight:700; font-family:var(--font-mono); color:var(--accent-cyan); cursor:pointer" onclick="openDmWith('${st.call}')">
              ${escapeHtml(st.call)}
            </div>
            <div style="font-size:0.7rem; color:var(--text-dim)">${escapeHtml(st.type || 'Nodo')}</div>
          </td>
          <td>${escapeHtml(st.dist || 'Mesh')}</td>
          <td>
            <span style="color:var(--accent-green); font-family:var(--font-mono)">${escapeHtml(st.snr || '--')}</span>
            <span style="color:var(--text-dim); font-size:0.75rem">(${escapeHtml(st.rssi || '--')})</span>
          </td>
          <td><span class="badge-tag">${st.hops || 0} hops</span></td>
          <td style="color:var(--text-muted); font-size:0.75rem">${st.last || 'Adesso'}</td>
          <td>
            <button class="btn-action" style="padding:0.2rem 0.5rem; font-size:0.75rem" onclick="openDmWith('${st.call}')">
              ✉️ DM
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderMatrix() {
      const container = document.getElementById("neighboursMatrixGrid");
      container.innerHTML = "";

      if (liveHeardStations.length === 0) {
        container.innerHTML = `<div class="matrix-card" style="text-align:center; color:var(--text-dim); padding:1rem">In ascolto della matrice topologica...</div>`;
        return;
      }

      liveHeardStations.forEach(st => {
        const card = document.createElement("div");
        card.className = "matrix-card";
        const snrNum = parseFloat(st.snr) || 0;
        const snrPct = Math.min(100, Math.max(10, ((snrNum + 20) / 35) * 100));

        card.innerHTML = `
          <div class="matrix-header">
            <span class="matrix-call" onclick="openDmWith('${st.call}')">${escapeHtml(st.call)}</span>
            <span class="badge-tag">${st.dist || 'RF Link'}</span>
          </div>
          <div class="signal-bar-wrap">
            <div class="signal-bar-fill" style="width:${snrPct}%; background:${snrNum > 0 ? 'var(--accent-green)' : (snrNum > -10 ? 'var(--accent-amber)' : 'var(--accent-red)')}"></div>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted)">
            <span>SNR: <strong style="color:var(--text-main)">${st.snr}</strong></span>
            <span>RSSI: <strong style="color:var(--text-main)">${st.rssi}</strong></span>
            <span>Salti: <strong style="color:var(--text-main)">${st.hops || 0}</strong></span>
          </div>
        `;
        container.appendChild(card);
      });
    }

    // ==========================================
    // MAPPA LEAFLET & RADAR
    // ==========================================
    let baseLayers = {};
    function initLeafletMap() {
      try {
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
          attribution: '&copy; Esri & Maxar',
          maxZoom: 19
        });

        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors',
          maxZoom: 19
        });

        const topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenTopoMap contributors',
          maxZoom: 17
        });

        leafletMap = L.map('aprsMap', {
          center: [ownLat, ownLon],
          zoom: 12,
          layers: [satelliteLayer]
        });

        baseLayers = {
          "🛰️ Satellite HD (Esri)": satelliteLayer,
          "🗺️ Stradale (OpenStreetMap)": osmLayer,
          "⛰️ Topografica (OpenTopoMap)": topoLayer
        };

        L.control.layers(baseLayers).addTo(leafletMap);

        updateOwnMapPosition(ownLat, ownLon);
      } catch (e) {
        console.warn("Leaflet map init warning:", e);
      }
    }

    function updateOwnMapPosition(lat, lon) {
      if (!leafletMap) return;
      if (mapMarkers["OWN"]) leafletMap.removeLayer(mapMarkers["OWN"]);

      const icon = L.divIcon({
        className: 'custom-map-icon',
        html: `<div style="background:#10b981; width:14px; height:14px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 12px #10b981"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });

      mapMarkers["OWN"] = L.marker([lat, lon], { icon: icon }).addTo(leafletMap)
        .bindPopup(`<strong>TU (${ownCallsign})</strong><br>Coordinate: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
      
      leafletMap.setView([lat, lon], 12);
    }

    function plotStationOnMap(call, lat, lon, dist) {
      if (!leafletMap) return;
      if (mapMarkers[call]) leafletMap.removeLayer(mapMarkers[call]);

      const icon = L.divIcon({
        className: 'custom-map-icon',
        html: `<div style="background:#06b6d4; width:12px; height:12px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 10px #06b6d4"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
      });

      mapMarkers[call] = L.marker([lat, lon], { icon: icon }).addTo(leafletMap)
        .bindPopup(`<strong>${call}</strong><br>Distanza: ${dist}<br><button onclick="openDmWith('${call}')" style="margin-top:4px; padding:2px 6px; font-size:11px">Invia Messaggio</button>`);

      // Disegna linea verso il nodo base
      L.polyline([[ownLat, ownLon], [lat, lon]], { color: '#06b6d4', weight: 1.5, opacity: 0.5, dashArray: '4, 4' }).addTo(leafletMap);
    }

    function toggleMapMode() {
      const mapEl = document.getElementById("aprsMap");
      const radarEl = document.getElementById("radarContainer");
      const btn = document.getElementById("btnToggleMapMode");

      if (mapMode === "map") {
        mapMode = "radar";
        mapEl.style.display = "none";
        radarEl.style.display = "flex";
        btn.textContent = "🗺️ Passa a Mappa Satellitare";
        renderRadar();
      } else {
        mapMode = "map";
        radarEl.style.display = "none";
        mapEl.style.display = "block";
        btn.textContent = "🎯 Passa a Radar Tattico";
        if (leafletMap) setTimeout(() => leafletMap.invalidateSize(), 100);
      }
    }

    function renderRadar() {
      const container = document.getElementById("radarContainer");
      if (!container || mapMode !== "radar") return;

      container.querySelectorAll(".radar-station-dot").forEach(d => d.remove());

      liveHeardStations.forEach((st, idx) => {
        const dot = document.createElement("div");
        dot.className = "radar-node-dot radar-station-dot";
        dot.style.color = "#06b6d4";
        dot.style.background = "#06b6d4";
        dot.onclick = () => openDmWith(st.call);

        let radiusPct = 30;
        if (st.distKm !== null && st.distKm > 0) {
          radiusPct = Math.min(44, Math.max(14, (st.distKm / 35) * 44));
        } else {
          radiusPct = 18 + ((idx * 8) % 24);
        }

        let hash = 0;
        for (let i = 0; i < st.call.length; i++) hash = (hash * 31 + st.call.charCodeAt(i)) & 0xFFFF;
        const angle = (hash % 360) * (Math.PI / 180);

        dot.style.top = `${50 + radiusPct * Math.sin(angle)}%`;
        dot.style.left = `${50 + radiusPct * Math.cos(angle)}%`;

        dot.innerHTML = `<div class="radar-node-label" style="color:#06b6d4">${escapeHtml(st.call)}</div>`;
        container.appendChild(dot);
      });
    }

    // ==========================================
    // LOG PACCHETTI RAW & RX INSPECTOR
    // ==========================================
    function addPacketLog(type, header, payload, hex) {
      const now = new Date();
      const time = now.toISOString().slice(11, 19);
      packetLogs.unshift({ time, type, header, payload, hex });
      if (packetLogs.length > 100) packetLogs.pop();
      renderPacketLog();
    }

    function renderPacketLog() {
      const tbody = document.getElementById("packetLogTableBody");
      if (!tbody) return;
      tbody.innerHTML = "";

      packetLogs.slice(0, 30).forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted)">${p.time}</td>
          <td><span class="badge-tag">${p.type}</span></td>
          <td style="font-family:var(--font-mono); font-size:0.75rem">${escapeHtml(p.header)}</td>
          <td style="font-size:0.8rem">${escapeHtml(p.payload)}</td>
          <td style="font-family:var(--font-mono); font-size:0.7rem; color:var(--text-dim)">${p.hex}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function clearPacketLog() {
      packetLogs = [];
      renderPacketLog();
    }

    function downloadPacketLog() {
      const lines = packetLogs.map(p => `[${p.time}] [${p.type}] ${p.header} | ${p.payload} | HEX: ${p.hex}`);
      const blob = new Blob([lines.join("\\n")], { type: "text/plain" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `meshcom_rxlog_${Date.now()}.txt`;
      a.click();
    }

    function updatePacketStats() {
      document.getElementById("cardStatsRx").textContent = `RX: ${rxStatsTotal}`;
      document.getElementById("cardStatsTx").textContent = `TX: ${txStatsTotal}`;
      document.getElementById("cardAcks").textContent = `ACK: ${ackStatsTotal}`;
    }

    // ==========================================
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
      if (typeof playRxChime === 'function') playRxChime();
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
    }

    // ==========================================
    // WEB BLUETOOTH ENGINE
    // ==========================================
    async function connectBle() {
      if (!navigator.bluetooth) {
        showToast("Web Bluetooth non supportato su questo browser. Usa Chrome o Edge.");
        return;
      }

      try {
        logBle("[BLE] Apertura selettore dispositivi...");
        showToast("Seleziona MC-a498-IU0TGU-10...");

        try {
          bleDevice = await navigator.bluetooth.requestDevice({
            filters: [
              { namePrefix: 'MC-' },
              { namePrefix: 'MeshCom' },
              { namePrefix: 'IU0TGU' }
            ],
            optionalServices: [NUS_SERVICE_UUID]
          });
        } catch (filterErr) {
          logBle("[BLE] Mostro tutte le periferiche Bluetooth disponibili...");
          bleDevice = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: [NUS_SERVICE_UUID]
          });
        }

        const devName = bleDevice.name || "MC-a498-IU0TGU-10";
        logBle(`[BLE] Selezionato: ${devName}`);
        document.getElementById("bleDeviceLabel").textContent = devName;
        document.getElementById("blePillName").textContent = `📶 ${devName}`;

        bleDevice.removeEventListener('gattserverdisconnected', onBleDisconnected);
        bleDevice.addEventListener('gattserverdisconnected', onBleDisconnected);

        // Retry loop per evitare l'errore 'Connection attempt failed' tipico di BlueZ se il socket e appena caduto
        let connected = false;
        let lastErr = null;
        for (let attempt = 1; attempt <= 3; attempt++) {
          try {
            logBle(`[BLE] Connessione GATT al nodo (tentativo ${attempt}/3)...`);
            bleServer = await bleDevice.gatt.connect();
            connected = true;
            logBle("[BLE] Server GATT connesso con successo!");
            break;
          } catch (connErr) {
            lastErr = connErr;
            logBle(`[BLE] Tentativo ${attempt} fallito (${connErr.message || connErr}). Attesa 1.5s per rilascio socket ESP32...`);
            await new Promise(r => setTimeout(r, 1500));
          }
        }

        if (!connected) {
          throw new Error(lastErr ? lastErr.message : "Connessione GATT fallita dopo 3 tentativi");
        }

        // Breve pausa di assestamento per negoziazione MTU di NimBLE su ESP32
        await new Promise(r => setTimeout(r, 350));

        logBle("[BLE] Acquisizione servizio Nordic UART...");
        const service = await bleServer.getPrimaryService(NUS_SERVICE_UUID);
        rxCharacteristic = await service.getCharacteristic(NUS_RX_CHAR_UUID);
        txCharacteristic = await service.getCharacteristic(NUS_TX_CHAR_UUID);

        await txCharacteristic.startNotifications();
        txCharacteristic.removeEventListener('characteristicvaluechanged', handleBleNotification);
        txCharacteristic.addEventListener('characteristicvaluechanged', handleBleNotification);
        logBle("[BLE] Notifiche TX attivate. Canale bidirezionale pronto!");

        await sendBleHandshake();

        document.getElementById("statusDot").className = "dot ble";
        document.getElementById("connStatusText").textContent = "BLE CONNESSO";
        document.getElementById("btnScanBle").style.display = "none";
        document.getElementById("btnDisconnectBle").style.display = "inline-flex";

        const hdrBtn = document.getElementById("btnHdrConnect");
        if (hdrBtn) {
          hdrBtn.innerHTML = "<span>🔴 Disconnetti</span>";
          hdrBtn.onclick = disconnectBle;
          hdrBtn.style.borderColor = "var(--border-subtle)";
          hdrBtn.style.color = "var(--text-muted)";
          hdrBtn.style.background = "rgba(255, 255, 255, 0.05)";
        }

        showToast(`Connesso a ${devName}!`);
        requestNodeTelemetry();

      } catch (err) {
        console.error("BLE Connect Error:", err);
        logBle(`[ERRORE BLE] ${err.message || err}`);
        showToast("Connessione non riuscita. Se il nodo e lontano, avvicinalo al PC.");
      }
    }

    async function sendBleHandshake() {
      if (!rxCharacteristic) return;
      try {
        logBle("[TX] Invio Handshake 0x10...");
        await rxCharacteristic.writeValue(new Uint8Array([0x04, 0x10, 0x20, 0x30]));

        const nowSec = Math.floor(Date.now() / 1000);
        const timeFrame = new Uint8Array(6);
        timeFrame[0] = 0x06;
        timeFrame[1] = 0x20;
        timeFrame[2] = nowSec & 0xFF;
        timeFrame[3] = (nowSec >> 8) & 0xFF;
        timeFrame[4] = (nowSec >> 16) & 0xFF;
        timeFrame[5] = (nowSec >> 24) & 0xFF;
        await rxCharacteristic.writeValue(timeFrame);
        logBle(`[OK] Handshake e Clock Sync (${nowSec}s) completati.`);
      } catch (e) {
        logBle(`[WARN] Errore handshake: ${e.message}`);
      }
    }

    function onBleDisconnected() {
      logBle("[BLE] Dispositivo disconnesso.");
      document.getElementById("statusDot").className = "dot offline";
      document.getElementById("connStatusText").textContent = "DISCONNESSO";
      document.getElementById("btnScanBle").style.display = "inline-flex";
      document.getElementById("btnDisconnectBle").style.display = "none";

      const hdrBtn = document.getElementById("btnHdrConnect");
      if (hdrBtn) {
        hdrBtn.innerHTML = "<span>📶 Connetti BLE</span>";
        hdrBtn.onclick = connectBle;
        hdrBtn.style.borderColor = "var(--accent-cyan)";
        hdrBtn.style.color = "var(--accent-cyan)";
        hdrBtn.style.background = "rgba(6,182,212,0.12)";
      }

      showToast("Nodo disconnesso. Clicca Riconnetti BLE per ricollegarlo.");
    }

    function disconnectBle() {
      if (bleDevice && bleDevice.gatt && bleDevice.gatt.connected) {
        bleDevice.gatt.disconnect();
      } else {
        onBleDisconnected();
      }
    }

    async function sendBleTextMessage(text, target) {
      if (!rxCharacteristic) {
        showToast("Nessun nodo BLE connesso");
        throw new Error("BLE non connesso");
      }

      let payload = text;
      if (!text.startsWith("--")) {
        payload = target === "*" ? `* ${text}` : `:${target}:${text}`;
      }

      const enc = new TextEncoder();
      const textBytes = enc.encode(payload);
      const frameLen = 2 + textBytes.length;
      const frame = new Uint8Array(frameLen);
      frame[0] = frameLen;
      frame[1] = 0xA0; // Frame 0xA0 testo/comando
      frame.set(textBytes, 2);

      logBle(`[TX BLE] "${payload}"`);
      await rxCharacteristic.writeValue(frame);
    }

    function logBle(msg) {
      const term = document.getElementById("bleLogTerminal");
      if (!term) return;
      const line = document.createElement("div");
      const time = new Date().toTimeString().split(" ")[0];
      line.textContent = `[${time}] ${msg}`;
      term.appendChild(line);
      term.scrollTop = term.scrollHeight;
    }

    function clearBleLog() {
      document.getElementById("bleLogTerminal").innerHTML = "";
    }

    // CLI Command Helpers
    function sendCliCommand() {
      const inp = document.getElementById("cliCommandInput");
      const cmd = inp.value.trim();
      if (!cmd) return;
      execDirectCmd(cmd);
      inp.value = "";
    }

    function execDirectCmd(cmd) {
      logBle(`[CLI TX] Invio: ${cmd}`);
      sendBleTextMessage(cmd, "*")
        .then(() => showToast(`Comando ${cmd} inviato!`))
        .catch(err => logBle(`[ERRORE] ${err.message}`));
    }

    function requestNodeTelemetry() {
      showToast("Interrogazione stato nodo...");
      execDirectCmd("--info");
      setTimeout(() => execDirectCmd("--wx"), 400);
      setTimeout(() => execDirectCmd("--pos"), 800);
    }

    function callNodeFn(fn) {
      execDirectCmd(`--${fn}`);
    }

    function saveNodeIdentity() {
      const call = document.getElementById("cfgCallsign").value.trim();
      const txt = document.getElementById("cfgAprsText").value.trim();
      const sym = document.getElementById("cfgSymbol").value;
      showToast("Salvataggio identità...");
      if (call) execDirectCmd(`--setcall ${call}`);
      if (txt) setTimeout(() => execDirectCmd(`--atxt ${txt}`), 300);
      if (sym) setTimeout(() => execDirectCmd(`--setsym ${sym}`), 600);
      setTimeout(() => execDirectCmd(`--save`), 900);
    }

    function saveRadioParams() {
      const freq = document.getElementById("cfgFreq").value.trim();
      const pwr = document.getElementById("cfgTxPower").value.trim();
      const sf = document.getElementById("cfgSf").value;
      showToast("Salvataggio parametri radio...");
      if (freq) execDirectCmd(`--setfreq ${freq}`);
      if (pwr) setTimeout(() => execDirectCmd(`--setpower ${pwr}`), 300);
      if (sf) setTimeout(() => execDirectCmd(`--setsf ${sf}`), 600);
      setTimeout(() => execDirectCmd(`--save`), 900);
    }

    function toggleMeshParam(param, enabled) {
      const val = enabled ? "on" : "off";
      execDirectCmd(`--${param} ${val}`);
    }

    function confirmReboot() {
      if (confirm("Vuoi davvero riavviare il nodo ESP32 IU0TGU-10?")) {
        execDirectCmd("--reboot");
      }
    }

    // ==========================================
    // UTILITY MATEMATICHE & MAIDENHEAD
    // ==========================================
    function calculateMaidenhead(lat, lon) {
      lon = lon + 180;
      lat = lat + 90;
      const f1 = String.fromCharCode(65 + Math.floor(lon / 20));
      const f2 = String.fromCharCode(65 + Math.floor(lat / 10));
      const d1 = Math.floor((lon % 20) / 2);
      const d2 = Math.floor(lat % 10);
      const l1 = String.fromCharCode(97 + Math.floor((lon - (Math.floor(lon / 2) * 2)) * 12));
      const l2 = String.fromCharCode(97 + Math.floor((lat - Math.floor(lat)) * 24));
      return `${f1}${f2}${d1}${d2}${l1}${l2}`.toUpperCase();
    }

    function calculateDistance(lat1, lon1, lat2, lon2) {
      const R = 6371;
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLon = (lon2 - lon1) * Math.PI / 180;
      const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
      return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    }

    function showToast(msg) {
      const t = document.getElementById("toast");
      document.getElementById("toastMsg").textContent = msg;
      t.classList.add("show");
      setTimeout(() => t.classList.remove("show"), 3000);
    }

    function escapeHtml(str) {
      return String(str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
  </script>
</body>
</html>
"""

output_path = "/home/user/.gemini/antigravity/scratch/meshcom-dashboard/index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

print(f"Generated {output_path} successfully ({len(HTML_CONTENT)} bytes).")
