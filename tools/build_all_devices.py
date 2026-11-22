#!/usr/bin/env python3
"""
8BitWave MeshCom Multi-Device Firmware Compiler & Packager
Compila e unifica le immagini firmware (.bin e FULL-0x0.bin) per tutti i dispositivi supportati da MeshCom 4.0.
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_ROOT = str(REPO_ROOT / "firmwares")
FIRMWARE_ROOT = "/home/user/MeshCom-Firmware"
DOCS_SOFTWARE_ROOT = "/home/user/Documenti/mhcom/SOFTWARE/firmwares"

DEVICES = {
    # HELTEC AUTOMATION
    "heltec_wifi_lora_32_V3": {
        "name": "Heltec WiFi LoRa 32 V3 / V3.2",
        "category": "Heltec",
        "env": "heltec_wifi_lora_32_V3",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + LoRa SX1262 + OLED 0.96 pollici"
    },
    "heltec_wifi_lora_32_V4": {
        "name": "Heltec WiFi LoRa 32 V4",
        "category": "Heltec",
        "env": "heltec_wifi_lora_32_V4",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "Nuova revisione ESP32-S3 + SX1262 + OLED 0.96 pollici con PMU ottimizzato"
    },
    "heltec_wifi_lora_32_V2": {
        "name": "Heltec WiFi LoRa 32 V2",
        "category": "Heltec",
        "env": "heltec_wifi_lora_32_V2",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "ESP32 Classic + SX1276/78 + OLED 0.96 pollici"
    },
    "heltec_wireless_stick": {
        "name": "Heltec Wireless Stick V3",
        "category": "Heltec",
        "env": "heltec_wireless_stick",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + Mini OLED 0.49 pollici a chiavetta"
    },
    "heltec_wireless_tracker": {
        "name": "Heltec Wireless Tracker",
        "category": "Heltec",
        "env": "heltec_wireless_tracker",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + TFT Colori 0.96 pollici + GPS Integrato"
    },
    "wireless-paper": {
        "name": "Heltec Wireless Paper",
        "category": "Heltec",
        "env": "wireless-paper",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + Schermo E-Paper 2.13 pollici"
    },
    "vision-master-e290": {
        "name": "Heltec Vision Master E290",
        "category": "Heltec",
        "env": "vision-master-e290",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + Schermo E-Paper 2.90 pollici"
    },
    "vision-master-e213": {
        "name": "Heltec Vision Master E213",
        "category": "Heltec",
        "env": "vision-master-e213",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + Schermo E-Paper 2.13 pollici"
    },

    # LILYGO / TTGO
    "ttgo_tbeam": {
        "name": "LilyGO TTGO T-Beam V1.1 / V1.2",
        "category": "LilyGO",
        "env": "ttgo_tbeam",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "ESP32 Classic + SX1276/78 + GPS NEO-6M/8M + Vano 18650"
    },
    "ttgo_tbeam_SX1262": {
        "name": "LilyGO TTGO T-Beam SX1262",
        "category": "LilyGO",
        "env": "ttgo_tbeam_SX1262",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "ESP32 Classic + SX1262 + GPS NEO-6M/8M + Vano 18650"
    },
    "ttgo_tbeam_SX1268": {
        "name": "LilyGO TTGO T-Beam SX1268",
        "category": "LilyGO",
        "env": "ttgo_tbeam_SX1268",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "ESP32 Classic + SX1268 (433MHz) + GPS + Vano 18650"
    },
    "ttgo_tbeam_supreme": {
        "name": "LilyGO T-Beam Supreme",
        "category": "LilyGO",
        "env": "ttgo_tbeam_supreme",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + GNSS Quectel L76K + PMU AXP2101 + RTC"
    },
    "LilyGo_T-Beam-1W": {
        "name": "LilyGO T-Beam 1W",
        "category": "LilyGO",
        "env": "LilyGo_T-Beam-1W",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + LoRa 1 Watt (30dBm) + GPS"
    },
    "ttgo-lora32-v21": {
        "name": "LilyGO TTGO LoRa32 V2.1 (T3 V1.6.1)",
        "category": "LilyGO",
        "env": "ttgo-lora32-v21",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "ESP32 Classic + SX1276/78 + OLED 0.96 pollici"
    },
    "LilyGo_T3_S3_V1_3": {
        "name": "LilyGO T3-S3 V1.3",
        "category": "LilyGO",
        "env": "LilyGo_T3_S3_V1_3",
        "arch": "esp32s3",
        "flash_size": "8MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + OLED / MicroSD"
    },
    "t_deck": {
        "name": "LilyGO T-Deck",
        "category": "LilyGO",
        "env": "t_deck",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + Display IPS TFT 2.8 pollici + Tastiera QWERTY + Trackball"
    },
    "t_deck_plus": {
        "name": "LilyGO T-Deck Plus",
        "category": "LilyGO",
        "env": "t_deck_plus",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + IPS 2.8 pollici + Tastiera QWERTY + GPS Integrato"
    },
    "t_deck_pro": {
        "name": "LilyGO T-Deck Pro",
        "category": "LilyGO",
        "env": "t_deck_pro",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + Tastiera QWERTY + Display + GPS L76K"
    },
    "T-ETH-ELITE_1262": {
        "name": "LilyGO T-ETH-Elite 1262",
        "category": "LilyGO",
        "env": "T-ETH-ELITE_1262",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + Porta Ethernet RJ45 W5500 (Gateway HAMNET/Internet)"
    },
    "LilyGo_T_Connect_Pro": {
        "name": "LilyGO T-Connect Pro",
        "category": "LilyGO",
        "env": "LilyGo_T_Connect_Pro",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 + SX1262 + 8MB PSRAM"
    },

    # EBYTE E22 & DIY GATEWAYS
    "E22-DevKitC": {
        "name": "ESP32 DevKitC + Ebyte E22 (SX1268 1W)",
        "category": "Ebyte_DIY",
        "env": "E22-DevKitC",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "ESP32 + Ebyte E22-400M30S (1 Watt / 30dBm SX1268)"
    },
    "E22_1262-DevKitC": {
        "name": "ESP32 DevKitC + Ebyte E22 (SX1262 1W)",
        "category": "Ebyte_DIY",
        "env": "E22_1262-DevKitC",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "ESP32 + Ebyte E22-900M30S (1 Watt / 30dBm SX1262)"
    },
    "E22_1262_S3-DevKitC-1-N16R8": {
        "name": "ESP32-S3 DevKitC-1 + Ebyte E22 SX1262 1W",
        "category": "Ebyte_DIY",
        "env": "E22_1262_S3-DevKitC-1-N16R8",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 N16R8 (16MB Flash, 8MB PSRAM) + Ebyte E22 SX1262 1 Watt"
    },
    "E22_1268_S3-DevKitC-1-N16R8": {
        "name": "ESP32-S3 DevKitC-1 + Ebyte E22 SX1268 1W",
        "category": "Ebyte_DIY",
        "env": "E22_1268_S3-DevKitC-1-N16R8",
        "arch": "esp32s3",
        "flash_size": "16MB",
        "bootloader_offset": "0x0000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot-s3.bin",
        "desc": "ESP32-S3 N16R8 + Ebyte E22 SX1268 1 Watt (433MHz)"
    },
    "esp32-loraprs-e22": {
        "name": "ESP32 LoRa-APRS E22",
        "category": "LoRa_APRS",
        "env": "esp32-loraprs-e22",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "Scheda dedicata LoRa-APRS con modulo Ebyte E22"
    },
    "esp32-loraprs-ra01": {
        "name": "ESP32 LoRa-APRS RA-01",
        "category": "LoRa_APRS",
        "env": "esp32-loraprs-ra01",
        "arch": "esp32",
        "flash_size": "4MB",
        "bootloader_offset": "0x1000",
        "bootloader": "bootloader.bin",
        "safeboot": "safeboot.bin",
        "desc": "Scheda economica LoRa-APRS con modulo RA-01 SX1278"
    }
}

COMMERCIAL_POPULAR = [
    "heltec_wifi_lora_32_V3",
    "heltec_wifi_lora_32_V4",
    "heltec_wifi_lora_32_V2",
    "heltec_wireless_tracker",
    "wireless-paper",
    "ttgo_tbeam",
    "ttgo_tbeam_SX1262",
    "ttgo_tbeam_supreme",
    "LilyGo_T-Beam-1W",
    "ttgo-lora32-v21",
    "t_deck",
    "t_deck_plus",
    "T-ETH-ELITE_1262",
    "E22-DevKitC"
]

def check_target_built(dev_key):
    info = DEVICES[dev_key]
    build_dir = Path(FIRMWARE_ROOT) / ".pio" / "build" / info["env"]
    firmware_bin = build_dir / "firmware.bin"
    return firmware_bin.exists()

def build_target(dev_key):
    info = DEVICES[dev_key]
    print(f"\n=======================================================")
    print(f" [COMPILAZIONE] Inizio compilazione per: {info['name']}")
    print(f" Target PlatformIO: {info['env']} ({info['arch']})")
    print(f"=======================================================")
    
    cmd = ["pio", "run", "-e", info["env"]]
    res = subprocess.run(cmd, cwd=FIRMWARE_ROOT)
    if res.returncode != 0:
        print(f"❌ ERRORE: Compilazione fallita per {info['env']}")
        return False

    return merge_and_package(dev_key)

def merge_and_package(dev_key):
    info = DEVICES[dev_key]
    build_dir = Path(FIRMWARE_ROOT) / ".pio" / "build" / info["env"]
    firmware_bin = build_dir / "firmware.bin"
    bootloader_bin = build_dir / info["bootloader"]
    partitions_bin = build_dir / "partitions.bin"
    otadata_bin = Path(FIRMWARE_ROOT) / "otadata.bin"
    safeboot_bin = Path(FIRMWARE_ROOT) / info["safeboot"]

    if not firmware_bin.exists():
        print(f"❌ Errore: {firmware_bin} non trovato!")
        return False

    # Output directory
    cat_dir = Path(OUTPUT_ROOT) / info["category"] / dev_key
    cat_dir.mkdir(parents=True, exist_ok=True)

    out_firmware = cat_dir / f"8BitWave-MeshCom-{dev_key}-firmware.bin"
    out_full = cat_dir / f"8BitWave-MeshCom-{dev_key}-FULL-0x0.bin"

    # 1. Copy OTA firmware
    shutil.copyfile(firmware_bin, out_firmware)
    print(f"✅ Firmware OTA pronto: {out_firmware} ({out_firmware.stat().st_size} bytes)")

    # 2. Merge into FULL-0x0.bin
    esptool_cmd = [
        "python3", "-m", "esptool",
        "--chip", info["arch"],
        "merge_bin",
        "-o", str(out_full),
        "--flash_mode", "dio",
        "--flash_size", info["flash_size"],
        info["bootloader_offset"], str(bootloader_bin),
        "0x8000", str(partitions_bin),
        "0xe000", str(otadata_bin),
        "0x10000", str(safeboot_bin),
        "0xc0000", str(firmware_bin)
    ]

    print(f"📦 Generazione immagine unificata 0x0 ({info['arch']})...")
    res = subprocess.run(esptool_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Errore merge_bin: {res.stderr}")
        return False

    print(f"🎉 SUCCESSO! Immagine completa pronta: {out_full} ({out_full.stat().st_size} bytes)")

    # Sincronizza anche nella cartella SOFTWARE se presente
    docs_cat_dir = Path(DOCS_SOFTWARE_ROOT) / info["category"] / dev_key
    try:
        docs_cat_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out_full, docs_cat_dir / out_full.name)
        shutil.copyfile(out_firmware, docs_cat_dir / out_firmware.name)
        print(f"📋 Copia sincronizzata in {docs_cat_dir}")
    except Exception as e:
        pass

    return True

def list_devices():
    print("\n📋 DISPOSITIVI SUPPORTATI DA 8BITWAVE / MESHCOM 4.0:")
    print("-" * 90)
    print(f"{'Chiave Target':30} | {'Categoria':12} | {'MCU':8} | {'Stato':10} | {'Descrizione'}")
    print("-" * 90)
    for k, v in DEVICES.items():
        status = "✅ PRONTO" if check_target_built(k) else "⏳ DA COMPILARE"
        print(f"{k:30} | {v['category']:12} | {v['arch']:8} | {status:10} | {v['name']}")
    print("-" * 90)

def main():
    parser = argparse.ArgumentParser(description="MeshCom Multi-Device Compiler")
    parser.add_argument("--list", action="store_true", help="Elenca tutti i dispositivi e lo stato di compilazione")
    parser.add_argument("--target", type=str, help="Compila uno specifico dispositivo per nome chiave")
    parser.add_argument("--group", type=str, choices=["popular", "all", "heltec", "lilygo", "ebyte"], help="Compila un gruppo di dispositivi")
    args = parser.parse_args()

    if args.list or len(sys.argv) == 1:
        list_devices()
        return

    if args.target:
        if args.target not in DEVICES:
            print(f"❌ Dispositivo '{args.target}' non riconosciuto! Usa --list per visualizzare la lista.")
            sys.exit(1)
        build_target(args.target)
        return

    if args.group:
        targets = []
        if args.group == "popular":
            targets = COMMERCIAL_POPULAR
        elif args.group == "all":
            targets = list(DEVICES.keys())
        elif args.group == "heltec":
            targets = [k for k, v in DEVICES.items() if v["category"] == "Heltec"]
        elif args.group == "lilygo":
            targets = [k for k, v in DEVICES.items() if v["category"] == "LilyGO"]
        elif args.group == "ebyte":
            targets = [k for k, v in DEVICES.items() if v["category"] == "Ebyte_DIY"]

        print(f"🚀 Avvio compilazione batch gruppo '{args.group}' ({len(targets)} dispositivi)...")
        success = 0
        for t in targets:
            ok = build_target(t)
            if ok:
                success += 1
        print(f"\n🏁 Completato! {success}/{len(targets)} firmware compilati e impacchettati con successo.")

if __name__ == "__main__":
    main()
