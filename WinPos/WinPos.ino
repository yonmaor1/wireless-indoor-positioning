#include <WiFi.h>
#include <BLEDevice.h>
#include <BLEAdvertising.h>

// Configuration
#define NODE_ID "ESP32-1"
#define WIFI_SSID "POS_WIFI_"
#define BLE_MFG_ID 0x1234
#define POS_X 0.5f
#define POS_Y 4.0f

// Transmit Power Control
int wifi_tx_power = 20;
int ble_tx_power = 3;

void setup() {
  Serial.begin(115200);
  
  // WiFi Setup
  WiFi.mode(WIFI_AP);
  WiFi.softAP(String(WIFI_SSID + String(NODE_ID)).c_str());
  esp_wifi_set_max_tx_power(wifi_tx_power * 4);

  // BLE Setup with encoded position + node ID
  BLEDevice::init(String("BLE_" + String(NODE_ID)).c_str());
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  
  uint8_t mfgData[11];
  memcpy(&mfgData[0], &BLE_MFG_ID, 2);
  mfgData[2] = (uint8_t)atoi(&NODE_ID[5]); // Extract node number (1/2/3)
  memcpy(&mfgData[3], &POS_X, 4);
  memcpy(&mfgData[7], &POS_Y, 4);
  
  BLEAdvertisementData advertisementData;
  advertisementData.setManufacturerData(String(mfgData, 11));
  pAdvertising->setAdvertisementData(advertisementData);
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, (esp_power_level_t)ble_tx_power);
  pAdvertising->start();
}

void loop() { delay(2000); }