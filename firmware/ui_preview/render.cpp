// Host visual verification of the real LVGL interface; fixture data never ships.
#include <lvgl.h>
#include "ui.h"
#include <cstdio>
#include <cstring>
#include <cassert>

static unsigned char pixels[480*480*3];
static lv_color_t draw_buffer[480*40];
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
int main(int argc,char **argv) {
  const char *directory=argc>1?argv[1]:".";
  bool fixture=argc>2 && std::strcmp(argv[2],"--fixture")==0;
  lv_init(); lv_disp_draw_buf_t buffer; lv_disp_draw_buf_init(&buffer,draw_buffer,nullptr,480*40);
  lv_disp_drv_t driver; lv_disp_drv_init(&driver); driver.hor_res=480;driver.ver_res=480;
  driver.draw_buf=&buffer;driver.flush_cb=flush;lv_disp_drv_register(&driver);
  ui_init(callback);
  UiSnapshot s{};
  std::snprintf(s.city,sizeof(s.city),"Bucharest");
  std::snprintf(s.firmware,sizeof(s.firmware),"1.0.0");
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
  std::puts("Rendered 14 pages; keyboard/reveal/credential preservation/byte limits and monotonic timer checks passed.");
}
