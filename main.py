import socket
import numpy as np

UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 12345

def process_rssi(rssi_values):
    """
    Process RSSI values by filtering and averaging.
    
    Args:
        rssi_values (list of list of int): RSSI values from multiple access points.
    
    Returns:
        list of float: Averaged RSSI values for each access point.
    """
    filtered_rssi = []
    for ap_values in rssi_values:
        # Filter out invalid RSSI values (e.g., -100 or lower)
        valid_values = [value for value in ap_values if value > -100]
        if valid_values:
            # Calculate the average of valid RSSI values
            avg_rssi = np.mean(valid_values)
        else:
            avg_rssi = -100  # Default value for no valid RSSI
        filtered_rssi.append(avg_rssi)
    return filtered_rssi

def calculate_position(rssi_values, ap_locations):
    """
    Calculate the estimated position based on RSSI values and access point locations.
    
    Args:
        rssi_values (list of float): Averaged RSSI values for each access point.
        ap_locations (list of tuple): Coordinates of access points [(x1, y1), (x2, y2), ...].
    
    Returns:
        tuple: Estimated position (x, y).
    """
    weights = []
    for rssi in rssi_values:
        # Convert RSSI to a weight (higher RSSI -> higher weight)
        weight = 10 ** (rssi / 10.0)
        weights.append(weight)
    
    # Normalize weights
    total_weight = sum(weights)
    if total_weight == 0:
        return (0, 0)  # Default position if no valid RSSI
    
    weights = [w / total_weight for w in weights]
    
    # Calculate weighted average position
    x = sum(w * loc[0] for w, loc in zip(weights, ap_locations))
    y = sum(w * loc[1] for w, loc in zip(weights, ap_locations))
    
    return (x, y)


def process_rssi_data(data):
    # Parse the incoming data
    try:
        ip, rssi = data.split(",")
        rssi = int(rssi)
        print(f"Received RSSI {rssi} from {ip}")
        # TODO : implement the above functions
    except ValueError:
        print("Invalid data received")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        process_rssi_data(data.decode())

if __name__ == "__main__":
    main()