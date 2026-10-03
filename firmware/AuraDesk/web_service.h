#pragma once

// Starts once after Wi-Fi receives an address. The service accepts HTTPS only.
void web_service_start();
void web_service_poll();
bool web_service_running();
