import numpy as np
from statistics import mean
import csv
import math
from datetime import datetime

rssis1, rssis2, rssis3 = [], [], []
with open("/Users/belleconnaught/Desktop/uni/S25/Wireless/wireless-indoor-positioning/logs/rssi_data_1_1_ble.csv", newline="") as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i != 0:
            # row == ["2025-04-24T02:43:46", "-48", "-49", "-59"]
            r1, r2, r3 = map(int, row[1:4])
            rssis1.append(r1)
            rssis2.append(r2)
            rssis3.append(r3)
avg1 = mean(rssis1)
avg2 = mean(rssis2)
avg3 = mean(rssis3)

d0 = 1.0  # reference distance in meters
# tx = 20 # for wifi
tx = 3 # for ble 
gain = 3.4
n = 2.5
anchors = [
  (0.0,  5.0),    # transmitter A is 5m up
  (10.0, 0.0),    # transmitter B is 10m to the right
  (10.0, 10.0),   # transmitter C is 10m up and 10m right
]

def rssi_to_distance(rssi):
    c = 3e8
    freq = 2.4e9
    k_dB = 20 * math.log10(4 * math.pi / c)
    num  = 3 + 3.4 - rssi - 20*math.log10(freq) - k_dB
    return 10 ** (num / 20)

def trilaterate(anchors, distances):
    (x1,y1),(x2,y2),(x3,y3) = anchors
    r1,r2,r3 = distances
    A = np.array([
      [2*(x2-x1), 2*(y2-y1)],
      [2*(x3-x1), 2*(y3-y1)]
    ])
    b = np.array([
      r1*r1 - r2*r2 - x1*x1 + x2*x2 - y1*y1 + y2*y2,
      r1*r1 - r3*r3 - x1*x1 + x3*x3 - y1*y1 + y3*y3
    ])
    return tuple(np.linalg.solve(A, b))

r1 = rssi_to_distance(avg1)
r2 = rssi_to_distance(avg2)
r3 = rssi_to_distance(avg3)
distances = [r1, r2, r3]   
x, y = trilaterate(anchors, distances)
print(f"Estimated position: x={x:.2f} m, y={y:.2f} m")
