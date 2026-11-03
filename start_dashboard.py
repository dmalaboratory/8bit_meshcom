#!/usr/bin/env python3
"""
MeshCom Tactical Dashboard - Local Secure Server Launcher
Permette l'esecuzione in Contesto Sicuro (Secure Context: localhost/HTTPS),
sbloccando il supporto per la Web Bluetooth API (navigator.bluetooth) e Web Serial.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import ssl
import subprocess

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path.startswith('/proxy?url='):
            import urllib.parse
            import urllib.request
            target_url = urllib.parse.unquote(self.path[11:])
            try:
                req = urllib.request.Request(target_url, headers={'User-Agent': 'MeshCom-Tactical-Proxy/1.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    content = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', response.headers.get('Content-Type', 'text/html; charset=utf-8'))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', '*')
                    self.end_headers()
                    self.wfile.write(content)
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f"Proxy error: {str(e)}".encode())
            return
        super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def end_headers(self):
        # Header CORS e Permissions Policy per Bluetooth e Web Serial
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Permissions-Policy', 'bluetooth=(self), serial=(self)')
        super().end_headers()

def main():
    os.chdir(DIRECTORY)
    
    use_https = "--https" in sys.argv
    port = 8443 if use_https else PORT

    print("=" * 65)
    print("🛰️  MESHCOM TACTICAL DASHBOARD - SERVER LOCALE")
    print("=" * 65)
    print(f"📁 Directory: {DIRECTORY}")

    server_address = ('', port)
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(server_address, Handler) as httpd:
        if use_https:
            # Genera certificato self-signed se non esiste
            cert_file = os.path.join(DIRECTORY, "cert.pem")
            key_file = os.path.join(DIRECTORY, "key.pem")
            if not os.path.exists(cert_file) or not os.path.exists(key_file):
                print("🔑 Generazione certificato SSL self-signed temporaneo...")
                subprocess.run([
                    "openssl", "req", "-x509", "-newkey", "rsa:2048",
                    "-keyout", key_file, "-out", cert_file,
                    "-days", "365", "-nodes",
                    "-subj", "/CN=localhost"
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            url = f"https://localhost:{port}"
        else:
            url = f"http://localhost:{port}"

        print(f"\n✅ Server attivo su: {url}")
        print("💡 In questo contesto (localhost), Chrome ed Edge ABILITANO")
        print("   la Web Bluetooth API (navigator.bluetooth) e Web Serial.\n")
        print("Premi CTRL+C per arrestare il server.")
        print("-" * 65)

        # Prova ad aprire il browser
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server arrestato.")

if __name__ == "__main__":
    main()
