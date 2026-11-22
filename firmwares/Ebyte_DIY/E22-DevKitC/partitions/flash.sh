#!/bin/bash
set -e

PORT="/dev/ttyUSB0"
if [ ! -z "$1" ]; then
  PORT="$1"
fi

echo "=================================================================="
echo "  🚀 8BITWAVE MESHCOM - ESP32 FLASH UTILITY"
echo "  Firmware Edition by IU0TGU (Generic Distribution)"
echo "=================================================================="
echo "Porta: $PORT"
echo "Baudrate: 460800"
echo "=================================================================="
echo ""
echo "💡 Se vedi 'Connecting...', tieni premuto BOOT e dai un tocco a EN."
echo ""

python3 -m esptool \
  --chip esp32 \
  --port "$PORT" \
  --baud 460800 \
  --before default-reset \
  --after hard-reset \
  write-flash \
  -z \
  --flash-mode dout \
  --flash-freq 40m \
  --flash-size 4MB \
  0x0 8BitWave-MeshCom-FULL-0x0.bin

echo ""
echo "=================================================================="
echo "  ✅ FLASH COMPLETATO CON SUCCESSO AL 100%!"
echo "=================================================================="
