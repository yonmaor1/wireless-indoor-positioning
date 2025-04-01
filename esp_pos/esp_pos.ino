#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "ssid"; // replace
const char* password = "pw"; // replace

WiFiUDP udp;
const int udpPort = 12345;
char incomingPacket[255];
IPAddress computerIP(192, 168, 1, 100); // replace with the computer's IP address

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
  udp.begin(udpPort);
}

void loop() {
  // Measure RSSI
  int rssi = WiFi.RSSI();

  // Send RSSI to the computer
  String message = String(WiFi.localIP()) + "," + String(rssi);
  udp.beginPacket(computerIP, udpPort);
  udp.print(message);
  udp.endPacket();

  delay(1000);
}