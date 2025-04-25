import csv, math, numpy as np
from statistics import mean

rssis = [[], [], []]
with open("logs/rssi_data_9_9_wifi.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for r in reader:
        for i,val in enumerate(r[1:4]):
            rssis[i].append(int(val))
avg1, avg2, avg3 = map(mean, rssis)

# true distances to anchors/transmitters
anchors = [(0,5), (10,0), (10,10)]
test_pt = (9,9)
true_ds = [math.hypot(test_pt[0]-ax, test_pt[1]-ay)
           for ax,ay in anchors]

# avg = np.array([avg1, avg2, avg3])
# d   = np.array(true_ds)
# A = np.vstack([np.ones_like(d), -10*np.log10(d)]).T
# rssi0, n = np.linalg.lstsq(A, avg, rcond=None)[0]

# def ble_dist(rssi):
#     return 1.0 * 10**((rssi0 - rssi)/(10*n))

avg = np.array([avg1, avg2, avg3])
d = np.array(true_ds)
A = np.vstack([np.ones_like(d), -10 * np.log10(d)]).T
rssi0_wifi, n_wifi = np.linalg.lstsq(A, avg, rcond=None)[0]

# --- 4) RSSI → distance conversion ---
def wifi_dist(rssi):
    return 10 ** ((rssi0_wifi - rssi) / (10 * n_wifi))

d1, d2, d3 = map(wifi_dist, (avg1, avg2, avg3))

def trilaterate(anchors, ds):
    (x1,y1),(x2,y2),(x3,y3) = anchors
    r1,r2,r3 = ds
    A = np.array([[2*(x2-x1),2*(y2-y1)],
                  [2*(x3-x1),2*(y3-y1)]])
    b = np.array([
        r1*r1 - r2*r2 - x1*x1 + x2*x2 - y1*y1 + y2*y2,
        r1*r1 - r3*r3 - x1*x1 + x3*x3 - y1*y1 + y3*y3
    ])
    return tuple(np.linalg.solve(A,b))

x_est, y_est = trilaterate(anchors, [d1,d2,d3])
print(f"Estimated position: x={x_est:.2f} m, y={y_est:.2f} m")
