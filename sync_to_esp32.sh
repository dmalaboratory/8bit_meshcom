#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  8BITWAVE MESHCOM - SYNC WEBGUI TO ESP32 FIRMWARE & APK"
echo "=========================================================="

HTML_SRC="/home/user/8bit_meshcom/index.html"
FW_DIR="/home/user/MeshCom-Firmware"
HEADER_DST="$FW_DIR/src/web_functions/dashboard_html.h"
DOCS_WEBGUI="/home/user/Documenti/mhcom/SOFTWARE/webgui/index.html"
ANDROID_ASSETS="/home/user/8bitwave_android/app/src/main/assets/index.html"

if [ ! -f "$HTML_SRC" ]; then
    echo "❌ Errore: $HTML_SRC non trovato!"
    exit 1
fi

echo "1. 🔄 Sincronizzazione index.html e assets con Documenti e Android assets..."
cp "$HTML_SRC" "$DOCS_WEBGUI"
cp "$HTML_SRC" "$ANDROID_ASSETS"
cp "/home/user/8bit_meshcom/leaflet.js" "/home/user/8bitwave_android/app/src/main/assets/leaflet.js"
cp "/home/user/8bit_meshcom/leaflet.css" "/home/user/8bitwave_android/app/src/main/assets/leaflet.css"

echo "2. 🗜️ Compressione GZIP (livello 9) e generazione $HEADER_DST..."
python3 - << 'EOF'
import gzip

html_path = "/home/user/8bit_meshcom/index.html"
with open(html_path, "rb") as f:
    data = f.read()

gz_data = gzip.compress(data, compresslevel=9)
gz_len = len(gz_data)

h_path = "/home/user/MeshCom-Firmware/src/web_functions/dashboard_html.h"
with open(h_path, "w") as f:
    f.write("#include <Arduino.h>\n")
    f.write("const unsigned char _tmp_dashboard_html_gz[] = {\n")
    for i in range(0, gz_len, 12):
        chunk = gz_data[i:i+12]
        line = "  " + ", ".join(f"0x{b:02x}" for b in chunk) + ",\n"
        f.write(line)
    f.write("};\n")
    f.write(f"const unsigned int _tmp_dashboard_html_gz_len = {gz_len};\n")

print(f"   -> Dimensione HTML: {len(data):,} bytes")
print(f"   -> Dimensione GZIP Flash: {gz_len:,} bytes")
EOF

echo "3. ⚙️ Compilazione Firmware PlatformIO (E22-DevKitC - DOUT 40MHz)..."
cd "$FW_DIR"
pio run -e E22-DevKitC

echo "4. 📦 Copia firmware.bin nelle cartelle di distribuzione e bundle..."
cp "$FW_DIR/.pio/build/E22-DevKitC/firmware.bin" "/home/user/8bit_meshcom/firmware.bin"
cp "$FW_DIR/.pio/build/E22-DevKitC/firmware.bin" "/home/user/Documenti/mhcom/SOFTWARE/firmware_custom/firmware.bin"
cp "$FW_DIR/.pio/build/E22-DevKitC/firmware.bin" "/home/user/8bit_meshcom/firmware_bundle/firmware.bin"

echo "4b. 🧩 Rigenerazione immagine unificata 8BitWave-MeshCom-FULL-0x0.bin..."
cd /home/user/8bit_meshcom/firmware_bundle
python3 -m esptool --chip esp32 merge-bin \
  --output 8BitWave-MeshCom-FULL-0x0.bin \
  --flash-mode dout \
  --flash-freq 40m \
  --flash-size 4MB \
  0x1000 bootloader.bin \
  0x8000 partitions.bin \
  0xe000 otadata.bin \
  0x10000 safeboot.bin \
  0xc0000 firmware.bin
cp 8BitWave-MeshCom-FULL-0x0.bin /home/user/8bit_meshcom/
cp 8BitWave-MeshCom-FULL-0x0.bin /home/user/Documenti/mhcom/SOFTWARE/firmware_custom/

echo "5. 📱 Ricompilazione pacchetto Android APK (Release Ottimizzato & R8)..."
cd /home/user/8bitwave_android
export JAVA_HOME=/home/user/.jdk17
export ANDROID_HOME=/home/user/Android/Sdk
export PATH=$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/bin:$PATH
./gradlew assembleRelease -q
cp app/build/outputs/apk/release/app-release.apk /home/user/8bit_meshcom/8BitWave-MeshCom.apk
cp app/build/outputs/apk/release/app-release.apk /home/user/Documenti/mhcom/SOFTWARE/8BitWave-MeshCom.apk

echo "----------------------------------------------------------"
echo "✅ SINCRONIZZAZIONE COMPLETATA CON SUCCESSO!"
echo "   - WebGUI flash: aggiornata"
echo "   - firmware.bin: pronto per il flash USB"
echo "   - 8BitWave-MeshCom.apk: generato"
echo "=========================================================="
