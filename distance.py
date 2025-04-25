import numpy as np
from statistics import mean
import csv
from datetime import datetime

rssis1, rssis2, rssis3 = [], [], []
with open("/Users/belleconnaught/Desktop/uni/S25/Wireless/wireless-indoor-positioning/logs/rssi_data_1_4-5_ble.csv", newline="") as f:
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
rssi0 = -20  
n = 2.5
anchors = [
  (0.0, 3.048),    # transmitter C 10 ft (3.048m) up
  (3.048, 0.0),   # transmitter B 10 ft (3.048m) to the right
  (0.0,  0.0),    # transmitter A at one corner
]

def rssi_to_distance(rssi, rssi0=rssi0, n=n, d0=d0):
    return d0 * 10 ** ((rssi0 - rssi) / (10 * n))

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
print(f"Estimated position: x={x/10:.2f} m, y={y/10:.2f} m")
