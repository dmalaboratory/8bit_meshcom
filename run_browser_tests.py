#!/usr/bin/env python3
"""
Test Suite Completa via Chrome DevTools Protocol per MeshCom Tactical Dashboard
1. Testa parsing APRS eliminando caratteri corrotti e byte di coda
2. Testa gestione frame ACK 0x41
3. Testa telemetria JSON (W, I, SN, G, MH)
4. Testa navigazione tra tutte le 9 schede
5. Salva screenshot di verifica
"""

import subprocess
import time
import json
import urllib.request
import base64
import websocket

def run_tests():
    print("=" * 65)
    print("🚀 AVVIO TEST BROWSER CHROME HEADLESS SU LOCALHOST:8080")
    print("=" * 65)

    proc = subprocess.Popen([
        'google-chrome', '--headless=new', '--disable-gpu',
        '--remote-debugging-port=9222',
        '--window-size=1440,900',
        'http://localhost:8080/index.html'
    ])
    time.sleep(2.0)

    try:
        # Trova la scheda con index.html
        res = urllib.request.urlopen('http://127.0.0.1:9222/json')
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

        print("\n--- TEST 1: VERIFICA STATO INIZIALE ---")
        call = eval_js("ownCallsign")
        print(f"✅ Callsign configurato: {call}")
        assert call == "IU0TGU-10"

        hdr_call = eval_js("document.getElementById('hdrCallsign').textContent")
        print(f"✅ Callsign Header: {hdr_call}")
        assert hdr_call == "IU0TGU-10"

        print("\n--- TEST 2: RISOLUZIONE BUG CARATTERI CORROTTI ---")
        # Simula il pacchetto esatto dello screenshot dell'utente:
        # Byte 0: 0x3A (':'), Byte 1..4: msgId, Byte 5: hops 6, Payload: "IQ4FH-10,IU0TGU-10>22251:Buonasera VKR\0\x88\x99\xAA\xBB\x12\x34"
        test_script = """
        (() => {
          const enc = new TextEncoder();
          const str = "IQ4FH-10,IU0TGU-10>22251:Buonasera VKR";
          const textBytes = enc.encode(str);
          const buf = new Uint8Array(6 + textBytes.length + 8);
          buf[0] = 0x3A; // ':'
          buf[1] = 0x36; buf[2] = 0x36; buf[3] = 0x52; buf[4] = 0x43;
          buf[5] = 0x06;
          buf.set(textBytes, 6);
          buf[6 + textBytes.length] = 0x00; // NULL TERMINATOR
          buf.set([0x88, 0x99, 0xAA, 0xBB, 0x12, 0x34], 6 + textBytes.length + 1); // TRAILER BINARIO
          
          parseIncomingBleFrame(buf, "test_hex_dump");
          return liveMessages[liveMessages.length - 1];
        })()
        """
        parsed_msg = eval_js(test_script)
        print(f"✅ Mittente pulito: {parsed_msg['src']}")
        print(f"✅ Destinazione pulita: {parsed_msg['dst']}")
        print(f"✅ Testo pulito (zero caratteri corrotti): \"{parsed_msg['text']}\"")
        print(f"✅ Percorso ripetitore (Via): {parsed_msg['via']}")
        assert parsed_msg['src'] == "IQ4FH-10"
        assert parsed_msg['dst'] == "22251"
        assert parsed_msg['text'] == "Buonasera VKR"

        print("\n--- TEST 3: GESTIONE FRAME ACK (0x41) ---")
        # Invia una conferma di consegna ACK (0x41) per il messaggio
        ack_script = """
        (() => {
          const ackBuf = new Uint8Array([0x41, 0x36, 0x36, 0x52, 0x43, 0x01, 0x07, 0x49, 0x51, 0x34, 0x46, 0x48, 0x2D, 0x31]);
          handleBleNotification({
            target: { value: new DataView(ackBuf.buffer) }
          });
          return { ackCount: ackStatsTotal, delivered: liveMessages[liveMessages.length - 1].delivered };
        })()
        """
        ack_res = eval_js(ack_script)
        print(f"✅ Conteggio ACK: {ack_res['ackCount']}")
        print(f"✅ Messaggio marcato come consegnato (✓✓): {ack_res['delivered']}")
        assert ack_res['ackCount'] == 1
        assert ack_res['delivered'] == True

        print("\n--- TEST 4: INIEZIONE TELEMETRIA JSON MESHCOM ---")
        json_inject = """
        (() => {
          parseNodeJson(JSON.stringify({
            TYP: "I",
            CALL: "IU0TGU-10",
            HWID: "ESP32-S3",
            FWVER: "v4.33b",
            BATV: 4.18,
            BATP: 96
          }));
          parseNodeJson(JSON.stringify({
            TYP: "SN",
            MQRG: 433.175,
            TXP: 20,
            MSF: 11,
            MSH: 1,
            GW: 1
          }));
          parseNodeJson(JSON.stringify({
            TYP: "W",
            TEMP: 21.8,
            HUM: 54,
            PRES: 1016.4,
            ALT: 92
          }));
          parseNodeJson(JSON.stringify({
            TYP: "G",
            LAT: 41.8905,
            LON: 12.4942,
            SAT: 9
          }));
          return {
            bat: document.getElementById('hdrBattery').textContent,
            freq: document.getElementById('cardFreq').textContent,
            temp: document.getElementById('cardTemp').textContent,
            locator: document.getElementById('cardLocator').textContent
          };
        })()
        """
        card_res = eval_js(json_inject)
        print(f"✅ Batteria aggiornata: {card_res['bat']}")
        print(f"✅ Frequenza Radio: {card_res['freq']}")
        print(f"✅ Temperatura Sensore: {card_res['temp']}")
        print(f"✅ QTH Locator calcolato: {card_res['locator']}")
        assert "4.18V" in card_res['bat']
        assert "433.175" in card_res['freq']
        assert "21.8" in card_res['temp']
        assert "JN61" in card_res['locator']

        print("\n--- TEST 5: VERIFICA DI TUTTE LE 9 SCHEDE ---")
        tabs = ['chat', 'mheard', 'map', 'wx', 'matrix', 'rxlog', 'spectrum', 'setup', 'connection']
        for tab_id in tabs:
            eval_js(f"switchTab('{tab_id}')")
            is_active = eval_js(f"document.getElementById('pane-{tab_id}').classList.contains('active')")
            assert is_active == True
            print(f"  [✓] Scheda '{tab_id}' attiva e renderizzata.")

        # Torna alla scheda chat per screenshot finale
        eval_js("switchTab('chat')")

        print("\n--- TEST 6: CATTURA SCREENSHOT VERIFICA ---")
        shot_res = send_cmd("Page.captureScreenshot", {"format": "png"})
        shot_b64 = shot_res.get("result", {}).get("data")
        if shot_b64:
            screenshot_path = "/home/user/.gemini/antigravity/scratch/meshcom-dashboard/verified_dashboard.png"
            with open(screenshot_path, "wb") as f:
                f.write(base64.b64decode(shot_b64))
            print(f"📸 Screenshot salvato con successo in: {screenshot_path}")

        ws.close()
        print("\n" + "=" * 65)
        print("🎉 TUTTI I TEST SUPERATI AL 100% CON SUCCESSO!")
        print("=" * 65)

    finally:
        proc.terminate()

if __name__ == "__main__":
    run_tests()
