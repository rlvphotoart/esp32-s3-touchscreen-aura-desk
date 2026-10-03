# GPIO constraints — ESP32-S3 with reported embedded 8 MB PSRAM

Date: 2026-10-03. This document separates **chip constraints** from an **official reference map for the firmware-declared board**. Neither is an electrically verified header pinout. No exploratory GPIO toggling, scanning or custom driver initialization was used to derive it. The owner reports no external GPIO connections. The original firmware's normal boot initializes its own display/touch hardware and declares `Jingcai:ESP32_4848S040C_I_Y_3`.

## Reserved and sensitive groups

| GPIO / signal | Chip role | Treatment for this device |
|---|---|---|
| GPIO26–32 | Main flash/PSRAM SPI0/1 bus | Reserve for memory; never probe or reconfigure casually |
| GPIO33–37 | Octal memory DQ4–DQ7 / DQS | Reserve: embedded 8 MB octal PSRAM owns these lines |
| GPIO35–37 specifically | Octal PSRAM DQ6, DQ7, DQS/DM | Not spare I/O even if header labels expose them |
| GPIO19 / GPIO20 | Native USB D− / D+; also ADC2 channels 8/9 | Declared profile uses them for touch SDA / LCD data6; do not reassign to native USB |
| GPIO0 | Boot strap, default weak pull-up | Avoid external loading at reset; do not adopt as a default peripheral pin |
| GPIO3 | JTAG-source strap, floating by default | Reserve during bring-up; effect depends on eFuse configuration |
| GPIO45 | VDD_SPI voltage strap, default weak pull-down | Reference profile uses touch SCL. Observed `VDD_SPI_FORCE=true` overrides this voltage strap with 3.3 V selection |
| GPIO46 | Boot/ROM-log strap, default weak pull-down | Preserve download-mode behavior; reserve during bring-up |
| GPIO39 / 40 / 41 / 42 | Pad JTAG: MTCK / MTDO / MTDI / MTMS | GPIO39 is LCD control CS in the profile; JTAG use conflicts with that assignment |
| GPIO43 / GPIO44 | Default UART0 TX / RX | Preserve the current serial/recovery path; PCB bridge wiring not yet proven pin by pin |
| EN / CHIP_PU | Chip enable/reset input | Not a GPIO; do not treat it as an application output |
| GPIO22–25 | No physical ESP32-S3 GPIO pads | Never select these numbers |

Memory restrictions and USB defaults: [ESP-IDF GPIO guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-reference/peripherals/gpio.html). In-package octal mapping: [hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html). Strap and UART/JTAG roles: [datasheet, sections 2–3](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf).

Read-only eFuse inspection reports pad and USB JTAG disable bits clear. This supports debug capability, but does not prove routing or an active debug session. At reset, GPIO0 high selects normal flash boot; GPIO0 low with GPIO46 low selects joint download boot. The actual board-button wiring remains unknown.

## Official reference mapping for the declared Jingcai profile

**Evidence:** original runtime logs name `Jingcai:ESP32_4848S040C_I_Y_3`, report successful initialization and a touch-controller product ID spelling `911`. Espressif's supported-board list associates the exact model with a 480 × 480 ST7701 RGB panel and GT911 touch. The assignments below are copied as factual pin values from the official profile at commit `92b790ed6d24b0678e2f45b1fc85f0abd2d41b33`; the installed firmware's precise library revision or any custom overrides have not been established. They are strong reference evidence, not a continuity measurement.

| Configured function | Reference GPIO(s) | Notes |
|---|---|---|
| ST7701 control SPI | CS 39, SCK 48, SDA 47 | 3-wire control channel, separate from RGB data |
| RGB timing | HSYNC 16, VSYNC 17, DE 18, PCLK 21 | Profile PCLK is 26 MHz; this is not a runtime measurement |
| RGB D0–D4 / blue | 4, 5, 6, 7, 15 | RGB565 bus blue bits 0–4 |
| RGB D5–D10 / green | 8, 20, 3, 46, 9, 10 | RGB565 bus green bits 0–5 |
| RGB D11–D15 / red | 11, 12, 13, 14, 0 | RGB565 bus red bits 0–4 |
| GT911 I2C | SCL 45, SDA 19 | I2C host 0, profile frequency 400 kHz |
| Panel backlight | 38 | Profile enables LEDC PWM, 1 kHz, 10-bit duty |
| LCD reset / display-enable GPIO | −1 / −1 | No pin assigned by the profile; −1 is a sentinel, not a GPIO |
| Touch reset / interrupt GPIO | −1 / −1 | No pin assigned by the profile |
| I/O expander | Disabled | No expander configured by this profile |

Sources: [official board list](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/master/docs/board/board_jingcai.md), [pinned board configuration](https://github.com/esp-arduino-libs/ESP32_Display_Panel/blob/92b790ed6d24b0678e2f45b1fc85f0abd2d41b33/src/board/supported/jingcai/BOARD_JINGCAI_ESP32_4848S040C_I_Y_3.h).

Do not treat GPIO4–21, GPIO38–39 or GPIO47–48 as spare pins on this board merely because they are valid chip GPIOs. The profile's display and touch occupy most of them. GPIO0/3/46 also need their reset-time strap behavior preserved even though they become LCD outputs after boot. GPIO45's observed eFuse override explains why touch SCL can share a generic memory-voltage strap. Native USB and the normal display/touch configuration cannot share GPIO19/20 simultaneously.

## Analog and RTC capability map

| Group | Analog function | Low-power role | Board status |
|---|---|---|---|
| GPIO1–10 | ADC1 channels 0–9 | RTC GPIO; GPIO1–10 also touch | Profile occupies GPIO3–10 for RGB; GPIO1/2 header availability unknown |
| GPIO11–14 | ADC2 channels 0–3; touch | RTC GPIO | Profile uses them for RGB; ADC2 DMA erratum also applies |
| GPIO15–18 | ADC2 channels 4–7 | RTC GPIO; GPIO15/16 can carry external 32 kHz crystal signals | Profile uses them for RGB data/timing |
| GPIO19–20 | ADC2 channels 8–9 | RTC GPIO | Touch/LCD assignments in the declared profile; also native USB pins |
| GPIO0, GPIO21 | No ADC channel | RTC GPIO | Profile uses RGB data15 / PCLK; GPIO0 remains a strap |
| GPIO26–48 | No ADC/touch channels | Digital GPIO group | Memory/strap/JTAG/UART restrictions above still apply |

Chip capacitive-touch channels are GPIO1–14, distinct from the external GT911 controller. RTC GPIOs are GPIO0–21. I2C, UART and general SPI signals are generally routable through the GPIO matrix; the reference assignments above consume many analog-capable pins. No new analog or external sensor pins are assigned. [GPIO API table](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-reference/peripherals/gpio.html), [ESP32-S3 capability header](https://github.com/espressif/esp-idf/blob/v6.1/components/soc/esp32s3/include/soc/soc_caps.h)

## Input-only pin check

The current ESP32-S3 datasheet marks GPIO46 as I/O/T; ESP-IDF v6.1's valid-output GPIO mask includes all valid GPIOs. Therefore this map does **not** label GPIO46 input-only. The ESP32-S2 input-only restriction and older generic ESP32 pin rules should not be transplanted to ESP32-S3. GPIO46 remains a sensitive boot strap regardless of output capability. [Datasheet pin table](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf), [release-pinned SoC output mask](https://github.com/espressif/esp-idf/blob/v6.1/components/soc/esp32s3/include/soc/soc_caps.h)

## Future allocation rule

For added peripherals, first verify which remaining pins are exposed and unoccupied on the physical PCB. The reference profile does not assign GPIO1/2/40/41/42, but that is not proof of free board connectors. Protect memory and straps, preserve the serial recovery path, and reserve the LCD/touch/backlight pins above. GPIO47/48 are LCD control signals here, not assumed RGB-LED pins. Boot-time glitches mean software initialization alone cannot guarantee safe actuator states. Use hardware defaults when an eventual attached device needs a defined startup state.

Treat chip I/O as 3.3 V logic; connector power pin labels do not imply 5 V-tolerant GPIO. Any future 5 V device needs appropriate electrical interfacing. [Electrical limits and startup glitches](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)

**Still UNKNOWN:** physical PCB revision, expansion-header routing, onboard buttons/LEDs outside the profile, and optional camera, microphone, amplifier, SD or TWAI hardware. No new peripheral scan was performed. Successful original driver initialization and the GT911 ID strengthen board matching, but do not establish visual correctness or touch-coordinate accuracy.
