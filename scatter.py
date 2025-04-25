import numpy as np
import matplotlib.pyplot as plt

# Anchor positions
anchors = [(0, 5), (10, 0), (10, 10)]

# Test points and corresponding errors
points = [(1, 1), (1, 4.5), (1, 9), (4.5, 1), (4.5, 4.5), (4.5, 9), (9, 1), (9, 4.5), (9, 9)]
ble_errors = [6.12, 1.64, 1.25, 0.31, 0.44, 0.42, 0.49, 0.19, 0.57]
wifi_errors = [2.34, 0.38, 2.71, 0.49, 0.42, 0.16, 1.01, 0.14, 1.11]

# Compute average distance to anchors for each point
avg_distances = [
    np.mean([np.hypot(x - ax, y - ay) for ax, ay in anchors])
    for x, y in points
]

# Scatter plot
plt.figure(figsize=(8, 6))
plt.scatter(avg_distances, ble_errors, label="BLE", marker="o")
plt.scatter(avg_distances, wifi_errors, label="Wi‑Fi", marker="s")

# Trend lines
m_ble, b_ble = np.polyfit(avg_distances, ble_errors, 1)
m_wifi, b_wifi = np.polyfit(avg_distances, wifi_errors, 1)
x_line = np.linspace(min(avg_distances), max(avg_distances), 100)
plt.plot(x_line, m_ble * x_line + b_ble, linestyle="--", label="BLE Trend")
plt.plot(x_line, m_wifi * x_line + b_wifi, linestyle="--", label="Wi‑Fi Trend")

plt.xlabel("Average Distance to Anchors (m)")
plt.ylabel("Localization Error (m)")
plt.title("Localization Error vs. Avg. Distance to Anchors")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("scatter_plot.png")
plt.show()
