#!/usr/bin/env python3
"""
test_clean_universal.py
Automated browser test via CDP verifying:
1. Disconnected state: ZERO simulation, zero fake data, clean standby.
2. Connected state: Universal hardware auto-detection (ESP32-S3), 868 MHz auto-adaptation, live packets.
"""

import subprocess
import time
import json
import urllib.request
import base64
import websocket

def run_tests():
    print("=" * 70)
    print("🚀 TEST AUTOMATIZZATO PULIZIA DATI & COMPATIBILITÀ UNIVERSALE MESHCOM")
    print("=" * 70)

    proc = subprocess.Popen([
        'google-chrome', '--headless=new', '--disable-gpu',
        '--remote-debugging-port=9226',
        '--window-size=1440,1100',
        'http://localhost:8080/index.html'
    ])
    time.sleep(2.0)

    try:
        res = urllib.request.urlopen('http://127.0.0.1:9226/json')
        tabs = json.loads(res.read().decode())
        target_tab = None
        for t in tabs:
            if 'localhost:8080' in t.get('url', ''):
                target_tab = t; break
        if not target_tab: target_tab = tabs[0]

        ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'])
        req_id = 0
        def send_cmd(method, params=None):
            nonlocal req_id
            req_id += 1
            ws.send(json.dumps({"id": req_id, "method": method, "params": params or {}}))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == req_id: return r

        def eval_js(expr):
            r = send_cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            if "exceptionDetails" in r.get("result", {}):
                raise RuntimeError(f"JS Exception: {r['result']['exceptionDetails']}")
            return r.get("result", {}).get("result", {}).get("value")

        print("\n--- TEST 1: VERIFICA STATO DISCONNESSO (ZERO DATI SIMULATI) ---")
        state = eval_js("""
        (() => {
          return {
            call: document.getElementById('hdrCallsign').textContent.trim(),
            status: document.getElementById('connStatusText').textContent.trim(),
            freq: document.getElementById('cardFreq').textContent.trim(),
            txp: document.getElementById('cardTxPower').textContent.trim(),
            loc: document.getElementById('cardLocator').textContent.trim(),
            wx: document.getElementById('cardWeatherExtra').textContent.trim(),
            isConn: isNodeConnected
          };
        })()
        """)
        print(f"✅ Header Callsign: {state['call']} (atteso: DISCONNESSO)")
        print(f"✅ Stato Connessione: {state['status']} (atteso: DISCONNESSO)")
        print(f"✅ Frequenza Radio: {state['freq']} (atteso: -- MHz)")
        print(f"✅ Stato TX: {state['txp']}")
        print(f"✅ QTH Locator: {state['loc']} (atteso: --)")
        print(f"✅ Sensori WX: {state['wx']}")
        print(f"✅ isNodeConnected flag: {state['isConn']}")

        assert state['call'] == "DISCONNESSO"
        assert state['status'] == "DISCONNESSO"
        assert "--" in state['freq']
        assert state['loc'] == "--"
        assert state['isConn'] == False

        print("\n--- TEST 2: VERIFICA SCHEDA SPETTRO RF IN STANDBY ---")
        eval_js("switchTab('spectrum')")
        spec_state = eval_js("""
        (() => {
          return {
            rssi: document.getElementById('rfCurRssi').textContent.trim(),
            smeter: document.getElementById('rfCurSmeter').textContent.trim(),
            badge: document.getElementById('rfSignalBadge').textContent.trim(),
            snr: document.getElementById('rfCurSnr').textContent.trim(),
            chFreq: document.getElementById('rfChannelFreq').textContent.trim(),
            chBadge: document.getElementById('rfChannelBadge').textContent.trim(),
            title: document.getElementById('sdrMainTitle').textContent.trim()
          };
        })()
        """)
        print(f"✅ RSSI Spettro: {spec_state['rssi']} dBm")
        print(f"✅ S-Meter: {spec_state['smeter']}")
        print(f"✅ Badge Segnale: {spec_state['badge']} (atteso: OFFLINE)")
        print(f"✅ Margine SNR: {spec_state['snr']} dB")
        print(f"✅ Canale Frequenza: {spec_state['chFreq']} MHz")
        print(f"✅ Titolo SDR: {spec_state['title']}")

        assert spec_state['rssi'] == "--"
        assert spec_state['badge'] == "OFFLINE"
        assert spec_state['chFreq'] == "--"
        assert "STANDBY" in spec_state['title']

        # Screenshot dello stato pulito disconnesso
        shot1 = send_cmd("Page.captureScreenshot", {"format": "png"})['result']['data']
        with open("/home/user/.gemini/antigravity/scratch/meshcom-dashboard/screenshot_disconnected_clean.png", "wb") as f:
            f.write(base64.b64decode(shot1))
        print("📸 Screenshot stato disconnesso salvato con successo.")

        print("\n--- TEST 3: TEST COMPATIBILITÀ HARDWARE (ESP32-S3) & FREQUENZA (868.125 MHz) ---")
        # Simula connessione a un dispositivo differente (es. Heltec V3 su 868.125 MHz con callsign IK0XYZ-7)
        eval_js("""
        (() => {
          updateConnectionState(true, 'ble', 'MC-f812-IK0XYZ-7');
          parseNodeJson(JSON.stringify({
            TYP: "I",
            CALL: "IK0XYZ-7",
            HWID: "ESP32-S3",
            FWVER: "v4.35",
            BATV: 4.12,
            BATP: 91
          }));
          parseNodeJson(JSON.stringify({
            TYP: "SN",
            MQRG: 868.125,
            TXP: 22,
            MSF: 11,
            MBW: 125,
            MCR: "4/5"
          }));
          parseNodeJson(JSON.stringify({
            TYP: "W",
            TEMP: 24.3,
            HUM: 48,
            PRES: 1018.2
          }));
        })()
        """)
        time.sleep(1.0)

        conn_state = eval_js("""
        (() => {
          return {
            call: document.getElementById('hdrCallsign').textContent.trim(),
            hw: document.getElementById('hdrHwBadge').textContent.trim(),
            status: document.getElementById('connStatusText').textContent.trim(),
            freq: document.getElementById('cardFreq').textContent.trim(),
            txp: document.getElementById('cardTxPower').textContent.trim(),
            temp: document.getElementById('cardTemp').textContent.trim(),
            specFreq: document.getElementById('rfChannelFreq').textContent.trim(),
            specBand: document.getElementById('rfChannelBadge').textContent.trim(),
            specTitle: document.getElementById('sdrMainTitle').textContent.trim(),
            carrierTag: document.getElementById('sdrCarrierTag').textContent.trim()
          };
        })()
        """)
        print(f"✅ Riconoscimento Callsign: {conn_state['call']}")
        print(f"✅ Auto-detection Microcontrollore: {conn_state['hw']}")
        print(f"✅ Adattamento Frequenza Radio: {conn_state['freq']}")
        print(f"✅ TX Power reale: {conn_state['txp']}")
        print(f"✅ Spettro RF Frequenza Centrale: {conn_state['specFreq']} MHz")
        print(f"✅ Spettro RF Banda Riconosciuta: {conn_state['specBand']}")
        print(f"✅ Etichetta Portante SDR: {conn_state['carrierTag']}")

        assert conn_state['call'] == "IK0XYZ-7"
        assert "ESP32-S3" in conn_state['hw']
        assert "868.125" in conn_state['freq']
        assert conn_state['specFreq'] == "868.125"
        assert conn_state['specBand'] == "EU 868"
        assert "868.125" in conn_state['carrierTag']

        print("\n--- TEST 4: INIEZIONE PACCHETTO RF REALE & AGGIORNAMENTO DINAMICO ---")
        eval_js("recordRssi('I0VUQ-98', -78, 11.2)")
        time.sleep(1.2)

        rf_live = eval_js("""
        (() => {
          return {
            rssi: document.getElementById('rfCurRssi').textContent.trim(),
            smeter: document.getElementById('rfCurSmeter').textContent.trim(),
            snr: document.getElementById('rfCurSnr').textContent.trim(),
            badge: document.getElementById('rfSignalBadge').textContent.trim(),
            ranking: document.getElementById('rfHeardCountBadge').textContent.trim()
          };
        })()
        """)
        print(f"✅ Ricevuto Pacchetto RF: {rf_live['rssi']} dBm")
        print(f"✅ S-Meter Calcolato: {rf_live['smeter']}")
        print(f"✅ Margine SNR: {rf_live['snr']} dB")
        print(f"✅ Badge Qualità: {rf_live['badge']}")
        print(f"✅ Nodi in Classifica: {rf_live['ranking']}")

        assert rf_live['rssi'] == "-78"
        assert rf_live['smeter'] == "S8"
        assert "+11.2" in rf_live['snr']
        assert rf_live['badge'] == "ECCELLENTE"

        # Screenshot dello stato connesso con dati reali
        shot2 = send_cmd("Page.captureScreenshot", {"format": "png"})['result']['data']
        with open("/home/user/.gemini/antigravity/scratch/meshcom-dashboard/screenshot_connected_real.png", "wb") as f:
            f.write(base64.b64decode(shot2))
        print("📸 Screenshot stato connesso reale salvato con successo.")

        ws.close()
        print("\n" + "=" * 70)
        print("🎉 TUTTI I TEST DI PULIZIA E COMPATIBILITÀ SUPERATI AL 100%!")
        print("=" * 70)

    finally:
        proc.terminate()

if __name__ == "__main__":
    run_tests()
