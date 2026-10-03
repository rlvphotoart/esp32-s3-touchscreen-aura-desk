#pragma once
#include "app_model.h"

// All calls belong to the LVGL owner task, with the board LVGL lock held.
void ui_init(UiActionCallback callback);
void ui_update(const UiSnapshot &snapshot);
void ui_show_page(int page);
