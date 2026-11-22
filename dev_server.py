#!/usr/bin/env python3
"""
8BitWave MeshCom IU0TGU - Multi-Threaded Live WebGUI Development Server
Server HTTP multi-thread con supporto completo a:
- Connessioni simultanee multiple (ThreadingHTTPServer)
- Live Reload automatico istantaneo via SSE senza bloccare il server
- Simulazione completa di tutte le risposte HTML di MeshCom (info, pos, wx, mheard, messaggi, rxlog)
- Gestione comandi CLI e regolazione potenza/frequenza in tempo reale
- Proxy CORS integrato
"""

import os
import sys
import time
import json
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import socketserver
import threading

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "index.html")

# Stato globale simulato del nodo MeshCom
node_state = {
    "CALL": "NOCALL",
    "HW": "ESP32 LoRa Node",
    "FW": "v4.35 8BitWave",
    "FREQ": "433.175",
    "TXP": 30,
    "SF": 12,
    "BW": 125,
    "CR": 5,
    "BAT_V": 4.18,
    "BAT_P": 98,
    "LAT": 41.9028,
    "LON": 12.4964,
    "ALT": 54,
    "LOC": "JN61fv",
    "TEMP": 21.8,
    "HUM": 55.4,
    "PRESS": 1014.2,
    "GATEWAY": True,
    "GATEWAY_SRV": "IT",
    "GATEWAY_POS": "pos",
    "NET_MODE": "auto",
    "POSTIME": 300,
    "TRACK": True,
    "SOLAR_V": 5.85,
    "SOLAR_MA": 380,
    "SOLAR_W": 2.22,
    "DUTY_CYCLE": 1.2,
    "AIRTIME_SEC": 43,
    "BLOCKED": ["SPAM01", "TESTCALL"],
    "KISS_TX": 12,
    "KISS_RX": 48
}

def execute_mock_cli(cmd):
    cmd = cmd.strip()
    c = cmd.lower()
    print(f"⌨️ [CLI Command] {cmd}")
    if c == "--help":
        return """MeshCom 4.39b (8BitWave Edition by IU0TGU)
Available CLI commands:
  --status             Display complete node telemetry & RF parameters
  --info               Hardware, ESP32 CPU, Flash and firmware version
  --wx                 Environmental weather sensors (BME280/INA226)
  --pos                GPS coordinates, altitude, Maidenhead QTH locator
  --show nodes         List all active mesh nodes in database
  --show blocked       List currently blacklisted / blocked callsigns
  --block <call>       Add callsign to blacklist (drop packets)
  --unblock <call>     Remove callsign from blacklist
  --freq <mhz>         Set LoRa RF frequency (e.g. 433.175 or 869.525)
  --txpower <dbm>      Set RF TX power (2 to 22 dBm)
  --gateway <on|off>   Enable/disable APRS-IS Internet gateway
  --wifiap <on|off>    Enable/disable Wi-Fi SoftAP hotspot mode
  --scan wifi          Scan available 2.4GHz Wi-Fi networks
  --batt               Battery voltage (V) and charge status (%)
  --kiss <on|off>      Enable/disable KISS TNC on TCP port 8001
  --reboot             Soft reboot ESP32 microcontroller"""
    elif c == "--status":
        return f"""Node: {node_state.get('CALL', 'IU0TGU-10')} | HW: ESP32 LoRa 1W | FW: 8BitWave v2.0
Freq: {node_state.get('FREQ', '433.175')} MHz | SF: {node_state.get('SF', 11)} | BW: {node_state.get('BW', 250)} kHz | TX: {node_state.get('TXP', 22)} dBm
GPS: {node_state.get('LAT', 41.9028)}° N, {node_state.get('LON', 12.4964)}° E ({node_state.get('LOC', 'JN61fv')}) | Alt: {node_state.get('ALT', 54)}m
Battery: {node_state.get('BAT_V', 4.14)}V ({node_state.get('BAT_P', 95)}%) | Solar: {node_state.get('SOLAR_V', 5.85)}V (+{node_state.get('SOLAR_MA', 380)} mA, {node_state.get('SOLAR_W', 2.22)}W)
Duty Cycle: {node_state.get('DUTY_CYCLE', 1.2)}% ({node_state.get('AIRTIME_SEC', 43)}s/360s) | Packets: 184 RX / 22 TX
Wi-Fi: {node_state.get('WIFI_MODE', 'AP')} ({node_state.get('WIFI_IP', '192.168.4.1')}) | KISS TCP: Port 8001 | Gateway: {'ON' if node_state.get('GATEWAY') else 'OFF'}
Uptime: 04h 22m 18s | Free Heap: 184,320 bytes"""
    elif c == "--info":
        return """8BitWave MeshCom Custom Firmware by IU0TGU
Base: MeshCom 4.39b | Board: ESP32-WROOM-32D (DevKitC DOUT 40MHz)
Flash: 4MB (4096KB) | Free Heap: 184,320 bytes | PSRAM: N/A
Radio IC: SX1262 SPI @ 10MHz | Power Amp: E22-400M30S (1 Watt)
Sensors: BME280 (I2C 0x76), INA226 (I2C 0x40), ATGM336H GPS
Bluetooth: BLE 4.2 Nordic UART Service | KISS Server: Port 8001
Build Date: Nov 2026 | Author: IU0TGU"""
    elif c == "--wx":
        return f"""WX Telemetry: Temp: {node_state.get('TEMP', 21.4)}°C | Hum: {node_state.get('HUM', 58)}% | Press: {node_state.get('PRESS', 1013.2)} hPa
Power / Solar (INA226): Bus: {node_state.get('BAT_V', 4.14)}V | Shunt: +{node_state.get('SOLAR_MA', 380)}mA | Power: {node_state.get('SOLAR_W', 2.22)}W | Solar Vin: {node_state.get('SOLAR_V', 5.85)}V
Status: Solar charging active (Net +{node_state.get('SOLAR_MA', 380)}mA) | Runtime est: >72 hours"""
    elif c == "--pos":
        return f"""GPS Position: {node_state.get('LAT', 41.9028)}° N, {node_state.get('LON', 12.4964)}° E | QTH Locator: {node_state.get('LOC', 'JN61fv')}
Altitude: {node_state.get('ALT', 54)} m | HDOP: 0.9 | Satellites: 8 (3D Fix) | Course: 000°"""
    elif c == "--show nodes":
        return """Active Mesh Nodes (3):
1. IU0TGU-MOBILE [ESP32 LoRa] - RSSI: -68 dBm, SNR: +10.5 dB, 0 hops (0.0 km, JN61fv)
2. IZ0XYZ [Heltec V3] - RSSI: -74 dBm, SNR: +8.2 dB, 1 hop (3.4 km, JN61et, 204° SSW)
3. IW0ABC-9 [T-Beam] - RSSI: -88 dBm, SNR: +4.0 dB, 2 hops (2.8 km, JN61fw, 035° NE)"""
    elif c.startswith("--block"):
        parts = cmd.split()
        if len(parts) >= 2:
            call = parts[1].upper()
            if call not in node_state["BLOCKED"]:
                node_state["BLOCKED"].append(call)
            return f"Added {call} to blacklist (total {len(node_state['BLOCKED'])} blocked). Packets from this call will be dropped."
        return "Usage: --block <CALLSIGN>"
    elif c.startswith("--unblock"):
        parts = cmd.split()
        if len(parts) >= 2:
            call = parts[1].upper()
            if call in node_state["BLOCKED"]:
                node_state["BLOCKED"].remove(call)
            return f"Removed {call} from blacklist (total {len(node_state['BLOCKED'])} blocked)."
        return "Usage: --unblock <CALLSIGN>"
    elif c == "--show blocked":
        blocked_list = ", ".join(node_state.get("BLOCKED", [])) or "Nessun nodo bloccato"
        return f"Blocked calls ({len(node_state.get('BLOCKED', []))}): {blocked_list}"
    elif c == "--batt":
        return f"Battery: {node_state.get('BAT_V', 4.14)} V ({node_state.get('BAT_P', 95)}% SoC) | Status: Charging | Solar Vin: {node_state.get('SOLAR_V', 5.85)} V (+{node_state.get('SOLAR_MA', 380)} mA)"
    elif c == "--scan wifi":
        return """Scanning 2.4 GHz Wi-Fi channels...
Found 4 networks:
1. MeshCom-Hotspot (CH 1, -54 dBm, WPA2)
2. Fibra-Home-2.4G (CH 6, -68 dBm, WPA2/WPA3)
3. HamRadio-Lab (CH 11, -72 dBm, WPA2)
4. DIGI-APRS-EXT (CH 6, -82 dBm, OPEN)"""
    elif c == "--reboot":
        return "ESP32 soft reboot scheduled in 2 seconds... Restarting system."
    elif c.startswith("--freq"):
        parts = cmd.split()
        if len(parts) >= 2:
            node_state["FREQ"] = parts[1]
            return f"LoRa frequency set to {parts[1]} MHz."
        return "Usage: --freq <MHz>"
    elif c.startswith("--txpower"):
        parts = cmd.split()
        if len(parts) >= 2:
            try:
                node_state["TXP"] = int(parts[1])
                return f"LoRa TX power set to {parts[1]} dBm."
            except: pass
        return "Usage: --txpower <dBm>"
    elif c.startswith("--setcall"):
        parts = cmd.split()
        if len(parts) >= 2:
            node_state["CALL"] = parts[1].upper()
            return f"Node callsign set to {node_state['CALL']}."
        return "Usage: --setcall <CALLSIGN>"
    elif c == "--wifiap on":
        node_state["WIFI_MODE"] = "AP"
        node_state["WIFI_IP"] = "192.168.4.1"
        return "Wi-Fi Access Point enabled (IP 192.168.4.1)."
    elif c == "--wifiap off":
        node_state["WIFI_MODE"] = "STA"
        node_state["WIFI_IP"] = "192.168.1.105"
        return "Wi-Fi Client Station mode enabled (IP 192.168.1.105)."
    elif c == "--gateway on":
        node_state["GATEWAY"] = True
        return "APRS-IS Gateway enabled."
    elif c == "--gateway off":
        node_state["GATEWAY"] = False
        return "APRS-IS Gateway disabled."
    else:
        return f"Command '{cmd}' executed successfully (returncode 0)."

mock_chat = [
    {
        "src": "IU0TGU",
        "dst": "*",
        "time": time.strftime("%H:%M:%S", time.localtime(time.time() - 180)),
        "text": "Stazione 8BitWave MeshCom IU0TGU attiva su 433.175 MHz - Nodo LoRa pronto."
    },
    {
        "src": "IZ0XYZ",
        "dst": "*",
        "time": time.strftime("%H:%M:%S", time.localtime(time.time() - 65)),
        "text": "Forte e chiaro sulla mesh da Roma Sud! Segnale 59+, SNR +9.2 dB."
    },
    {
        "src": "IW0ABC-9",
        "dst": "222",
        "time": time.strftime("%H:%M:%S", time.localtime(time.time() - 15)),
        "text": "QSO confermato sul canale 222 Gruppo Italia."
    }
]

# Track file modification time for live reload
last_mtime = os.path.getmtime(INDEX_FILE) if os.path.exists(INDEX_FILE) else 0
subscribers = []
subscribers_lock = threading.Lock()

def file_watcher():
    global last_mtime
    while True:
        try:
            if os.path.exists(INDEX_FILE):
                curr_mtime = os.path.getmtime(INDEX_FILE)
                if curr_mtime != last_mtime:
                    last_mtime = curr_mtime
                    print(f"🔄 [Live Reload] index.html modificato! Invio refresh ai browser connessi...")
                    with subscribers_lock:
                        for q in list(subscribers):
                            try:
                                q.append("reload")
                            except Exception:
                                subscribers.remove(q)
        except Exception:
            pass
        time.sleep(0.5)

class DevServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        # Mute repetitive polling logs to keep terminal readable
        msg = format % args
        if any(k in msg for k in ["/?page=", "/live-reload", "/?getmessages", "/nodesettings.json"]):
            return
        super().log_message(format, *args)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-MC, Content-Type, Authorization, *')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. LIVE RELOAD SSE
        if path == "/live-reload":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            queue = []
            with subscribers_lock:
                subscribers.append(queue)
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    if queue:
                        msg = queue.pop(0)
                        self.wfile.write(f"data: {msg}\n\n".encode())
                        self.wfile.flush()
                    time.sleep(0.3)
            except Exception:
                pass
            finally:
                with subscribers_lock:
                    if queue in subscribers:
                        subscribers.remove(queue)
            return

        # 2. PROXY HANDLER
        if path.startswith("/proxy"):
            target_url = query.get("url", [""])[0]
            if target_url:
                try:
                    req = urllib.request.Request(target_url, headers={'User-Agent': 'MeshCom-Tactical-Proxy/1.0'})
                    with urllib.request.urlopen(req, timeout=4) as response:
                        body = response.read()
                        self.send_response(200)
                        self.send_header('Content-Type', response.headers.get('Content-Type', 'text/html; charset=utf-8'))
                        self.end_headers()
                        self.wfile.write(body)
                        return
                except Exception as e:
                    self.send_response(502)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(f"Proxy error: {e}".encode())
                    return

        # 3. MESHCOM NATIVE WI-FI REST HTML ENDPOINTS
        page = query.get("page", [""])[0]

        # 3a. /?page=info
        if page == "info":
            html = f"""<!DOCTYPE html><html><body>
<table>
  <tr><td>Call:</td><td>{node_state['CALL']}</td></tr>
  <tr><td>Hardware:</td><td>{node_state['HW']}</td></tr>
  <tr><td>Firmware:</td><td>{node_state['FW']}</td></tr>
  <tr><td>Frequency:</td><td>{node_state['FREQ']} MHz</td></tr>
  <tr><td>TX Power:</td><td>{node_state['TXP']} dBm</td></tr>
  <tr><td>Spreading Factor (SF):</td><td>{node_state['SF']}</td></tr>
  <tr><td>Bandwidth:</td><td>{node_state['BW']} kHz</td></tr>
  <tr><td>Coding Rate (CR):</td><td>{node_state['CR']}</td></tr>
  <tr><td>Battery:</td><td>{node_state['BAT_V']}V ({node_state['BAT_P']}%)</td></tr>
  <tr><td>WiFi RSSI:</td><td>-52 dBm</td></tr>
  <tr><td>APRS text:</td><td>MeshCom {node_state['CALL']} 8BitWave</td></tr>
</table>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # 3b. /?page=position
        if page == "position":
            html = f"""<!DOCTYPE html><html><body>
<table>
  <tr><td>Latitude</td><td>{node_state['LAT']} N</td></tr>
  <tr><td>Longitude</td><td>{node_state['LON']} E</td></tr>
  <tr><td>Altitude</td><td>{node_state['ALT']} m</td></tr>
  <tr><td>Locator</td><td>{node_state['LOC']}</td></tr>
</table>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # 3c. /?page=wx
        if page == "wx":
            html = f"""<!DOCTYPE html><html><body>
<table>
  <tr><td>Temperature</td><td>{node_state['TEMP']} °C</td></tr>
  <tr><td>Humidity</td><td>{node_state['HUM']} %</td></tr>
  <tr><td>QNH</td><td>{node_state['PRESS']} hPa</td></tr>
  <tr><td>Altitude asl</td><td>{node_state['ALT']} m</td></tr>
  <tr><td>Gas</td><td>115 kOhm</td></tr>
</table>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # 3d. /?page=mheard
        if page == "mheard":
            html = f"""<!DOCTYPE html><html><body>
<div class="cardlayout">
  <div class="cardlabel">
    <a href="?call=IU0TGU-MOBILE">IU0TGU-MOBILE</a>
    <span class="font-small">(Adesso)</span>
  </div>
  <div class="flex-auto-wrap">
    <div><span class="font-bold">RSSI:</span> <span>-68 dBm</span></div>
    <div><span class="font-bold">SNR:</span> <span>10.5 dB</span></div>
    <div><span class="font-bold">Hops:</span> <span>0</span></div>
    <div><span class="font-bold">Hardware:</span> <span>ESP32 LoRa</span></div>
    <div><span class="font-bold">Battery:</span> <span>4.14V (95%)</span></div>
    <div><span class="font-bold">Lat:</span> <span>N 41.9028</span></div>
    <div><span class="font-bold">Lon:</span> <span>E 12.4964</span></div>
    <div><span class="font-bold">Dist:</span> <span>0.0 km</span></div>
  </div>
</div>
<div class="cardlayout">
  <div class="cardlabel">
    <a href="?call=IZ0XYZ">IZ0XYZ</a>
    <span class="font-small">(1m fa)</span>
  </div>
  <div class="flex-auto-wrap">
    <div><span class="font-bold">RSSI:</span> <span>-74 dBm</span></div>
    <div><span class="font-bold">SNR:</span> <span>8.2 dB</span></div>
    <div><span class="font-bold">Hops:</span> <span>1</span></div>
    <div><span class="font-bold">Hardware:</span> <span>Heltec V3</span></div>
    <div><span class="font-bold">Battery:</span> <span>3.95V (80%)</span></div>
    <div><span class="font-bold">Lat:</span> <span>N 41.8750</span></div>
    <div><span class="font-bold">Lon:</span> <span>E 12.4800</span></div>
    <div><span class="font-bold">Dist:</span> <span>3.4 km</span></div>
  </div>
</div>
<div class="cardlayout">
  <div class="cardlabel">
    <a href="?call=IW0ABC-9">IW0ABC-9</a>
    <span class="font-small">(4m fa)</span>
  </div>
  <div class="flex-auto-wrap">
    <div><span class="font-bold">RSSI:</span> <span>-88 dBm</span></div>
    <div><span class="font-bold">SNR:</span> <span>4.0 dB</span></div>
    <div><span class="font-bold">Hops:</span> <span>2</span></div>
    <div><span class="font-bold">Hardware:</span> <span>T-Beam SX1262</span></div>
    <div><span class="font-bold">Battery:</span> <span>4.02V (86%)</span></div>
    <div><span class="font-bold">Lat:</span> <span>N 41.9200</span></div>
    <div><span class="font-bold">Lon:</span> <span>E 12.5100</span></div>
    <div><span class="font-bold">Dist:</span> <span>2.8 km</span></div>
  </div>
</div>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # 3e. /?getmessages
        if "getmessages" in query:
            msg_html_list = []
            for m in mock_chat:
                is_send = "message-send" if m["src"] == node_state["CALL"] else "message-recv"
                msg_html_list.append(f"""
<div class="message {is_send}">
  <p><a href="?call={m['src']}">{m['src']}</a> &gt; {m['dst']}</p>
  <p class="font-small">{m['time']}</p>
  <p class="font-normal">{m['text']}</p>
</div>""")
            html = f"<!DOCTYPE html><html><body>{''.join(msg_html_list)}</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # 3f. /?page=rxlog
        if page == "rxlog":
            html = f"""<!DOCTYPE html><html><body>
<table>
  <tr><th>Time</th><th>Type</th><th>Source</th><th>Dest</th><th>SNR</th><th>RSSI</th></tr>
  <tr><td>{time.strftime('%H:%M:%S')}</td><td>TEXT</td><td>IZ0XYZ</td><td>ALL</td><td>+8.2 dB</td><td>-74 dBm</td></tr>
  <tr><td>{time.strftime('%H:%M:%S', time.localtime(time.time() - 30))}</td><td>POS</td><td>IU0TGU-MOBILE</td><td>APRS</td><td>+10.5 dB</td><td>-68 dBm</td></tr>
  <tr><td>{time.strftime('%H:%M:%S', time.localtime(time.time() - 75))}</td><td>ACK</td><td>IW0ABC-9</td><td>IU0TGU</td><td>+4.0 dB</td><td>-88 dBm</td></tr>
</table>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # 4. SETPARAM & CONFIGURATION ENDPOINTS (/setparam/?...)
        if path.startswith("/setparam") or "setparam" in path:
            print(f"⚙️ [MeshCom SetParam] {parsed.query}")
            for k, vals in query.items():
                val = vals[0]
                if k == "wifiap":
                    node_state["WIFI_MODE"] = "AP" if val.lower() in ["on", "1", "true"] else "STA"
                    node_state["WIFI_IP"] = "192.168.4.1" if node_state["WIFI_MODE"] == "AP" else "192.168.1.105"
                    print(f"   -> Wi-Fi Mode impostato su: {node_state['WIFI_MODE']} (IP: {node_state['WIFI_IP']})")
                elif k == "setssid":
                    node_state["WIFI_SSID"] = val
                    print(f"   -> Wi-Fi SSID impostato su: {val}")
                elif k == "setpwd":
                    node_state["WIFI_PWD"] = val
                    print(f"   -> Wi-Fi Password salvata ({len(val)} caratteri)")
                elif k in ["setbtcode", "bt_code"]:
                    node_state["BLE_PIN"] = val
                    print(f"   -> BLE PIN Pairing impostato su: {val}")
                elif k in ["webpwd", "setwebpwd"]:
                    node_state["WEB_PWD"] = val
                    print(f"   -> Web Admin Password aggiornata ({len(val)} caratteri)")
                elif k in ["passwd", "setpasswd"]:
                    node_state["RM_PWD"] = val
                    print(f"   -> Remote Management (RM1) Password aggiornata")
                elif k in ["rmstrict", "rmstrictsecurity"]:
                    node_state["RM_STRICT"] = val
                    print(f"   -> RM Strict Security impostato su: {val}")
                elif k in ["gateway"]:
                    node_state["GATEWAY"] = (val.lower() in ["on", "1", "true"])
                    print(f"   -> Gateway APRS-IS impostato su: {node_state['GATEWAY']}")
                elif k in ["gatewaysrv"]:
                    node_state["GATEWAY_SRV"] = val.upper()
                    print(f"   -> Server Gateway APRS impostato su: {val.upper()}")
                elif k in ["gatewaypos"]:
                    node_state["GATEWAY_POS"] = val.lower()
                    print(f"   -> Gateway Posizione impostata su: {val.lower()}")
                elif k in ["setnet"]:
                    node_state["NET_MODE"] = val.lower()
                    print(f"   -> Rete Gateway impostata su: {val.lower()}")
                elif k in ["postime"]:
                    try: node_state["POSTIME"] = int(val)
                    except: pass
                    print(f"   -> Cadenza Beacon APRS impostata su: {val}s")
                elif k in ["track"]:
                    node_state["TRACK"] = (val.lower() in ["on", "1", "true"])
                    print(f"   -> SmartBeaconing APRS impostato su: {node_state['TRACK']}")
                elif k == "txpower":
                    try: node_state["TXP"] = int(val)
                    except: pass
                elif k == "setcall":
                    node_state["CALL"] = val
                elif k == "manualcommand":
                    # Esegui comando CLI completo
                    out = execute_mock_cli(val)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "ok": True,
                        "returncode": 0,
                        "output": out,
                        "state": node_state,
                        "blocked": node_state.get("BLOCKED", [])
                    }).encode())
                    return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": True,
                "returncode": 0,
                "state": node_state,
                "blocked": node_state.get("BLOCKED", [])
            }).encode())
            return

        # 5. COMMANDS & ACTIONS
        if "command" in query or "manualcommand" in query:
            cmd = (query.get("command") or query.get("manualcommand"))[0]
            print(f"⌨️ [MeshCom Cmd] {cmd}")
            if "--freq" in cmd:
                parts = cmd.split()
                if len(parts) >= 2: node_state["FREQ"] = parts[1]
            elif "--setcall" in cmd:
                parts = cmd.split()
                if len(parts) >= 2: node_state["CALL"] = parts[1]
            elif "--wifiap on" in cmd:
                node_state["WIFI_MODE"] = "AP"
                node_state["WIFI_IP"] = "192.168.4.1"
            elif "--wifiap off" in cmd:
                node_state["WIFI_MODE"] = "STA"
                node_state["WIFI_IP"] = "192.168.1.105"
            elif "--bleshort" in cmd:
                node_state["BLE_FMT"] = "short"
            elif "--blelong" in cmd:
                node_state["BLE_FMT"] = "long"
            elif "--gateway on" in cmd:
                node_state["GATEWAY"] = True
                print("   -> Gateway APRS-IS: ON")
            elif "--gateway off" in cmd:
                node_state["GATEWAY"] = False
                print("   -> Gateway APRS-IS: OFF")
            elif "--gateway srv" in cmd:
                parts = cmd.split()
                if len(parts) >= 3:
                    node_state["GATEWAY_SRV"] = parts[2].upper()
                    print(f"   -> Server Gateway APRS: {parts[2].upper()}")
            elif "--gateway pos" in cmd:
                node_state["GATEWAY_POS"] = "pos"
                print("   -> Inoltro Posizione Gateway: ON (pos)")
            elif "--gateway nopos" in cmd:
                node_state["GATEWAY_POS"] = "nopos"
                print("   -> Inoltro Posizione Gateway: OFF (nopos)")
            elif "--track on" in cmd:
                node_state["TRACK"] = True
            elif "--track off" in cmd:
                node_state["TRACK"] = False
            elif "--postime" in cmd:
                parts = cmd.split()
                if len(parts) >= 2:
                    try: node_state["POSTIME"] = int(parts[1])
                    except: pass
            elif "--sendpos" in cmd or "--sendtrack" in cmd:
                print("   -> 📍 Beacon APRS posizione inviato verso aprs.fi e LoRa!")
            elif "--txpower" in cmd:
                parts = cmd.split()
                if len(parts) >= 2:
                    try: node_state["TXP"] = int(parts[1])
                    except: pass
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"OK [Command executed: {cmd}]".encode())
            return

        if "sendmessage" in query:
            txt = query["sendmessage"][0]
            print(f"💬 [MeshCom TX] Inviato: {txt}")
            mock_chat.append({
                "src": node_state["CALL"],
                "dst": "*",
                "time": time.strftime("%H:%M:%S"),
                "text": txt
            })
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK [Message queued]")
            return

        # 6. WI-FI SCAN ENDPOINT: /wifiscan or /?wifiscan
        if path == "/wifiscan" or "wifiscan" in query or "scanwifi" in query:
            print("🔍 [DevServer] Esecuzione scansione reti Wi-Fi 2.4 GHz...")
            scan_results = [
                {"ssid": "Vodafone-Fibra-Casa", "rssi": -48, "auth": 3, "ch": 1},
                {"ssid": "TIM-WiFi-Fibra", "rssi": -62, "auth": 3, "ch": 6},
                {"ssid": "HamNet-Rome-Gateway", "rssi": -71, "auth": 3, "ch": 11},
                {"ssid": "Hotspot-IU0TGU-Mobile", "rssi": -42, "auth": 4, "ch": 1},
                {"ssid": "FASTWEB-AP-Outdoor", "rssi": -81, "auth": 3, "ch": 6},
                {"ssid": "Rete-Libera-Open", "rssi": -86, "auth": 0, "ch": 11}
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(scan_results).encode())
            return

        # 7. COMPATIBILITY JSON API: /nodesettings.json
        if path == "/nodesettings.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(node_state).encode())
            return

        # 8. CALLFUNCTION HANDLER (/callfunction/?otaupdate etc.)
        if path.startswith("/callfunction") or "callfunction" in path:
            print(f"⚡ [DevServer CallFunction] Query: {parsed.query}")
            action = "unknown"
            if "otaupdate" in parsed.query or "otaupdate" in query:
                action = "otaupdate"
                print("🚀 [DevServer OTA] Ricevuto trigger riavvio Safeboot OTA! Commutazione su partizione safeboot...")
            elif "reboot" in parsed.query:
                action = "reboot"
                print("🔄 [DevServer Reboot] Ricevuto riavvio nodo...")
            elif "sendpos" in parsed.query:
                action = "sendpos"
                print("📍 [DevServer SendPos] Invio beacon APRS forzato...")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "action": action, "returncode": 0, "msg": "Rebooting to Safeboot OTA Updater..."}).encode())
            return

        # 9. SAFEBOOT OTA UPDATE UI (/update)
        if path == "/update":
            safeboot_html = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MeshCom Safeboot OTA Updater</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 1rem; }
    .ota-card { background: #131b2e; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 2rem; max-width: 480px; width: 100%; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
    .badge { display: inline-block; padding: 0.25rem 0.65rem; border-radius: 999px; font-size: 0.72rem; font-weight: 700; background: rgba(6,182,212,0.15); color: #06b6d4; border: 1px solid #06b6d4; margin-bottom: 1rem; }
    h1 { font-size: 1.25rem; font-weight: 800; margin: 0 0 0.5rem 0; color: #fff; }
    p { font-size: 0.8rem; color: #94a3b8; line-height: 1.5; margin-bottom: 1.5rem; }
    .dropzone { border: 2px dashed rgba(6,182,212,0.4); border-radius: 8px; padding: 1.5rem; text-align: center; cursor: pointer; background: rgba(0,0,0,0.25); margin-bottom: 1rem; transition: border-color 0.2s; }
    .dropzone:hover { border-color: #06b6d4; }
    .btn-update { width: 100%; padding: 0.75rem; border: none; border-radius: 6px; font-weight: 700; font-size: 0.85rem; color: #fff; background: linear-gradient(135deg, #06b6d4, #2563eb); cursor: pointer; transition: opacity 0.2s; }
    .btn-update:disabled { opacity: 0.5; cursor: not-allowed; }
    .progress-bar-wrap { width: 100%; height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden; margin: 1rem 0; display: none; }
    .progress-bar { width: 0%; height: 100%; background: linear-gradient(90deg, #06b6d4, #10b981); transition: width 0.2s; }
    .status-msg { font-size: 0.78rem; text-align: center; color: #38bdf8; min-height: 1.2rem; }
  </style>
</head>
<body>
  <div class="ota-card">
    <div class="badge">ESP32 SAFEBOOT RECOVERY</div>
    <h1>MeshCom OTA Firmware Updater</h1>
    <p>Dispositivo in modalità provvisoria <strong>Safeboot</strong> (partizione factory). Seleziona il file <code>firmware.bin</code> compilato per riscrivere la partizione principale via Wi-Fi.</p>
    
    <div class="dropzone" onclick="document.getElementById('fwFile').click()">
      <input type="file" id="fwFile" accept=".bin" style="display:none" onchange="fileSelected(this.files)">
      <div style="font-size: 2rem; margin-bottom: 0.5rem">📦</div>
      <div id="fileLabel" style="font-size: 0.85rem; font-weight: 700">Clicca per selezionare firmware.bin</div>
      <div style="font-size: 0.7rem; color: #64748b">Dimensione massima: 3.2 MB</div>
    </div>

    <div class="progress-bar-wrap" id="progWrap">
      <div class="progress-bar" id="progBar"></div>
    </div>
    <div class="status-msg" id="statusMsg"></div>

    <button class="btn-update" id="btnUpload" disabled onclick="startUpload()">⚡ Avvia Flash Firmware OTA</button>

    <div style="margin-top: 1.5rem; text-align: center">
      <a href="/" style="font-size: 0.75rem; color: #64748b; text-decoration: none">➜ Annulla e torna alla WebGUI principale</a>
    </div>
  </div>

  <script>
    let chosenFile = null;
    function fileSelected(files) {
      if (!files || files.length === 0) return;
      chosenFile = files[0];
      document.getElementById('fileLabel').textContent = chosenFile.name + ' (' + (chosenFile.size / 1024 / 1024).toFixed(2) + ' MB)';
      document.getElementById('btnUpload').disabled = false;
      document.getElementById('statusMsg').textContent = 'File pronto per il caricamento.';
    }

    function startUpload() {
      if (!chosenFile) return;
      const btn = document.getElementById('btnUpload');
      const wrap = document.getElementById('progWrap');
      const bar = document.getElementById('progBar');
      const msg = document.getElementById('statusMsg');
      btn.disabled = true;
      wrap.style.display = 'block';
      msg.textContent = 'Caricamento firmware via Wi-Fi in corso...';

      let pct = 0;
      const timer = setInterval(() => {
        pct += 10;
        bar.style.width = pct + '%';
        msg.textContent = 'Scrittura flash ESP32: ' + pct + '%...';
        if (pct >= 100) {
          clearInterval(timer);
          bar.style.background = '#10b981';
          msg.innerHTML = '✅ <strong>Flash completato con successo!</strong> Riavvio del nodo MeshCom tra 3s...';
          setTimeout(() => {
            window.location.href = '/?tab=connection';
          }, 3500);
        }
      }, 250);
    }
  </script>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(safeboot_html.encode())
            return

        if path == "/" or path == "/index":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ["/update", "/ota/upload"]:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            print(f"📦 [DevServer OTA POST] Ricevuti {len(post_data):,} bytes di firmware per flash!")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return
        self.send_response(404)
        self.end_headers()

import ssl

HTTPS_PORT = 8443
CERT_FILE = os.path.join(BASE_DIR, "cert.pem")
KEY_FILE = os.path.join(BASE_DIR, "key.pem")

def run_https_server():
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
            https_address = ('0.0.0.0', HTTPS_PORT)
            httpd_ssl = ThreadingHTTPServer(https_address, DevServerHandler)
            httpd_ssl.socket = ssl_context.wrap_socket(httpd_ssl.socket, server_side=True)
            httpd_ssl.serve_forever()
        except Exception as e:
            print(f"  ⚠️ HTTPS non avviato: {e}")

def run_server():
    watcher_thread = threading.Thread(target=file_watcher, daemon=True)
    watcher_thread.start()

    https_thread = threading.Thread(target=run_https_server, daemon=True)
    https_thread.start()

    server_address = ('0.0.0.0', PORT)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer(server_address, DevServerHandler)
    print("=" * 65)
    print(f"  📡 8BITWAVE MESHCOM - SECURE DEV SERVER (HTTP & HTTPS TLS)")
    print("=" * 65)
    print(f"  HTTP:           http://localhost:{PORT}")
    print(f"  HTTPS (TLS):    https://localhost:{HTTPS_PORT}")
    print(f"  Security:       X-Content-Type-Options, Frame-Options, X-MC Guard")
    print(f"  Live Reload:    ATTIVO")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dev Server arrestato.")

if __name__ == "__main__":
    run_server()
