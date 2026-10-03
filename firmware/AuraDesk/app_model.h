#pragma once
#include <stdint.h>

enum class UiAction : uint8_t {
  ScanWifi, ConnectWifi, DisconnectWifi, RefreshData, SetBrightness,
  SetLocation, Reboot, ExploreOffline, OpenBrowser, ForgetWifi, SetApiWidget
};
using UiActionCallback = void (*)(UiAction, const char *, const char *);

struct WifiEntry { char ssid[33]; int16_t rssi; bool secure; };
struct ForecastDay { char day[16]; float low, high, rain; int16_t code; };
struct ApiWidget { char label[28], value[48], unit[16]; bool enabled, valid; int32_t ageMinutes; };
struct UiSnapshot {
  char clock[16], date[48], city[48], timezone[48], ssid[33], ip[20];
  char connection[48], message[100], firmware[24], resetReason[32];
  char weatherTime[32], airTime[32], rateDate[16], sunrise[8], sunset[8];
  char adminCode[12], browserUrl[64];
  bool wifiConnected, timeSynced, internetAvailable, setupRequired;
  bool weatherValid, airValid, ratesValid, fetching, scanning;
  float temperature, feelsLike, humidity, wind, rain, aqi, pm25, eurRon, eurUsd;
  double latitude, longitude;
  int16_t weatherCode, rssi;
  int32_t weatherAgeMinutes, airAgeMinutes;
  uint32_t uptimeSeconds, freeHeap, minimumHeap, psramBytes;
  uint8_t brightness, wifiCount;
  WifiEntry networks[12];
  ForecastDay forecast[3];
  ApiWidget widgets[2];
};

void app_dispatch(UiAction action, const char *first = "", const char *second = "");
bool app_get_snapshot(UiSnapshot &out);
bool app_get_widget_config(unsigned index, char *out, unsigned capacity);
