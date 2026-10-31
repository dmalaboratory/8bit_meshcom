#!/usr/bin/env python3
"""
MeshCom Bluetooth LE Direct Connection Tester per MC-a498 IU0TGU-10
"""

import asyncio
import sys
from bleak import BleakScanner, BleakClient

NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # Client Write -> Node
NUS_TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # Node Notify -> Client

TARGET_PATTERNS = ["a498", "iu0tgu", "mc-a498", "iu0tgu-10"]

def notification_handler(sender, data):
    print(f"\n[RX BLE] Ricevuti {len(data)} byte dal nodo:")
    if len(data) > 0:
        msg_type = data[0]
        try:
            text = data[1:].decode("utf-8", errors="replace")
            if msg_type == 0x44:
                print(f"  📊 Telemetria JSON (0x44): {text}")
            elif msg_type == 0x40:
                print(f"  💬 Messaggio Mesh (0x40): {text}")
            elif msg_type == 0x91:
                print(f"  📡 Lista MHeard (0x91): {text}")
            else:
                print(f"  📝 Frame (0x{msg_type:02X}): {text}")
        except Exception:
            print(f"  Hex: {data.hex()}")

async def main():
    custom_target = sys.argv[1].lower() if len(sys.argv) > 1 else None
    targets = [custom_target] if custom_target else TARGET_PATTERNS

    print("=" * 65)
    print("🛰️  TEST CONNESSIONE BLUETOOTH MESHCOM")
    print(f"🎯 Target identificato: MC-a498 IU0TGU-10")
    print("=" * 65)
    print("⏳ In ascolto del broadcast BLE... (premi CTRL+C per annullare)")
    print("⚠️  IMPORTANTE: Assicurati che l'app MeshCom sullo smartphone sia")
    print("   chiusa o con Bluetooth spento, altrimenti l'ESP32 non trasmette!\n")

    found_device = None

    def on_detect(device, adv):
        nonlocal found_device
        name = (device.name or adv.local_name or "").lower()
        addr = device.address.lower()
        
        matches = any(p in name or p in addr.replace(":", "") for p in targets)
        if matches and not found_device:
            print(f"\n🎉 TROVATO NODO! {device.name} [{device.address}]")
            print(f"📶 Livello segnale RSSI: {adv.rssi} dBm")
            found_device = device

    scanner = BleakScanner(detection_callback=on_detect)
    await scanner.start()

    # Loop di ascolto continuo (fino a 45 secondi)
    for sec in range(45):
        if found_device:
            break
        await asyncio.sleep(1)
        if sec % 5 == 0 and sec > 0:
            print(f"   [{sec}s] In attesa del rilascio/annuncio da parte del nodo...")

    await scanner.stop()

    if not found_device:
        print("\n\n❌ Il nodo non è stato rilevato nei 45 secondi.")
        print("Verifica che:")
        print("1. L'ESP32 non sia al momento collegato all'app del telefono.")
        print("2. Il nodo sia acceso entro 3-5 metri dal PC.")
        return

    print(f"\n🔗 Connessione GATT a {found_device.address}...")
    try:
        async with BleakClient(found_device.address, timeout=12.0) as client:
            print(f"✅ Connesso con successo al GATT Server!")

            # Sottoscrizione notifiche
            print("📡 Abilitazione notifiche Nordic UART...")
            await client.start_notify(NUS_TX_CHAR_UUID, notification_handler)

            # Invio Hello Handshake 0x10
            print("🤝 Invio Hello Handshake MeshCom (0x10)...")
            hello_frame = bytearray([0x04, 0x10, 0x20, 0x30])
            await client.write_gatt_char(NUS_RX_CHAR_UUID, hello_frame)

            # Invio Sync Timestamp 0x20
            now_sec = int(asyncio.get_event_loop().time())
            time_frame = bytearray(6)
            time_frame[0] = 0x06
            time_frame[1] = 0x20
            time_frame[2:6] = now_sec.to_bytes(4, byteorder='little')
            print("⏱️  Invio sincronizzazione orologio UTC (0x20)...")
            await client.write_gatt_char(NUS_RX_CHAR_UUID, time_frame)

            print("\n" + "=" * 65)
            print("🟢 LINK BLUETOOTH CON IU0TGU-10 OPERATIVO E STABILITO!")
            print("=" * 65)
            print("In ascolto della telemetria dal nodo per 15 secondi...")
            await asyncio.sleep(15)

            print("\n✨ Test terminato con successo.")

    except Exception as e:
        print(f"\n❌ Errore durante la sessione GATT: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrotto dall'utente.")
