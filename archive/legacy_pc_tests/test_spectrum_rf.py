#!/usr/bin/env python3
"""
Test Suite and Screenshot Capture for Modern Tactical SDR RF Spectrum & Waterfall
"""

import subprocess
import time
import json
import urllib.request
import base64
import websocket

def test_spectrum():
    print("=" * 65)
    print("🚀 AVVIO TEST SDR RF SPECTRUM & WATERFALL IN CHROME")
    print("=" * 65)

    proc = subprocess.Popen([
        'google-chrome', '--headless=new', '--disable-gpu',
        '--remote-debugging-port=9223',
        '--window-size=1440,950',
        'http://localhost:8080/index.html'
    ])
    time.sleep(2.0)

    try:
        res = urllib.request.urlopen('http://127.0.0.1:9223/json')
        tabs = json.loads(res.read().decode())
        target_tab = None
        for t in tabs:
            if 'localhost:8080' in t.get('url', ''):
                target_tab = t
                break
        if not target_tab:
            target_tab = tabs[0]

        ws_url = target_tab['webSocketDebuggerUrl']
        print(f"🔗 Connesso a DevTools: {ws_url}")
        ws = websocket.create_connection(ws_url)

        req_id = 0
        def send_cmd(method, params=None):
            nonlocal req_id
            req_id += 1
            msg = {"id": req_id, "method": method, "params": params or {}}
            ws.send(json.dumps(msg))
            while True:
                reply = json.loads(ws.recv())
                if reply.get("id") == req_id:
                    return reply

        def eval_js(expr):
            r = send_cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            if "exceptionDetails" in r.get("result", {}):
                raise RuntimeError(f"JS Exception: {r['result']['exceptionDetails']}")
            return r.get("result", {}).get("result", {}).get("value")

        print("\n--- TEST 1: APERTURA SCHEDA 'SPECTRUM' ---")
        eval_js("switchTab('spectrum')")
        is_active = eval_js("document.getElementById('pane-spectrum').classList.contains('active')")
        print(f"✅ Scheda 'spectrum' attiva: {is_active}")
        assert is_active == True

        print("\n--- TEST 2: VERIFICA CANVAS SDR FFT E WATERFALL ---")
        canvases_ok = eval_js("""
        (() => {
          const fft = document.getElementById('sdrFftCanvas');
          const wf = document.getElementById('sdrWaterfallCanvas');
          const trend = document.getElementById('rssiTrendCanvas');
          return {
            fftW: fft ? fft.width : 0,
            fftH: fft ? fft.height : 0,
            wfW: wf ? wf.width : 0,
            wfH: wf ? wf.height : 0,
            trendW: trend ? trend.width : 0
          };
        })()
        """)
        print(f"✅ Dimensioni Canvas FFT: {canvases_ok['fftW']}x{canvases_ok['fftH']}")
        print(f"✅ Dimensioni Canvas Waterfall: {canvases_ok['wfW']}x{canvases_ok['wfH']}")
        print(f"✅ Dimensioni Canvas Trend: {canvases_ok['trendW']}")
        assert canvases_ok['fftW'] > 0
        assert canvases_ok['wfW'] > 0

        print("\n--- TEST 3: TRIGGER SIMULATED LORA RF BURSTS ---")
        # Inietta alcuni burst realistici da nodi noti
        eval_js("recordRssi('IU0TGU-10', -84, 9.5)")
        time.sleep(0.3)
        eval_js("recordRssi('I0VUQ-98', -76, 12.0)")
        time.sleep(0.3)
        eval_js("recordRssi('IK0ZSN-1', -98, 5.2)")
        time.sleep(0.3)
        eval_js("triggerSimulatedRfBurst()")

        # Attendi che i frame renderizzino e scorrano sulla cascata
        time.sleep(1.8)

        hud_state = eval_js("""
        (() => {
          return {
            rssi: document.getElementById('rfCurRssi').textContent,
            smeter: document.getElementById('rfCurSmeter').textContent,
            snr: document.getElementById('rfCurSnr').textContent,
            totalPkt: sdrTotalPacketsAnalyzed,
            rankingCount: document.getElementById('rfHeardCountBadge').textContent,
            historyLength: rssiHistory.length
          };
        })()
        """)
        print(f"✅ HUD Livello RSSI Corrente: {hud_state['rssi']} dBm")
        print(f"✅ HUD S-Meter: {hud_state['smeter']}")
        print(f"✅ HUD SNR Margin: {hud_state['snr']} dB")
        print(f"✅ Pacchetti Totali Analizzati: {hud_state['totalPkt']}")
        print(f"✅ Nodi in Classifica RF: {hud_state['rankingCount']}")
        print(f"✅ Storico Trend Punti: {hud_state['historyLength']}")

        assert hud_state['totalPkt'] >= 4
        assert hud_state['historyLength'] >= 4

        print("\n--- TEST 4: VERIFICA CAMBIO PALETTE SDR ---")
        eval_js("changeSdrPalette('thermal')")
        pal = eval_js("sdrPalette")
        assert pal == "thermal"
        time.sleep(0.4)
        eval_js("changeSdrPalette('tactical')")
        pal = eval_js("sdrPalette")
        assert pal == "tactical"
        print(f"✅ Cambio Palette Colori testato con successo.")

        print("\n--- TEST 5: CATTURA SCREENSHOT AD ALTA DEFINIZIONE ---")
        shot_res = send_cmd("Page.captureScreenshot", {"format": "png"})
        shot_b64 = shot_res.get("result", {}).get("data")
        if shot_b64:
            out_img = "/home/user/.gemini/antigravity/scratch/meshcom-dashboard/screenshot_spectrum.png"
            with open(out_img, "wb") as f:
                f.write(base64.b64decode(shot_b64))
            print(f"📸 Screenshot Spettro RF salvato: {out_img}")

            # Salva anche nell'artifact dir
            art_img = "/home/user/.gemini/antigravity/brain/48ae432a-edce-407b-830c-90d114ea9bd3/screenshot_spectrum.png"
            with open(art_img, "wb") as f:
                f.write(base64.b64decode(shot_b64))
            print(f"📸 Screenshot copiato in Artifacts: {art_img}")

        ws.close()
        print("\n" + "=" * 65)
        print("🎉 TUTTI I TEST DELLO SPETTRO SDR SUPERATI CON SUCCESSO!")
        print("=" * 65)

    finally:
        proc.terminate()

if __name__ == "__main__":
    test_spectrum()
