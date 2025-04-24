#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_gap_ble_api.h"

#define DEVICE_NAME "ESP32-1"
const uint16_t BLE_MFG_ID = 0x1234;
const float POS_X = 0.5;
const float POS_Y = 4.0;
const int ble_tx_power = 3; // 0-9 (ESP_BLE_PWR_TYPE_ADV)

// BLE Event Handler
void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param) {
  if (event == ESP_GAP_BLE_ADV_START_COMPLETE_EVT) {
    if(param->adv_start_cmpl.status != ESP_OK) {
      Serial.printf("Adv start failed: %s\n", esp_err_to_name(param->adv_start_cmpl.status));
    } else {
      Serial.println("BLE Advertising Started");
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Initializing BLE...");

  // 1. Release classic BT memory
  esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT);

  // 2. Initialize BLE controller
  esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
  if(esp_bt_controller_init(&bt_cfg) != ESP_OK) {
    Serial.println("BT Controller init failed");
    return;
  }

  // 3. Enable BLE controller
  if(esp_bt_controller_enable(ESP_BT_MODE_BLE) != ESP_OK) {
    Serial.println("BT Controller enable failed");
    return;
  }

  // 4. Initialize Bluedroid stack
  if(esp_bluedroid_init() != ESP_OK) {
    Serial.println("Bluedroid init failed");
    return;
  }

  // 5. Enable Bluedroid stack
  if(esp_bluedroid_enable() != ESP_OK) {
    Serial.println("Bluedroid enable failed");
    return;
  }

  // 6. Register GAP callback (MUST DO THIS BEFORE ADV)
  esp_ble_gap_register_callback(gap_event_handler);

  // 7. Set TX Power
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, (esp_power_level_t)ble_tx_power);

  // 8. Configure advertising data
  uint8_t mfgData[11];
  memcpy(&mfgData[0], &BLE_MFG_ID, 2);
  mfgData[2] = 1; // Node number
  memcpy(&mfgData[3], &POS_X, 4);
  memcpy(&mfgData[7], &POS_Y, 4);

  if(esp_ble_gap_config_adv_data_raw(mfgData, sizeof(mfgData)) != ESP_OK) {
    Serial.println("Config raw adv data failed");
    return;
  }

  // 9. Start advertising
  esp_ble_adv_params_t adv_params = {
    .adv_int_min = 0x20,
    .adv_int_max = 0x40,
    .adv_type = ADV_TYPE_IND,
    .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
    .channel_map = ADV_CHNL_ALL,
    .adv_filter_policy = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
  };

  Serial.println("Starting BLE Advertising...");
  esp_ble_gap_start_advertising(&adv_params);
}

void loop() {
  // Just keep advertising - no need to restart
  delay(1000);
}
