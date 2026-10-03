#include "app_service.h"
#include "web_service.h"
#include "firmware_version.h"
#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <Preferences.h>
#include <LittleFS.h>
#include <esp_http_client.h>
#include <esp_tls.h>
#include <esp_crt_bundle.h>
#include <esp_heap_caps.h>
#include <esp_system.h>
#include <esp_psram.h>
#include <time.h>
#include <math.h>
#include <algorithm>
#include <atomic>

namespace {
constexpr uint32_t WEATHER_INTERVAL = 30UL * 60 * 1000;
constexpr uint32_t AIR_INTERVAL = 60UL * 60 * 1000;
constexpr uint32_t RATE_INTERVAL = 6UL * 60 * 60 * 1000;
constexpr size_t HTTP_LIMIT = 32768;
SemaphoreHandle_t stateMutex;
QueueHandle_t commands;
TaskHandle_t networkTask;
UiSnapshot state{};
Preferences prefs;
String savedSsid, savedPassword, city = "Bucharest", zone = "Europe/Bucharest";
double latitude = 44.4268, longitude = 26.1025;
uint32_t nextWeather, nextAir, nextRates, nextRetry, connectionStart, lastCache;
bool fsReady, forceRefresh, webStarted;
uint32_t nextWebRetry;
std::atomic<bool> initialized{false};
volatile uint16_t lastDisconnectReason;
time_t weatherFetched, airFetched;
time_t widgetFetched[2];
uint32_t nextWidget[2];
char widgetConfig[2][513]{};
struct Command { UiAction action; char first[129], second[513]; };
struct PsramAllocator : ArduinoJson::Allocator {
  void *allocate(size_t n) override { return heap_caps_malloc(n, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT); }
  void deallocate(void *p) override { heap_caps_free(p); }
  void *reallocate(void *p, size_t n) override { return heap_caps_realloc(p, n, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT); }
} jsonAllocator;
struct HttpBody { String data; bool tooLarge = false, tlsFailure = false; };
struct HttpOutcome { const char *error = nullptr; uint16_t status = 0; };

template<size_t N> void text(char (&target)[N], const char *value) { strlcpy(target, value ? value : "", N); }
void lock() { xSemaphoreTake(stateMutex, portMAX_DELAY); }
void unlock() { xSemaphoreGive(stateMutex); }
void message(const char *value) { lock(); text(state.message, value); unlock(); }
String encoded(const String &value) {
  String result; result.reserve(value.length() * 3);
  const char hex[] = "0123456789ABCDEF";
  for (size_t i=0;i<value.length();++i) { uint8_t c=value[i]; if (isalnum(c)||c=='-'||c=='_'||c=='.') result+=(char)c;
    else { result+='%'; result+=hex[c>>4]; result+=hex[c&15]; } }
  return result;
}
esp_err_t httpEvent(esp_http_client_event_t *event) {
  auto *body = static_cast<HttpBody *>(event->user_data);
  if((event->event_id==HTTP_EVENT_ERROR || event->event_id==HTTP_EVENT_DISCONNECTED) && event->data) {
    int tlsCode=0, tlsFlags=0;
    const esp_err_t tlsError=esp_tls_get_and_clear_last_error(static_cast<esp_tls_error_handle_t>(event->data),&tlsCode,&tlsFlags);
    if(tlsCode || tlsFlags || tlsError==ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED) body->tlsFailure=true;
  }
  if (event->event_id == HTTP_EVENT_ON_DATA) {
    if (body->data.length() + event->data_len > HTTP_LIMIT) { body->tooLarge=true; return ESP_FAIL; }
    if (!body->data.concat(static_cast<const char *>(event->data), event->data_len)) { body->tooLarge=true; return ESP_FAIL; }
  }
  return ESP_OK;
}
bool getHttps(const String &url, String &result, HttpOutcome *outcome=nullptr) {
  if(outcome) *outcome=HttpOutcome{};
  const auto fail=[outcome](const char *reason) { if(outcome) outcome->error=reason; return false; };
  if(!url.startsWith("https://") || url.indexOf('#')>=0) return fail("Use a public HTTPS address without credentials.");
  int hostEnd=url.indexOf('/',8), query=url.indexOf('?',8);
  if(hostEnd<0 || (query>=0 && query<hostEnd)) hostEnd=query;
  if(hostEnd<0) hostEnd=url.length();
  String host=url.substring(8,hostEnd);
  if(host.indexOf('@')>=0) return fail("Use a public HTTPS address without credentials.");
  int port=host.indexOf(':'); if(port>=0) host=host.substring(0,port);
  IPAddress resolved;
  if(!WiFi.hostByName(host.c_str(),resolved)) return fail("API hostname could not be resolved. Try again later.");
  if(resolved[0]==0 || resolved[0]==10 || resolved[0]==127 || resolved[0]>=224 ||
     (resolved[0]==169 && resolved[1]==254) || (resolved[0]==172 && resolved[1]>=16 && resolved[1]<=31) ||
     (resolved[0]==192 && resolved[1]==168) || (resolved[0]==100 && resolved[1]>=64 && resolved[1]<=127)) return fail("The API must resolve to a public internet address.");
  HttpBody body; body.data.reserve(4096);
  esp_http_client_config_t config{};
  config.url=url.c_str(); config.timeout_ms=12000; config.event_handler=httpEvent;
  config.user_data=&body; config.crt_bundle_attach=esp_crt_bundle_attach;
  config.buffer_size=2048; config.buffer_size_tx=1024; config.disable_auto_redirect=true;
  auto client=esp_http_client_init(&config);
  if (!client) return fail("Unable to prepare the request. Try again later.");
  esp_http_client_set_header(client,"User-Agent","AURA-Desk/1.0 (personal dashboard)");
  const esp_err_t err=esp_http_client_perform(client);
  const int status=esp_http_client_get_status_code(client);
  if(outcome && status>0 && status<=599) outcome->status=status;
  esp_http_client_cleanup(client);
  // An authenticated HTTPS response proves reachability even when a provider
  // refuses one request. A failed widget must not demote an established router.
  if(status>=100 && status<=599) { lock(); state.internetAvailable=true; unlock(); }
  if(body.tooLarge) return fail("API response exceeds 32 KB. Choose a smaller endpoint.");
  if(err!=ESP_OK) {
    if(body.tlsFailure) { if(outcome) outcome->status=0; return fail("Secure connection failed. Check the clock or try another API."); }
    return fail("API request failed or timed out. Try again later.");
  }
  if(status!=200) {
    if(status==401 || status==403) return fail("Provider refused access. Choose a public API that needs no key.");
    if(status==404) return fail("API address was not found. Check its endpoint.");
    if(status==429) return fail("Provider rate limit reached. Retrying in 5 minutes.");
    if(status>=300 && status<400) return fail("API redirected the request. Use its final HTTPS address.");
    return fail("Provider returned an HTTP error. Check the API address.");
  }
  if(body.data.isEmpty()) return fail("API returned an empty response.");
  result=std::move(body.data); return true;
}
bool finiteNumber(JsonVariantConst value) { return value.is<float>() && isfinite(value.as<float>()); }
void configureClock() {
  // Full daylight-saving rules for the chosen region; no guessed UTC offset.
  const char *rule="UTC0";
  if(zone=="Europe/Bucharest"||zone=="Europe/Helsinki"||zone=="Europe/Athens"||zone=="Europe/Sofia") rule="EET-2EEST,M3.5.0/3,M10.5.0/4";
  else if(zone=="Europe/Amsterdam"||zone=="Europe/Berlin"||zone=="Europe/Budapest"||zone=="Europe/Brussels"||zone=="Europe/Belgrade"||zone=="Europe/Madrid"||zone=="Europe/Paris"||zone=="Europe/Prague"||zone=="Europe/Rome"||zone=="Europe/Stockholm"||zone=="Europe/Warsaw"||zone=="Europe/Vienna"||zone=="Europe/Zurich") rule="CET-1CEST,M3.5.0/2,M10.5.0/3";
  else if(zone=="Europe/London"||zone=="Europe/Dublin"||zone=="Europe/Lisbon") rule="GMT0BST,M3.5.0/1,M10.5.0/2";
  else if(zone=="Europe/Istanbul"||zone=="Europe/Moscow") rule="MSK-3";
  else if(zone=="America/New_York") rule="EST5EDT,M3.2.0/2,M11.1.0/2";
  else if(zone=="America/Chicago") rule="CST6CDT,M3.2.0/2,M11.1.0/2";
  else if(zone=="America/Denver") rule="MST7MDT,M3.2.0/2,M11.1.0/2";
  else if(zone=="America/Los_Angeles") rule="PST8PDT,M3.2.0/2,M11.1.0/2";
  else if(zone=="Asia/Tokyo") rule="JST-9";
  else if(zone=="Asia/Dubai") rule="GST-4";
  else if(zone=="Asia/Singapore") rule="SGT-8";
  configTzTime(rule,"pool.ntp.org","time.cloudflare.com");
  lock(); text(state.timezone,strcmp(rule,"UTC0")==0 ? "UTC" : zone.c_str()); unlock();
}
void syncConnectionState() {
  const bool connected=WiFi.status()==WL_CONNECTED;
  const time_t now=time(nullptr);
  lock(); state.wifiConnected=connected; state.timeSynced=now>1735689600;
  state.rssi=connected ? WiFi.RSSI() : 0;
  text(state.ip,connected ? WiFi.localIP().toString().c_str() : "");
  text(state.ssid,savedSsid.c_str());
  if (connected) { text(state.connection,state.internetAvailable ? "Online" : "Router connected");
    snprintf(state.browserUrl,sizeof(state.browserUrl),"https://%s",state.ip); }
  else { state.internetAvailable=false; text(state.connection,savedSsid.isEmpty() ? "Offline" : "Connecting"); state.browserUrl[0]=0; }
  unlock();
}
void beginConnection() {
  if(savedSsid.isEmpty()) return;
  WiFi.disconnect(false,false); delay(100);
  WiFi.begin(savedSsid.c_str(),savedPassword.c_str());
  connectionStart=millis(); nextRetry=millis()+30000;
  message("Connecting to your router...");
}
void scanNetworks() {
  lock(); state.scanning=true; unlock(); message("Looking for 2.4 GHz networks...");
  const int count=WiFi.scanNetworks(false,true,false,200);
  lock(); state.wifiCount=0;
  for(int i=0;i<count && state.wifiCount<12;i++) {
    const String ssid=WiFi.SSID(i); if(ssid.isEmpty()) continue;
    bool duplicate=false; for(int j=0;j<state.wifiCount;j++) if(ssid==state.networks[j].ssid) duplicate=true;
    if(duplicate) continue;
    auto &entry=state.networks[state.wifiCount++]; text(entry.ssid,ssid.c_str());
    entry.rssi=WiFi.RSSI(i); entry.secure=WiFi.encryptionType(i)!=WIFI_AUTH_OPEN;
  }
  state.scanning=false; unlock(); WiFi.scanDelete();
  message(count<0 ? "Scan unavailable. Enter your network manually." : "Choose your network, or enter it manually.");
}
bool fetchWeather() {
  String url="https://api.open-meteo.com/v1/forecast?latitude="+String(latitude,5)+"&longitude="+String(longitude,5);
  url+="&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m";
  url+="&hourly=precipitation_probability&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max&forecast_days=3&timezone="+encoded(zone);
  String body; if(!getHttps(url,body)) return false;
  JsonDocument doc(&jsonAllocator); if(deserializeJson(doc,body)) return false;
  const auto validIso=[](const char *value,bool timestamp) {
    if(!value) return false; const size_t n=strlen(value);
    if(timestamp ? (n!=16 && n!=19) : n!=10) return false;
    for(size_t i=0;i<n;i++) {
      if(i==4 || i==7) {if(value[i]!='-') return false;}
      else if(i==10) {if(value[i]!='T') return false;}
      else if(i==13 || i==16) {if(value[i]!=':') return false;}
      else if(value[i]<'0' || value[i]>'9') return false;
    }
    int year=atoi(value),month=atoi(value+5),day=atoi(value+8);
    if(year<2000 || year>2099 || month<1 || month>12 || day<1) return false;
    const int days[]={31,28,31,30,31,30,31,31,30,31,30,31};
    int maximum=days[month-1]+(month==2 && year%4==0 && (year%100!=0 || year%400==0));
    return day<=maximum && (!timestamp || (atoi(value+11)<=23 && atoi(value+14)<=59 && (n==16 || atoi(value+17)<=59)));
  };
  const auto weatherCode=[](JsonVariantConst value) {
    if(!finiteNumber(value)) return false;const float number=value.as<float>();
    if(number<0 || number>99 || number!=floorf(number)) return false;
    switch(int(number)) {case 0:case 1:case 2:case 3:case 45:case 48:case 51:case 53:case 55:case 56:case 57:case 61:case 63:case 65:case 66:case 67:case 71:case 73:case 75:case 77:case 80:case 81:case 82:case 85:case 86:case 95:case 96:case 99:return true;default:return false;}
  };
  JsonObjectConst current=doc["current"].as<JsonObjectConst>();
  if(!finiteNumber(current["temperature_2m"]) || !finiteNumber(current["apparent_temperature"]) || !finiteNumber(current["relative_humidity_2m"]) || !finiteNumber(current["wind_speed_10m"]) || !weatherCode(current["weather_code"]) || !current["time"].is<const char *>()) return false;
  if(current["relative_humidity_2m"].as<float>()<0 || current["relative_humidity_2m"].as<float>()>100 || current["wind_speed_10m"].as<float>()<0) return false;
  const char *currentTime=current["time"].as<const char *>();if(!validIso(currentTime,true)) return false;
  JsonObjectConst daily=doc["daily"].as<JsonObjectConst>();
  const char *required[]={"time","temperature_2m_min","temperature_2m_max","precipitation_probability_max","weather_code"};
  for(const char *key:required) if(!daily[key].is<JsonArrayConst>() || daily[key].size()<3) return false;
  ForecastDay forecast[3]{};
  const auto dayNumber=[](const char *value) {
    const int year=atoi(value),month=atoi(value+5),day=atoi(value+8),previous=year-1;
    const int cumulative[]={0,31,59,90,120,151,181,212,243,273,304,334};
    return 365*previous+previous/4-previous/100+previous/400+cumulative[month-1]+day+(month>2 && year%4==0 && (year%100!=0 || year%400==0));
  };
  for(int i=0;i<3;i++) {
    if(!daily["time"][i].is<const char *>() || !validIso(daily["time"][i].as<const char *>(),false) ||
       !finiteNumber(daily["temperature_2m_min"][i]) || !finiteNumber(daily["temperature_2m_max"][i]) ||
       !finiteNumber(daily["precipitation_probability_max"][i]) || !weatherCode(daily["weather_code"][i])) return false;
    if(i==0 ? strncmp(daily["time"][0].as<const char *>(),currentTime,10)!=0 : dayNumber(daily["time"][i].as<const char *>())!=dayNumber(daily["time"][i-1].as<const char *>())+1) return false;
    auto &day=forecast[i];text(day.day,i==0?"Today":i==1?"Tomorrow":"Next day");
    day.low=daily["temperature_2m_min"][i].as<float>();day.high=daily["temperature_2m_max"][i].as<float>();
    day.rain=daily["precipitation_probability_max"][i].as<float>();day.code=daily["weather_code"][i].as<int>();
    if(day.low>day.high || day.rain<0 || day.rain>100) return false;
  }
  // An absent/unmatched hourly probability is unknown, rather than zero rain.
  float rain=NAN;
  auto hours=doc["hourly"]["time"].as<JsonArrayConst>();
  auto probabilities=doc["hourly"]["precipitation_probability"].as<JsonArrayConst>();
  if(!hours.isNull() && hours.size()==probabilities.size()) for(size_t i=0;i<hours.size();i++) {
    if(!hours[i].is<const char *>() || !validIso(hours[i].as<const char *>(),true)) continue;
    if(strncmp(hours[i].as<const char *>(),currentTime,13)==0) {
      if(finiteNumber(probabilities[i])) {const float p=probabilities[i].as<float>();if(p>=0 && p<=100) rain=p;}
      break;
    }
  }
  const char *rise=daily["sunrise"][0].is<const char *>()?daily["sunrise"][0].as<const char *>():nullptr;
  const char *set=daily["sunset"][0].is<const char *>()?daily["sunset"][0].as<const char *>():nullptr;
  // Polar days/nights can have no sunrise/sunset; preserve the missing state.
  if((rise && !validIso(rise,true)) || (set && !validIso(set,true))) return false;
  lock(); state.temperature=current["temperature_2m"]; state.feelsLike=current["apparent_temperature"];
  state.humidity=current["relative_humidity_2m"]; state.wind=current["wind_speed_10m"];
  state.weatherCode=current["weather_code"].as<int>();state.rain=rain;text(state.weatherTime,currentTime);
  for(int i=0;i<3;i++) state.forecast[i]=forecast[i];
  state.sunrise[0]=state.sunset[0]=0;
  if(rise) {memcpy(state.sunrise,rise+11,5);state.sunrise[5]=0;}
  if(set) {memcpy(state.sunset,set+11,5);state.sunset[5]=0;}
  state.weatherValid=true; state.internetAvailable=true; weatherFetched=time(nullptr); state.weatherAgeMinutes=0; unlock();
  return true;
}
bool fetchAir() {
  String url="https://air-quality-api.open-meteo.com/v1/air-quality?latitude="+String(latitude,5)+"&longitude="+String(longitude,5)+"&current=european_aqi,pm2_5&timezone="+encoded(zone);
  String body; if(!getHttps(url,body)) return false;
  JsonDocument doc(&jsonAllocator); if(deserializeJson(doc,body)) return false;
  auto current=doc["current"].as<JsonObjectConst>();
  if(!finiteNumber(current["european_aqi"]) || !finiteNumber(current["pm2_5"]) || current["european_aqi"].as<float>()<0 || current["pm2_5"].as<float>()<0 || !current["time"].is<const char *>()) return false;
  const char *timestamp=current["time"].as<const char *>();const size_t n=strlen(timestamp);
  if(n!=16 && n!=19) return false;
  for(size_t i=0;i<n;i++) {
    if(i==4 || i==7) {if(timestamp[i]!='-') return false;}
    else if(i==10) {if(timestamp[i]!='T') return false;}
    else if(i==13 || i==16) {if(timestamp[i]!=':') return false;}
    else if(timestamp[i]<'0' || timestamp[i]>'9') return false;
  }
  const int year=atoi(timestamp),month=atoi(timestamp+5),day=atoi(timestamp+8);
  if(year<2000 || year>2099 || month<1 || month>12 || day<1 || atoi(timestamp+11)>23 || atoi(timestamp+14)>59 || (n==19 && atoi(timestamp+17)>59)) return false;
  const int days[]={31,28,31,30,31,30,31,31,30,31,30,31};
  if(day>days[month-1]+(month==2 && year%4==0 && (year%100!=0 || year%400==0))) return false;
  lock(); state.aqi=current["european_aqi"]; state.pm25=current["pm2_5"]; state.airValid=true;
  text(state.airTime,timestamp);airFetched=time(nullptr);state.airAgeMinutes=0;state.internetAvailable=true;unlock();return true;
}
float xmlRate(const String &body,const char *currency) {
  String marker="currency=\""+String(currency)+"\""; int p=body.indexOf(marker); if(p<0) return NAN;
  p=body.indexOf("rate=\"",p); if(p<0) return NAN; p+=6; int end=body.indexOf('"',p);
  if(end<0 || end-p>20) return NAN; return body.substring(p,end).toFloat();
}
bool fetchRates() {
  String body; if(!getHttps("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml",body)) return false;
  body.replace('\'', '"'); const float ron=xmlRate(body,"RON"), usd=xmlRate(body,"USD");
  int p=body.indexOf("time=\""); if(p<0 || !isfinite(ron) || ron<=0 || !isfinite(usd) || usd<=0) return false;
  String date=body.substring(p+6,p+16); if(date.length()!=10 || date[4]!='-' || date[7]!='-') return false;
  lock(); state.eurRon=ron; state.eurUsd=usd; text(state.rateDate,date.c_str()); state.ratesValid=true; state.internetAvailable=true; unlock(); return true;
}
bool publicWidgetUrl(const String &value) {
  if(!value.startsWith("https://") || value.length()>200 || value.indexOf('#')>=0) return false;
  for(size_t i=0;i<value.length();++i) if(uint8_t(value[i])<=32 || uint8_t(value[i])>=127 || value[i]=='\\') return false;
  int end=value.indexOf('/',8), query=value.indexOf('?',8);
  if(end<0 || (query>=0 && query<end)) end=query;
  if(end<0) end=value.length(); String host=value.substring(8,end); host.toLowerCase();
  if(host.endsWith(":443")) host.remove(host.length()-4);
  if(host.isEmpty() || host.indexOf('@')>=0 || host.indexOf(':')>=0 || host.indexOf('%')>=0 || host.endsWith(".") || host.indexOf('.')<0 ||
     host=="localhost" || host.endsWith(".localhost") || host.endsWith(".local") || host.endsWith(".internal") || host.endsWith(".lan") || host.endsWith(".home")) return false;
  unsigned a,b,c,d; char trailing;
  if(sscanf(host.c_str(),"%u.%u.%u.%u%c",&a,&b,&c,&d,&trailing)==4 &&
     (a>255 || b>255 || c>255 || d>255 || a==0 || a==10 || a==127 || a>=224 || (a==169&&b==254) ||
      (a==172&&b>=16&&b<=31) || (a==192&&b==168) || (a==100&&b>=64&&b<=127))) return false;
  return true;
}
bool validWidgetPath(const String &path) {
  if(path.isEmpty() || path.length()>80 || path[0]=='.' || path[path.length()-1]=='.' || path.indexOf("..")>=0) return false;
  for(size_t i=0;i<path.length();++i) {
    const uint8_t c=path[i];
    if(!((c>='a'&&c<='z') || (c>='A'&&c<='Z') || (c>='0'&&c<='9') || c=='_' || c=='-' || c=='.')) return false;
  }
  return true;
}
bool validateWidgetOptions(JsonVariantConst options,const char *&problem) {
  const auto fail=[&problem](const char *reason) { problem=reason; return false; };
  if(!options.is<JsonObjectConst>()) return fail("Widget settings must be a JSON object.");
  for(const char *key:{"label","unit","url","field"}) {
    JsonVariantConst value=options[key];
    if(!value.isUnbound() && !value.is<const char*>()) return fail("Widget label, unit, address, and field must be text.");
    if(value.is<const char*>()) {
      JsonString string=value.as<JsonString>();
      for(size_t i=0;i<string.size();++i) if(uint8_t(string.c_str()[i])<32) return fail("Widget text contains unsupported control characters.");
    }
  }
  const char *label=options["label"] | "", *unit=options["unit"] | "";
  String url=options["url"] | "", path=options["field"] | "";
  if(!*label || strlen(label)>27 || strlen(unit)>15 || url.length()>200 || path.length()>80) return fail("Use a short label (27 bytes), unit (15), address (200), and field (80).");
  if(!options["enabled"].isUnbound() && !options["enabled"].is<bool>()) return fail("Widget enabled must be true or false.");
  if(!options["interval"].isUnbound() && !options["interval"].is<uint32_t>()) return fail("Refresh interval must be a whole number of seconds.");
  const bool enabled=options["enabled"] | false;
  const uint32_t interval=options["interval"] | 1800U;
  if(interval<300 || interval>86400) return fail("Choose a refresh interval from 300 to 86400 seconds.");
  if((enabled || !url.isEmpty()) && !publicWidgetUrl(url)) return fail("Use a public HTTPS address on port 443 without credentials.");
  if((enabled || !path.isEmpty()) && !validWidgetPath(path)) return fail("Use a dot path such as current.value or data.0.price.");
  problem=nullptr; return true;
}
bool configureWidget(unsigned index,const char *json) {
  if(index>1 || !json || strlen(json)>512) return false;
  JsonDocument doc(&jsonAllocator); if(deserializeJson(doc,json)) return false;
  const char *problem=nullptr; if(!validateWidgetOptions(doc.as<JsonVariantConst>(),problem)) return false;
  const char *label=doc["label"] | "API widget", *unit=doc["unit"] | "";
  const bool enabled=doc["enabled"] | false;
  lock(); strlcpy(widgetConfig[index],json,sizeof(widgetConfig[index]));
  auto &widget=state.widgets[index]; text(widget.label,label); text(widget.unit,unit);
  widget.enabled=enabled; widget.valid=false; widget.fetching=false; widget.ageMinutes=-1;
  widget.value[0]=0; widget.error[0]=0; widget.httpStatus=0; widgetFetched[index]=0; unlock();
  nextWidget[index]=0; return true;
}
bool selectWidgetValue(JsonVariantConst root,const String &path,JsonVariantConst &out,const char *&problem) {
  const auto fail=[&problem](const char *reason) { problem=reason; return false; };
  if(!validWidgetPath(path)) return fail("JSON field path is invalid. Use dot-separated fields.");
  JsonVariantConst value=root; size_t start=0;
  while(start<path.length()) {
    int end=path.indexOf('.',start); if(end<0) end=path.length(); String part=path.substring(start,end);
    if(value.is<JsonArrayConst>()) {
      size_t selected=0;
      for(size_t n=0;n<part.length();++n) {
        const uint8_t c=part[n];
        if(c<'0' || c>'9') return fail("An array field needs a zero-based numeric index, such as data.0.price.");
        const unsigned digit=c-'0';
        if(selected>(SIZE_MAX-digit)/10) return fail("JSON array index is too large.");
        selected=selected*10+digit;
      }
      JsonArrayConst array=value.as<JsonArrayConst>();
      if(selected>=array.size()) return fail("JSON array index is outside the returned data. Check the field path.");
      value=array[selected];
    } else if(value.is<JsonObjectConst>()) {
      value=value[part.c_str()];
      if(value.isUnbound()) return fail("JSON field was not found. Check the provider response and dot path.");
    } else return fail("The field path continues through a value that is not an object or array.");
    if(value.isNull()) return fail("JSON field is null. The provider has no value for it yet.");
    start=end+1;
  }
  out=value; problem=nullptr; return true;
}
bool formatWidgetValue(JsonVariantConst value,String &display,const char *&problem) {
  const auto fail=[&problem](const char *reason) { problem=reason; return false; };
  display=String();
  if(value.is<const char*>()) {
    JsonString string=value.as<JsonString>();
    if(!string.size()) return fail("JSON field is empty. Choose a field with a value.");
    if(string.size()>47) return fail("JSON field is longer than 47 bytes. Choose a shorter value.");
    for(size_t i=0;i<string.size();++i) if(uint8_t(string.c_str()[i])<32) return fail("JSON text contains unsupported control characters.");
    display=value.as<String>();
  } else if(value.is<bool>()) display=value.as<bool>() ? "Yes" : "No";
  else if(value.is<double>()) {
    if(!isfinite(value.as<double>())) return fail("JSON number is not finite. Choose a valid numeric field.");
    serializeJson(value,display);
  } else return fail("Choose one number, text, or boolean field; objects and arrays cannot be displayed.");
  if(display.isEmpty() || display.length()>47) return fail("JSON value cannot fit the display. Choose a shorter field.");
  problem=nullptr; return true;
}
void widgetFailure(unsigned index,const char *reason,uint16_t status) {
  lock(); auto &widget=state.widgets[index];
  text(widget.error,reason); widget.httpStatus=status; widget.fetching=false;
  // A later failure retains the last verified value and its original age.
  unlock();
}
bool fetchWidget(unsigned index) {
  if(index>1) return false;
  lock(); state.widgets[index].fetching=true; state.widgets[index].error[0]=0; state.widgets[index].httpStatus=0; unlock();
  char config[513];
  if(!app_get_widget_config(index,config,sizeof(config))) { widgetFailure(index,"Widget has no saved configuration.",0); return false; }
  JsonDocument options(&jsonAllocator);
  if(deserializeJson(options,config)) { widgetFailure(index,"Saved widget settings could not be read. Save them again.",0); return false; }
  String body; HttpOutcome outcome;
  if(!getHttps(options["url"].as<String>(),body,&outcome)) { widgetFailure(index,outcome.error ? outcome.error : "API request failed. Try again later.",outcome.status); return false; }
  JsonDocument data(&jsonAllocator);
  if(deserializeJson(data,body)) { widgetFailure(index,"API did not return valid JSON. Choose a JSON endpoint.",outcome.status); return false; }
  const char *problem=nullptr; JsonVariantConst value;
  if(!selectWidgetValue(data.as<JsonVariantConst>(),options["field"].as<String>(),value,problem)) { widgetFailure(index,problem,outcome.status); return false; }
  String display;
  if(!formatWidgetValue(value,display,problem)) { widgetFailure(index,problem,outcome.status); return false; }
  lock(); auto &widget=state.widgets[index]; text(widget.value,display.c_str()); widget.valid=true;
  widget.fetching=false; widget.error[0]=0; widget.httpStatus=outcome.status; widget.ageMinutes=0;
  widgetFetched[index]=time(nullptr); state.internetAvailable=true; unlock();
  return true;
}
void loadCache() {
  if(!fsReady || !LittleFS.exists("/cache.json")) return;
  File file=LittleFS.open("/cache.json","r"); JsonDocument doc(&jsonAllocator);
  if(!file || file.size()>8192 || deserializeJson(doc,file)) { file.close(); return; } file.close();
  if(String(doc["city"] | "")!=city) return;
  const auto validIso=[](const char *value,bool timestamp) {
    if(!value) return false;const size_t n=strlen(value);
    if(timestamp ? (n!=16 && n!=19) : n!=10) return false;
    for(size_t i=0;i<n;i++) {
      if(i==4 || i==7) {if(value[i]!='-') return false;}
      else if(i==10) {if(value[i]!='T') return false;}
      else if(i==13 || i==16) {if(value[i]!=':') return false;}
      else if(value[i]<'0' || value[i]>'9') return false;
    }
    int year=atoi(value),month=atoi(value+5),day=atoi(value+8);
    if(year<2000 || year>2099 || month<1 || month>12 || day<1) return false;
    const int days[]={31,28,31,30,31,30,31,31,30,31,30,31};
    int maximum=days[month-1]+(month==2 && year%4==0 && (year%100!=0 || year%400==0));
    return day<=maximum && (!timestamp || (atoi(value+11)<=23 && atoi(value+14)<=59 && (n==16 || atoi(value+17)<=59)));
  };
  const auto validClock=[](JsonVariantConst value) {
    if(!value.is<const char *>()) return false;const char *s=value.as<const char *>();
    if(!*s) return true;
    return strlen(s)==5 && s[0]>='0' && s[0]<='9' && s[1]>='0' && s[1]<='9' && s[2]==':' && s[3]>='0' && s[3]<='9' && s[4]>='0' && s[4]<='9' && atoi(s)<=23 && atoi(s+3)<=59;
  };
  const auto validFetched=[](JsonVariantConst value) {
    if(!value.is<int64_t>()) return false;const int64_t timestamp=value.as<int64_t>();
    if(timestamp<1735689600LL || timestamp>=4102444800LL) return false;
    const time_t now=time(nullptr);return now<1735689600 || timestamp<=int64_t(now)+300;
  };
  const auto validCode=[](JsonVariantConst value) {
    if(!finiteNumber(value)) return false;const float number=value.as<float>();
    if(number<0 || number>99 || number!=floorf(number)) return false;
    switch(int(number)) {case 0:case 1:case 2:case 3:case 45:case 48:case 51:case 53:case 55:case 56:case 57:case 61:case 63:case 65:case 66:case 67:case 71:case 73:case 75:case 77:case 80:case 81:case 82:case 85:case 86:case 95:case 96:case 99:return true;default:return false;}
  };
  bool weatherOk=doc["weatherValid"].is<bool>() && doc["weatherValid"].as<bool>() &&
    finiteNumber(doc["temperature"]) && finiteNumber(doc["feelsLike"]) && finiteNumber(doc["humidity"]) &&
    doc["humidity"].as<float>()>=0 && doc["humidity"].as<float>()<=100 && finiteNumber(doc["wind"]) && doc["wind"].as<float>()>=0 &&
    validCode(doc["weatherCode"]) && doc["weatherTime"].is<const char *>() && validIso(doc["weatherTime"].as<const char *>(),true) &&
    validFetched(doc["weatherFetched"]) && validClock(doc["sunrise"]) && validClock(doc["sunset"]) &&
    doc["forecast"].is<JsonArrayConst>() && doc["forecast"].size()==3;
  if(!doc["rain"].isNull() && (!finiteNumber(doc["rain"]) || doc["rain"].as<float>()<0 || doc["rain"].as<float>()>100)) weatherOk=false;
  if(weatherOk) for(int i=0;i<3;i++) {
    JsonObjectConst day=doc["forecast"][i].as<JsonObjectConst>();const char *expected=i==0?"Today":i==1?"Tomorrow":"Next day";
    if(day.isNull() || !day["day"].is<const char *>() || strcmp(day["day"].as<const char *>(),expected)!=0 ||
       !finiteNumber(day["low"]) || !finiteNumber(day["high"]) || day["low"].as<float>()>day["high"].as<float>() ||
       !finiteNumber(day["rain"]) || day["rain"].as<float>()<0 || day["rain"].as<float>()>100 || !validCode(day["code"])) {weatherOk=false;break;}
  }
  const bool airOk=doc["airValid"].is<bool>() && doc["airValid"].as<bool>() && finiteNumber(doc["aqi"]) && doc["aqi"].as<float>()>=0 &&
    finiteNumber(doc["pm25"]) && doc["pm25"].as<float>()>=0 && doc["airTime"].is<const char *>() && validIso(doc["airTime"].as<const char *>(),true) && validFetched(doc["airFetched"]);
  const bool ratesOk=doc["ratesValid"].is<bool>() && doc["ratesValid"].as<bool>() && finiteNumber(doc["eurRon"]) && doc["eurRon"].as<float>()>0 &&
    finiteNumber(doc["eurUsd"]) && doc["eurUsd"].as<float>()>0 && doc["rateDate"].is<const char *>() && validIso(doc["rateDate"].as<const char *>(),false);
  lock();
  if(weatherOk) {
    state.temperature=doc["temperature"];state.feelsLike=doc["feelsLike"];state.humidity=doc["humidity"];state.wind=doc["wind"];state.rain=doc["rain"].isNull()?NAN:doc["rain"].as<float>();state.weatherCode=doc["weatherCode"];
    text(state.weatherTime,doc["weatherTime"] | ""); text(state.sunrise,doc["sunrise"] | ""); text(state.sunset,doc["sunset"] | "");
    state.weatherValid=true;weatherFetched=doc["weatherFetched"].as<int64_t>();state.weatherAgeMinutes=-1;
    for(int i=0;i<3;i++) { auto &day=state.forecast[i]; auto src=doc["forecast"][i];
      text(day.day,src["day"] | ""); day.low=src["low"]; day.high=src["high"]; day.rain=src["rain"]; day.code=src["code"]; }
  }
  if(airOk) {state.aqi=doc["aqi"];state.pm25=doc["pm25"];text(state.airTime,doc["airTime"].as<const char *>());state.airValid=true;airFetched=doc["airFetched"].as<int64_t>();state.airAgeMinutes=-1;}
  if(ratesOk) {state.eurRon=doc["eurRon"];state.eurUsd=doc["eurUsd"];text(state.rateDate,doc["rateDate"].as<const char *>());state.ratesValid=true;}
  unlock();
}
void saveCache() {
  if(!fsReady || (lastCache && millis()-lastCache<3600000)) return;
  UiSnapshot s; app_get_snapshot(s); JsonDocument doc(&jsonAllocator);
  doc["city"]=city; doc["weatherValid"]=s.weatherValid; doc["airValid"]=s.airValid; doc["ratesValid"]=s.ratesValid;
  doc["temperature"]=s.temperature; doc["feelsLike"]=s.feelsLike; doc["humidity"]=s.humidity; doc["wind"]=s.wind; doc["rain"]=s.rain; doc["weatherCode"]=s.weatherCode;
  doc["weatherTime"]=s.weatherTime; doc["sunrise"]=s.sunrise; doc["sunset"]=s.sunset; doc["weatherFetched"]=(int64_t)weatherFetched;
  for(int i=0;i<3;i++) { auto day=doc["forecast"].add<JsonObject>(); day["day"]=s.forecast[i].day; day["low"]=s.forecast[i].low; day["high"]=s.forecast[i].high; day["rain"]=s.forecast[i].rain; day["code"]=s.forecast[i].code; }
  doc["aqi"]=s.aqi; doc["pm25"]=s.pm25; doc["airTime"]=s.airTime; doc["airFetched"]=(int64_t)airFetched;
  doc["eurRon"]=s.eurRon; doc["eurUsd"]=s.eurUsd; doc["rateDate"]=s.rateDate;
  File file=LittleFS.open("/cache.tmp","w"); if(!file) return;
  const size_t written=serializeJson(doc,file); file.flush(); file.close();
  if(written) { LittleFS.remove("/cache.json"); LittleFS.rename("/cache.tmp","/cache.json"); lastCache=millis(); }
}
void setLocation(const char *name) {
  if(WiFi.status()!=WL_CONNECTED || time(nullptr)<1735689600) { message("Connect to internet before searching for a city."); return; }
  message("Finding your city..."); String body;
  if(!getHttps("https://geocoding-api.open-meteo.com/v1/search?name="+encoded(name)+"&count=1&language=en&format=json",body)) { message("City search unavailable. Try again later."); return; }
  JsonDocument doc(&jsonAllocator); if(deserializeJson(doc,body) || doc["results"].size()==0) { message("City not found. Try a larger nearby city."); return; }
  auto result=doc["results"][0]; if(!finiteNumber(result["latitude"]) || !finiteNumber(result["longitude"])) return;
  city=result["name"].as<String>(); zone=result["timezone"] | "Europe/Bucharest";
  latitude=result["latitude"]; longitude=result["longitude"];
  prefs.putString("city",city); prefs.putString("zone",zone); prefs.putDouble("lat",latitude); prefs.putDouble("lon",longitude);
  lock(); text(state.city,city.c_str()); state.latitude=latitude; state.longitude=longitude; state.weatherValid=false; state.airValid=false; unlock();
  if(fsReady) LittleFS.remove("/cache.json"); lastCache=0;
  configureClock(); forceRefresh=true; message("Location saved. Updating your dashboard...");
}
void handleCommand(const Command &cmd) {
  switch(cmd.action) {
    case UiAction::ScanWifi: scanNetworks(); break;
    case UiAction::ConnectWifi:
      if(!cmd.first[0] || strlen(cmd.first)>32 || strlen(cmd.second)>63 || (cmd.second[0] && strlen(cmd.second)<8)) { message("Use an SSID up to 32 characters and a valid Wi-Fi password."); break; }
      savedSsid=cmd.first; savedPassword=cmd.second; prefs.putString("ssid",savedSsid); prefs.putString("pass",savedPassword);
      prefs.putBool("explored",true); lock(); state.setupRequired=false; unlock(); beginConnection(); break;
    case UiAction::DisconnectWifi: WiFi.disconnect(false,false); savedSsid=""; message("Disconnected. Your saved network is retained."); break;
    case UiAction::ForgetWifi: WiFi.disconnect(false,true); savedSsid=""; savedPassword=""; prefs.remove("ssid"); prefs.remove("pass"); message("Saved network removed."); break;
    case UiAction::RefreshData: forceRefresh=true; break;
    case UiAction::SetBrightness: { int value=atoi(cmd.first); value=constrain(value,10,100); prefs.putUChar("bright",value); lock(); state.brightness=value; unlock(); break; }
    case UiAction::SetAlwaysOn: {
      const bool enabled=cmd.first[0]=='1';
      if(prefs.getBool("alwaysOn",false)!=enabled && !prefs.putBool("alwaysOn",enabled))
        message("Display mode changed, but could not be saved. Try again.");
      break;
    }
    case UiAction::SetLocation: if(strlen(cmd.first)>=2) setLocation(cmd.first); break;
    case UiAction::ExploreOffline: prefs.putBool("explored",true); lock(); state.setupRequired=false; unlock(); message("Offline tools are ready. Connect Wi-Fi in Settings."); break;
    case UiAction::Reboot: message("Restarting..."); delay(2000); ESP.restart(); break;
    case UiAction::OpenBrowser: break;
    case UiAction::SetApiWidget: {
      const int index=atoi(cmd.first); if(index<0 || index>1 || !configureWidget(index,cmd.second)) { message("Check the widget URL, field and refresh interval."); break; }
      prefs.putString(index==0?"widget0":"widget1",cmd.second); message("API widget saved. Fetching its value..."); break;
    }
  }
}
void networkWorker(void *) {
  if(!prefs.begin("aura",false)) { message("Settings storage unavailable. Restart the device."); vTaskDelete(nullptr); return; }
  savedSsid=prefs.getString("ssid",""); savedPassword=prefs.getString("pass","");
  city=prefs.getString("city","Bucharest"); zone=prefs.getString("zone","Europe/Bucharest");
  latitude=prefs.getDouble("lat",44.4268); longitude=prefs.getDouble("lon",26.1025);
  lock(); text(state.city,city.c_str()); state.latitude=latitude; state.longitude=longitude;
  state.brightness=constrain(prefs.getUChar("bright",80),10,100); state.setupRequired=savedSsid.isEmpty() && !prefs.getBool("explored",false); unlock();
  lock(); state.alwaysOnDisplay=prefs.getBool("alwaysOn",false); unlock();
  for(unsigned i=0;i<2;i++) { String config=prefs.getString(i==0?"widget0":"widget1",""); if(!config.isEmpty()) configureWidget(i,config.c_str()); }
  fsReady=LittleFS.begin(true,"/littlefs",10,"storage"); loadCache();
  WiFi.persistent(false);
  // Core 3.1.1 iterates an unlocked callback vector. Register before mode()
  // starts event delivery so startup cannot invalidate the dispatch iterator.
  WiFi.onEvent([](WiFiEvent_t,WiFiEventInfo_t info){ lastDisconnectReason=info.wifi_sta_disconnected.reason; },ARDUINO_EVENT_WIFI_STA_DISCONNECTED);
  WiFi.mode(WIFI_STA); WiFi.setAutoReconnect(false);
  configureClock(); if(!savedSsid.isEmpty()) beginConnection(); initialized=true;
  for(;;) {
    Command cmd; if(xQueueReceive(commands,&cmd,pdMS_TO_TICKS(100))==pdTRUE) handleCommand(cmd);
    syncConnectionState(); const uint32_t now=millis();
    if(WiFi.status()!=WL_CONNECTED) {
      if(!savedSsid.isEmpty() && (int32_t)(now-nextRetry)>=0) {
        message(lastDisconnectReason==202 || lastDisconnectReason==204 ? "Router rejected the connection. Check Wi-Fi credentials." : "Router unavailable. Retrying automatically...");
        WiFi.reconnect(); nextRetry=now+30000;
      }
      continue;
    }
    if(!webStarted && (int32_t)(now-nextWebRetry)>=0) { web_service_start(); webStarted=web_service_running(); nextWebRetry=millis()+60000; }
    if(time(nullptr)<1735689600) { message("Router connected. Synchronizing time for secure data..."); continue; }
    if(forceRefresh) { nextWeather=nextAir=nextRates=now; nextWidget[0]=nextWidget[1]=now; forceRefresh=false; }
    bool attempted=false, ok=false;
    lock(); state.fetching=true; unlock();
    if((int32_t)(now-nextWeather)>=0) { attempted=true; bool result=fetchWeather(); ok|=result; nextWeather=millis()+(result?WEATHER_INTERVAL:60000); }
    if((int32_t)(now-nextAir)>=0) { attempted=true; bool result=fetchAir(); ok|=result; nextAir=millis()+(result?AIR_INTERVAL:120000); }
    if((int32_t)(now-nextRates)>=0) { attempted=true; bool result=fetchRates(); ok|=result; nextRates=millis()+(result?RATE_INTERVAL:300000); }
    for(unsigned i=0;i<2;i++) {
      UiSnapshot current; app_get_snapshot(current);
      if(current.widgets[i].enabled && (int32_t)(millis()-nextWidget[i])>=0) {
        attempted=true; const bool result=fetchWidget(i); ok|=result;
        char config[513]; app_get_widget_config(i,config,sizeof(config)); JsonDocument options(&jsonAllocator); deserializeJson(options,config);
        nextWidget[i]=millis()+(result ? (options["interval"] | 1800U)*1000 : 300000);
      }
    }
    lock(); state.fetching=false; unlock();
    if(attempted) { message(ok ? "Update complete. Each card shows its own data age." : "Data service unavailable. Saved values are retained."); if(ok) saveCache(); }
    web_service_poll();
  }
}
} // namespace

void app_dispatch(UiAction action,const char *first,const char *second) {
  if(!commands) return; Command cmd{}; cmd.action=action;
  strlcpy(cmd.first,first?first:"",sizeof(cmd.first)); strlcpy(cmd.second,second?second:"",sizeof(cmd.second));
  if(xQueueSend(commands,&cmd,0)!=pdTRUE) message("One moment. A previous action is still being processed.");
  else if(action==UiAction::SetAlwaysOn) { lock(); state.alwaysOnDisplay=cmd.first[0]=='1'; unlock(); }
}
bool app_get_snapshot(UiSnapshot &out) { if(!stateMutex) return false; lock(); out=state; unlock(); return true; }
bool app_validate_widget_config(const char *json,char *error,unsigned capacity) {
  const char *problem=nullptr; bool valid=false;
  if(!json || strlen(json)>512) problem="Widget settings exceed the supported size.";
  else {
    JsonDocument doc(&jsonAllocator);
    if(deserializeJson(doc,json)) problem="Widget settings must be valid JSON.";
    else valid=validateWidgetOptions(doc.as<JsonVariantConst>(),problem);
  }
  if(error && capacity) strlcpy(error,problem ? problem : "",capacity);
  return valid;
}
bool app_get_widget_config(unsigned index,char *out,unsigned capacity) { if(index>1 || !out || !capacity || !stateMutex) return false; lock(); strlcpy(out,widgetConfig[index],capacity); unlock(); return out[0]; }
bool app_service_init() {
  stateMutex=xSemaphoreCreateMutex(); commands=xQueueCreate(8,sizeof(Command));
  if(!stateMutex || !commands) return false;
  text(state.city,"Bucharest"); text(state.timezone,"Europe/Bucharest"); text(state.firmware,"AURA Desk " AURA_VERSION);
  text(state.clock,"--:--"); text(state.date,"Your day, in view."); text(state.connection,"Offline"); text(state.message,"Connect your router to bring your dashboard online.");
  state.setupRequired=true; state.brightness=80; state.latitude=latitude; state.longitude=longitude; state.psramBytes=esp_psram_get_size();
  snprintf(state.adminCode,sizeof(state.adminCode),"%06lu",(unsigned long)(100000+esp_random()%900000));
  snprintf(state.resetReason,sizeof(state.resetReason),"Reset %d",(int)esp_reset_reason());
  const auto result=xTaskCreatePinnedToCore(networkWorker,"aura-network",16384,nullptr,1,&networkTask,0);
  if(result!=pdPASS) { message("Network service could not start."); }
  return result==pdPASS;
}
void app_service_tick() {
  const time_t now=time(nullptr); struct tm timeInfo{};
  lock(); state.uptimeSeconds=millis()/1000; state.freeHeap=ESP.getFreeHeap(); state.minimumHeap=ESP.getMinFreeHeap();
  if(now>1735689600 && localtime_r(&now,&timeInfo)) { strftime(state.clock,sizeof(state.clock),"%H:%M",&timeInfo); strftime(state.date,sizeof(state.date),"%A, %d %B",&timeInfo); state.timeSynced=true; }
  state.weatherAgeMinutes=state.weatherValid && now>1735689600 && weatherFetched>0 ? std::max<int32_t>(0,(now-weatherFetched)/60) : -1;
  state.airAgeMinutes=state.airValid && now>1735689600 && airFetched>0 ? std::max<int32_t>(0,(now-airFetched)/60) : -1;
  for(unsigned i=0;i<2;i++) state.widgets[i].ageMinutes=state.widgets[i].valid && now>1735689600 && widgetFetched[i]>0 ? std::max<int32_t>(0,(now-widgetFetched[i])/60) : -1;
  unlock();
}
bool app_startup_healthy() { return initialized && networkTask && fsReady && esp_psram_get_size()>=0x800000 && ESP.getFreeHeap()>24000; }
