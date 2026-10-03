#include "web_service.h"
#include "app_model.h"
#include <Arduino.h>
#include <ArduinoJson.h>
#include <esp_https_server.h>
#include <esp_ota_ops.h>
#include <esp_app_desc.h>
#include <esp_app_format.h>
#include <esp_random.h>
#include <esp_timer.h>
#include <nvs.h>
#include <mbedtls/pk.h>
#include <mbedtls/ecp.h>
#include <mbedtls/x509_crt.h>
#include <mbedtls/oid.h>
#include <cstring>
#include <cmath>

extern bool app_get_snapshot(UiSnapshot &snapshot);

namespace {
httpd_handle_t server = nullptr;
char certPem[2048], keyPem[512];
struct Session { char token[65], csrf[65]; uint64_t created, used; };
Session sessions[3] = {};
uint64_t pairWindow = 0, pairBlockedUntil = 0;
unsigned pairFailures = 0;
constexpr size_t MAX_OTA = 5 * 1024 * 1024;
constexpr uint64_t IDLE_MS = 30 * 60 * 1000;
constexpr uint64_t LIFE_MS = 8 * 60 * 60 * 1000;
uint64_t nowMs() { return uint64_t(esp_timer_get_time()) / 1000; }

void randomHex(char *out, size_t bytes) {
  uint8_t raw[32]; esp_fill_random(raw, bytes);
  constexpr char hex[] = "0123456789abcdef";
  for (size_t i=0; i<bytes; ++i) { out[i*2]=hex[raw[i]>>4]; out[i*2+1]=hex[raw[i]&15]; }
  out[bytes*2]=0; memset(raw, 0, sizeof(raw));
}
bool equalSecret(const char *a, const char *b) {
  size_t al=strlen(a), bl=strlen(b); if (al != bl) return false;
  unsigned difference=0; for (size_t i=0;i<al;++i) difference |= unsigned(a[i]^b[i]);
  return difference == 0;
}
String header(httpd_req_t *r, const char *name, size_t maximum=512) {
  size_t n=httpd_req_get_hdr_value_len(r,name);
  if (!n || n>maximum) return String();
  char *buffer=new(std::nothrow) char[n+1]; if(!buffer) return String();
  String value;
  if(httpd_req_get_hdr_value_str(r,name,buffer,n+1)==ESP_OK) value=buffer;
  delete[] buffer; return value;
}
void privacyHeaders(httpd_req_t *r) {
  httpd_resp_set_hdr(r,"Cache-Control","no-store");
  httpd_resp_set_hdr(r,"X-Content-Type-Options","nosniff");
  httpd_resp_set_hdr(r,"Referrer-Policy","no-referrer");
  httpd_resp_set_hdr(r,"X-Frame-Options","DENY");
}
esp_err_t jsonReply(httpd_req_t *r, const char *status, JsonDocument &doc) {
  String body; serializeJson(doc,body); privacyHeaders(r);
  httpd_resp_set_status(r,status); httpd_resp_set_type(r,"application/json");
  return httpd_resp_send(r,body.c_str(),body.length());
}
esp_err_t error(httpd_req_t *r, const char *status, const char *message) {
  JsonDocument doc; doc["error"]=message; return jsonReply(r,status,doc);
}
bool trustedHost(httpd_req_t *r) {
  String host=header(r,"Host",80); host.toLowerCase();
  if(host.endsWith(":443")) host.remove(host.length()-4);
  UiSnapshot s{}; if(!app_get_snapshot(s)) return false;
  return host==s.ip || host=="aura-desk.local";
}
bool sameOrigin(httpd_req_t *r) {
  if(!trustedHost(r)) return false;
  String origin=header(r,"Origin",100), host=header(r,"Host",80);
  return origin==String("https://")+host;
}
Session *authenticate(httpd_req_t *r, bool mutation) {
  if(!trustedHost(r)) { error(r,"403 Forbidden","Use this device's local address."); return nullptr; }
  String cookies=header(r,"Cookie",1024), token;
  int start=0;
  while(start<int(cookies.length())) {
    int end=cookies.indexOf(';',start); if(end<0) end=cookies.length();
    String part=cookies.substring(start,end); part.trim();
    if(part.startsWith("aura_session=")) {token=part.substring(13); break;}
    start=end+1;
  }
  uint64_t now=nowMs();
  for(auto &s:sessions) {
    if(s.token[0] && (now-s.used>IDLE_MS || now-s.created>LIFE_MS)) memset(&s,0,sizeof(s));
    if(s.token[0] && equalSecret(s.token,token.c_str())) {
      if(mutation && (!sameOrigin(r) || !equalSecret(s.csrf,header(r,"X-Aura-CSRF",80).c_str()))) {
        error(r,"403 Forbidden","Refresh this page before trying again."); return nullptr;
      }
      s.used=now; return &s;
    }
  }
  error(r,"401 Unauthorized","Pair with the code shown on the device."); return nullptr;
}
bool readJson(httpd_req_t *r, JsonDocument &doc, size_t maximum=1024) {
  if(r->content_len<=0 || size_t(r->content_len)>maximum || !header(r,"Content-Type",80).startsWith("application/json")) {
    error(r,"400 Bad Request","Send a small JSON request."); return false;
  }
  String body; if(!body.reserve(r->content_len+1)) { error(r,"503 Service Unavailable","Please try again."); return false; }
  char block[256]; int remaining=r->content_len;
  while(remaining>0) {
    int n=httpd_req_recv(r,block,remaining>int(sizeof(block))?sizeof(block):remaining);
    if(n<=0) { error(r,"408 Request Timeout","The request was interrupted."); return false; }
    body.concat(block,n); remaining-=n;
  }
  DeserializationError result=deserializeJson(doc,body);
  // Erase credentials from the temporary request string after parsing.
  for(size_t i=0;i<body.length();++i) body.setCharAt(i,'\0');
  if(result) { error(r,"400 Bad Request","The request is not valid JSON."); return false; }
  return true;
}

const char HTML[] PROGMEM = R"AURA(<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AURA Desk</title>
<style>:root{color-scheme:light;--ink:#172b40;--muted:#657587;--blue:#315ddf;--line:#dde3e7}*{box-sizing:border-box}body{margin:0;background:#f4f5f0;color:var(--ink);font:16px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:960px;margin:auto;padding:32px 20px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:32px}.brand{font-weight:800;letter-spacing:.14em}.brand span{font-weight:400;letter-spacing:.02em}h1{font-size:clamp(32px,6vw,52px);letter-spacing:-.04em;margin:8px 0}h2{font-size:20px;margin:0 0 20px}p{line-height:1.55;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}.card{padding:24px;background:white;border:1px solid var(--line);border-radius:22px}.hero{font-size:40px;letter-spacing:-.03em;margin:10px 0}label{display:block;font-size:14px;font-weight:600;margin:16px 0 8px}input,button{font:inherit;border-radius:12px;min-height:48px}input{padding:12px;width:100%;border:1px solid #c5ced7;background:#fafbf9;color:var(--ink)}input[type=range]{padding:0}button{border:0;background:var(--blue);color:white;padding:12px 20px;font-weight:650;cursor:pointer;margin-top:16px}button.secondary{background:#eaf0f7;color:var(--ink)}button:disabled{opacity:.5;cursor:wait}.small{font-size:13px}.chip{background:#e9f3ef;color:#177d70;padding:8px 12px;border-radius:20px;font-size:13px}.pair{max-width:480px;margin:8vh auto}.hide{display:none!important}.notice{padding:14px 18px;border-radius:14px;background:#eaf0f7;min-height:48px;margin:20px 0}.notice.bad{background:#f9e8eb;color:#b23d4a}progress{width:100%;height:16px;margin-top:16px}footer{font-size:13px;color:var(--muted);padding:30px 0}a{color:var(--blue)}.value{font-size:28px;font-weight:650;margin:8px 0}.inline{display:flex;gap:12px;align-items:center}.inline input{width:auto}pre{white-space:pre-wrap;font:13px ui-monospace,monospace;line-height:1.6}</style>
<main><header><div class="brand">AURA <span>Desk</span></div><span class="chip">Local · HTTPS</span></header>
<section id="pair" class="card pair"><h1>Your desk,<br>connected.</h1><p>Enter the six-digit pairing code shown in Settings → Browser configuration on the device. Your browser connects directly to your AURA Desk.</p><form id="pairform"><label for="code">Pairing code</label><input id="code" type="password" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" autocomplete="one-time-code" required><button>Pair this browser</button></form><p class="small">AURA uses its own device certificate. Your browser may ask you to trust this local device on first visit. Proceed only at the local address shown on your device.</p></section>
<section id="desk" class="hide"><h1>At a glance.</h1><p id="welcome">Connecting to your desk…</p><div class="grid"><div class="card"><h2>Today</h2><div id="clock" class="hero">—</div><p id="date">—</p><div id="weather" class="value">—</div><p id="weatherage">Waiting for a weather update.</p></div><div class="card"><h2>Air &amp; currency</h2><div id="air" class="value">—</div><p id="airage">Regional air-quality model</p><div id="rates" class="value">—</div><p id="ratedate">ECB reference rates</p></div></div>
<div class="grid" style="margin-top:16px"><form id="settings" class="card"><h2>Make it yours</h2><label for="city">City</label><input id="city" maxlength="47" required><label for="brightness">Brightness <span id="brightnessvalue"></span></label><input id="brightness" type="range" min="10" max="100"><div class="inline"><input id="alwayson" type="checkbox" aria-describedby="alwaysonhint"><label for="alwayson">Always-on display</label></div><p id="alwaysonhint" class="small">Keep your chosen brightness. When off, the display dims after 3 minutes without touch.</p><button>Save settings</button></form><form id="wifi" class="card"><h2>Router connection</h2><p id="connection">—</p><label for="ssid">Network name · 2.4 GHz</label><input id="ssid" maxlength="32" autocomplete="off" required><label for="password">Wi-Fi password</label><input id="password" type="password" maxlength="63" autocomplete="new-password"><div class="inline"><input id="reveal" type="checkbox"><label for="reveal">Show password</label></div><button>Connect to network</button><p class="small">The browser connection may close while the device changes networks. Reopen the address shown on the device.</p></form></div>
<h2 style="margin-top:32px">Your data, your way.</h2><p>Choose two public HTTPS JSON APIs. Dot paths select a field, for example <code>current.temperature</code>. These widgets support public data without API keys or credentials.</p>
<div class="grid"><form id="widget0" class="card"><h2>Data widget 1</h2><div id="widgetvalue0" class="value">Not configured</div><p id="widgetage0" class="small">Choose a public data source below.</p><div class="inline"><input id="widgetenabled0" type="checkbox"><label for="widgetenabled0">Enabled</label></div><label for="widgetlabel0">Display label</label><input id="widgetlabel0" maxlength="27" value="API widget 1" required><label for="widgeturl0">Public HTTPS API address</label><input id="widgeturl0" type="url" maxlength="200" placeholder="https://example.org/data.json"><label for="widgetfield0">JSON field · dot path</label><input id="widgetfield0" maxlength="80" placeholder="current.value"><label for="widgetunit0">Unit · optional</label><input id="widgetunit0" maxlength="15" placeholder="°C"><label for="widgetinterval0">Refresh interval · seconds</label><input id="widgetinterval0" type="number" min="300" max="86400" step="1" value="1800"><button>Save widget 1</button></form>
<form id="widget1" class="card"><h2>Data widget 2</h2><div id="widgetvalue1" class="value">Not configured</div><p id="widgetage1" class="small">Choose a public data source below.</p><div class="inline"><input id="widgetenabled1" type="checkbox"><label for="widgetenabled1">Enabled</label></div><label for="widgetlabel1">Display label</label><input id="widgetlabel1" maxlength="27" value="API widget 2" required><label for="widgeturl1">Public HTTPS API address</label><input id="widgeturl1" type="url" maxlength="200" placeholder="https://example.org/data.json"><label for="widgetfield1">JSON field · dot path</label><input id="widgetfield1" maxlength="80" placeholder="current.value"><label for="widgetunit1">Unit · optional</label><input id="widgetunit1" maxlength="15" placeholder="°C"><label for="widgetinterval1">Refresh interval · seconds</label><input id="widgetinterval1" type="number" min="300" max="86400" step="1" value="1800"><button>Save widget 2</button></form></div>
<div class="grid" style="margin-top:16px"><div class="card"><h2>Device health</h2><pre id="health">—</pre><button id="refresh" class="secondary">Refresh data</button> <button id="export" class="secondary">Export settings</button><p class="small">Settings exports exclude passwords, pairing codes, and private keys.</p></div><form id="update" class="card"><h2>Firmware update</h2><p>Upload an AURA Desk application <strong>.bin</strong>. Keep power connected. Combined flash backups and bootloader images are not update files.</p><input id="binary" type="file" accept=".bin,application/octet-stream" required><button id="upload">Install update</button><progress id="progress" max="100" value="0" class="hide"></progress><p id="updatestate" class="small"></p></form></div></section>
<div id="notice" class="notice hide" role="status" aria-live="polite"></div><footer>Designed for your desk. Data: <a href="https://open-meteo.com/" target="_blank" rel="noreferrer">Open-Meteo</a> · CAMS ENSEMBLE · <a href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html" target="_blank" rel="noreferrer">ECB</a>. Forecast data and reference rates are shown with their source dates.</footer></main>
<script>
const $=id=>document.getElementById(id);let csrf='',first=true,updating=false;
function notice(text,bad=false){$('notice').textContent=text;$('notice').className='notice'+(bad?' bad':'')}
async function api(path,method='GET',data){const options={method,credentials:'same-origin',cache:'no-store',headers:{}};if(method!=='GET'){options.headers['X-Aura-CSRF']=csrf;options.headers['Content-Type']='application/json';options.body=JSON.stringify(data||{})}const response=await fetch(path,options);const result=await response.json();if(!response.ok){if(response.status===401){$('pair').classList.remove('hide');$('desk').classList.add('hide');csrf=''}throw Error(result.error||'Please try again.')}return result}
function showStatus(s){csrf=s.csrf;$('pair').classList.add('hide');$('desk').classList.remove('hide');$('welcome').textContent=s.city+' · '+s.connection;$('clock').textContent=s.timeSynced?s.clock:'Time pending';$('date').textContent=s.timeSynced?s.date:'Connect to the internet to sync time';$('weather').textContent=s.weatherValid?s.temperature.toFixed(1)+' °C':'—';$('weatherage').textContent=s.weatherValid?(s.weatherAgeMinutes>=0?'Regional forecast · updated '+s.weatherAgeMinutes+' min ago':'Regional forecast · saved data, age unavailable'):'Waiting for first weather update';$('air').textContent=s.airValid?'European AQI '+Math.round(s.aqi):'—';$('airage').textContent=s.airValid?(s.airAgeMinutes>=0?'CAMS regional model · updated '+s.airAgeMinutes+' min ago':'CAMS regional model · saved data, age unavailable'):'Waiting for first air-quality update';$('rates').textContent=s.ratesValid?'1 EUR = '+s.eurRon.toFixed(4)+' RON':'—';$('ratedate').textContent=s.ratesValid?'ECB reference · '+s.rateDate:'Waiting for reference rates';$('connection').textContent=s.connection+' · '+s.ssid;$('health').textContent='Firmware  '+s.firmware+'\nAddress   '+s.ip+'\nUptime    '+s.uptimeSeconds+' s\nFree heap '+s.freeHeap+' bytes\nMin heap  '+s.minimumHeap+' bytes\nPSRAM     '+s.psramBytes+' bytes\nSignal    '+s.rssi+' dBm\nReset     '+s.resetReason;if(first){$('city').value=s.city;$('brightness').value=s.brightness;$('brightnessvalue').textContent=s.brightness+'%';$('alwayson').checked=!!s.alwaysOnDisplay;$('ssid').value=s.ssid;for(let i=0;i<2;i++){const c=(s.widgetConfig||[])[i]||{};$('widgetlabel'+i).value=c.label||'API widget '+(i+1);$('widgeturl'+i).value=c.url||'';$('widgetfield'+i).value=c.field||'';$('widgetunit'+i).value=c.unit||'';$('widgetinterval'+i).value=c.interval||1800;$('widgetenabled'+i).checked=!!c.enabled}first=false}for(let i=0;i<2;i++){const w=(s.widgets||[])[i]||{};$('widgetvalue'+i).textContent=w.enabled?(w.valid?w.value+(w.unit?' '+w.unit:''):'—'):'Disabled';$('widgetage'+i).textContent=w.enabled?(w.valid?(w.ageMinutes>=0?w.label+' · updated '+w.ageMinutes+' min ago':w.label+' · saved data, age unavailable'):'Waiting for first update'):'Enable a public data source below.'}}
async function poll(){if(updating)return;try{showStatus(await api('/api/status'))}catch(e){if(csrf)notice('The device is temporarily unavailable. Reconnecting…',true)}}
$('pairform').onsubmit=async e=>{e.preventDefault();try{const s=await api('/api/pair','POST',{code:$('code').value});$('code').value='';csrf=s.csrf;first=true;await poll();notice('This browser is paired.')}catch(e){notice(e.message,true)}};
$('brightness').oninput=()=>{$('brightnessvalue').textContent=$('brightness').value+'%'};
$('settings').onsubmit=async e=>{e.preventDefault();try{await api('/api/settings','POST',{city:$('city').value.trim(),brightness:Number($('brightness').value),alwaysOnDisplay:$('alwayson').checked});notice('Settings saved. Location data will refresh shortly.')}catch(e){notice(e.message,true)}};
$('wifi').onsubmit=async e=>{e.preventDefault();try{await api('/api/wifi','POST',{ssid:$('ssid').value,password:$('password').value});$('password').value='';notice('Connecting to the selected network. Check the address on the device.')}catch(e){notice(e.message,true)}};
$('reveal').onchange=()=>{$('password').type=$('reveal').checked?'text':'password'};
$('refresh').onclick=async()=>{try{await api('/api/refresh','POST',{});notice('Refresh requested.')}catch(e){notice(e.message,true)}};
$('export').onclick=async()=>{try{const d=await api('/api/export'),a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:'application/json'}));a.href=u;a.download='aura-desk-settings.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),5000)}catch(e){notice(e.message,true)}};
for(let i=0;i<2;i++)$('widget'+i).onsubmit=async e=>{e.preventDefault();try{await api('/api/widget','POST',{index:i,label:$('widgetlabel'+i).value.trim(),url:$('widgeturl'+i).value.trim(),field:$('widgetfield'+i).value.trim(),unit:$('widgetunit'+i).value.trim(),interval:Number($('widgetinterval'+i).value)||1800,enabled:$('widgetenabled'+i).checked});notice('Data widget saved. Its first update will appear shortly.')}catch(e){notice(e.message,true)}};
$('update').onsubmit=e=>{e.preventDefault();const file=$('binary').files[0];if(!file||file.size<1024||file.size>5242880){notice('Choose an application .bin between 1 KB and 5 MB.',true);return}updating=true;$('upload').disabled=true;$('progress').classList.remove('hide');$('updatestate').textContent='Uploading. Keep the device powered.';const x=new XMLHttpRequest();x.open('POST','/api/ota');x.setRequestHeader('Content-Type','application/octet-stream');x.setRequestHeader('X-Aura-CSRF',csrf);x.timeout=180000;x.upload.onprogress=e=>{if(e.lengthComputable)$('progress').value=Math.round(e.loaded/e.total*100)};x.onload=()=>{let result={};try{result=JSON.parse(x.responseText)}catch(e){}if(x.status===200){$('progress').value=100;$('updatestate').textContent='Update verified. The device is restarting.';notice('Update installed. Wait for the device to restart, then reload this page.')}else{notice(result.error||'Update failed. Current firmware remains active.',true);$('upload').disabled=false;updating=false}};x.onerror=x.ontimeout=()=>{notice('Connection interrupted. Check the device before retrying.',true);$('upload').disabled=false;updating=false};x.send(file)};
poll();setInterval(poll,10000);
</script></html>)AURA";

esp_err_t rootHandler(httpd_req_t *r) {
  if(!trustedHost(r)) return error(r,"403 Forbidden","Use the address shown on the device.");
  privacyHeaders(r); httpd_resp_set_type(r,"text/html; charset=utf-8");
  httpd_resp_set_hdr(r,"Content-Security-Policy","default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");
  return httpd_resp_send(r,HTML,sizeof(HTML)-1);
}
esp_err_t pairHandler(httpd_req_t *r) {
  if(!sameOrigin(r)) return error(r,"403 Forbidden","Pair from this device's browser page.");
  uint64_t now=nowMs();
  if(now<pairBlockedUntil) return error(r,"429 Too Many Requests","Wait one minute before trying again.");
  if(now-pairWindow>60000) {pairWindow=now;pairFailures=0;}
  JsonDocument request; if(!readJson(r,request,256)) return ESP_OK;
  UiSnapshot snapshot{}; if(!app_get_snapshot(snapshot)) return error(r,"503 Service Unavailable","Device is starting.");
  const char *code=request["code"] | "";
  if(strlen(code)!=6 || !equalSecret(code,snapshot.adminCode)) {
    if(++pairFailures>=5) pairBlockedUntil=now+60000;
    return error(r,"401 Unauthorized","The code does not match. Check Settings → Browser configuration on the device.");
  }
  pairFailures=0;
  Session *selected=&sessions[0];
  for(auto &s:sessions) if(!s.token[0] || now-s.used>IDLE_MS || now-s.created>LIFE_MS) {selected=&s;break;} else if(s.used<selected->used) selected=&s;
  randomHex(selected->token,32); randomHex(selected->csrf,32); selected->created=selected->used=now;
  char cookie[160]; snprintf(cookie,sizeof(cookie),"aura_session=%s; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=28800",selected->token);
  httpd_resp_set_hdr(r,"Set-Cookie",cookie);
  JsonDocument reply; reply["csrf"]=selected->csrf; reply["paired"]=true;
  return jsonReply(r,"200 OK",reply);
}
esp_err_t statusHandler(httpd_req_t *r) {
  Session *session=authenticate(r,false); if(!session) return ESP_OK;
  UiSnapshot s{}; if(!app_get_snapshot(s)) return error(r,"503 Service Unavailable","Device is starting.");
  JsonDocument d;
  d["csrf"]=session->csrf; d["clock"]=s.clock; d["date"]=s.date; d["city"]=s.city; d["timezone"]=s.timezone;
  d["ssid"]=s.ssid; d["ip"]=s.ip; d["connection"]=s.connection; d["firmware"]=s.firmware; d["resetReason"]=s.resetReason;
  d["wifiConnected"]=s.wifiConnected; d["internetAvailable"]=s.internetAvailable; d["timeSynced"]=s.timeSynced;
  d["weatherValid"]=s.weatherValid; d["airValid"]=s.airValid; d["ratesValid"]=s.ratesValid; d["fetching"]=s.fetching;
  d["temperature"]=s.temperature; d["feelsLike"]=s.feelsLike; d["humidity"]=s.humidity; d["wind"]=s.wind; d["rain"]=s.rain;
  d["aqi"]=s.aqi; d["pm25"]=s.pm25; d["eurRon"]=s.eurRon; d["eurUsd"]=s.eurUsd;
  d["weatherAgeMinutes"]=s.weatherAgeMinutes; d["airAgeMinutes"]=s.airAgeMinutes; d["rateDate"]=s.rateDate;
  d["uptimeSeconds"]=s.uptimeSeconds; d["freeHeap"]=s.freeHeap; d["minimumHeap"]=s.minimumHeap; d["psramBytes"]=s.psramBytes;
  d["rssi"]=s.rssi; d["brightness"]=s.brightness; d["alwaysOnDisplay"]=s.alwaysOnDisplay;
  JsonArray readings=d["widgets"].to<JsonArray>(), configurations=d["widgetConfig"].to<JsonArray>();
  for(uint8_t i=0;i<2;++i) {
    const auto &widget=s.widgets[i]; JsonObject w=readings.add<JsonObject>();
    w["label"]=widget.label;w["value"]=widget.value;w["unit"]=widget.unit;
    w["enabled"]=widget.enabled;w["valid"]=widget.valid;w["ageMinutes"]=widget.ageMinutes;
    char config[512]={};JsonDocument parsed;
    if(app_get_widget_config(i,config,sizeof(config)) && !deserializeJson(parsed,config)) configurations.add(parsed.as<JsonObject>());
    else configurations.add<JsonObject>();
  }
  return jsonReply(r,"200 OK",d);
}
esp_err_t settingsHandler(httpd_req_t *r) {
  if(!authenticate(r,true)) return ESP_OK;
  JsonDocument request; if(!readJson(r,request)) return ESP_OK;
  if(!request.is<JsonObject>()) return error(r,"400 Bad Request","Send an object with the settings to change.");
  JsonVariant cityValue=request["city"], brightnessValue=request["brightness"];
  JsonVariant alwaysOn=request["alwaysOnDisplay"];
  bool hasCity=!cityValue.isUnbound(), hasBrightness=!brightnessValue.isUnbound();
  bool hasAlwaysOn=!alwaysOn.isUnbound();
  if(!hasCity && !hasBrightness && !hasAlwaysOn) return error(r,"400 Bad Request","Choose a city, brightness, or always-on display setting.");
  const char *city=cityValue | ""; int brightness=brightnessValue | -1;
  if(hasCity) {
    if(!cityValue.is<const char*>() || !*city || strlen(city)>47) return error(r,"400 Bad Request","Enter a city up to 47 bytes.");
    for(const unsigned char *p=reinterpret_cast<const unsigned char*>(city);*p;++p) if(*p<32) return error(r,"400 Bad Request","City contains unsupported characters.");
  }
  if(hasBrightness && (!brightnessValue.is<int>() || brightness<10 || brightness>100)) return error(r,"400 Bad Request","Choose a brightness from 10 to 100.");
  if(hasAlwaysOn && !alwaysOn.is<bool>()) return error(r,"400 Bad Request","Always-on display must be true or false.");
  UiSnapshot snapshot{};
  if(hasCity && !app_get_snapshot(snapshot)) return error(r,"503 Service Unavailable","Device is starting.");
  if(hasBrightness) {
    char value[4]; snprintf(value,sizeof(value),"%d",brightness);
    app_dispatch(UiAction::SetBrightness,value,"");
  }
  if(hasCity && strcmp(city,snapshot.city)!=0) app_dispatch(UiAction::SetLocation,city,"");
  if(hasAlwaysOn) app_dispatch(UiAction::SetAlwaysOn,alwaysOn.as<bool>() ? "1" : "0","");
  JsonDocument reply; reply["accepted"]=true; return jsonReply(r,"202 Accepted",reply);
}
esp_err_t wifiHandler(httpd_req_t *r) {
  if(!authenticate(r,true)) return ESP_OK;
  JsonDocument request; if(!readJson(r,request,512)) return ESP_OK;
  const char *ssid=request["ssid"] | "", *password=request["password"] | "";
  size_t passwordLen=strlen(password);
  if(!*ssid || strlen(ssid)>32 || passwordLen>63 || (passwordLen>0 && passwordLen<8)) return error(r,"400 Bad Request","Use a network name up to 32 bytes and a password of 8–63 characters, or leave it empty for an open network.");
  app_dispatch(UiAction::ConnectWifi,ssid,password);
  request.clear(); JsonDocument reply; reply["accepted"]=true;
  return jsonReply(r,"202 Accepted",reply);
}
esp_err_t refreshHandler(httpd_req_t *r) {
  if(!authenticate(r,true)) return ESP_OK;
  JsonDocument request; if(!readJson(r,request,64)) return ESP_OK;
  app_dispatch(UiAction::RefreshData); JsonDocument reply; reply["accepted"]=true;
  return jsonReply(r,"202 Accepted",reply);
}
esp_err_t exportHandler(httpd_req_t *r) {
  if(!authenticate(r,false)) return ESP_OK;
  UiSnapshot s{}; if(!app_get_snapshot(s)) return error(r,"503 Service Unavailable","Device is starting.");
  JsonDocument d; d["product"]="AURA Desk"; d["formatVersion"]=1; d["firmware"]=s.firmware;
  d["city"]=s.city; d["latitude"]=s.latitude; d["longitude"]=s.longitude; d["timezone"]=s.timezone; d["brightness"]=s.brightness; d["alwaysOnDisplay"]=s.alwaysOnDisplay;
  JsonArray widgets=d["widgets"].to<JsonArray>();
  for(uint8_t i=0;i<2;++i) {char config[512]={};JsonDocument parsed;if(app_get_widget_config(i,config,sizeof(config)) && !deserializeJson(parsed,config)) widgets.add(parsed.as<JsonObject>());else widgets.add<JsonObject>();}
  return jsonReply(r,"200 OK",d);
}
bool publicApiUrl(const char *url) {
  String value(url); if(!value.startsWith("https://") || value.length()>200 || value.indexOf('#')>=0) return false;
  for(size_t i=0;i<value.length();++i) if(uint8_t(value[i])<=32 || uint8_t(value[i])>=127 || value[i]=='\\') return false;
  int end=value.indexOf('/',8), query=value.indexOf('?',8);
  if(end<0 || (query>=0 && query<end)) end=query;
  if(end<0) end=value.length(); String host=value.substring(8,end);host.toLowerCase();
  if(host.endsWith(":443")) host.remove(host.length()-4);
  if(host.isEmpty() || host.indexOf('@')>=0 || host.indexOf(':')>=0 || host.indexOf('%')>=0 || host.endsWith(".") || host.indexOf('.')<0 || host=="localhost" || host.endsWith(".localhost") || host.endsWith(".local") || host.endsWith(".internal") || host.endsWith(".lan") || host.endsWith(".home")) return false;
  unsigned a,b,c,d;char trailing;
  if(sscanf(host.c_str(),"%u.%u.%u.%u%c",&a,&b,&c,&d,&trailing)==4) {
    if(a>255||b>255||c>255||d>255 || a==0 || a==10 || a==127 || a>=224 || (a==169&&b==254) || (a==172&&b>=16&&b<=31) || (a==192&&b==168) || (a==100&&b>=64&&b<=127)) return false;
  }
  return true;
}
esp_err_t widgetHandler(httpd_req_t *r) {
  if(!authenticate(r,true)) return ESP_OK;
  JsonDocument request; if(!readJson(r,request,1024)) return ESP_OK;
  int index=request["index"] | -1; const char *label=request["label"] | "",*url=request["url"] | "",*field=request["field"] | "",*unit=request["unit"] | "";
  int interval=request["interval"] | 1800;bool enabled=request["enabled"] | false;
  if(index<0 || index>1 || !*label || strlen(label)>27 || strlen(unit)>15 || strlen(url)>200 || strlen(field)>80 || interval<300 || interval>86400) return error(r,"400 Bad Request","Use a short label, unit, and refresh interval from 300 to 86400 seconds.");
  for(const char *p=label;*p;++p) if(uint8_t(*p)<32) return error(r,"400 Bad Request","The label contains unsupported characters.");
  for(const char *p=unit;*p;++p) if(uint8_t(*p)<32) return error(r,"400 Bad Request","The unit contains unsupported characters.");
  if(enabled && (!publicApiUrl(url) || !*field)) return error(r,"400 Bad Request","Choose a public HTTPS JSON address and a field path. Private network addresses and credentials are unsupported.");
  if(*url && !publicApiUrl(url)) return error(r,"400 Bad Request","Choose a public HTTPS API address without credentials.");
  if(*field=='.' || (*field && field[strlen(field)-1]=='.') || strstr(field,"..")) return error(r,"400 Bad Request","Use a dot path such as current.value.");
  for(const char *p=field;*p;++p) if(!isalnum(uint8_t(*p)) && *p!='_' && *p!='-' && *p!='.') return error(r,"400 Bad Request","Field paths contain letters, numbers, underscores, dashes and dots.");
  JsonDocument config;config["label"]=label;config["url"]=url;config["field"]=field;config["unit"]=unit;config["interval"]=interval;config["enabled"]=enabled;
  if(measureJson(config)>=512) return error(r,"400 Bad Request","Widget configuration is too long.");
  char serialized[512];serializeJson(config,serialized,sizeof(serialized));char selected[2]={char('0'+index),0};
  app_dispatch(UiAction::SetApiWidget,selected,serialized);JsonDocument reply;reply["accepted"]=true;
  return jsonReply(r,"202 Accepted",reply);
}
esp_err_t otaHandler(httpd_req_t *r) {
  if(!authenticate(r,true)) return ESP_OK;
  const esp_partition_t *partition=esp_ota_get_next_update_partition(nullptr);
  if(!partition) return error(r,"409 Conflict","No inactive update slot is available.");
  if(r->content_len<1024 || size_t(r->content_len)>MAX_OTA || size_t(r->content_len)>partition->size || header(r,"Content-Type",80)!="application/octet-stream")
    return error(r,"413 Payload Too Large","Upload an application .bin between 1 KB and 5 MB.");
  esp_ota_handle_t ota=0; esp_err_t result=esp_ota_begin(partition,r->content_len,&ota);
  if(result!=ESP_OK) return error(r,"503 Service Unavailable","Unable to prepare the inactive update slot.");
  uint8_t buffer[4096]; size_t remaining=r->content_len;
  constexpr size_t PREFIX_SIZE=sizeof(esp_image_header_t)+sizeof(esp_image_segment_header_t)+sizeof(uint32_t);
  uint8_t prefix[PREFIX_SIZE]; size_t prefixLength=0; bool imageChecked=false;
  while(remaining) {
    int received=httpd_req_recv(r,reinterpret_cast<char*>(buffer),remaining>sizeof(buffer)?sizeof(buffer):remaining);
    if(received<=0) {esp_ota_abort(ota); return error(r,"408 Request Timeout","Upload interrupted. Current firmware remains active.");}
    if(prefixLength<PREFIX_SIZE) {
      size_t take=PREFIX_SIZE-prefixLength; if(take>size_t(received)) take=received;
      memcpy(prefix+prefixLength,buffer,take);prefixLength+=take;
    }
    if(!imageChecked && prefixLength==PREFIX_SIZE) {
      esp_image_header_t image{};memcpy(&image,prefix,sizeof(image));
      uint32_t applicationMagic=0;memcpy(&applicationMagic,prefix+sizeof(esp_image_header_t)+sizeof(esp_image_segment_header_t),sizeof(applicationMagic));
      if(image.magic!=ESP_IMAGE_HEADER_MAGIC || image.chip_id!=ESP_CHIP_ID_ESP32S3 || applicationMagic!=ESP_APP_DESC_MAGIC_WORD) {
        esp_ota_abort(ota);return error(r,"400 Bad Request","Choose an ESP32-S3 application image, not a bootloader or full-flash backup.");
      }
      imageChecked=true;
    }
    result=esp_ota_write(ota,buffer,received);
    if(result!=ESP_OK) {esp_ota_abort(ota); return error(r,"400 Bad Request","Image rejected. Current firmware remains active.");}
    remaining-=received;
  }
  result=esp_ota_end(ota);
  if(result!=ESP_OK) return error(r,"400 Bad Request","Image verification failed. Current firmware remains active.");
  if(esp_ota_set_boot_partition(partition)!=ESP_OK) return error(r,"500 Internal Server Error","Unable to activate the verified update.");
  JsonDocument reply; reply["verified"]=true; reply["restarting"]=true;
  esp_err_t sent=jsonReply(r,"200 OK",reply);
  // The queued reboot action gives the response two seconds to leave the socket.
  app_dispatch(UiAction::Reboot,"2000",""); return sent;
}

int hardwareRng(void *, unsigned char *out, size_t len) {esp_fill_random(out,len);return 0;}
bool certificate() {
  nvs_handle_t nvs; if(nvs_open("aura_tls",NVS_READWRITE,&nvs)!=ESP_OK) return false;
  size_t certLength=sizeof(certPem), keyLength=sizeof(keyPem);
  if(nvs_get_str(nvs,"certificate",certPem,&certLength)==ESP_OK && nvs_get_str(nvs,"private_key",keyPem,&keyLength)==ESP_OK) {nvs_close(nvs);return true;}
  memset(certPem,0,sizeof(certPem));memset(keyPem,0,sizeof(keyPem));
  mbedtls_pk_context key; mbedtls_pk_init(&key);
  mbedtls_x509write_cert crt; mbedtls_x509write_crt_init(&crt);
  int result=mbedtls_pk_setup(&key,mbedtls_pk_info_from_type(MBEDTLS_PK_ECKEY));
  if(!result) result=mbedtls_ecp_gen_key(MBEDTLS_ECP_DP_SECP256R1,mbedtls_pk_ec(key),hardwareRng,nullptr);
  mbedtls_x509write_crt_set_version(&crt,MBEDTLS_X509_CRT_VERSION_3);
  mbedtls_x509write_crt_set_md_alg(&crt,MBEDTLS_MD_SHA256);
  mbedtls_x509write_crt_set_subject_key(&crt,&key); mbedtls_x509write_crt_set_issuer_key(&crt,&key);
  const char *subject="CN=aura-desk.local,O=AURA Desk";
  if(!result) result=mbedtls_x509write_crt_set_subject_name(&crt,subject);
  if(!result) result=mbedtls_x509write_crt_set_issuer_name(&crt,subject);
  uint8_t serial[16];esp_fill_random(serial,sizeof(serial));serial[0]&=0x7F;serial[0]|=1;
  if(!result) result=mbedtls_x509write_crt_set_serial_raw(&crt,serial,sizeof(serial));
  if(!result) result=mbedtls_x509write_crt_set_validity(&crt,"20260101000000","20401231235959");
  if(!result) result=mbedtls_x509write_crt_set_basic_constraints(&crt,0,-1);
  if(!result) result=mbedtls_x509write_crt_set_key_usage(&crt,MBEDTLS_X509_KU_DIGITAL_SIGNATURE);
  // DER GeneralNames: one DNS-name entry for the advertised mDNS hostname.
  const unsigned char san[]={0x30,0x11,0x82,0x0f,'a','u','r','a','-','d','e','s','k','.','l','o','c','a','l'};
  if(!result) result=mbedtls_x509write_crt_set_extension(&crt,MBEDTLS_OID_SUBJECT_ALT_NAME,MBEDTLS_OID_SIZE(MBEDTLS_OID_SUBJECT_ALT_NAME),0,san,sizeof(san));
  if(!result) result=mbedtls_pk_write_key_pem(&key,reinterpret_cast<unsigned char*>(keyPem),sizeof(keyPem));
  if(!result) result=mbedtls_x509write_crt_pem(&crt,reinterpret_cast<unsigned char*>(certPem),sizeof(certPem),hardwareRng,nullptr);
  mbedtls_x509write_crt_free(&crt);mbedtls_pk_free(&key);
  bool saved=false;
  if(!result && nvs_set_str(nvs,"private_key",keyPem)==ESP_OK && nvs_set_str(nvs,"certificate",certPem)==ESP_OK && nvs_commit(nvs)==ESP_OK) saved=true;
  nvs_close(nvs);
  if(!saved) {memset(keyPem,0,sizeof(keyPem));memset(certPem,0,sizeof(certPem));}
  return saved;
}
void registerEndpoint(const char *uri,httpd_method_t method,esp_err_t(*handler)(httpd_req_t*)) {
  httpd_uri_t endpoint{}; endpoint.uri=uri;endpoint.method=method;endpoint.handler=handler;
  if(httpd_register_uri_handler(server,&endpoint)!=ESP_OK) Serial.println("[web] Endpoint registration failed");
}
} // namespace

void web_service_start() {
  if(server) return;
  if(!certificate()) {Serial.println("[web] Device certificate unavailable");return;}
  httpd_ssl_config_t config=HTTPD_SSL_CONFIG_DEFAULT();
  config.httpd.stack_size=16384;config.httpd.max_open_sockets=3;config.httpd.max_uri_handlers=9;
  config.httpd.recv_wait_timeout=10;config.httpd.send_wait_timeout=10;
  config.servercert=reinterpret_cast<const uint8_t*>(certPem);config.servercert_len=strlen(certPem)+1;
  config.prvtkey_pem=reinterpret_cast<const uint8_t*>(keyPem);config.prvtkey_len=strlen(keyPem)+1;
  if(httpd_ssl_start(&server,&config)!=ESP_OK) {server=nullptr;Serial.println("[web] HTTPS server could not start");return;}
  registerEndpoint("/",HTTP_GET,rootHandler);registerEndpoint("/api/pair",HTTP_POST,pairHandler);
  registerEndpoint("/api/status",HTTP_GET,statusHandler);registerEndpoint("/api/settings",HTTP_POST,settingsHandler);
  registerEndpoint("/api/wifi",HTTP_POST,wifiHandler);registerEndpoint("/api/refresh",HTTP_POST,refreshHandler);
  registerEndpoint("/api/export",HTTP_GET,exportHandler);registerEndpoint("/api/ota",HTTP_POST,otaHandler);
  registerEndpoint("/api/widget",HTTP_POST,widgetHandler);
  Serial.println("[web] Local HTTPS management ready");
}
void web_service_poll() {}
bool web_service_running() {return server!=nullptr;}
