import os
from datetime import datetime
import struct
import math
import time
from scapy.all import Dot11, sniff
from bleak import BleakScanner as Scanner

class PositionCalculator:
    def __init__(self, tech_type):
        self.nodes = {
            '1': {'x': 0.5, 'y': 4.0},
            '2': {'x': 7.5, 'y': 7.5},
            '3': {'x': 8.0, 'y': 1.0}
        }
        # Technology-specific parameters (from paper)
        self.pl0 = 35 if tech_type == 'wifi' else 40
        self.n = 2.7 if tech_type == 'wifi' else 3.2
        self.xσ = 4 if tech_type == 'wifi' else 5

    def rssi_to_distance(self, rssi, tx_power):
        return 10 ** ((tx_power - rssi - self.pl0 - self.xσ) / (10 * self.n))

    def trilaterate(self, distances):
        # Implementation from paper's equations
        ap1 = self.nodes['1']
        ap2 = self.nodes['2']
        ap3 = self.nodes['3']
        
        d1 = distances['1']
        d2 = distances['2']
        d3 = distances['3']

        x = (ap3['x']**2 + d1**2 - d2**2) / (2 * ap3['x'])
        y = (ap3['x']**2 + ap3['y']**2 + d1**2 - d2**2 - 2 * ap3['x'] * x) / (2 * ap3['y'])
        return (x, y)

def scan_wifi():
    devices = {}
    def packet_handler(pkt):
        if pkt.haslayer(Dot11) and pkt.type == 0 and pkt.subtype == 8:
            ssid = pkt[Dot11].info.decode()
            if ssid.startswith("POS_WIFI_"):
                node_id = ssid.split('_')[-1][-1]  # Last character
                devices[node_id] = pkt.dBm_AntSignal
    sniff(iface="en0", prn=packet_handler, timeout=5, store=0)
    return devices

def scan_ble():
    scanner = Scanner()
    devices = scanner.scan(5.0)
    ble_devices = {}
    
    for dev in devices:
        for (adtype, desc, value) in dev.getScanData():
            if adtype == 0xff and value.startswith("1234"):
                data = bytes.fromhex(value[4:])  # Skip company ID
                node_id = str(data[0])
                x = struct.unpack('<f', data[1:5])[0]
                y = struct.unpack('<f', data[5:9])[0]
                ble_devices[node_id] = dev.rssi
    return ble_devices

if __name__ == "__main__":

    # Data logging
    log_dir = os.path.join("log", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(log_dir, exist_ok=True)

    wifi_log_path = os.path.join(log_dir, "wifi.log")
    ble_log_path = os.path.join(log_dir, "ble.log")

    wifi_log_file = open(wifi_log_path, "a")
    ble_log_file = open(ble_log_path, "a")

    # Setup

    wifi_calculator = PositionCalculator('wifi')
    ble_calculator = PositionCalculator('ble')
    
    try:
        while True:
            print("\n=== New Scan ===")
            
            # WiFi Positioning
            wifi_measurements = scan_wifi()
            if len(wifi_measurements) >= 3:
                wifi_distances = {
                    n: wifi_calculator.rssi_to_distance(rssi, 20)
                    for n, rssi in wifi_measurements.items()
                }
                wifi_pos = wifi_calculator.trilaterate(wifi_distances)
                print(f"WiFi Position: X={wifi_pos[0]:.2f}m, Y={wifi_pos[1]:.2f}m")
                wifi_log_file.write(f"{datetime.now().isoformat()} - {wifi_pos[0]:.2f} - {wifi_pos[1]:.2f}\n")
            
            # BLE Positioning
            ble_measurements = scan_ble()
            if len(ble_measurements) >= 3:
                ble_distances = {
                    n: ble_calculator.rssi_to_distance(rssi, 3)
                    for n, rssi in ble_measurements.items()
                }
                ble_pos = ble_calculator.trilaterate(ble_distances)
                print(f"BLE Position:  X={ble_pos[0]:.2f}m, Y={ble_pos[1]:.2f}m")
                ble_log_file.write(f"{datetime.now().isoformat()} - {ble_pos[0]:.2f} - {ble_pos[1]:.2f}\n")
            
            time.sleep(2)
    finally:
        wifi_log_file.close()
        ble_log_file.close()
        print("Logs saved.")