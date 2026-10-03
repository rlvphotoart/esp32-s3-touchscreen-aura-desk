// Host visual verification of the real LVGL interface; fixture data never ships.
#include <lvgl.h>
#include "ui.h"
#include "firmware_version.h"
#include <cstdio>
#include <cstring>
#include <cassert>

static unsigned char pixels[480*480*3];
static lv_color_t draw_buffer[480*40];
static lv_point_t touch_point{};
static bool touch_pressed=false;
static void read_touch(lv_indev_drv_t *,lv_indev_data_t *data) {
  data->point=touch_point;
  data->state=touch_pressed?LV_INDEV_STATE_PR:LV_INDEV_STATE_REL;
}
static void flush(lv_disp_drv_t *driver,const lv_area_t *area,lv_color_t *data) {
  for(int y=area->y1;y<=area->y2;y++) for(int x=area->x1;x<=area->x2;x++) {
    uint32_t c=lv_color_to32(*data++);
    if(x>=0&&x<480&&y>=0&&y<480) {
      unsigned char *p=&pixels[(y*480+x)*3]; p[0]=(c>>16)&255; p[1]=(c>>8)&255; p[2]=c&255;
    }
  }
  lv_disp_flush_ready(driver);
}
static UiAction last_action=UiAction::RefreshData;
static unsigned action_count=0;
static char action_first[100],action_second[100];
static void callback(UiAction action,const char *first,const char *second) {
  last_action=action;action_count++;
  std::snprintf(action_first,sizeof(action_first),"%s",first);
  std::snprintf(action_second,sizeof(action_second),"%s",second);
}
static lv_obj_t *find_textarea(lv_obj_t *root,unsigned target,unsigned &count) {
  if(lv_obj_check_type(root,&lv_textarea_class) && count++==target) return root;
  for(uint32_t i=0;i<lv_obj_get_child_cnt(root);i++) {
    if(auto found=find_textarea(lv_obj_get_child(root,i),target,count)) return found;
  }
  return nullptr;
}
static lv_obj_t *find_label(lv_obj_t *root,const char *caption) {
  if(lv_obj_check_type(root,&lv_label_class) && std::strcmp(lv_label_get_text(root),caption)==0) return root;
  for(uint32_t i=0;i<lv_obj_get_child_cnt(root);i++) {
    if(auto found=find_label(lv_obj_get_child(root,i),caption)) return found;
  }
  return nullptr;
}
static lv_obj_t *find_keyboard(lv_obj_t *root) {
  if(lv_obj_check_type(root,&lv_keyboard_class)) return root;
  for(uint32_t i=0;i<lv_obj_get_child_cnt(root);i++) {
    if(auto found=find_keyboard(lv_obj_get_child(root,i))) return found;
  }
  return nullptr;
}
static lv_obj_t *find_switch(lv_obj_t *root) {
  if(lv_obj_check_type(root,&lv_switch_class)) return root;
  for(uint32_t i=0;i<lv_obj_get_child_cnt(root);i++) {
    if(auto found=find_switch(lv_obj_get_child(root,i))) return found;
  }
  return nullptr;
}
static void tap_at(int x,int y) {
  touch_point.x=x;touch_point.y=y;touch_pressed=true;
  lv_tick_inc(35);lv_timer_handler();
  touch_pressed=false;lv_tick_inc(35);lv_timer_handler();
}
static void print_labels(lv_obj_t *root) {
  if(lv_obj_check_type(root,&lv_label_class)) std::fprintf(stderr,"Label: %s\n",lv_label_get_text(root));
  for(uint32_t i=0;i<lv_obj_get_child_cnt(root);i++) print_labels(lv_obj_get_child(root,i));
}
static void tap_label(const char *caption) {
  lv_obj_update_layout(lv_scr_act());
  lv_obj_t *label=find_label(lv_scr_act(),caption);
  if(!label) {std::fprintf(stderr,"Missing tappable caption: %s\n",caption);print_labels(lv_scr_act());}
  assert(label);
  lv_obj_update_layout(lv_scr_act());lv_area_t bounds;
  lv_obj_get_coords(lv_obj_get_parent(label),&bounds);
  tap_at((bounds.x1+bounds.x2)/2,(bounds.y1+bounds.y2)/2);
}
int main(int argc,char **argv) {
  const char *directory=argc>1?argv[1]:".";
  bool fixture=argc>2 && std::strcmp(argv[2],"--fixture")==0;
  lv_init(); lv_disp_draw_buf_t buffer; lv_disp_draw_buf_init(&buffer,draw_buffer,nullptr,480*40);
  lv_disp_drv_t driver; lv_disp_drv_init(&driver); driver.hor_res=480;driver.ver_res=480;
  driver.draw_buf=&buffer;driver.flush_cb=flush;lv_disp_drv_register(&driver);
  lv_indev_drv_t touch;lv_indev_drv_init(&touch);touch.type=LV_INDEV_TYPE_POINTER;
  touch.read_cb=read_touch;lv_indev_drv_register(&touch);
  ui_init(callback);
  UiSnapshot s{};
  std::snprintf(s.city,sizeof(s.city),"Bucharest");
  std::snprintf(s.firmware,sizeof(s.firmware),"AURA Desk " AURA_VERSION);
  std::snprintf(s.connection,sizeof(s.connection),"Offline");
  s.setupRequired=true; s.brightness=80; s.weatherAgeMinutes=-1; s.airAgeMinutes=-1;
  s.psramBytes=8*1024*1024; s.freeHeap=221184;s.minimumHeap=180224;
  if(fixture) {
    s.timeSynced=true; s.wifiConnected=true;s.internetAvailable=true;
    s.weatherValid=true;s.airValid=true;s.ratesValid=true;
    std::snprintf(s.clock,sizeof(s.clock),"19:42");std::snprintf(s.date,sizeof(s.date),"Saturday, 3 October");
    std::snprintf(s.connection,sizeof(s.connection),"Online");std::snprintf(s.ssid,sizeof(s.ssid),"Preview network");
    std::snprintf(s.ip,sizeof(s.ip),"192.0.2.1");std::snprintf(s.browserUrl,sizeof(s.browserUrl),"https://192.0.2.1/");
    std::snprintf(s.adminCode,sizeof(s.adminCode),"000000");
    s.temperature=18;s.feelsLike=17;s.humidity=61;s.wind=8;s.aqi=24;s.pm25=7.2;
    s.eurRon=5.0891;s.eurUsd=1.1724;s.weatherCode=1;s.weatherAgeMinutes=3;s.airAgeMinutes=21;
    std::snprintf(s.rateDate,sizeof(s.rateDate),"2026-10-02");
    std::snprintf(s.sunrise,sizeof(s.sunrise),"07:14");std::snprintf(s.sunset,sizeof(s.sunset),"18:53");
    for(int i=0;i<3;i++) {
      std::snprintf(s.forecast[i].day,sizeof(s.forecast[i].day),i==0?"Today":i==1?"Sunday":"Monday");
      s.forecast[i].high=20+i;s.forecast[i].low=10+i;s.forecast[i].rain=10+10*i;
    }
  }
  ui_update(s);
  const char *names[]={"home","weather","tools","settings","network","password","location","about","air","rates","timer","welcome","browser","api_widgets"};
  for(int page=0;page<14;page++) {
    ui_show_page(page);ui_update(s);lv_tick_inc(100);lv_timer_handler();lv_refr_now(nullptr);
    char path[512];std::snprintf(path,sizeof(path),"%s/%s%s.ppm",directory,names[page],fixture?"_fixture":"_offline");
    FILE *file=std::fopen(path,"wb");assert(file);std::fprintf(file,"P6\n480 480\n255\n");
    assert(std::fwrite(pixels,1,sizeof(pixels),file)==sizeof(pixels));std::fclose(file);
  }
  // Settings presents both display controls immediately and changes modes without
  // rebuilding the screen, emitting duplicate commands, or changing brightness.
  ui_show_page(3); lv_obj_update_layout(lv_scr_act());
  lv_obj_t *always_on=find_switch(lv_scr_act()); assert(always_on);
  lv_area_t bounds; lv_obj_get_coords(always_on,&bounds);
  assert(bounds.y1>=72 && bounds.y2<409);
  assert(!lv_obj_has_state(always_on,LV_STATE_CHECKED));
  assert(find_label(lv_scr_act(),"Dims after 3 minutes of inactivity."));
  unsigned setting_before=action_count;
  for(int i=0;i<20;i++) ui_update(s);
  assert(action_count==setting_before && find_switch(lv_scr_act())==always_on);
  lv_obj_add_state(always_on,LV_STATE_CHECKED);
  lv_event_send(always_on,LV_EVENT_VALUE_CHANGED,nullptr);
  assert(action_count==setting_before+1 && last_action==UiAction::SetAlwaysOn);
  assert(std::strcmp(action_first,"1")==0);
  assert(find_label(lv_scr_act(),"Keeps your selected brightness."));
  s.alwaysOnDisplay=true;
  for(int i=0;i<20;i++) ui_update(s);
  assert(action_count==setting_before+1 && find_switch(lv_scr_act())==always_on);
  ui_show_page(0); ui_show_page(3);
  always_on=find_switch(lv_scr_act()); assert(always_on);
  assert(lv_obj_has_state(always_on,LV_STATE_CHECKED));
  lv_tick_inc(100);lv_timer_handler();lv_refr_now(nullptr);
  char mode_path[512];std::snprintf(mode_path,sizeof(mode_path),"%s/settings_always_on%s.ppm",directory,fixture?"_fixture":"_offline");
  FILE *mode_file=std::fopen(mode_path,"wb"); assert(mode_file);
  std::fprintf(mode_file,"P6\n480 480\n255\n");
  assert(std::fwrite(pixels,1,sizeof(pixels),mode_file)==sizeof(pixels));std::fclose(mode_file);
  lv_obj_clear_state(always_on,LV_STATE_CHECKED);
  lv_event_send(always_on,LV_EVENT_VALUE_CHANGED,nullptr);
  assert(action_count==setting_before+2 && last_action==UiAction::SetAlwaysOn);
  assert(std::strcmp(action_first,"0")==0);
  s.alwaysOnDisplay=false; ui_update(s);
  assert(action_count==setting_before+2 && !lv_obj_has_state(always_on,LV_STATE_CHECKED));
  // A browser-origin setting update is reflected without dispatching it again.
  s.alwaysOnDisplay=true; ui_update(s);
  assert(action_count==setting_before+2 && lv_obj_has_state(always_on,LV_STATE_CHECKED));
  lv_obj_t *about=find_label(lv_scr_act(),"About & diagnostics"); assert(about);
  lv_obj_scroll_to_view_recursive(lv_obj_get_parent(about),LV_ANIM_OFF);
  lv_obj_update_layout(lv_scr_act()); lv_obj_get_coords(lv_obj_get_parent(about),&bounds);
  assert(bounds.y1>=72 && bounds.y2<409);
  lv_obj_t *home=find_label(lv_scr_act(),"Home"); assert(home);
  lv_obj_get_coords(lv_obj_get_parent(home),&bounds); assert(bounds.y1==424 && bounds.y2==479);
  s.alwaysOnDisplay=false; ui_update(s);
  // A network/status refresh must not discard typed credentials or focused widgets.
  ui_show_page(5); unsigned count=0;lv_obj_t *ssid=find_textarea(lv_scr_act(),0,count);
  count=0;lv_obj_t *password=find_textarea(lv_scr_act(),1,count);assert(ssid&&password);
  lv_textarea_set_text(ssid,"Test network");lv_textarea_set_text(password,"test-only-password");
  for(int i=0;i<20;i++) {ui_update(s);lv_tick_inc(100);lv_timer_handler();}
  assert(std::strcmp(lv_textarea_get_text(ssid),"Test network")==0);
  assert(std::strcmp(lv_textarea_get_text(password),"test-only-password")==0);
  assert(lv_textarea_get_password_mode(password));
  assert(lv_textarea_get_password_show_time(password)==0);
  lv_obj_t *reveal=find_label(lv_scr_act(),"Show");assert(reveal);
  lv_event_send(lv_obj_get_parent(reveal),LV_EVENT_CLICKED,nullptr);
  assert(!lv_textarea_get_password_mode(password));
  lv_obj_t *hide=find_label(lv_scr_act(),"Hide");assert(hide);
  lv_event_send(lv_obj_get_parent(hide),LV_EVENT_CLICKED,nullptr);
  assert(lv_textarea_get_password_mode(password));
  lv_obj_t *kb=find_keyboard(lv_scr_act());assert(kb);
  lv_keyboard_set_mode(kb,LV_KEYBOARD_MODE_SPECIAL);
  assert(lv_keyboard_get_mode(kb)==LV_KEYBOARD_MODE_SPECIAL);
  lv_event_send(kb,LV_EVENT_READY,nullptr);
  assert(last_action==UiAction::ConnectWifi);
  assert(std::strcmp(action_first,"Test network")==0);
  assert(std::strcmp(action_second,"test-only-password")==0);
  unsigned before=action_count;
  lv_textarea_set_text(ssid,"éééééééééééééééééé"); // 18 characters, 36 bytes.
  lv_event_send(kb,LV_EVENT_READY,nullptr);assert(action_count==before);
  ui_show_page(10);
  lv_obj_update_layout(lv_scr_act());
  lv_obj_t *start=find_label(lv_scr_act(),"Start");assert(start);
  lv_event_send(lv_obj_get_parent(start),LV_EVENT_CLICKED,nullptr);
  lv_tick_inc(2000);lv_timer_handler();ui_update(s);
  assert(find_label(lv_scr_act(),"24:58"));
  lv_obj_t *pause=find_label(lv_scr_act(),"Pause");assert(pause);
  lv_event_send(lv_obj_get_parent(pause),LV_EVENT_CLICKED,nullptr);
  lv_tick_inc(5000);lv_timer_handler();ui_update(s);
  assert(find_label(lv_scr_act(),"24:58"));
  // Exercise the user's real navigation sequences through LVGL pointer hit tests.
  ui_show_page(2);tap_label("5 min countdown");
  assert(find_label(lv_scr_act(),"05:00"));
  tap_at(36,32);assert(find_label(lv_scr_act(),"A little more focus"));
  tap_label("Open timer");
  bool focus_entry=find_label(lv_scr_act(),"Focus session") &&
    find_label(lv_scr_act(),"25 minutes") && find_label(lv_scr_act(),"50 minutes");
  std::printf("Navigation probe: countdown -> Tools -> Open timer selects Focus = %s\n",focus_entry?"PASS":"FAIL");
  assert(focus_entry);
  tap_label("50 minutes");assert(find_label(lv_scr_act(),"50:00"));
  tap_label("25 minutes");assert(find_label(lv_scr_act(),"25:00"));
  tap_label("Start");lv_tick_inc(2000);lv_timer_handler();
  tap_at(36,32);tap_label("Open timer");
  assert(find_label(lv_scr_act(),"Focus session") && find_label(lv_scr_act(),"Pause"));
  assert(find_label(lv_scr_act(),"24:58"));
  tap_label("Pause");lv_tick_inc(5000);lv_timer_handler();
  assert(find_label(lv_scr_act(),"24:58"));
  tap_at(36,32);tap_label("15 min countdown");
  assert(find_label(lv_scr_act(),"Countdown") && find_label(lv_scr_act(),"15:00"));
  tap_label("5 minutes");assert(find_label(lv_scr_act(),"05:00"));
  tap_label("15 minutes");assert(find_label(lv_scr_act(),"15:00"));
  tap_label("Start");lv_tick_inc(2000);lv_timer_handler();
  assert(find_label(lv_scr_act(),"14:58"));
  tap_label("Pause");lv_tick_inc(5000);lv_timer_handler();
  assert(find_label(lv_scr_act(),"14:58"));
  tap_at(36,32);tap_label("Open timer");
  assert(find_label(lv_scr_act(),"Focus session") && find_label(lv_scr_act(),"25:00"));
  tap_label("50 minutes");assert(find_label(lv_scr_act(),"50:00"));
  tap_label("25 minutes");assert(find_label(lv_scr_act(),"25:00"));
  std::puts("Pointer regression: 5/15 countdown presets and start/pause; Focus 25/50 switching and running-session reopen passed.");
  ui_show_page(3);lv_obj_update_layout(lv_scr_act());
  lv_obj_t *browser=find_label(lv_scr_act(),"Browser configuration");assert(browser);
  lv_obj_scroll_to_view_recursive(lv_obj_get_parent(browser),LV_ANIM_OFF);
  lv_obj_update_layout(lv_scr_act());lv_obj_get_coords(lv_obj_get_parent(browser),&bounds);
  const int browser_x=(bounds.x1+bounds.x2)/2,browser_y=(bounds.y1+bounds.y2)/2;
  tap_at(browser_x,browser_y);bool browser_first=find_label(lv_scr_act(),"Browser access");
  assert(browser_first);tap_at(36,32);
  assert(find_label(lv_scr_act(),"Settings"));
  tap_at(browser_x,browser_y);bool browser_second=find_label(lv_scr_act(),"Browser access");
  std::printf("Navigation probe: Settings Browser row -> back -> same row tap reopens = %s\n",browser_second?"PASS":"FAIL");
  std::fflush(stdout);assert(focus_entry && browser_second);
  // The fixed header shortcut stays usable independently of Settings scroll.
  for(unsigned i=0;i<5;i++) {
    tap_at(36,32);tap_label("Browser");
    assert(find_label(lv_scr_act(),"Browser access"));
    std::snprintf(s.adminCode,sizeof(s.adminCode),"%06u",123400+i);
    std::snprintf(s.browserUrl,sizeof(s.browserUrl),"https://192.0.2.%u/",10+i);
    s.wifiConnected=true;ui_update(s);
    assert(find_label(lv_scr_act(),s.adminCode) && find_label(lv_scr_act(),s.browserUrl));
  }
  s.wifiConnected=false;ui_update(s);
  assert(find_label(lv_scr_act(),"Connect to Wi-Fi first"));
  tap_at(36,32);tap_label("Browser");
  assert(find_label(lv_scr_act(),"Browser access") && find_label(lv_scr_act(),"Connect to Wi-Fi first"));
  lv_obj_t *code=find_label(lv_scr_act(),s.adminCode);assert(code);
  lv_obj_get_coords(code,&bounds);assert(bounds.x1>=20 && bounds.x2<460 && bounds.y1>=214 && bounds.y2<330);
  std::puts("Pointer regression: Browser header/back/reopen five times, scrolled-row restoration, refreshed code/address and offline hint passed.");
  std::puts("Rendered 14 pages and both display modes; always-on, timer/navigation, Browser/reopen, keyboard/reveal/credential preservation/byte limits and monotonic timer checks passed.");
}
