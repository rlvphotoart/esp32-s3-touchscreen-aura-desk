#!/usr/bin/env python3
"""Run offline regressions against actual firmware widget C++ functions.

The host harness uses the installed ArduinoJson dependency and copies function
bodies directly from the firmware source. Only platform services are stubbed:
mutexes, memory allocation, Arduino String, clock and HTTPS transport. No network,
hardware, user configuration or credentials are accessed. Temporary generated
source/binaries are removed on completion. Output contains fixed test labels.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def extract_function(source, name):
    match = re.search(r"(?m)^[\w:<>,*& ]+\b" + re.escape(name) + r"\([^;]*?\)\s*\{", source)
    if not match:
        raise RuntimeError("Required firmware widget function is missing: " + name)
    start = source.index("{", match.start())
    depth = 0
    state = "code"
    i = start
    while i < len(source):
        char = source[i]
        following = source[i:i+2]
        if state == "line":
            if char == "\n":
                state = "code"
        elif state == "comment":
            if following == "*/":
                state = "code"
                i += 1
        elif state in ("string", "char"):
            if char == "\\":
                i += 1
            elif (state == "string" and char == '"') or (state == "char" and char == "'"):
                state = "code"
        elif following == "//":
            state = "line"
            i += 1
        elif following == "/*":
            state = "comment"
            i += 1
        elif char in ('"', "'"):
            state = "string" if char == '"' else "char"
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():i+1]
        i += 1
    raise RuntimeError("Firmware widget function could not be parsed: " + name)


HOST_PREFIX = r'''
#include <ArduinoJson.h>
#include "app_model.h"
#include <algorithm>
#include <cassert>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <limits>
#include <string>
#include <vector>
using std::isfinite;
class String {
  std::string data;
public:
  using const_iterator=std::string::const_iterator;
  String()=default;
  String(const char *value):data(value?value:""){}
  String(const std::string &value):data(value){}
  String(int value):data(std::to_string(value)){}
  String(unsigned value):data(std::to_string(value)){}
  String(long value):data(std::to_string(value)){}
  String(unsigned long value):data(std::to_string(value)){}
  const_iterator begin()const{return data.begin();}
  const_iterator end()const{return data.end();}
  size_t length() const {return data.length();}
  bool isEmpty() const {return data.empty();}
  const char *c_str() const {return data.c_str();}
  char operator[](size_t index) const {return data[index];}
  bool startsWith(const char *value) const {return data.rfind(value,0)==0;}
  bool endsWith(const char *value) const {std::string suffix(value);return data.size()>=suffix.size()&&data.compare(data.size()-suffix.size(),suffix.size(),suffix)==0;}
  int indexOf(char value,size_t from=0) const {auto found=data.find(value,from);return found==std::string::npos?-1:int(found);}
  int indexOf(const char *value,size_t from=0) const {auto found=data.find(value,from);return found==std::string::npos?-1:int(found);}
  String substring(size_t start,size_t end=std::string::npos) const {return start>=data.size()?String():String(data.substr(start,end==std::string::npos?end:end-start));}
  long toInt() const {return std::strtol(data.c_str(),nullptr,10);}
  void toLowerCase(){for(char &c:data)c=char(std::tolower(static_cast<unsigned char>(c)));}
  void trim(){auto begin=data.find_first_not_of(" \t\r\n");auto end=data.find_last_not_of(" \t\r\n");data=begin==std::string::npos?"":data.substr(begin,end-begin+1);}
  void remove(size_t start,size_t count=std::string::npos){if(start<data.size())data.erase(start,count);}
  bool reserve(size_t count){data.reserve(count);return true;}
  bool concat(const char *value,size_t count){data.append(value,count);return true;}
  size_t write(uint8_t value){data.push_back(char(value));return 1;}
  size_t write(const uint8_t *value,size_t count){data.append(reinterpret_cast<const char *>(value),count);return count;}
  String &operator+=(char value){data+=value;return *this;}
  String &operator+=(const String &value){data+=value.data;return *this;}
  bool operator==(const char *value) const {return data==value;}
  friend String operator+(const String &left,const String &right){return String(left.data+right.data);}
};
template<> struct ArduinoJson::Converter<String> {
  static String fromJson(JsonVariantConst value){return value.is<const char *>()?String(value.as<const char *>()):String();}
  static bool checkJson(JsonVariantConst value){return value.is<const char *>();}
  static void toJson(const String &value,JsonVariant target){target.set(value.c_str());}
};
struct HostAllocator:ArduinoJson::Allocator {
  void *allocate(size_t count) override{return std::malloc(count);}
  void deallocate(void *p) override{std::free(p);}
  void *reallocate(void *p,size_t count) override{return std::realloc(p,count);}
} jsonAllocator;
UiSnapshot state{};
char widgetConfig[2][513]{};
uint32_t nextWidget[2]{};
time_t widgetFetched[2]{};
void lock(){}
void unlock(){}
template<size_t N>void text(char (&target)[N],const char *value){std::snprintf(target,N,"%s",value?value:"");}
bool app_get_widget_config(unsigned index,char *out,unsigned capacity){if(index>1||!out||!capacity)return false;std::snprintf(out,capacity,"%s",widgetConfig[index]);return out[0];}
bool fakeTransportOk=true;
int fakeHttpStatus=200;
String fakeBody;
const char *fakeFailureReason="Test transport failed.";
struct HttpOutcome {const char *error=nullptr;uint16_t status=0;};
bool getHttps(const String &,String &result,HttpOutcome *outcome=nullptr){if(outcome){outcome->status=fakeHttpStatus;outcome->error=(!fakeTransportOk||fakeHttpStatus!=200)?fakeFailureReason:nullptr;}if(!fakeTransportOk||fakeHttpStatus!=200)return false;result=fakeBody;return true;}
using esp_err_t=int;
constexpr int ESP_OK=0;
struct httpd_req_t {std::string body;int status=0;std::string response;};
bool authenticate(httpd_req_t *,bool){return true;}
bool readJson(httpd_req_t *r,JsonDocument &doc,unsigned maximum){if(r->body.size()>maximum||deserializeJson(doc,r->body)){r->status=400;return false;}return true;}
int error(httpd_req_t *r,const char *status,const char *){r->status=std::atoi(status);return 0;}
int jsonReply(httpd_req_t *r,const char *status,const JsonDocument &doc){r->status=std::atoi(status);serializeJson(doc,r->response);return 0;}
unsigned dispatchCount=0;
std::string dispatchedSlot,dispatchedConfig;
void app_dispatch(UiAction action,const char *first,const char *second){assert(action==UiAction::SetApiWidget);dispatchCount++;dispatchedSlot=first;dispatchedConfig=second;}
'''


HOST_TESTS = r'''
static unsigned assertions=0;
static void check(bool valid,const char *name){assertions++;if(!valid){std::fprintf(stderr,"FAIL: %s\n",name);std::exit(1);}}
static JsonDocument config(bool enabled=true,unsigned index=0){
  JsonDocument doc;doc["index"]=index;doc["label"]="Public reading";doc["url"]="https://example.org/data.json";
  doc["field"]="current.value";doc["unit"]="%";doc["interval"]=300;doc["enabled"]=enabled;return doc;
}
static void request_check(JsonDocument &doc,int expected,const char *name){
  httpd_req_t request;serializeJson(doc,request.body);unsigned before=dispatchCount;widgetHandler(&request);
  check(request.status==expected,name);check(dispatchCount==before+(expected==202),"Invalid widget requests do not dispatch");
}
static bool configure(unsigned index=0,const char *field="current.value"){
  JsonDocument doc=config(true,index);doc.remove("index");doc["field"]=field;std::string encoded;serializeJson(doc,encoded);return configureWidget(index,encoded.c_str());
}
int main(){
  for(unsigned i=0;i<2;i++){
    JsonDocument doc=config(true,i);request_check(doc,202,"Both widget slots accept public no-key configuration");
    check(dispatchedSlot==std::to_string(i),"Widget dispatch uses the selected slot");
    JsonDocument stored;check(!deserializeJson(stored,dispatchedConfig),"Dispatched config is valid JSON");
    check(stored["field"]=="current.value"&&stored["interval"]==300&&stored["enabled"]==true,"Selected field, interval and enabled state survive configuration dispatch");
  }
  for(const char *field:{".current.value","current.value.","current..value","current value","current[value]"}){
    JsonDocument doc=config();doc["field"]=field;request_check(doc,400,"Malformed dot paths are rejected before dispatch");
  }
  for(const char *url:{"http://example.org/data.json","https://example.org/data.json#part","https://localhost/data.json","https://127.0.0.1/data.json","https://u:p@example.org/data.json","https://example.org:444/data.json"}){
    JsonDocument doc=config();doc["url"]=url;request_check(doc,400,"Unsupported URL configuration is rejected");
  }
  for(int interval:{299,86401}){JsonDocument doc=config();doc["interval"]=interval;request_check(doc,400,"Interval range is enforced");}
  {JsonDocument doc=config();doc["label"]=std::string(28,'x');request_check(doc,400,"Label byte bound is enforced");}
  {JsonDocument doc=config();doc["label"]="éééééééééééééé";request_check(doc,400,"UTF-8 label is measured in firmware bytes");}
  {JsonDocument doc=config();doc["unit"]=std::string(16,'x');request_check(doc,400,"Unit byte bound is enforced");}
  {JsonDocument doc=config();doc["index"]=2;request_check(doc,400,"Invalid slot is rejected");}
  {JsonDocument doc=config();doc["enabled"]="true";request_check(doc,400,"String enabled state is rejected");}
  {JsonDocument doc=config();doc["interval"]=300.5;request_check(doc,400,"Fractional interval is rejected");}
  for(const char *field:{"label","url","field","unit"}){JsonDocument doc=config();doc[field]=std::string("ok\0hidden",9);request_check(doc,400,"Original request rejects embedded NUL before canonicalization");}
  {JsonDocument doc=config(false);doc["url"]="";doc["field"]="";request_check(doc,202,"Disabled empty configuration is supported");}

  check(configure(),"Backend accepts valid configuration");
  for(const char *body:{"{\"current\":{\"value\":0}}","{\"current\":{\"value\":false}}","{\"current\":{\"value\":\"Ready\"}}"}){
    fakeTransportOk=true;fakeHttpStatus=200;fakeBody=body;check(fetchWidget(0),"Zero, false and string scalar readings are valid");
    check(state.widgets[0].valid&&state.widgets[0].ageMinutes==0,"Successful reading has validity and age");
    check(!state.widgets[0].error[0]&&!state.widgets[0].fetching,"Successful reading clears widget error and fetching state");
    if(std::strstr(body,"false"))check(std::string(state.widgets[0].value)=="No","Boolean false is formatted as a readable value");
  }
  fakeBody="{\"current\":{\"value\":42}}";check(fetchWidget(0),"Initial retained reading is valid");
  state.widgets[0].ageMinutes=7;
  const std::string previous=state.widgets[0].value;
  for(const char *body:{"not-json","{}","{\"current\":{\"value\":null}}","{\"current\":{\"value\":{}}}","{\"current\":{\"value\":[]}}","{\"current\":{\"value\":\"\"}}","{\"current\":{\"value\":\"bad\\nline\"}}"}){
    fakeBody=body;check(!fetchWidget(0),"Invalid JSON, missing/null, non-scalar and unreadable values are rejected");
    check(state.widgets[0].valid&&std::string(state.widgets[0].value)==previous&&state.widgets[0].ageMinutes==7,"Failed refresh retains prior successful reading and age");
    check(state.widgets[0].error[0]&&!state.widgets[0].fetching,"Failure exposes an error and clears fetching state");
  }
  fakeHttpStatus=404;fakeTransportOk=false;check(!fetchWidget(0),"HTTP/network failure is rejected");
  check(state.widgets[0].httpStatus==404&&state.widgets[0].error[0],"HTTP failure retains status and actionable error");
  fakeHttpStatus=0;fakeFailureReason="Secure connection could not be established.";
  check(!fetchWidget(0),"TLS-style transport failure is rejected without an HTTP response");
  check(state.widgets[0].httpStatus==0&&state.widgets[0].error[0]&&!state.widgets[0].fetching,"TLS-style failure records an error, zero HTTP status and a completed request");
  check(state.widgets[0].valid&&std::string(state.widgets[0].value)==previous&&state.widgets[0].ageMinutes==7,"TLS-style failure preserves the last verified reading and age");
  fakeHttpStatus=200;fakeTransportOk=true;
  fakeBody="{\"current\":{\"value\":42}}";check(fetchWidget(0),"A valid update recovers after an HTTP failure");
  check(!state.widgets[0].error[0]&&state.widgets[0].httpStatus==200&&state.widgets[0].ageMinutes==0,"Recovery clears the prior error and records successful HTTP status and age");
  {JsonDocument data;data["current"]["value"]=std::string(48,'x');std::string body;serializeJson(data,body);fakeBody=body;check(!fetchWidget(0),"Scalar text above the display byte bound is rejected");}
  {JsonDocument data;data["value"]=std::numeric_limits<double>::infinity();String display;const char *problem=nullptr;check(!formatWidgetValue(data["value"],display,problem)&&problem,"Nonfinite numeric scalar is rejected with a reason");}
  check(configure(0,"data.0.intensity.forecast"),"Array field configuration is accepted");
  fakeBody="{\"data\":[{\"intensity\":{\"forecast\":0}}]}";check(fetchWidget(0),"Array index zero selects numeric zero");
  check(std::string(state.widgets[0].value)=="0","Zero is rendered as a reading rather than missing data");
  for(const char *field:{"data.1.intensity.forecast","data.-1.intensity.forecast","data.x.intensity.forecast","data.42949672960.intensity.forecast","data.184467440737095516160.intensity.forecast"}){
    check(configure(0,field),"Syntactically supported path reaches array validation");check(!fetchWidget(0),"Missing, invalid and overflowing array index fails safely");
  }
  check(configure(0,"data.0.price"),"Public price-style array path configuration is accepted");
  fakeBody="{\"data\":[{\"price\":0}]}";check(fetchWidget(0),"Price-style numeric zero is a valid reading");
  check(std::string(state.widgets[0].value)=="0","Price-style zero is not silently dropped");
  check(configure(0,"data.0.quotes.0.price"),"Documented public price example nested array path is accepted");
  fakeBody="{\"data\":[{\"quotes\":[{\"price\":123.45}]}]}";check(fetchWidget(0),"Public price example selects both zero-based array indices");
  check(std::string(state.widgets[0].value)=="123.45","Public price example displays the selected scalar");
  const std::string retainedConfig=widgetConfig[0],retainedValue=state.widgets[0].value;
  {JsonDocument doc=config();doc["field"]="current.value.";std::string encoded;serializeJson(doc,encoded);check(!configureWidget(0,encoded.c_str()),"Invalid replacement configuration is rejected by backend");}
  check(widgetConfig[0]==retainedConfig&&std::string(state.widgets[0].value)==retainedValue&&state.widgets[0].valid,"Invalid replacement does not modify current configuration or reading");
  check(configure(1),"Configuring the second slot succeeds independently");
  check(!state.widgets[1].valid&&!state.widgets[1].error[0]&&state.widgets[1].ageMinutes==-1,"Replacement configuration clears stale value validity/error/age");
  check(std::string(state.widgets[0].value)==retainedValue&&state.widgets[0].valid,"Changing widget two preserves widget one reading");
  check(configure(0)&&!state.widgets[0].valid&&!state.widgets[0].value[0]&&!state.widgets[0].error[0]&&state.widgets[0].ageMinutes==-1,"Valid replacement clears the previous reading rather than relabeling stale data");
  std::printf("PASS: %u actual-source widget assertions (host platform/HTTPS stubs; no hardware or network)\n",assertions);
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="clang++")
    args = parser.parse_args()
    backend = (ROOT / "firmware/AuraDesk/app_service.cpp").read_text()
    web = (ROOT / "firmware/AuraDesk/web_service.cpp").read_text()
    names = ["publicApiUrl", "widgetHandler"]
    chunks = [extract_function(web, name) for name in names]
    # Updated backend helper names are discovered from the real source to keep
    # the harness focused on the production selection/format/error functions.
    for name in ("publicWidgetUrl", "validWidgetPath", "validateWidgetOptions", "configureWidget",
                 "selectWidgetValue", "formatWidgetValue", "widgetFailure", "fetchWidget",
                 "app_validate_widget_config"):
        if re.search(r"(?m)^[\w:<>,*& ]+\b" + name + r"\(", backend):
            chunks.append(extract_function(backend, name))
    with tempfile.TemporaryDirectory(prefix="aura-widget-host-") as directory:
        source = Path(directory) / "widget_checks.cpp"
        binary = Path(directory) / "widget_checks"
        presets = json.loads((ROOT / "docs/PUBLIC_API_CATALOG.json").read_text())["presets"]
        catalog_checks = []
        for item in presets:
            config = {key: item[key] for key in ("label", "url", "field", "unit", "interval")}
            config["url"] = config["url"].replace("{latitude}", "-90.0000").replace("{longitude}", "-180.0000")
            config["enabled"] = True
            encoded = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
            for slot in (0, 1):
                catalog_checks.append('{const char *encoded=R"PRESET(' + encoded + ')PRESET";char problem[96]={};'
                    'check(app_validate_widget_config(encoded,problem,sizeof(problem)),"Catalog fits actual backend validation");'
                    'JsonDocument request;deserializeJson(request,encoded);request["index"]=' + str(slot) + ';'
                    'request_check(request,202,"Catalog is accepted by actual HTTP widget handler");'
                    'check(configureWidget(' + str(slot) + ',encoded),"Catalog persists in either actual widget slot");}')
        tests = HOST_TESTS.replace('  std::printf("PASS:', "\n".join(catalog_checks) + '\n  std::printf("PASS:')
        source.write_text(HOST_PREFIX + "\n\n".join(chunks) + tests)
        source.chmod(0o600)
        compiled = subprocess.run([args.compiler, "-std=c++17", "-O1", "-Wall", "-Wextra",
                                   "-I" + str(ROOT / ".toolchains/arduino/user/libraries/ArduinoJson/src"),
                                   "-I" + str(ROOT / "firmware/AuraDesk"), str(source), "-o", str(binary)],
                                  capture_output=True, text=True)
        if compiled.returncode:
            diagnostic = (compiled.stdout + compiled.stderr).replace(str(ROOT), "<workspace>").replace(directory, "<temporary>")
            print(diagnostic, file=sys.stderr, end="")
            return 1
        checked = subprocess.run([str(binary)], capture_output=True, text=True)
        print(checked.stdout, end="")
        print(checked.stderr, file=sys.stderr, end="")
        return checked.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print("FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1)
