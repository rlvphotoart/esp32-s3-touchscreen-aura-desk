#include "ui.h"
#include <lvgl.h>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdlib>

namespace {
constexpr uint32_t CANVAS=0xF4F5F0, CARD=0xFFFFFF, INK=0x172B40,
  MUTED=0x657587, LINE=0xDDE3E7, BLUE=0x315DDF, TEAL=0x177D70,
  AMBER=0xB36D13, RED=0xB23D4A, DOCK_MUTED=0x9FAFC0;
enum Page { HOME, WEATHER, TOOLS, SETTINGS, NETWORK, PASSWORD, LOCATION,
  ABOUT, AIR, RATES, TIMER, WELCOME, BROWSER, API_DATA };
enum Command { C_SCAN=100, C_CONNECT, C_SHOW_PASSWORD, C_REFRESH, C_BRIGHTNESS, C_ALWAYS_ON,
  C_SAVE_LOCATION, C_EXPLORE, C_TIMER_TOGGLE, C_TIMER_RESET, C_PRESET25,
  C_PRESET50, C_COUNTDOWN5, C_COUNTDOWN15, C_STOPWATCH, C_FORGET, C_REBOOT,
  C_OPEN_FOCUS };
UiActionCallback dispatch=nullptr;
UiSnapshot model{};
Page page=WELCOME;
bool first_snapshot=true, password_visible=false;
char chosen_ssid[33]{};
struct Widgets {
  lv_obj_t *status=nullptr, *clock=nullptr, *date=nullptr, *temp=nullptr,
    *condition=nullptr, *feels=nullptr, *aqi=nullptr, *aqi_hint=nullptr,
    *rate=nullptr, *rate_hint=nullptr, *focus=nullptr, *focus_label=nullptr,
    *focus_hint=nullptr, *updated=nullptr,
    *message=nullptr, *network_list=nullptr, *settings_body=nullptr,
    *ssid=nullptr, *password=nullptr,
    *keyboard=nullptr, *show=nullptr, *city=nullptr, *brightness=nullptr,
    *brightness_value=nullptr, *always_on=nullptr, *always_on_hint=nullptr,
    *timer_value=nullptr, *timer_state=nullptr,
    *timer_button=nullptr, *connect_button=nullptr, *weather_icon=nullptr,
    *detail=nullptr, *forecast[3]{}, *metrics[4]{}, *widget_title[2]{},
    *widget_value[2]{}, *widget_age[2]{};
} w;
uint32_t network_hash=0;
lv_coord_t settings_scroll_y=0;
int last_icon_code=-999;
enum TimerMode { FOCUS, COUNTDOWN, STOPWATCH };
TimerMode timer_mode=FOCUS;
uint32_t timer_duration=25UL*60*1000, timer_elapsed=0, timer_last_tick=0;
bool timer_running=false, timer_complete=false;

lv_color_t color(uint32_t c) { return lv_color_hex(c); }
void send(UiAction action,const char *a="",const char *b="") {
  if(dispatch) dispatch(action,a,b);
}
lv_obj_t *panel(lv_obj_t *parent,int x,int y,int width,int height,
                uint32_t bg=CANVAS,int radius=0,bool border=false) {
  lv_obj_t *o=lv_obj_create(parent);
  lv_obj_remove_style_all(o);
  lv_obj_set_pos(o,x,y); lv_obj_set_size(o,width,height);
  lv_obj_set_style_bg_color(o,color(bg),0);
  lv_obj_set_style_bg_opa(o,LV_OPA_COVER,0);
  lv_obj_set_style_radius(o,radius,0);
  lv_obj_set_style_border_color(o,color(LINE),0);
  lv_obj_set_style_border_width(o,border?1:0,0);
  lv_obj_set_style_pad_all(o,0,0);
  lv_obj_clear_flag(o,LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_clear_flag(o,LV_OBJ_FLAG_CLICKABLE);
  return o;
}
lv_obj_t *text(lv_obj_t *parent,int x,int y,int width,int height,const char *value,
               const lv_font_t *font=&lv_font_montserrat_16,uint32_t fg=INK) {
  lv_obj_t *o=lv_label_create(parent);
  lv_obj_set_pos(o,x,y); lv_obj_set_size(o,width,height);
  lv_label_set_long_mode(o,LV_LABEL_LONG_DOT);
  lv_label_set_text(o,value?value:"");
  lv_obj_set_style_text_font(o,font,0);
  lv_obj_set_style_text_color(o,color(fg),0);
  lv_obj_set_style_pad_all(o,0,0);
  lv_obj_clear_flag(o,LV_OBJ_FLAG_CLICKABLE);
  return o;
}
void center(lv_obj_t *o) { lv_obj_set_style_text_align(o,LV_TEXT_ALIGN_CENTER,0); }
void set(lv_obj_t *o,const char *value) {
  if(o && std::strcmp(lv_label_get_text(o),value?value:"")!=0)
    lv_label_set_text(o,value?value:"");
}
void show(Page p);
void refresh_widgets();
void action(lv_event_t *event);
lv_obj_t *button(lv_obj_t *parent,int x,int y,int width,int height,
                const char *caption,int command,uint32_t bg=BLUE,
                uint32_t fg=CARD,const lv_font_t *font=&lv_font_montserrat_16) {
  lv_obj_t *o=lv_btn_create(parent);
  lv_obj_remove_style_all(o);
  lv_obj_set_pos(o,x,y); lv_obj_set_size(o,width,height);
  lv_obj_set_style_bg_color(o,color(bg),0);
  lv_obj_set_style_bg_opa(o,LV_OPA_COVER,0);
  lv_obj_set_style_radius(o,14,0);
  lv_obj_set_style_bg_color(o,color(bg==CARD?0xE9EDF4:bg==INK?0x29445E:0x254BBC),LV_STATE_PRESSED);
  lv_obj_set_style_transform_zoom(o,250,LV_STATE_PRESSED);
  lv_obj_set_style_pad_all(o,0,0);
  lv_obj_add_event_cb(o,action,LV_EVENT_CLICKED,reinterpret_cast<void *>(static_cast<intptr_t>(command)));
  lv_obj_t *label=text(o,10,0,width-20,height,caption,font,fg);
  center(label); lv_obj_set_height(label,LV_SIZE_CONTENT);
  lv_obj_align(label,LV_ALIGN_CENTER,0,0);
  return o;
}
void clickable(lv_obj_t *o,int command) {
  lv_obj_add_flag(o,LV_OBJ_FLAG_CLICKABLE);
  lv_obj_add_event_cb(o,action,LV_EVENT_CLICKED,reinterpret_cast<void *>(static_cast<intptr_t>(command)));
  lv_obj_set_style_bg_color(o,color(0xE9EDF4),LV_STATE_PRESSED);
}
void header(const char *title,Page back=HOME,bool browserShortcut=false) {
  button(lv_scr_act(),12,8,48,48,LV_SYMBOL_LEFT,back,CANVAS,INK,&lv_font_montserrat_20);
  text(lv_scr_act(),72,19,browserShortcut?258:324,34,title,&lv_font_montserrat_24);
  if(browserShortcut) button(lv_scr_act(),350,8,110,48,"Browser",BROWSER,CARD,BLUE);
}
void dock(Page selected) {
  lv_obj_t *bar=panel(lv_scr_act(),0,424,480,56,INK);
  const char *names[]={"Home","Weather","Tools","Settings"};
  for(int i=0;i<4;i++) {
    lv_obj_t *b=button(bar,i*120,0,120,56,names[i],i,INK,
      selected==i?CARD:DOCK_MUTED,&lv_font_montserrat_14);
    lv_obj_set_style_radius(b,0,0);
    if(selected==i) panel(b,42,0,36,3,BLUE,2);
  }
}
void sun(lv_obj_t *parent,int x,int y,int size,uint32_t fg) {
  panel(parent,x+size/4,y+size/4,size/2,size/2,fg,LV_RADIUS_CIRCLE);
  panel(parent,x+size/2-1,y,2,size/6,fg,1);
  panel(parent,x+size/2-1,y+size*5/6,2,size/6,fg,1);
  panel(parent,x,y+size/2-1,size/6,2,fg,1);
  panel(parent,x+size*5/6,y+size/2-1,size/6,2,fg,1);
}
void weather_glyph(int code) {
  if(!w.weather_icon || code==last_icon_code) return;
  last_icon_code=code; lv_obj_clean(w.weather_icon);
  lv_obj_update_layout(w.weather_icon);
  int size=lv_obj_get_width(w.weather_icon);
  if(code<0) {
    panel(w.weather_icon,size/4,size/2-1,size/2,2,MUTED,1); return;
  }
  if(code==0) { sun(w.weather_icon,0,0,size,AMBER); return; }
  if(code<=2) sun(w.weather_icon,size/3,0,size*2/3,AMBER);
  uint32_t cloud_color=code<=3?0x94A4B6:MUTED;
  int base=size*6/10;
  panel(w.weather_icon,size/10,base-size/5,size*8/10,size/4,cloud_color,size/8);
  panel(w.weather_icon,size/5,base-size*4/10,size*4/10,size*4/10,cloud_color,LV_RADIUS_CIRCLE);
  panel(w.weather_icon,size*5/10,base-size*3/10,size*3/10,size*3/10,cloud_color,LV_RADIUS_CIRCLE);
  if(code==45||code==48) {
    panel(w.weather_icon,size/10,size*8/10,size*8/10,2,MUTED,1);
    panel(w.weather_icon,size/5,size*9/10,size*6/10,2,MUTED,1);
  } else if(code>=51) {
    for(int i=0;i<3;i++) panel(w.weather_icon,size*(3+i*2)/10,size*8/10,2,size/6,BLUE,1);
  }
}
const char *condition(int code) {
  if(code==0) return "Clear sky";
  if(code<=3) return "Partly cloudy";
  if(code==45||code==48) return "Fog";
  if(code>=51&&code<=57) return "Drizzle";
  if(code>=61&&code<=67) return "Rain";
  if(code>=71&&code<=77) return "Snow";
  if(code>=80&&code<=82) return "Rain showers";
  if(code>=85&&code<=86) return "Snow showers";
  if(code>=95) return "Thunderstorm";
  return "Weather";
}
const char *air_description(float aqi) {
  if(aqi<=20) return "Good"; if(aqi<=40) return "Fair";
  if(aqi<=60) return "Moderate"; if(aqi<=80) return "Poor";
  if(aqi<=100) return "Very poor"; return "Extremely poor";
}
uint32_t air_color(float aqi) { return aqi<=40?TEAL:aqi<=60?AMBER:RED; }
void age(char *out,size_t len,int minutes,bool valid=false) {
  if(minutes<0) std::snprintf(out,len,valid?"Saved data / age unavailable":"Waiting for first update");
  else if(minutes==0) std::snprintf(out,len,"Updated just now");
  else if(minutes<60) std::snprintf(out,len,"Updated %d min ago",minutes);
  else std::snprintf(out,len,"Updated %d h %d min ago",minutes/60,minutes%60);
}
lv_obj_t *home_card(int x,int y,const char *title,Page destination) {
  lv_obj_t *card=panel(lv_scr_act(),x,y,214,96,CARD,20,true);
  text(card,16,12,182,20,title,&lv_font_montserrat_14,MUTED);
  clickable(card,destination); return card;
}
void build_home() {
  text(lv_scr_act(),20,16,186,22,"AURA DESK",&lv_font_montserrat_16);
  lv_obj_t *status_btn=button(lv_scr_act(),272,4,188,48,"",NETWORK,CANVAS,TEAL);
  w.status=text(status_btn,8,15,172,24,"Offline",&lv_font_montserrat_14,MUTED);
  lv_obj_set_style_text_align(w.status,LV_TEXT_ALIGN_RIGHT,0);
  w.clock=text(lv_scr_act(),20,62,300,62,"--:--",&lv_font_montserrat_48);
  w.date=text(lv_scr_act(),20,130,300,24,"Connect to synchronize time",&lv_font_montserrat_14,MUTED);
  lv_obj_t *weather=panel(lv_scr_act(),326,56,134,104,CANVAS);
  clickable(weather,WEATHER); w.weather_icon=panel(weather,88,0,34,34,CANVAS);
  w.temp=text(weather,0,41,134,40,"--",&lv_font_montserrat_32);
  w.condition=text(weather,0,84,134,20,"Weather",&lv_font_montserrat_14,MUTED);
  lv_obj_t *a=home_card(20,178,"OUTSIDE",WEATHER);
  w.feels=text(a,16,34,182,34,"--",&lv_font_montserrat_24);
  text(a,16,72,182,18,"Feels like",&lv_font_montserrat_14,MUTED);
  a=home_card(246,178,"AIR QUALITY",AIR);
  w.aqi=text(a,16,34,182,34,"--",&lv_font_montserrat_24);
  w.aqi_hint=text(a,16,72,182,18,"European AQI",&lv_font_montserrat_14,MUTED);
  a=home_card(20,286,"EUR / RON",RATES);
  w.rate=text(a,16,34,182,34,"--",&lv_font_montserrat_24);
  w.rate_hint=text(a,16,72,182,18,"Reference rate",&lv_font_montserrat_14,MUTED);
  a=home_card(246,286,"FOCUS",TIMER);
  w.focus_label=lv_obj_get_child(a,0);
  w.focus=text(a,16,34,182,34,"25:00",&lv_font_montserrat_24);
  w.focus_hint=text(a,16,72,182,18,"Ready when you are",&lv_font_montserrat_14,MUTED);
  w.updated=text(lv_scr_act(),20,397,440,18,"Connect to Wi-Fi to receive updates",&lv_font_montserrat_14,MUTED);
  dock(HOME);
}
void build_weather() {
  header("Weather");
  text(lv_scr_act(),20,67,330,22,model.city,&lv_font_montserrat_16,MUTED);
  button(lv_scr_act(),382,62,78,48,"Refresh",C_REFRESH,CARD,BLUE,&lv_font_montserrat_14);
  w.temp=text(lv_scr_act(),20,101,230,62,"--",&lv_font_montserrat_48);
  w.condition=text(lv_scr_act(),20,170,420,28,"Waiting for weather",&lv_font_montserrat_20);
  w.metrics[3]=text(lv_scr_act(),20,197,440,18,"Sunrise / sunset unavailable",&lv_font_montserrat_14,MUTED);
  w.weather_icon=panel(lv_scr_act(),347,120,66,66,CANVAS);
  const char *labels[]={"Feels like","Humidity","Wind"};
  for(int i=0;i<3;i++) {
    lv_obj_t *p=panel(lv_scr_act(),20+i*150,225,140,66,CARD,14);
    text(p,12,10,116,20,labels[i],&lv_font_montserrat_14,MUTED);
    w.metrics[i]=text(p,12,36,116,27,"--",&lv_font_montserrat_20);
  }
  for(int i=0;i<3;i++) {
    lv_obj_t *p=panel(lv_scr_act(),20+i*150,304,140,68,CARD,14);
    w.forecast[i]=text(p,12,8,116,58,"--",&lv_font_montserrat_14);
    lv_label_set_long_mode(w.forecast[i],LV_LABEL_LONG_WRAP);
  }
  w.updated=text(lv_scr_act(),20,380,440,18,"Waiting for first update",&lv_font_montserrat_14,MUTED);
  text(lv_scr_act(),20,400,440,18,"Regional forecast / Open-Meteo",&lv_font_montserrat_14,MUTED);
  dock(WEATHER);
}
void build_tools() {
  header("A little more focus");
  text(lv_scr_act(),20,68,440,40,"Simple tools. Space to think.",&lv_font_montserrat_16,MUTED);
  lv_obj_t *p=panel(lv_scr_act(),20,119,440,128,INK,20);
  text(p,20,16,380,27,"Focus session",&lv_font_montserrat_24,CARD);
  text(p,20,55,380,22,"25 or 50 minutes, at your pace",&lv_font_montserrat_16,DOCK_MUTED);
  button(p,278,72,142,48,"Open timer",C_OPEN_FOCUS,BLUE,CARD);
  button(lv_scr_act(),20,266,214,76,"5 min countdown",C_COUNTDOWN5,CARD,INK);
  button(lv_scr_act(),246,266,214,76,"15 min countdown",C_COUNTDOWN15,CARD,INK);
  button(lv_scr_act(),20,360,440,48,"Stopwatch",C_STOPWATCH,CARD,INK);
  dock(TOOLS);
}
void row(lv_obj_t *parent,int y,const char *name,const char *value,int command) {
  lv_obj_t *o=panel(parent,0,y,440,64,CARD,14,true);
  text(o,16,11,356,23,name,&lv_font_montserrat_16);
  text(o,16,37,356,19,value,&lv_font_montserrat_14,MUTED);
  text(o,398,22,24,24,LV_SYMBOL_RIGHT,&lv_font_montserrat_16,MUTED);
  clickable(o,command);
}
void build_settings() {
  header("Settings",HOME,true);
  lv_obj_t *body=panel(lv_scr_act(),20,72,440,337,CANVAS);
  w.settings_body=body;
  lv_obj_add_flag(body,LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_scroll_dir(body,LV_DIR_VER);
  lv_obj_set_style_bg_color(body,color(LINE),LV_PART_SCROLLBAR);
  lv_obj_set_style_bg_opa(body,LV_OPA_COVER,LV_PART_SCROLLBAR);
  lv_obj_set_style_width(body,3,LV_PART_SCROLLBAR);
  row(body,0,"Network",model.wifiConnected?model.ssid:"Connect to your router",NETWORK);
  row(body,76,"Location",model.city[0]?model.city:"Bucharest (editable default)",LOCATION);
  lv_obj_t *p=panel(body,0,152,440,184,CARD,14,true);
  text(p,16,12,310,22,"Display brightness",&lv_font_montserrat_16);
  w.brightness_value=text(p,340,12,80,22,"--",&lv_font_montserrat_16,MUTED);
  w.brightness=lv_slider_create(p);
  lv_obj_set_pos(w.brightness,26,65); lv_obj_set_size(w.brightness,386,12);
  lv_slider_set_range(w.brightness,10,100);
  lv_slider_set_value(w.brightness,model.brightness?model.brightness:80,LV_ANIM_OFF);
  lv_obj_set_style_bg_color(w.brightness,color(LINE),LV_PART_MAIN);
  lv_obj_set_style_bg_color(w.brightness,color(BLUE),LV_PART_INDICATOR);
  lv_obj_set_style_bg_color(w.brightness,color(BLUE),LV_PART_KNOB);
  lv_obj_set_style_pad_all(w.brightness,12,LV_PART_KNOB);
  lv_obj_add_event_cb(w.brightness,action,LV_EVENT_RELEASED,reinterpret_cast<void *>(C_BRIGHTNESS));
  panel(p,16,96,408,1,LINE);
  text(p,16,111,326,23,"Always-on display",&lv_font_montserrat_16);
  w.always_on_hint=text(p,16,146,408,22,"",&lv_font_montserrat_14,MUTED);
  w.always_on=lv_switch_create(p);
  lv_obj_set_pos(w.always_on,358,106); lv_obj_set_size(w.always_on,64,40);
  lv_obj_set_ext_click_area(w.always_on,4);
  lv_obj_set_style_bg_color(w.always_on,color(LINE),LV_PART_MAIN);
  lv_obj_set_style_bg_color(w.always_on,color(BLUE),LV_PART_INDICATOR|LV_STATE_CHECKED);
  lv_obj_set_style_bg_color(w.always_on,color(CARD),LV_PART_KNOB);
  if(model.alwaysOnDisplay) lv_obj_add_state(w.always_on,LV_STATE_CHECKED);
  lv_obj_add_event_cb(w.always_on,action,LV_EVENT_VALUE_CHANGED,reinterpret_cast<void *>(C_ALWAYS_ON));
  row(body,348,"Browser configuration",model.wifiConnected?model.ip:"Connect to Wi-Fi first",BROWSER);
  row(body,424,"API widgets","Your own public data sources",API_DATA);
  row(body,500,"About & diagnostics","AURA Desk / Horizon interface",ABOUT);
  lv_obj_update_layout(body);
  lv_obj_scroll_to_y(body,settings_scroll_y,LV_ANIM_OFF);
  dock(SETTINGS);
}
void build_network_list();
void build_network() {
  header("Your network",SETTINGS);
  text(lv_scr_act(),20,67,330,23,"2.4 GHz Wi-Fi",&lv_font_montserrat_16,MUTED);
  button(lv_scr_act(),350,60,110,48,"Refresh",C_SCAN,CARD,BLUE);
  w.message=text(lv_scr_act(),20,112,440,42,"Searching for nearby networks...",&lv_font_montserrat_14,MUTED);
  lv_label_set_long_mode(w.message,LV_LABEL_LONG_WRAP);
  w.network_list=panel(lv_scr_act(),20,164,440,220,CANVAS);
  lv_obj_add_flag(w.network_list,LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_scroll_dir(w.network_list,LV_DIR_VER);
  lv_obj_set_style_bg_color(w.network_list,color(LINE),LV_PART_SCROLLBAR);
  lv_obj_set_style_bg_opa(w.network_list,LV_OPA_COVER,LV_PART_SCROLLBAR);
  lv_obj_set_style_width(w.network_list,3,LV_PART_SCROLLBAR);
  button(lv_scr_act(),20,404,284,56,"Enter network manually",PASSWORD,CARD,INK);
  button(lv_scr_act(),316,404,144,56,"Home",HOME,BLUE);
  build_network_list(); send(UiAction::ScanWifi);
}
void select_network(lv_event_t *event) {
  auto index=static_cast<unsigned>(reinterpret_cast<uintptr_t>(lv_event_get_user_data(event)));
  if(index<model.wifiCount && index<12) {
    std::snprintf(chosen_ssid,sizeof(chosen_ssid),"%s",model.networks[index].ssid);
    show(PASSWORD);
  }
}
void build_network_list() {
  if(!w.network_list) return;
  lv_obj_clean(w.network_list);
  for(unsigned i=0;i<model.wifiCount && i<12;i++) {
    const WifiEntry &n=model.networks[i];
    lv_obj_t *o=panel(w.network_list,0,i*64,440,56,CARD,14,true);
    text(o,16,10,314,23,n.ssid,&lv_font_montserrat_16);
    char detail[48]; std::snprintf(detail,sizeof(detail),"%s / %d dBm",n.secure?"Secured":"Open",n.rssi);
    text(o,16,34,350,18,detail,&lv_font_montserrat_14,MUTED);
    text(o,395,18,30,26,LV_SYMBOL_RIGHT,&lv_font_montserrat_16,MUTED);
    lv_obj_add_flag(o,LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(o,select_network,LV_EVENT_CLICKED,reinterpret_cast<void *>(static_cast<uintptr_t>(i)));
    lv_obj_set_style_bg_color(o,color(0xE9EDF4),LV_STATE_PRESSED);
  }
  if(!model.wifiCount) text(w.network_list,16,18,408,58,model.scanning?"Scanning...":"No networks yet. Refresh or enter a network manually.",&lv_font_montserrat_16,MUTED);
}
void focus_input(lv_event_t *event) {
  if(w.keyboard) lv_keyboard_set_textarea(w.keyboard,lv_event_get_target(event));
}
lv_obj_t *input(int x,int y,int width,const char *value,const char *placeholder,int maxlen) {
  lv_obj_t *o=lv_textarea_create(lv_scr_act());
  lv_obj_set_pos(o,x,y); lv_obj_set_size(o,width,48);
  lv_textarea_set_one_line(o,true); lv_textarea_set_max_length(o,maxlen);
  lv_textarea_set_text(o,value); lv_textarea_set_placeholder_text(o,placeholder);
  lv_obj_set_style_text_font(o,&lv_font_montserrat_16,0);
  lv_obj_set_style_text_color(o,color(INK),0);
  lv_obj_set_style_bg_color(o,color(CARD),0);
  lv_obj_set_style_border_color(o,color(LINE),0);
  lv_obj_set_style_border_width(o,1,0); lv_obj_set_style_radius(o,12,0);
  lv_obj_set_style_pad_all(o,12,0);
  lv_obj_set_style_border_color(o,color(BLUE),LV_STATE_FOCUSED);
  lv_obj_add_event_cb(o,focus_input,LV_EVENT_FOCUSED,nullptr);
  lv_obj_add_event_cb(o,focus_input,LV_EVENT_CLICKED,nullptr);
  return o;
}
void keyboard_event(lv_event_t *event) {
  if(lv_event_get_code(event)==LV_EVENT_CANCEL) {
    show(page==PASSWORD?NETWORK:SETTINGS);
  } else if(lv_event_get_code(event)==LV_EVENT_READY) {
    if(page==PASSWORD && w.connect_button) lv_event_send(w.connect_button,LV_EVENT_CLICKED,nullptr);
    else if(page==LOCATION && w.city && lv_textarea_get_text(w.city)[0]) {
      send(UiAction::SetLocation,lv_textarea_get_text(w.city)); show(WEATHER);
    }
  }
}
void keyboard(lv_obj_t *target,int y=296,int height=184) {
  w.keyboard=lv_keyboard_create(lv_scr_act());
  lv_obj_set_align(w.keyboard,LV_ALIGN_TOP_LEFT);
  lv_obj_set_pos(w.keyboard,0,y); lv_obj_set_size(w.keyboard,480,height);
  lv_keyboard_set_mode(w.keyboard,LV_KEYBOARD_MODE_TEXT_LOWER);
  lv_keyboard_set_textarea(w.keyboard,target);
  lv_keyboard_set_popovers(w.keyboard,false);
  lv_obj_set_style_bg_color(w.keyboard,color(LINE),LV_PART_MAIN);
  lv_obj_set_style_pad_all(w.keyboard,5,LV_PART_MAIN);
  lv_obj_set_style_pad_row(w.keyboard,5,LV_PART_MAIN);
  lv_obj_set_style_pad_column(w.keyboard,4,LV_PART_MAIN);
  lv_obj_set_style_bg_color(w.keyboard,color(CARD),LV_PART_ITEMS);
  lv_obj_set_style_text_color(w.keyboard,color(INK),LV_PART_ITEMS);
  lv_obj_set_style_text_font(w.keyboard,&lv_font_montserrat_16,LV_PART_ITEMS);
  lv_obj_set_style_radius(w.keyboard,5,LV_PART_ITEMS);
  lv_obj_set_style_border_width(w.keyboard,0,LV_PART_ITEMS);
  lv_obj_set_style_shadow_width(w.keyboard,0,LV_PART_ITEMS);
  lv_obj_add_event_cb(w.keyboard,keyboard_event,LV_EVENT_READY,nullptr);
  lv_obj_add_event_cb(w.keyboard,keyboard_event,LV_EVENT_CANCEL,nullptr);
}
void build_password() {
  header("Connect to Wi-Fi",NETWORK);
  text(lv_scr_act(),20,70,440,20,"NETWORK NAME",&lv_font_montserrat_14,MUTED);
  w.ssid=input(20,94,440,chosen_ssid,"Network name",32);
  text(lv_scr_act(),20,151,440,20,"PASSWORD",&lv_font_montserrat_14,MUTED);
  w.password=input(20,175,330,"","Leave blank for an open network",64);
  lv_textarea_set_password_mode(w.password,true);
  lv_textarea_set_password_show_time(w.password,0);
  password_visible=false;
  w.show=button(lv_scr_act(),360,175,100,48,"Show",C_SHOW_PASSWORD,CARD,INK);
  w.connect_button=button(lv_scr_act(),20,233,160,52,"Connect",C_CONNECT,BLUE);
  w.message=text(lv_scr_act(),194,234,266,53,"Your password stays on this device.",&lv_font_montserrat_14,MUTED);
  lv_label_set_long_mode(w.message,LV_LABEL_LONG_WRAP);
  keyboard(chosen_ssid[0]?w.password:w.ssid);
}
void build_location() {
  header("Set your location",SETTINGS);
  text(lv_scr_act(),20,76,440,48,"Enter a city. The weather location is resolved online.",&lv_font_montserrat_16,MUTED);
  lv_label_set_long_mode(lv_obj_get_child(lv_scr_act(),2),LV_LABEL_LONG_WRAP);
  w.city=input(20,143,440,model.city,"City, country",47);
  button(lv_scr_act(),20,208,156,52,"Save location",C_SAVE_LOCATION,BLUE);
  w.message=text(lv_scr_act(),192,210,268,54,"Bucharest is an editable default, not a detected location.",&lv_font_montserrat_14,MUTED);
  lv_label_set_long_mode(w.message,LV_LABEL_LONG_WRAP);
  keyboard(w.city,292,188);
}
void build_about() {
  header("About AURA",SETTINGS);
  lv_obj_t *body=panel(lv_scr_act(),20,70,440,390,CANVAS);
  lv_obj_add_flag(body,LV_OBJ_FLAG_SCROLLABLE); lv_obj_set_scroll_dir(body,LV_DIR_VER);
  lv_obj_set_style_bg_color(body,color(LINE),LV_PART_SCROLLBAR);
  lv_obj_set_style_bg_opa(body,LV_OPA_COVER,LV_PART_SCROLLBAR);
  lv_obj_set_style_width(body,3,LV_PART_SCROLLBAR);
  text(body,0,0,440,36,"AURA Desk",&lv_font_montserrat_32);
  text(body,0,43,440,24,"Horizon / an original interface",&lv_font_montserrat_16,MUTED);
  w.detail=text(body,0,84,440,216,"",&lv_font_montserrat_14);
  lv_label_set_long_mode(w.detail,LV_LABEL_LONG_WRAP);
  text(body,0,316,440,28,"Sources & data",&lv_font_montserrat_20);
  lv_obj_t *sources=text(body,0,354,440,190,
    "Weather: Open-Meteo.\nAir quality: Open-Meteo / CAMS ENSEMBLE.\nWeather and air quality are regional model data.\nRates: ECB reference rates; publication dates shown.\nOpen-Meteo hosted free access is for personal, non-commercial use.\nClock: network time; Europe/Bucharest.",
    &lv_font_montserrat_14,MUTED);
  lv_label_set_long_mode(sources,LV_LABEL_LONG_WRAP);
  button(body,0,560,214,52,"Restart device",C_REBOOT,CARD,INK);
  button(body,226,560,214,52,"Forget Wi-Fi",C_FORGET,CARD,RED);
}
void build_air() {
  header("Air quality");
  text(lv_scr_act(),20,70,440,23,model.city,&lv_font_montserrat_16,MUTED);
  lv_obj_t *p=panel(lv_scr_act(),20,111,440,173,INK,20);
  text(p,20,16,400,22,"EUROPEAN AIR QUALITY INDEX",&lv_font_montserrat_14,DOCK_MUTED);
  w.aqi=text(p,20,55,220,63,"--",&lv_font_montserrat_48,CARD);
  w.aqi_hint=text(p,20,125,400,28,"Waiting for data",&lv_font_montserrat_20,CARD);
  w.detail=text(lv_scr_act(),20,307,440,50,"PM2.5: --",&lv_font_montserrat_20);
  lv_label_set_long_mode(w.detail,LV_LABEL_LONG_WRAP);
  w.updated=text(lv_scr_act(),20,372,440,20,"Waiting for first update",&lv_font_montserrat_14,MUTED);
  text(lv_scr_act(),20,399,440,20,"Regional model / Open-Meteo + CAMS",&lv_font_montserrat_14,MUTED);
  dock(HOME);
}
void build_browser() {
  header("Browser access",SETTINGS);
  lv_obj_t *intro=text(lv_scr_act(),20,74,440,53,
    "Connect your phone or computer to the same router. Open this local address:",
    &lv_font_montserrat_16,MUTED);
  lv_label_set_long_mode(intro,LV_LABEL_LONG_WRAP);
  w.detail=text(lv_scr_act(),20,142,440,54,model.wifiConnected?model.browserUrl:"Connect to Wi-Fi first",
    &lv_font_montserrat_20,BLUE);
  lv_label_set_long_mode(w.detail,LV_LABEL_LONG_WRAP);
  lv_obj_t *p=panel(lv_scr_act(),20,214,440,116,INK,20);
  text(p,20,14,400,22,"DEVICE PAIRING CODE",&lv_font_montserrat_14,DOCK_MUTED);
  w.metrics[3]=text(p,20,47,400,59,model.adminCode[0]?model.adminCode:"------",&lv_font_montserrat_48,CARD);
  center(w.metrics[3]);
  lv_obj_t *note=text(lv_scr_act(),20,351,440,98,
    "The browser uses encrypted HTTPS. On first connection, trust this device's local certificate. Enter the pairing code on the page to change settings or install an update.",
    &lv_font_montserrat_14,MUTED);
  lv_label_set_long_mode(note,LV_LABEL_LONG_WRAP);
}
void build_api_data() {
  header("Your data",SETTINGS);
  text(lv_scr_act(),20,70,440,24,"Two configurable public API widgets",&lv_font_montserrat_16,MUTED);
  for(int i=0;i<2;i++) {
    lv_obj_t *p=panel(lv_scr_act(),20,117+i*137,440,118,CARD,20,true);
    w.widget_title[i]=text(p,20,13,400,25,"API widget",&lv_font_montserrat_16,MUTED);
    w.widget_value[i]=text(p,20,47,400,35,"Not configured",&lv_font_montserrat_24);
    w.widget_age[i]=text(p,20,91,400,18,"Configure from your browser",&lv_font_montserrat_14,MUTED);
  }
  button(lv_scr_act(),20,403,440,56,"Configure from browser",BROWSER,BLUE);
}
void build_rates() {
  header("Currency reference");
  text(lv_scr_act(),20,70,440,42,"Dated reference rates. Values are not executable quotes.",&lv_font_montserrat_16,MUTED);
  lv_obj_t *p=panel(lv_scr_act(),20,125,440,118,INK,20);
  text(p,20,16,400,20,"1 EURO",&lv_font_montserrat_14,DOCK_MUTED);
  w.rate=text(p,20,50,400,52,"-- RON",&lv_font_montserrat_32,CARD);
  p=panel(lv_scr_act(),20,260,440,83,CARD,20,true);
  text(p,20,14,400,22,"EUR / USD",&lv_font_montserrat_14,MUTED);
  w.detail=text(p,20,40,400,33,"--",&lv_font_montserrat_24);
  w.rate_hint=text(lv_scr_act(),20,362,440,24,"Waiting for a reference rate",&lv_font_montserrat_16,MUTED);
  text(lv_scr_act(),20,399,440,20,"Source: European Central Bank",&lv_font_montserrat_14,MUTED);
  dock(HOME);
}
void timer_display();
void build_timer() {
  header(timer_mode==FOCUS?"Focus session":timer_mode==COUNTDOWN?"Countdown":"Stopwatch",TOOLS);
  text(lv_scr_act(),20,75,440,25,timer_mode==FOCUS?"One thing at a time.":"Time, without distractions.",&lv_font_montserrat_16,MUTED);
  lv_obj_t *p=panel(lv_scr_act(),20,126,440,160,INK,24);
  w.timer_value=text(p,20,29,400,67,"25:00",&lv_font_montserrat_48,CARD); center(w.timer_value);
  w.timer_state=text(p,20,109,400,27,"Ready when you are",&lv_font_montserrat_16,DOCK_MUTED); center(w.timer_state);
  w.timer_button=button(lv_scr_act(),20,305,286,56,"Start",C_TIMER_TOGGLE,BLUE);
  button(lv_scr_act(),318,305,142,56,"Reset",C_TIMER_RESET,CARD,INK);
  if(timer_mode==FOCUS) {
    button(lv_scr_act(),20,380,214,48,"25 minutes",C_PRESET25,CARD,INK);
    button(lv_scr_act(),246,380,214,48,"50 minutes",C_PRESET50,CARD,INK);
  } else if(timer_mode==COUNTDOWN) {
    button(lv_scr_act(),20,380,214,48,"5 minutes",C_COUNTDOWN5,CARD,INK);
    button(lv_scr_act(),246,380,214,48,"15 minutes",C_COUNTDOWN15,CARD,INK);
  } else text(lv_scr_act(),20,387,440,47,"Timers continue while you browse. A reboot ends the session.",&lv_font_montserrat_14,MUTED);
  timer_display();
}
void build_welcome() {
  text(lv_scr_act(),28,27,424,24,"AURA DESK",&lv_font_montserrat_16);
  panel(lv_scr_act(),28,95,70,5,BLUE,3);
  text(lv_scr_act(),28,126,424,114,"Your day,\nin view.",&lv_font_montserrat_48);
  lv_label_set_long_mode(lv_obj_get_child(lv_scr_act(),2),LV_LABEL_LONG_WRAP);
  lv_obj_t *intro=text(lv_scr_act(),28,266,424,74,
    "A calmer place for weather, air quality, time and focus. Connect your router to begin.",&lv_font_montserrat_16,MUTED);
  lv_label_set_long_mode(intro,LV_LABEL_LONG_WRAP);
  button(lv_scr_act(),28,361,424,56,"Connect Wi-Fi",NETWORK,BLUE);
  button(lv_scr_act(),28,423,424,48,"Explore offline",C_EXPLORE,CANVAS,INK);
}
void show(Page p) {
  if(page==SETTINGS && w.settings_body) settings_scroll_y=lv_obj_get_scroll_y(w.settings_body);
  page=p; w=Widgets{}; network_hash=0; last_icon_code=-999;
  lv_obj_clean(lv_scr_act());
  lv_obj_set_style_bg_color(lv_scr_act(),color(CANVAS),0);
  lv_obj_set_style_bg_opa(lv_scr_act(),LV_OPA_COVER,0);
  lv_obj_set_style_pad_all(lv_scr_act(),0,0);
  lv_obj_clear_flag(lv_scr_act(),LV_OBJ_FLAG_SCROLLABLE);
  switch(p) {
    case HOME: build_home(); break; case WEATHER: build_weather(); break;
    case TOOLS: build_tools(); break; case SETTINGS: build_settings(); break;
    case NETWORK: build_network(); break; case PASSWORD: build_password(); break;
    case LOCATION: build_location(); break; case ABOUT: build_about(); break;
    case AIR: build_air(); break; case RATES: build_rates(); break;
    case TIMER: build_timer(); break; case WELCOME: build_welcome(); break;
    case BROWSER: build_browser(); break;
    case API_DATA: build_api_data(); break;
  }
  refresh_widgets();
}
void timer_display() {
  uint32_t duration=timer_mode==STOPWATCH?timer_elapsed:
    timer_elapsed>=timer_duration?0:timer_duration-timer_elapsed;
  uint32_t seconds=(duration+(timer_mode==STOPWATCH?0:999))/1000;
  char buf[24];
  if(seconds>=3600) std::snprintf(buf,sizeof(buf),"%lu:%02lu:%02lu",
    static_cast<unsigned long>(seconds/3600),static_cast<unsigned long>((seconds/60)%60),static_cast<unsigned long>(seconds%60));
  else std::snprintf(buf,sizeof(buf),"%02lu:%02lu",static_cast<unsigned long>(seconds/60),static_cast<unsigned long>(seconds%60));
  set(w.timer_value,buf); set(w.focus,buf);
  set(w.focus_label,timer_mode==FOCUS?"FOCUS":timer_mode==COUNTDOWN?"COUNTDOWN":"STOPWATCH");
  set(w.focus_hint,timer_complete?"Session complete":timer_running?"In progress":timer_elapsed?"Paused":"Ready when you are");
  set(w.timer_state,timer_complete?"Session complete":timer_running?"In progress":timer_elapsed?"Paused":"Ready when you are");
  if(w.timer_button) set(lv_obj_get_child(w.timer_button,0),timer_running?"Pause":timer_complete?"Start again":timer_elapsed?"Resume":"Start");
  if(w.timer_value) lv_obj_set_style_text_color(w.timer_value,color(timer_complete?0x68D4B8:CARD),0);
}
void timer_tick(lv_timer_t *) {
  uint32_t now=lv_tick_get(), delta=now-timer_last_tick; timer_last_tick=now;
  if(timer_running) {
    if(timer_mode==STOPWATCH) {
      if(timer_elapsed<359999000UL) timer_elapsed+=delta;
      if(timer_elapsed>359999000UL) timer_elapsed=359999000UL;
    } else {
      timer_elapsed+=delta;
      if(timer_elapsed>=timer_duration) {
        timer_elapsed=timer_duration; timer_running=false; timer_complete=true;
      }
    }
  }
  timer_display();
}
void timer_preset(TimerMode mode,uint32_t minutes) {
  timer_mode=mode; timer_duration=minutes*60*1000; timer_elapsed=0;
  timer_running=false; timer_complete=false; timer_last_tick=lv_tick_get(); show(TIMER);
}
void action(lv_event_t *event) {
  int command=static_cast<int>(reinterpret_cast<intptr_t>(lv_event_get_user_data(event)));
  if(command>=HOME && command<=API_DATA) {
    if(command==PASSWORD) chosen_ssid[0]='\0';
    show(static_cast<Page>(command)); return;
  }
  switch(command) {
    case C_SCAN: send(UiAction::ScanWifi); set(w.message,"Searching for nearby networks..."); break;
    case C_CONNECT:
      if(w.ssid && lv_textarea_get_text(w.ssid)[0]) {
        if(model.wifiConnected && std::strcmp(model.ssid,lv_textarea_get_text(w.ssid))==0) {
          show(HOME); break;
        }
        if(std::strlen(lv_textarea_get_text(w.ssid))>32 || std::strlen(lv_textarea_get_text(w.password))>64) {
          set(w.message,"Network names allow 32 bytes; passwords allow 64 bytes."); break;
        }
        send(UiAction::ConnectWifi,lv_textarea_get_text(w.ssid),lv_textarea_get_text(w.password));
        set(w.message,"Connecting to router...");
      } else set(w.message,"Enter a network name first.");
      break;
    case C_SHOW_PASSWORD:
      password_visible=!password_visible;
      lv_textarea_set_password_mode(w.password,!password_visible);
      set(lv_obj_get_child(w.show,0),password_visible?"Hide":"Show"); break;
    case C_REFRESH: send(UiAction::RefreshData); break;
    case C_BRIGHTNESS: {
      char value[8]; std::snprintf(value,sizeof(value),"%d",lv_slider_get_value(w.brightness));
      send(UiAction::SetBrightness,value); break;
    }
    case C_ALWAYS_ON:
      model.alwaysOnDisplay=lv_obj_has_state(w.always_on,LV_STATE_CHECKED);
      send(UiAction::SetAlwaysOn,model.alwaysOnDisplay?"1":"0");
      set(w.always_on_hint,model.alwaysOnDisplay?"Keeps your selected brightness.":"Dims after 3 minutes of inactivity.");
      break;
    case C_SAVE_LOCATION:
      if(w.city && lv_textarea_get_text(w.city)[0]) {
        send(UiAction::SetLocation,lv_textarea_get_text(w.city));
        show(WEATHER);
      } else set(w.message,"Enter a city first.");
      break;
    case C_EXPLORE: send(UiAction::ExploreOffline); show(HOME); break;
    case C_TIMER_TOGGLE:
      if(timer_complete) { timer_elapsed=0; timer_complete=false; }
      timer_running=!timer_running; timer_last_tick=lv_tick_get(); timer_display(); break;
    case C_TIMER_RESET:
      timer_elapsed=0; timer_running=false; timer_complete=false; timer_display(); break;
    case C_OPEN_FOCUS:
      if(timer_mode==FOCUS) show(TIMER);
      else timer_preset(FOCUS,25);
      break;
    case C_PRESET25: timer_preset(FOCUS,25); break;
    case C_PRESET50: timer_preset(FOCUS,50); break;
    case C_COUNTDOWN5: timer_preset(COUNTDOWN,5); break;
    case C_COUNTDOWN15: timer_preset(COUNTDOWN,15); break;
    case C_STOPWATCH: timer_preset(STOPWATCH,0); break;
    case C_FORGET: send(UiAction::ForgetWifi); show(NETWORK); break;
    case C_REBOOT: send(UiAction::Reboot); break;
  }
}
void refresh_widgets() {
  char buf[700], part[100];
  set(w.status,model.wifiConnected?(model.internetAvailable?"Online":"Wi-Fi connected"):"Offline");
  set(w.clock,model.timeSynced?model.clock:"--:--");
  set(w.date,model.timeSynced?model.date:"Connect to synchronize time");
  weather_glyph(model.weatherValid?model.weatherCode:-1);
  if(model.weatherValid) {
    std::snprintf(buf,sizeof(buf),"%.0f °C",model.temperature); set(w.temp,buf);
    set(w.condition,condition(model.weatherCode));
    std::snprintf(buf,sizeof(buf),"%.0f °C",model.feelsLike); set(w.feels,buf); set(w.metrics[0],buf);
    std::snprintf(buf,sizeof(buf),"%.0f%%",model.humidity); set(w.metrics[1],buf);
    std::snprintf(buf,sizeof(buf),"%.0f km/h",model.wind); set(w.metrics[2],buf);
    if(page==WEATHER) {
      std::snprintf(buf,sizeof(buf),"Sunrise %s / sunset %s",model.sunrise[0]?model.sunrise:"--",model.sunset[0]?model.sunset:"--");
      set(w.metrics[3],buf);
    }
    for(int i=0;i<3;i++) {
      const ForecastDay &f=model.forecast[i];
      std::snprintf(buf,sizeof(buf),"%s\n%.0f° / %.0f°\nRain %.0f%%",f.day,f.high,f.low,f.rain);
      set(w.forecast[i],buf);
    }
  } else {
    set(w.temp,"--"); set(w.feels,"--"); set(w.condition,page==HOME?"No data yet":"Waiting for weather");
    for(auto metric:w.metrics) set(metric,"--");
  }
  if(model.airValid) {
    std::snprintf(buf,sizeof(buf),"%.0f",model.aqi); set(w.aqi,buf);
    set(w.aqi_hint,air_description(model.aqi));
    if(w.aqi && page==HOME) lv_obj_set_style_text_color(w.aqi,color(air_color(model.aqi)),0);
    if(page==AIR) {
      std::snprintf(buf,sizeof(buf),"PM2.5: %.1f ug/m3\nEuropean index / regional forecast",model.pm25); set(w.detail,buf);
    }
  } else { set(w.aqi,"--"); set(w.aqi_hint,page==HOME?"European AQI":"Waiting for data"); }
  if(model.ratesValid) {
    std::snprintf(buf,sizeof(buf),page==RATES?"%.4f RON":"%.4f",model.eurRon); set(w.rate,buf);
    std::snprintf(buf,sizeof(buf),"%s",model.rateDate); set(w.rate_hint,buf);
    if(page==RATES) { std::snprintf(buf,sizeof(buf),"%.4f USD",model.eurUsd); set(w.detail,buf); }
  } else { set(w.rate,page==RATES?"-- RON":"--"); set(w.rate_hint,page==RATES?"Waiting for reference rate":"Not updated yet"); }
  if(w.updated) {
    const bool valid=page==AIR?model.airValid:model.weatherValid;
    if(page==AIR) age(buf,sizeof(buf),model.airValid?model.airAgeMinutes:-1,model.airValid);
    else age(buf,sizeof(buf),model.weatherValid?model.weatherAgeMinutes:-1,model.weatherValid);
    if(!model.wifiConnected) {
      if(valid) {
        std::snprintf(part,sizeof(part),"Offline / %s",buf); set(w.updated,part);
      } else set(w.updated,"Connect to Wi-Fi to receive updates");
    } else if(model.fetching) set(w.updated,"Refreshing data...");
    else if((page==AIR&&model.airAgeMinutes>180)||(page!=AIR&&model.weatherAgeMinutes>120)) {
      std::snprintf(part,sizeof(part),"Saved data / %s",buf); set(w.updated,part);
    } else set(w.updated,buf);
  }
  if(page==NETWORK) {
    std::snprintf(buf,sizeof(buf),"%s%s%s",model.connection,
      model.message[0]?" / ":"",model.message); set(w.message,buf);
    uint32_t hash=2166136261UL;
    const unsigned char *bytes=reinterpret_cast<const unsigned char *>(model.networks);
    for(size_t i=0;i<sizeof(model.networks);i++) { hash^=bytes[i]; hash*=16777619UL; }
    hash^=model.wifiCount; hash^=model.scanning?0x10000:0;
    if(hash!=network_hash) { network_hash=hash; build_network_list(); }
  }
  if(page==PASSWORD && w.message) {
    if(model.wifiConnected) {
      std::snprintf(buf,sizeof(buf),"%s. Tap Continue.",model.internetAvailable?"Internet ready":"Router connected / checking internet");
      set(w.message,buf);
      if(w.connect_button && std::strcmp(model.ssid,lv_textarea_get_text(w.ssid))==0)
        set(lv_obj_get_child(w.connect_button,0),"Continue");
    } else if(model.connection[0] && std::strcmp(model.connection,"Offline")!=0) {
      std::snprintf(buf,sizeof(buf),"%s%s%s",model.connection,model.message[0]?" / ":"",model.message); set(w.message,buf);
    }
  }
  if(page==SETTINGS && w.brightness_value) {
    std::snprintf(buf,sizeof(buf),"%d%%",lv_slider_get_value(w.brightness)); set(w.brightness_value,buf);
    if(model.alwaysOnDisplay) lv_obj_add_state(w.always_on,LV_STATE_CHECKED);
    else lv_obj_clear_state(w.always_on,LV_STATE_CHECKED);
    set(w.always_on_hint,model.alwaysOnDisplay?"Keeps your selected brightness.":"Dims after 3 minutes of inactivity.");
  }
  if(page==ABOUT && w.detail) {
    std::snprintf(buf,sizeof(buf),
      "Firmware %s\nUptime %lu min / reset: %s\nHeap %lu KB / minimum %lu KB\nPSRAM %lu MB\nNetwork: %s / %d dBm\nBrowser: %s\nPairing is required for configuration and updates.\nWeather: %s\nAir quality: %s\nReference rates: %s",
      model.firmware,static_cast<unsigned long>(model.uptimeSeconds/60),model.resetReason,
      static_cast<unsigned long>(model.freeHeap/1024),static_cast<unsigned long>(model.minimumHeap/1024),
      static_cast<unsigned long>(model.psramBytes/(1024*1024)),model.wifiConnected?model.ssid:"Offline",model.rssi,
      model.wifiConnected?model.browserUrl:"available after Wi-Fi setup",model.weatherTime[0]?model.weatherTime:"not fetched",
      model.airTime[0]?model.airTime:"not fetched",model.rateDate[0]?model.rateDate:"not fetched");
    set(w.detail,buf);
  }
  if(page==BROWSER) {
    set(w.detail,model.wifiConnected?model.browserUrl:"Connect to Wi-Fi first");
    set(w.metrics[3],model.adminCode[0]?model.adminCode:"------");
  }
  if(page==API_DATA) {
    for(int i=0;i<2;i++) {
      const ApiWidget &widget=model.widgets[i];
      if(widget.label[0]) set(w.widget_title[i],widget.label);
      else { std::snprintf(buf,sizeof(buf),"API widget %d",i+1); set(w.widget_title[i],buf); }
      if(!widget.enabled) {
        set(w.widget_value[i],"Not configured"); set(w.widget_age[i],"Configure from your browser");
      } else if(!widget.valid) {
        set(w.widget_value[i],"--"); set(w.widget_age[i],"Waiting for first update");
      } else {
        std::snprintf(buf,sizeof(buf),"%s%s%s",widget.value,widget.unit[0]?" ":"",widget.unit);
        set(w.widget_value[i],buf); age(buf,sizeof(buf),widget.ageMinutes,true);
        if(!model.wifiConnected) {
          std::snprintf(part,sizeof(part),"Offline / %s",buf);set(w.widget_age[i],part);
        } else set(w.widget_age[i],buf);
      }
    }
  }
  timer_display();
}
} // namespace

void ui_init(UiActionCallback callback) {
  dispatch=callback;
  timer_last_tick=lv_tick_get();
  lv_timer_create(timer_tick,200,nullptr);
  show(WELCOME);
}
void ui_update(const UiSnapshot &snapshot) {
  model=snapshot;
  if(first_snapshot) {
    first_snapshot=false;
    if(!model.setupRequired) show(HOME);
  }
  refresh_widgets();
}
void ui_show_page(int target) {
  if(target>=HOME && target<=API_DATA) { show(static_cast<Page>(target)); refresh_widgets(); }
}
