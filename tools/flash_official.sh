#!/bin/bash
set -e

echo "=================================================================="
echo "  🚀 8BITWAVE MESHCOM - ESP32 FLASH TOOL (tool-esptoolpy 4.11.0)"
echo "=================================================================="
echo "Porta: /dev/ttyUSB0"
echo "Baudrate: 460800"
echo "Flash Mode: DOUT 40MHz"
echo "=================================================================="

BOOTLOADER="/home/user/MeshCom-Firmware/.pio/build/E22-DevKitC/bootloader.bin"
PARTITIONS="/home/user/MeshCom-Firmware/.pio/build/E22-DevKitC/partitions.bin"
OTADATA="/home/user/MeshCom-Firmware/otadata.bin"
SAFEBOOT="/home/user/MeshCom-Firmware/safeboot.bin"
FIRMWARE="/home/user/MeshCom-Firmware/.pio/build/E22-DevKitC/firmware.bin"

/home/user/.local/bin/pio pkg exec -p "tool-esptoolpy" -- esptool.py \
  --chip esp32 \
  --port /dev/ttyUSB0 \
  -b 460800 \
  --connect-attempts 20 \
  --before default_reset \
  --after hard_reset \
  write_flash \
  -z \
  --flash_mode dout \
  --flash_freq 40m \
  --flash_size 4MB \
  0x1000 "$BOOTLOADER" \
  0x8000 "$PARTITIONS" \
  0xe000 "$OTADATA" \
  0x10000 "$SAFEBOOT" \
  0xc0000 "$FIRMWARE"

echo "=================================================================="
echo "  ✅ FLASH SCRITTO E VERIFICATO CON SUCCESSO AL 100%!"
echo "=================================================================="
