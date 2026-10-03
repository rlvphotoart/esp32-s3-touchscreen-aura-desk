#!/usr/bin/env python3
"""Check actual HTTP response completion policy using offline SDK stubs.

Exercises production privacyHeaders/finishResponse/jsonReply/rootHandler function
bodies. Header values and send/close calls are captured in RAM. No server, TLS,
device, network, user identity or credentials are accessed. TLS memory recovery
still requires the separate device/browser test.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from test_widgets import ROOT, HOST_PREFIX, extract_function


SDK_STUBS = r'''
#include <map>
using esp_err_t=int;
constexpr int ESP_OK=0,ESP_FAIL=-1;
struct httpd_req_t {
  void *handle=this;
  int socket=7,sendResult=0,closeResult=0;
  std::map<std::string,std::string> headers;
  std::vector<std::string> calls;
  std::string body,status,type;
};
int httpd_resp_set_hdr(httpd_req_t *r,const char *name,const char *value){r->headers[name]=value;return ESP_OK;}
int httpd_resp_set_status(httpd_req_t *r,const char *value){r->status=value;return ESP_OK;}
int httpd_resp_set_type(httpd_req_t *r,const char *value){r->type=value;return ESP_OK;}
int httpd_req_to_sockfd(httpd_req_t *r){return r->socket;}
int httpd_sess_trigger_close(void *handle,int socket){auto *r=static_cast<httpd_req_t*>(handle);assert(socket==r->socket);r->calls.push_back("close");return r->closeResult;}
int httpd_resp_send(httpd_req_t *r,const char *body,size_t length){r->calls.push_back("send");r->body.assign(body,length);return r->sendResult;}
bool trusted=true;
bool trustedHost(httpd_req_t *){return trusted;}
int error(httpd_req_t *r,const char *status,const char *){r->status=status;return 0;}
const char HTML[]="Offline HTML fixture";
'''

CHECKS = r'''
unsigned assertions=0;
void check(bool valid,const char *name){assertions++;if(!valid){std::fprintf(stderr,"FAIL: %s\n",name);std::exit(1);}}
int main(){
  httpd_req_t r;privacyHeaders(&r);
  check(r.headers["Connection"]=="close","Responses advertise connection close");
  check(r.headers["Cache-Control"]=="no-store"&&r.headers["Referrer-Policy"]=="no-referrer","Response privacy policy is preserved");
  check(r.headers["X-Content-Type-Options"]=="nosniff"&&r.headers["X-Frame-Options"]=="DENY","Response content protections are preserved");
  r=httpd_req_t{};r.handle=&r;r.sendResult=-17;
  check(finishResponse(&r,r.sendResult)==-17&&r.calls.empty(),"Send failure propagates without queuing a close");
  r=httpd_req_t{};r.handle=&r;r.closeResult=-9;
  check(finishResponse(&r,ESP_OK)==ESP_FAIL&&r.calls==std::vector<std::string>{"close"},"Close queue failure propagates to the server");
  r=httpd_req_t{};r.handle=&r;
  JsonDocument doc;doc["value"]=0;
  check(jsonReply(&r,"200 OK",doc)==ESP_OK,"Successful JSON response completes");
  check(r.calls==std::vector<std::string>{"send","close"},"JSON bytes are sent before the close is queued");
  check(r.type=="application/json"&&r.status=="200 OK"&&r.headers["Connection"]=="close","JSON response retains content type, status and close policy");
  JsonDocument decoded;check(!deserializeJson(decoded,r.body)&&decoded["value"]==0,"JSON response body is complete before connection release");
  r=httpd_req_t{};r.handle=&r;r.sendResult=-17;
  check(jsonReply(&r,"200 OK",doc)==-17&&r.calls==std::vector<std::string>{"send"},"JSON send failure is propagated without a second close");
  r=httpd_req_t{};r.handle=&r;r.closeResult=-9;
  check(jsonReply(&r,"200 OK",doc)==ESP_FAIL&&r.calls==std::vector<std::string>{"send","close"},"JSON close queue failure propagates after send");
  r=httpd_req_t{};r.handle=&r;trusted=true;
  check(rootHandler(&r)==ESP_OK&&r.calls==std::vector<std::string>{"send","close"},"HTML response sends before connection release");
  check(r.body==HTML&&r.type=="text/html; charset=utf-8"&&r.headers["Connection"]=="close","HTML content and response policy are preserved");
  check(!r.headers["Content-Security-Policy"].empty(),"HTML CSP survives the response lifecycle change");
  r=httpd_req_t{};r.handle=&r;r.sendResult=-17;
  check(rootHandler(&r)==-17&&r.calls==std::vector<std::string>{"send"},"HTML send failure propagates without double close");
  r=httpd_req_t{};r.handle=&r;r.closeResult=-9;
  check(rootHandler(&r)==ESP_FAIL,"HTML close queue failure propagates");
  r=httpd_req_t{};r.handle=&r;trusted=false;
  rootHandler(&r);check(r.status=="403 Forbidden"&&r.calls.empty(),"Host authentication guard remains ahead of HTML dispatch");
  std::printf("PASS: %u actual-source HTTP response policy assertions (offline SDK stubs; TLS/device checks separate)\n",assertions);
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="clang++")
    args = parser.parse_args()
    web = (ROOT / "firmware/AuraDesk/web_service.cpp").read_text()
    functions = [extract_function(web, name) for name in
                 ("privacyHeaders", "finishResponse", "jsonReply", "rootHandler")]
    prefix = HOST_PREFIX.split("struct HostAllocator")[0]
    with tempfile.TemporaryDirectory(prefix="aura-http-host-") as directory:
        source = Path(directory) / "http_checks.cpp"
        binary = Path(directory) / "http_checks"
        source.write_text(prefix + SDK_STUBS + "\n".join(functions) + CHECKS)
        source.chmod(0o600)
        compiled = subprocess.run([args.compiler, "-std=c++17", "-O1", "-Wall", "-Wextra",
                                   "-I" + str(ROOT / ".toolchains/arduino/user/libraries/ArduinoJson/src"),
                                   "-I" + str(ROOT / "firmware/AuraDesk"), str(source), "-o", str(binary)],
                                  capture_output=True, text=True)
        if compiled.returncode:
            print((compiled.stdout+compiled.stderr).replace(str(ROOT), "<workspace>").replace(directory, "<temporary>"),
                  file=sys.stderr, end="")
            return 1
        tested = subprocess.run([str(binary)], capture_output=True, text=True)
        print(tested.stdout, end="")
        print(tested.stderr, file=sys.stderr, end="")
        return tested.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print("FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1)
