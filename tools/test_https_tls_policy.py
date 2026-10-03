#!/usr/bin/env python3
"""Exercise actual HTTPS trust attachment and cipher policy with offline SDK stubs.

The harness compiles production attachApiRoots/getHttps function bodies. It checks
attachment failure/order, cipher storage/termination and HTTP client defaults;
it does not emulate certificate validation or prove a real server handshake.
No device, network, saved settings or credentials are accessed.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from test_widgets import HOST_PREFIX, ROOT, extract_function


STUBS = r'''
using esp_err_t=int;
constexpr int ESP_OK=0,ESP_FAIL=-1,VERIFY_REQUIRED=2;
constexpr int MBEDTLS_TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256=0xC02F;
constexpr int MBEDTLS_TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384=0xC030;
constexpr int MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256=0xC02B;
constexpr int MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384=0xC02C;
static const uint16_t defaultGroups[]={29,23,24,25,0};
static const uint16_t defaultSignatures[]={0x0401,0x0403,0};
struct mbedtls_ssl_config {
  const uint16_t *groups=defaultGroups,*signatures=defaultSignatures;
  const int *suites=nullptr;
  int authmode=VERIFY_REQUIRED;
  const char *hostname="expected.example";
  bool trustAttached=false;
};
esp_err_t rootResult=ESP_OK;
void *attachedConfiguration=nullptr;
mbedtls_ssl_config *cipherConfiguration=nullptr;
const int *assignedSuites=nullptr;
std::vector<std::string> calls;
esp_err_t esp_crt_bundle_attach(void *conf){
  calls.push_back("roots");attachedConfiguration=conf;
  if(rootResult==ESP_OK)static_cast<mbedtls_ssl_config*>(conf)->trustAttached=true;
  return rootResult;
}
void mbedtls_ssl_conf_ciphersuites(mbedtls_ssl_config *conf,const int *suites){
  calls.push_back("ciphers");cipherConfiguration=conf;assignedSuites=suites;conf->suites=suites;
}
struct HttpBody {String data;bool tooLarge=false,tlsFailure=false;};
struct HttpOutcome {const char *error=nullptr;uint16_t status=0;};
int httpEvent(void *){return ESP_OK;}
struct IPAddress {uint8_t bytes[4]{203,0,113,10};uint8_t operator[](size_t i)const{return bytes[i];}};
struct WifiStub {bool hostByName(const char *,IPAddress &){return true;}} WiFi;
struct {bool internetAvailable=false;} state;
void lock(){}
void unlock(){}
struct esp_http_client_config_t {
  const char *url=nullptr;
  int timeout_ms=0,buffer_size=0,buffer_size_tx=0;
  int (*event_handler)(void *)=nullptr;
  void *user_data=nullptr;
  esp_err_t (*crt_bundle_attach)(void *)=nullptr;
  bool disable_auto_redirect=false,skip_cert_common_name_check=false;
  const char *common_name=nullptr,*cert_pem=nullptr,*username=nullptr,*password=nullptr;
};
esp_http_client_config_t captured;
mbedtls_ssl_config clientTls;
unsigned initCount=0,performCount=0,cleanupCount=0;
void *esp_http_client_init(const esp_http_client_config_t *config){
  ++initCount;captured=*config;clientTls=mbedtls_ssl_config{};
  if(config->crt_bundle_attach&&config->crt_bundle_attach(&clientTls)!=ESP_OK)return nullptr;
  return &captured;
}
int esp_http_client_set_header(void *,const char *,const char *){return ESP_OK;}
int esp_http_client_perform(void *){++performCount;static_cast<HttpBody*>(captured.user_data)->data="{}";return ESP_OK;}
int esp_http_client_get_status_code(void *){return 200;}
void esp_http_client_cleanup(void *){++cleanupCount;}
'''

CHECKS = r'''
unsigned assertions=0;
void check(bool valid,const char *name){++assertions;if(!valid){std::fprintf(stderr,"FAIL: %s\n",name);std::exit(1);}}
int main(){
  static const int original[]={99,0};
  mbedtls_ssl_config conf;conf.suites=original;
  rootResult=-42;
  check(attachApiRoots(&conf)==-42,"Root attachment failure propagates exactly");
  check(attachedConfiguration==&conf&&calls==std::vector<std::string>{"roots"},"Failed attachment never configures ciphers");
  check(conf.suites==original&&conf.groups==defaultGroups&&conf.signatures==defaultSignatures&&!conf.trustAttached&&conf.authmode==VERIFY_REQUIRED&&std::string(conf.hostname)=="expected.example","Failed attachment preserves TLS configuration");
  rootResult=ESP_OK;calls.clear();
  check(attachApiRoots(&conf)==ESP_OK,"Successful trusted root attachment succeeds");
  check(calls==std::vector<std::string>{"roots","ciphers"},"Roots attach before the cipher policy");
  check(attachedConfiguration==&conf&&cipherConfiguration==&conf,"Both callbacks receive the original SSL configuration pointer");
  check(assignedSuites&&assignedSuites[0]==0xC02F&&assignedSuites[1]==0xC030&&assignedSuites[2]==0xC02B&&assignedSuites[3]==0xC02C&&assignedSuites[4]==0,"Only four ECDHE RSA/ECDSA AES-GCM suites are offered with a zero terminator");
  check(conf.authmode==VERIFY_REQUIRED&&std::string(conf.hostname)=="expected.example"&&conf.trustAttached&&conf.groups==defaultGroups&&conf.signatures==defaultSignatures,"Cipher policy preserves authentication, hostname, groups and signature settings");
  const int *retained=assignedSuites;
  mbedtls_ssl_config second;
  check(attachApiRoots(&second)==ESP_OK&&assignedSuites==retained,"Cipher storage is shared and stable across configurations");
  check(retained[0]==0xC02F&&retained[1]==0xC030&&retained[2]==0xC02B&&retained[3]==0xC02C&&retained[4]==0&&conf.suites==retained,"Cipher preferences remain valid after attachment returns and another call completes");
  calls.clear();String result;HttpOutcome outcome;
  check(getHttps("https://public.example/data.json",result,&outcome),"Actual HTTPS client setup accepts a public fixture request");
  check(initCount==1&&performCount==1&&cleanupCount==1,"Client performs and cleans up one prepared request");
  check(captured.crt_bundle_attach==attachApiRoots&&calls==std::vector<std::string>{"roots","ciphers"},"Production HTTP client is wired to the trusted root/cipher wrapper");
  check(!captured.skip_cert_common_name_check&&captured.common_name==nullptr,"Production client keeps hostname-derived certificate name checks enabled");
  check(captured.cert_pem==nullptr&&clientTls.trustAttached&&clientTls.authmode==VERIFY_REQUIRED&&clientTls.groups==defaultGroups&&clientTls.signatures==defaultSignatures,"Client retains bundle verification plus default groups and signatures");
  check(!captured.username&&!captured.password,"Client adds no account credentials");
  check(captured.disable_auto_redirect&&captured.timeout_ms==12000,"Bounded request and no-redirect policy are preserved");
  rootResult=-42;calls.clear();
  check(!getHttps("https://public.example/data.json",result,&outcome),"HTTP initialization fails closed when bundle attachment fails");
  check(initCount==2&&performCount==1&&cleanupCount==1&&calls==std::vector<std::string>{"roots"},"Failed trust setup neither configures ciphers nor performs a request");
  check(outcome.error&&outcome.status==0,"Failed trust setup exposes a failure without claiming an HTTP response");
  std::printf("PASS: %u actual-source HTTPS TLS policy assertions (offline SDK stubs; live handshake verification separate)\n",assertions);
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="clang++")
    args = parser.parse_args()
    service = (ROOT / "firmware/AuraDesk/app_service.cpp").read_text()
    attachment = extract_function(service, "attachApiRoots")
    request = extract_function(service, "getHttps")
    if not re.search(r"\bstatic\s+const\s+int\s+suites\s*\[\s*\]", attachment):
        raise RuntimeError("TLS cipher storage must have static const lifetime")
    prefix = HOST_PREFIX.split("struct HostAllocator")[0]
    with tempfile.TemporaryDirectory(prefix="aura-tls-host-") as directory:
        source, binary = Path(directory) / "tls_checks.cpp", Path(directory) / "tls_checks"
        source.write_text(prefix + STUBS + attachment + request + CHECKS)
        source.chmod(0o600)
        compiled = subprocess.run([args.compiler, "-std=c++17", "-O1", "-Wall", "-Wextra",
                                   "-I" + str(ROOT / ".toolchains/arduino/user/libraries/ArduinoJson/src"),
                                   "-I" + str(ROOT / "firmware/AuraDesk"), str(source), "-o", str(binary)],
                                  capture_output=True, text=True)
        if compiled.returncode:
            print((compiled.stdout + compiled.stderr).replace(str(ROOT), "<workspace>").replace(directory, "<temporary>"),
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
