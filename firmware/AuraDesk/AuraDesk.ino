#include <Arduino.h>
#include <esp_display_panel.hpp>
#include <lvgl.h>
#include <esp_ota_ops.h>
#include <esp_heap_caps.h>
#include <esp_psram.h>
#include <mbedtls/sha256.h>
#include "lvgl_v8_port.h"
#include "app_service.h"
#include "ui.h"
#include "firmware_version.h"

using namespace esp_panel::drivers;
using namespace esp_panel::board;
Board *auraBoard;
bool boardHealthy, updateConfirmed;
bool startupFailureHandled;
uint32_t lastUpdate;
String serialLine;
uint8_t appliedBrightness=255;
uint32_t lastDisplayIdle;

// Keep Arduino from accepting a new image before display, storage and services start.
extern "C" bool verifyRollbackLater(void) { return true; }

void handleStartupFailure() {
  if(startupFailureHandled) return; startupFailureHandled=true;
  esp_ota_img_states_t imageState;
  const esp_partition_t *running=esp_ota_get_running_partition();
  if(esp_ota_get_state_partition(running,&imageState)==ESP_OK && imageState==ESP_OTA_IMG_PENDING_VERIFY) {
    Serial.println("AURA_HEALTH failed; rolling back pending update");
    esp_ota_mark_app_invalid_rollback_and_reboot();
  }
  Serial.println("AURA_FATAL startup unavailable; serial recovery remains available");
}

void printStatus() {
  UiSnapshot s; if(!app_get_snapshot(s)) return;
  Serial.printf("AURA_STATUS version=" AURA_VERSION " uptime=%lu heap=%lu min_heap=%lu psram=%lu wifi=%d internet=%d time=%d weather=%d air=%d rates=%d board=%d always_on=%d backlight=%d idle_ms=%lu dimmed=%d\n",
    (unsigned long)s.uptimeSeconds,(unsigned long)s.freeHeap,(unsigned long)s.minimumHeap,(unsigned long)s.psramBytes,
    s.wifiConnected,s.internetAvailable,s.timeSynced,s.weatherValid,s.airValid,s.ratesValid,boardHealthy,
    s.alwaysOnDisplay,auraBoard->getBacklight()->getBrightness(),(unsigned long)lastDisplayIdle,
    auraBoard->getBacklight()->getBrightness()<s.brightness);
}
void captureScreen() {
  lvgl_port_lock(-1);
  const size_t length=lv_snapshot_buf_size_needed(lv_scr_act(),LV_IMG_CF_TRUE_COLOR);
  auto *buffer=static_cast<uint8_t *>(heap_caps_malloc(length,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
  lv_img_dsc_t descriptor{};
  const bool ok=buffer && lv_snapshot_take_to_buf(lv_scr_act(),LV_IMG_CF_TRUE_COLOR,&descriptor,buffer,length)==LV_RES_OK;
  lvgl_port_unlock();
  if(ok) {
    uint8_t digest[32]; char hash[65];
    mbedtls_sha256(buffer,descriptor.data_size,digest,0);
    for(unsigned i=0;i<32;i++) snprintf(hash+i*2,3,"%02x",digest[i]);
    esp_log_level_set("*",ESP_LOG_NONE);
    Serial.printf("\nAURA_SCREEN %u %u %lu %s\n",descriptor.header.w,descriptor.header.h,(unsigned long)descriptor.data_size,hash);
    Serial.write(buffer,descriptor.data_size); Serial.flush(); Serial.print("\nAURA_SCREEN_END\n");
    esp_log_level_set("*",ESP_LOG_WARN);
  } else Serial.println("AURA_ERROR screenshot unavailable");
  if(buffer) heap_caps_free(buffer);
}
void command(const String &line) {
  if(line=="info"||line=="status"||line=="heap"||line=="uptime"||line=="version") printStatus();
  else if(line=="help") Serial.println("help info status heap uptime version screenshot wifi-scan refresh screen:<page> reboot:confirm");
  else if(line=="screenshot") captureScreen();
  else if(line=="wifi-scan") app_dispatch(UiAction::ScanWifi);
  else if(line=="refresh") app_dispatch(UiAction::RefreshData);
  else if(line=="reboot:confirm") app_dispatch(UiAction::Reboot);
  else if(line.startsWith("screen:")) { lvgl_port_lock(-1); ui_show_page(line.substring(7).toInt()); lvgl_port_unlock(); }
  else if(!line.isEmpty()) Serial.println("AURA_ERROR unknown command; enter help");
}
void setup() {
  Serial.begin(115200); Serial.setDebugOutput(false); delay(100);
  esp_log_level_set("wifi",ESP_LOG_WARN); esp_log_level_set("httpd",ESP_LOG_WARN);
  Serial.println("AURA_BOOT firmware=" AURA_VERSION " board=Jingcai-4848S040C target=ESP32-S3");
  Serial.printf("AURA_MEMORY physical_psram=%lu usable_psram=%lu flash=%lu sdk=%s\n",(unsigned long)esp_psram_get_size(),(unsigned long)ESP.getPsramSize(),(unsigned long)ESP.getFlashChipSize(),ESP.getSdkVersion());
  if(!psramFound() || esp_psram_get_size()<0x800000) { Serial.println("AURA_FATAL required PSRAM unavailable"); return; }
  auraBoard=new Board();
  if(!auraBoard->init()) { Serial.println("AURA_FATAL board init"); return; }
  auto lcd=auraBoard->getLCD(); lcd->configFrameBufferNumber(LVGL_PORT_DISP_BUFFER_NUM);
  static_cast<BusRGB *>(lcd->getBus())->configRGB_BounceBufferSize(480*10);
  if(!auraBoard->begin() || !lvgl_port_init(lcd,auraBoard->getTouch())) { Serial.println("AURA_FATAL display/touch"); return; }
  if(!app_service_init()) { Serial.println("AURA_FATAL services allocation"); return; }
  lvgl_port_lock(-1); ui_init(app_dispatch); lvgl_port_unlock();
  boardHealthy=true; Serial.println("AURA_READY display=480x480 touch=GT911 ui=Horizon");
}
void loop() {
  if(!boardHealthy) { if(millis()>10000) handleStartupFailure(); delay(100); return; }
  while(Serial.available()) { char c=Serial.read(); if(c=='\n'||c=='\r') { command(serialLine); serialLine=""; }
    else if(c>=32 && serialLine.length()<128) serialLine+=c; }
  const uint32_t now=millis();
  if(now-lastUpdate>=1000) {
    lastUpdate=now; app_service_tick(); UiSnapshot s; app_get_snapshot(s);
    lvgl_port_lock(-1); ui_update(s);
    const uint32_t idle=lv_disp_get_inactive_time(nullptr); lvgl_port_unlock();
    lastDisplayIdle=idle;
    uint8_t target=!s.alwaysOnDisplay && idle>180000 ? max(10,(int)s.brightness/5) : s.brightness;
    if(target!=appliedBrightness && auraBoard->getBacklight()->setBrightness(target)) appliedBrightness=target;
  }
  if(!updateConfirmed && now>8000 && app_startup_healthy()) {
    esp_ota_img_states_t imageState;
    const esp_partition_t *running=esp_ota_get_running_partition();
    const esp_err_t stateResult=esp_ota_get_state_partition(running,&imageState);
    const esp_err_t validated=esp_ota_mark_app_valid_cancel_rollback();
    if(validated==ESP_OK || stateResult!=ESP_OK || imageState!=ESP_OTA_IMG_PENDING_VERIFY) {
      updateConfirmed=true; Serial.println("AURA_HEALTH startup=passed rollback=ready"); printStatus();
    }
  }
  if(!updateConfirmed && now>60000) handleStartupFailure();
  delay(10);
}
