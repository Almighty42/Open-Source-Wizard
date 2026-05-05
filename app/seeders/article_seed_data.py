ARTICLES = [
    {
        "title": "AI in Embedded Development: Practical Uses Without the Hype",
        "slug": "ai-in-embedded-development",
        "excerpt": "LLMs won't replace embedded engineers — but they're already cutting debug time in half and generating driver boilerplate in seconds. Here's how I actually use AI tools in my firmware workflow.",
        "read_time": 8,
        "is_featured": True,
        "status": "published",
        "created_at": "2026-05-01T12:41:00+02:00",
        "published_at": "2026-05-01T12:41:00+02:00",
        "seo_title": "AI in Embedded Development — Practical Guide",
        "seo_description": "A practical guide to using AI tools like Copilot and Claude in embedded C firmware development. Where it helps, where it doesn't, and a real workflow example.",
        "tags": ["AI", "Embedded", "ESP32", "C", "Debugging"],
        "category": "Embedded Systems",
        "cover": "uploads/articles/ai-embedded-cover.jpg",
        "inline_assets": [
            "uploads/articles/ai-copilot-screenshot.png",
            "uploads/articles/esp32-breadboard.jpg",
        ],
        "diagrams": [
            "uploads/diagrams/cloud-vs-edge-ai.svg",
            "uploads/diagrams/i2c-sensor-block.png",
        ],
        "attachments": [
            "uploads/files/sensor_driver_port.c",
            "uploads/files/ai-embedded-workflow-checklist.pdf",
        ],
        "videos": [
            "uploads/videos/esp32-demo.mp4",
        ],
        "body": """\
There's a growing split in the embedded community. Half the engineers I talk to swear by AI coding tools.
The other half won't touch them — convinced that LLMs hallucinate register addresses and don't understand timing constraints.

Both sides have a point. This article isn't about hype. It's about where AI tools *actually* help in a firmware workflow,
and where they'll waste your time or silently break your code.

# The Honest Reality

AI models are trained predominantly on web, cloud, and application-layer code.
They've seen far less embedded C, and almost no vendor-specific HAL code for a niche MCU like the STM32G0 or RP2040.
That gap matters.

But "less useful than for web dev" isn't the same as "useless." There are specific parts of the embedded workflow
where AI provides genuine leverage — and a few where it's actively dangerous.

# Where AI Actually Helps

## 1. Boilerplate and Peripheral Initialization

This is the clearest win. Initializing a UART, configuring a SPI peripheral, or setting up a GPIO interrupt
requires the same structural pattern every time.

```c
// Prompt: "Generate a STM32 HAL UART init for 115200 baud, 8N1, with DMA RX"
// Result was 90% correct — needed one fix for the DMA stream assignment
UART_HandleTypeDef huart2;

void MX_USART2_UART_Init(void) {
    huart2.Instance        = USART2;
    huart2.Init.BaudRate   = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits   = UART_STOPBITS_1;
    huart2.Init.Parity     = UART_PARITY_NONE;
    huart2.Init.Mode       = UART_MODE_TX_RX;
    HAL_UART_Init(&huart2);
}
```

### Why it matters

When you open a 3-year-old driver written by someone who left the company,
asking an LLM to explain what a function does and what could go wrong is genuinely useful.

#### The issue

Here

## 2. Understanding Unfamiliar Code

When you open a 3-year-old driver written by someone who left the company,
asking an LLM to explain what a function does and what could go wrong is genuinely useful.

![Copilot suggesting C code in Neovim](asset:uploads/articles/ai-copilot-screenshot.png)

```c
// Pasted a 60-line I2C transaction handler into Claude.
// It immediately flagged a missing timeout guard on the ACK poll loop —
// which would have caused the MCU to hang on a disconnected sensor.
while (!(I2C1->SR1 & I2C_SR1_ADDR)); // no timeout — hangs forever if NACK
```

![I2C bus topology](asset:uploads/diagrams/i2c-sensor-block.png)

## 3. Writing Unit Tests

```c
// Prompt: "Write Unity test cases for this CRC16 implementation"
void test_crc16_nominal(void) {
    uint8_t data[] = {0x01, 0x02, 0x03};
    TEST_ASSERT_EQUAL_HEX16(0xBE26, crc16(data, 3));
}

void test_crc16_empty(void) {
    TEST_ASSERT_EQUAL_HEX16(0xFFFF, crc16(NULL, 0));
}
```

![ESP32 sensor demo](asset:uploads/videos/esp32-demo.mp4)

# Where AI Will Waste Your Time

## 4. Tool Comparison

Here's how the main AI tools stack up for embedded work:

| Tool | Best For | Embedded Awareness | Free Tier |
|------|----------|--------------------|-----------|
| GitHub Copilot | Autocomplete, boilerplate | Medium | No |
| Claude | Code explanation, refactoring | High | Yes (limited) |
| ChatGPT | General questions, docs | Medium | Yes |
| Cursor | Full file edits, multi-file | Medium | Yes (limited) |

Copilot wins for in-editor flow. Claude wins for understanding and explaining existing code.

## 5. Useful Resources

If you want to go deeper, these are worth reading:

- [ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/latest/) — the authoritative reference for bare-metal ESP32 development
- [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity) — lightweight C unit testing, works great with AI-generated test cases
- [MISRA C 2012 Guidelines](https://misra.org.uk/misra-c/) — if you're in safety-critical territory, read this before touching AI output
- [Edge Impulse Docs](https://docs.edgeimpulse.com/) — best starting point for on-device ML

Also worth noting: `HAL_UART_Init()` returns a `HAL_StatusTypeDef` — always check it, AI-generated code often omits this.

> **Rule:** Any value that comes from a datasheet must be verified against the datasheet.
> AI output is a starting point, not a source of truth.



- Register addresses and bit masks — always verify
- RTOS stack sizes and interrupt priorities — you own this
- Anything safety-critical (IEC 61508, ISO 26262, MISRA C) — keep AI out

# A Real Workflow Example

Here's how I used AI when porting a sensor driver from Arduino to bare-metal ESP32:

1. Pasted the Arduino library into Claude, asked it to identify all hardware-dependent calls
2. Generated an abstraction layer with AI, mapping those calls to ESP-IDF equivalents
3. Used Copilot for the boilerplate ESP-IDF I2C master init
4. Debugged a timing issue by describing the symptoms — it suggested a missing stop condition before repeated start, which was correct

Total time: ~2 hours. My estimate without AI: 4–5 hours for an unfamiliar SDK.

# Edge AI: Running Models On-Device

Modern MCUs like the STM32H7 or ESP32-S3 have enough compute to run small neural networks
for keyword detection, gesture recognition, or anomaly detection on sensor data.
Frameworks like **TensorFlow Lite for Microcontrollers** and **Edge Impulse** make the deployment pipeline accessible.

This is a bigger topic that deserves its own article.
""",
    },
    {
        "title": "Building a Portable Raspberry Pi NAS",
        "slug": "portable-raspberry-pi-nas",
        "excerpt": "A compact, battery-backed NAS built around the Raspberry Pi 4, a USB hub, and two SSDs in a 3D-printed enclosure. This is the full build log.",
        "read_time": 11,
        "is_featured": True,
        "status": "published",
        "seo_title": "Portable Raspberry Pi NAS — Full Build Log",
        "seo_description": "How I built a portable NAS with a Raspberry Pi 4, dual SSDs, and a 3D-printed enclosure. Includes parts list, wiring, and software setup.",
        "tags": ["Raspberry Pi", "Linux", "Docker", "Python"],
        "category": "Self-Hosting",
        "cover": "uploads/articles/portable-nas-cover.jpg",
        "inline_assets": ["uploads/articles/nas-internals.jpg"],
        "diagrams": [],
        "attachments": ["uploads/files/portable-nas-bom.pdf"],
        "body": """\
I wanted a NAS I could take anywhere — one that fits in a backpack, runs off a battery,
and doesn't require a wall socket to be useful. This is the full build log.

# Goals

- Dual SSD storage (RAID 1 via `mdadm` or simple JBOD)
- Battery-backed (5–6 hours runtime)
- Gigabit ethernet + WiFi
- Runs Docker for services like Samba, Syncthing, and a lightweight dashboard
- Fits in a 3D-printed enclosure under 200mm × 120mm

# Parts

| Part | Notes |
|---|---|
| Raspberry Pi 4 (4GB) | Main compute |
| 2× Samsung 870 EVO 500GB | Connected via USB 3.0 hub |
| Waveshare UPS HAT | 18650 battery pack, I2C fuel gauge |
| 4-port USB 3.0 hub | Powered, plugged into Pi USB 3 port |
| 3D-printed enclosure | Designed in FreeCAD |

# Power Budget

The Pi 4 under load draws roughly 3–4W. Two SSDs at ~2W each gives a worst-case draw
of about 8W. With a 4-cell 18650 pack at ~15Wh, that gives approximately 1.5–2 hours
under full load, or 4–5 hours at idle.

```bash
# Check current draw live via I2C fuel gauge
python3 -c "
import smbus2
bus = smbus2.SMBus(1)
raw = bus.read_word_data(0x36, 0x09)
voltage = raw * 1.25 / 1000 / 16
print(f'Voltage: {voltage:.2f}V')
"
```

# Software Stack

```yaml
# docker-compose.yml
services:
  samba:
    image: dperson/samba
    volumes:
      - /mnt/data:/share

  syncthing:
    image: syncthing/syncthing
    ports:
      - "8384:8384"
    volumes:
      - /mnt/data/sync:/var/syncthing
```

# What I'd Change

The USB 3.0 hub introduces occasional disconnects under high sequential write load.
Next version I'd use a proper PCIe-to-SATA HAT instead.
""",
    },
    {
        "title": "What I Learned Debugging an E-Ink Refresh Bug",
        "slug": "eink-refresh-bug",
        "excerpt": "Three hours chasing a ghosting artifact on a Waveshare 4.2-inch display. The culprit was a missing deep sleep call before power-off.",
        "read_time": 5,
        "is_featured": False,
        "status": "published",
        "seo_title": "Debugging E-Ink Display Refresh Ghosting",
        "seo_description": "How a missing deep sleep command on a Waveshare e-ink display caused persistent ghosting artifacts and how I found it.",
        "tags": ["E-Ink", "ESP32", "Debugging", "C"],
        "category": "Embedded Systems",
        "cover": "uploads/articles/eink-debug-cover.jpg",
        "inline_assets": [],
        "diagrams": [],
        "attachments": [],
        "body": """\
The symptom was straightforward: after power-cycling the ESP32, the previous frame
was still visible as a faint ghost behind the new content. A partial refresh artifact
that shouldn't exist after a full refresh cycle.

# What I Tried First

- Forced a full refresh (`EPD_4IN2_Clear()`) on boot — ghost persisted
- Increased the power-on delay before sending the init sequence — no change
- Swapped the display with a spare unit — same behavior

# The Actual Cause

After reading the Waveshare wiki more carefully, I found this note buried at the bottom:

> Before cutting power to the display, always call `EPD_Sleep()`.
> Failure to do so may result in persistent image retention.

```c
// What I was doing — just cutting power
gpio_set_level(PIN_PWR, 0);

// What I should have been doing
EPD_4IN2_Sleep();
vTaskDelay(pdMS_TO_TICKS(100)); // let the deep sleep complete
gpio_set_level(PIN_PWR, 0);
```

The display's internal controller needs to execute a deep sleep sequence
that clears its internal framebuffer before power is removed.
Without it, the last image leaks into the next refresh cycle.

# Lesson

Always read the full datasheet, not just the example code.
The Waveshare examples do call `EPD_Sleep()` — I had removed it
thinking it was unnecessary boilerplate.
""",
    },
    {
        "title": "Use of AI in Embedded Development",
        "slug": "ai-in-embedded-development-article",
        "excerpt": "LLMs won't replace embedded engineers — but they're already cutting debug time in half and generating driver boilerplate in seconds. Here's how I actually use AI tools in my firmware workflow.",
        "read_time": 8,
        "is_featured": True,
        "status": "published",
        "seo_title": "",
        "seo_description": "",
        "tags": ["AI", "Embedded", "ESP32", "C", "Debugging"],
        "category": "Embedded Systems",
        "cover": "assets/cover.png",
        "inline_assets": [],
        "diagrams": [],
        "attachments": [],
        "body": """\
There's a growing split in the embedded community. Half the engineers I talk to swear by AI coding tools. The other half won't touch them — convinced that LLMs hallucinate register addresses and don't understand timing constraints.

Both sides have a point. This article isn't about hype. It's about where AI tools *actually* help in a firmware workflow, and where they'll waste your time or silently break your code.

# The Honest Reality

AI models are trained predominantly on web, cloud, and application-layer code. They've seen far less embedded C, and almost no vendor-specific HAL code for a niche MCU like the STM32G0 or RP2040. That gap matters.

But "less useful than for web dev" isn't the same as "useless." There are specific parts of the embedded workflow where AI provides genuine leverage — and a few where it's actively dangerous.

# Where AI actually helps

## 1. Boilerplate and Peripheral Initialization

This is the clearest win. Initializing a UART, configuring a SPI peripheral, or setting up a GPIO interrupt requires the same structural pattern every time. The logic isn't clever — it's just tedious and error-prone to type from scratch.

```c
// Prompt: "Generate a STM32 HAL UART init for 115200 baud, 8N1, with DMA RX"

// Result was 90% correct — needed one fix for the DMA stream assignment
```

AI tools like GitHub Copilot or Claude are good at this. Give them the target MCU, the peripheral, and the config parameters. Verify the output against the reference manual, but expect to spend 2 minutes reviewing instead of 20 minutes writing.


## 2. Understanding Unfamiliar Code

This is the use case I reach for most. When you open a 3-year-old driver written by someone who left the company, asking an LLM "explain what this function does and what could go wrong" is genuinely useful. It won't catch every issue, but it surfaces the non-obvious parts quickly.

```c
// Pasted a 60-line I2C transaction handler into Claude. 
// It immediately flagged a missing timeout guard on the ACK poll loop — 
// which would have caused the MCU to hang on a disconnected sensor.
```

The same applies when you're learning a new vendor SDK. Instead of parsing 50 pages of PDF documentation, you can ask targeted questions about specific functions and get synthesized answers in seconds.  [ 1 ]

## 3. Writing Unit Tests

Embedded engineers tend to write few unit tests. The tooling friction is real — setting up a test harness for firmware is harder than for a web service. AI can generate initial test scaffolding quickly.

```c
#include <stdint.h>
#include <string.h>
 
#define BUFFER_SIZE 128

typedef struct {
    uint8_t data[BUFFER_SIZE];
    uint32_t len;
} Buffer;

static void buffer_clear(Buffer *buf) {
    memset(buf->data, 0, BUFFER_SIZE);
    buf->len = 0;
}
```

```python
import os
from dataclasses import dataclass
 
@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
 
def load_config(path: str) -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No config at {path}")
    return Config()
```

```cpp
#include <vector>
#include <string>

class Logger {
public:
    explicit Logger(std::string name) : name_(std::move(name)) {}

    void log(const std::string& msg) {
        entries_.push_back(name_ + ": " + msg);
    }

private:
    std::string name_;
    std::vector<std::string> entries_;
};
```

```bash
#!/bin/bash
set -euo pipefail

TARGET="/var/www/app"
BACKUP="${TARGET}.bak"

if [ -d "$TARGET" ]; then
    cp -r "$TARGET" "$BACKUP"
    echo "Backup created at $BACKUP"
fi

systemctl restart nginx
```

```javascript
const fetchArticle = async (slug) => {
    const res = await fetch(`/api/articles/${slug}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
};

document.querySelectorAll(".article-link").forEach(el => {
    el.addEventListener("click", async (e) => {
        e.preventDefault();
        const article = await fetchArticle(el.dataset.slug);
        console.log(article);
    });
});
```

```css
:root {
    --color-bg: #fdfdfc;
    --color-fg: #1a1a18;
}

.card {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    border: 1px solid var(--color-fg);
    background: var(--color-bg);
}

.card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test</title>
    <link rel="stylesheet" href="/static/css/app.css">
</head>
<body>
    <main id="app">
        <h1>Hello</h1>
    </main>
    <script src="/static/js/app.js" defer></script>
</body>
</html>
```

```yaml
services:
  app:
    image: myapp:latest
    ports:
      - "8080:8080"
    environment:
      - DEBUG=false
      - DB_HOST=postgres
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
```

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "debug": false
  },
  "database": {
    "url": "postgresql://user:pass@localhost/db",
    "pool_size": 5
  }
}
```

The tests won't be perfect, but having a skeleton to edit is faster than building from zero.

## 4. Debugging with AI as a Sounding Board

Debugging embedded code is often a time-consuming loop of forming hypotheses and testing them. Describing your bug to an AI — precisely, with relevant code and hardware context — forces you to articulate the problem clearly, which often surfaces the answer yourself. When it doesn't, the AI's suggested hypotheses are sometimes useful starting points.

Productivity studies back this up: developers using AI assistants report completing debugging tasks up to **55% faster** in controlled settings. [ 2 ] The gain is smaller in deeply hardware-specific situations, but it's not zero.

# Where AI Will Waste Your Time

## Register Addresses and Timing Constraints

Do not trust AI-generated register addresses, bit masks, or timing values without checking them against the datasheet. This is where hallucinations are most dangerous in embedded work. An incorrect bitmask in a peripheral config register won't always cause an obvious failure — it might just silently misconfigure your hardware.

> Rule → Any value that comes from a datasheet must be verified against the datasheet. AI output is a starting point, not a source of truth.

## RTOS Task and Interrupt Design

Stack sizes, priority assignments, and interrupt latency calculations require understanding of your specific hardware and workload. AI can describe general RTOS patterns correctly, but it can't know that your ADC ISR fires every 50μs and your FreeRTOS tick is 1ms. Always own the concurrency design yourself.

## Anything Safety-Critical

IEC 61508, ISO 26262, MISRA C — if your code is going into medical devices, automotive systems, or industrial safety applications, AI-generated code doesn't meet the audit trail and traceability requirements. Keep it out of that path.

# A Real Workflow Example

Here's how I used AI when porting a sensor driver from Arduino to bare-metal ESP32:

1. Pasted the Arduino library into Claude, asked it to identify all hardware-dependent calls (Wire, SPI, delay, millis).
2. Generated an abstraction layer with AI, mapping those calls to ESP-IDF equivalents — reviewed it line by line.
3. Used Copilot for the boilerplate ESP-IDF I2C master init.
4.  Debugged a timing issue by describing the symptoms to Claude (incorrect readings on fast back-to-back reads). It suggested a missing stop condition before repeated start — which was correct.

Total time: ~2 hours. My estimate without AI: 4–5 hours for an unfamiliar SDK.

# Edge AI: Running Models On-Device

A separate but related topic is running ML inference *on* embedded hardware — what the industry calls Edge AI or TinyML.

Modern MCUs like the STM32H7 or ESP32-S3 have enough compute to run small neural networks for tasks like keyword detection, gesture recognition, or anomaly detection on sensor data. Frameworks like TensorFlow Lite for Microcontrollers and Edge Impulse make the deployment pipeline accessible.

The Bosch SoundSee system — deployed on the ISS — is a compelling real-world example: deep learning models running directly on the device, classifying machine audio and detecting bearing wear with over 90% accuracy. [ 3 ]

This is a bigger topic that deserves its own article.

# Summary

AI tools are genuinely useful in embedded development — for the right tasks. Use them to accelerate the repetitive and structural work. Be skeptical of anything that touches hardware-specific values. And never skip verification against the datasheet and reference manual.

The embedded engineer's job isn't going away. The skill ceiling is just shifting toward knowing which parts of the workflow to delegate and which to own.

""",
    },
    {
    "title": "Writing a UART Driver from Scratch on STM32",
    "slug": "uart-driver-stm32",
    "excerpt": "No HAL, no CubeMX. Just registers, a reference manual, and a working serial driver by the end. A ground-up walkthrough of bare-metal UART on the STM32F4.",
    "read_time": 13,
    "is_featured": True,
    "status": "published",
    "seo_title": "Bare-Metal UART Driver STM32 — No HAL",
    "seo_description": "Step-by-step guide to writing a UART driver from scratch on the STM32F4 without HAL or CubeMX. Register-level programming explained.",
    "tags": ["STM32", "C", "Embedded", "Debugging"],
    "category": "Embedded Systems",
    "cover": "uploads/articles/uart-stm32-cover.jpg",
    "inline_assets": [],
    "diagrams": [],
    "attachments": [],
    "body": """\
Most STM32 tutorials start with CubeMX. You click through a GUI, generate a project, and a working UART appears as if by magic. That is fine for shipping a product. It is terrible for actually understanding what is happening. This article skips the magic and writes the driver register by register.

Target: STM32F411, USART2, 115200 baud, 8N1, TX only first, then RX with interrupt-driven ring buffer.

# Clock Setup

Before touching USART2, you need to know which bus it lives on. On the STM32F4, USART2 is on APB1. The reference manual (RM0383) section 6.3 gives you the clock tree.

```c
// Enable USART2 clock
RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

// Enable GPIOA clock (PA2 = TX, PA3 = RX)
RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
```

The order matters. Configure the GPIO clock before you touch the GPIO registers, or you will fault immediately with no useful error message.

# GPIO Alternate Function Configuration

PA2 and PA3 need to be set to alternate function mode, and then the specific alternate function number (AF7 for USART2 on this package) needs to be written to the AFR registers.

```c
// Set PA2 and PA3 to alternate function mode (MODER = 0b10)
GPIOA->MODER &= ~((3 << (2*2)) | (3 << (3*2)));
GPIOA->MODER |=  ((2 << (2*2)) | (2 << (3*2)));

// Set alternate function 7 (USART2) for PA2 and PA3
// Both pins are in AFRL (covers pins 0–7)
GPIOA->AFR &= ~((0xF << (4*2)) | (0xF << (4*3)));
GPIOA->AFR |=  ((7   << (4*2)) | (7   << (4*3)));
```

This is where the reference manual earns its keep — but note that the alternate function mapping lives in the device datasheet (DS10314), not the reference manual. They are separate documents. The datasheet has the pin/AF table. The reference manual has the register descriptions. You need both.

## GPIO Speed and Output Type

For UART at 115200 baud, the default speed setting is fine. For higher baud rates (1Mbaud+) you should explicitly set the output speed:

```c
// Set PA2 to high speed (needed for baud rates above ~1Mbaud)
GPIOA->OSPEEDR |= (3 << (2*2));
```

# Baud Rate Calculation

The baud rate register (BRR) splits into a mantissa and a fractional part. The formula is:

```
USARTDIV = fCK / (16 × BaudRate)
```

With APB1 running at 42MHz and a target of 115200 baud:

```
USARTDIV = 42,000,000 / (16 × 115200) = 22.786
Mantissa = 22     → 0x16
Fraction = 0.786 × 16 = 12.57 → round to 13 → 0xD
BRR = (0x16 << 4) | 0xD = 0x016D
```

```c
USART2->BRR = 0x016D;
```

If you get this wrong the UART will transmit garbage — not silence, not nothing, actual garbage bytes. Always calculate by hand first, then verify on a logic analyser or oscilloscope.

# Enabling the Peripheral

```c
// Enable TX, RX, and the USART peripheral itself
USART2->CR1 |= USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
```

Do not enable `USART_CR1_UE` until all configuration is complete. The reference manual explicitly states that certain fields must not be written while UE is set.

# Transmit: Polling

```c
void uart_putchar(uint8_t c) {
    while (!(USART2->SR & USART_SR_TXE));
    USART2->DR = c;
}

void uart_print(const char *s) {
    while (*s) uart_putchar((uint8_t)*s++);
}
```

`TXE` (Transmit Data Register Empty) goes high when the data register can accept a new byte. This is a blocking, polling transmit — correct for bringing up the peripheral, not ideal for production.

## Waiting for Transmission Complete

If you need to know when the last byte has actually shifted out of the hardware (before disabling the peripheral or entering sleep), wait for `TC` not `TXE`:

```c
void uart_flush(void) {
    while (!(USART2->SR & USART_SR_TC));
}
```

`TXE` means the shift register has accepted your byte. `TC` means the shift register has finished clocking it out onto the wire. For most logging use cases you want `TXE`. For RS-485 direction switching you need `TC`.

# Receive: Interrupt-Driven Ring Buffer

Polling RX works for a terminal echo test. For anything real, use the RXNE interrupt with a ring buffer so the main loop can process bytes at its own pace.

```c
#define RX_BUF_SIZE 128

static volatile uint8_t rx_buf[RX_BUF_SIZE];
static volatile uint8_t rx_head = 0;
static volatile uint8_t rx_tail = 0;

void USART2_IRQHandler(void) {
    if (USART2->SR & USART_SR_RXNE) {
        rx_buf[rx_head] = (uint8_t)USART2->DR;
        rx_head = (rx_head + 1) % RX_BUF_SIZE;
    }

    // Clear overrun error if it occurred — otherwise RXNE stops firing
    if (USART2->SR & USART_SR_ORE) {
        volatile uint32_t dummy = USART2->DR;
        (void)dummy;
    }
}

uint8_t uart_available(void) {
    return rx_head != rx_tail;
}

uint8_t uart_read(void) {
    while (!uart_available());
    uint8_t c = rx_buf[rx_tail];
    rx_tail = (rx_tail + 1) % RX_BUF_SIZE;
    return c;
}
```

Enable the interrupt in the NVIC and in the USART control register:

```c
USART2->CR1 |= USART_CR1_RXNEIE;
NVIC_SetPriority(USART2_IRQn, 1);
NVIC_EnableIRQ(USART2_IRQn);
```

The overrun error handling in the ISR is not optional. If your main loop is slow and bytes arrive faster than you read them, `ORE` sets and the `RXNE` interrupt stops firing until you clear it. The clear sequence on the STM32F4 is a read of SR followed by a read of DR — which the ISR already performs when it reads the received byte. But if you only check `RXNE` and `ORE` has set without `RXNE`, you need the dummy read to clear it.

# DMA Transmit

For transmitting large buffers (log dumps, binary protocol frames), DMA is the right approach. It frees the CPU entirely.

```c
void uart_dma_send(const uint8_t *data, uint16_t len) {
    // Wait for previous DMA transfer to complete
    while (DMA1_Stream6->CR & DMA_SxCR_EN);

    // Configure DMA1 Stream6 (USART2 TX)
    DMA1_Stream6->PAR  = (uint32_t)&USART2->DR;
    DMA1_Stream6->M0AR = (uint32_t)data;
    DMA1_Stream6->NDTR = len;
    DMA1_Stream6->CR   = (4 << DMA_SxCR_CHSEL_Pos)  // Channel 4 = USART2_TX
                       | DMA_SxCR_MINC               // Memory increment
                       | DMA_SxCR_DIR_0              // Memory to peripheral
                       | DMA_SxCR_EN;

    USART2->CR3 |= USART_CR3_DMAT;  // Enable USART DMA transmit request
}
```

DMA channel assignments are in the reference manual (RM0383 table 28). They are fixed per peripheral — you cannot choose them. Getting the channel wrong means the DMA controller ignores the request silently.

# Testing the Driver

The simplest test: echo every received byte back to the sender.

```c
int main(void) {
    SystemClock_Config();
    uart_init();
    uart_print("UART ready\r\n");

    while (1) {
        if (uart_available()) {
            uint8_t c = uart_read();
            uart_putchar(c);
        }
    }
}
```

Connect a USB-UART adapter, open a terminal at 115200 baud, and start typing. Every character should echo back. If it does, your driver is working. If you see garbage, your baud rate calculation is wrong. If you see nothing, your GPIO alternate function configuration is wrong — check the datasheet pin/AF table again.

## The Pattern Generalises

The workflow you used here — enable clocks, configure GPIO alternate functions, set BRR, configure CR1, enable peripheral — is exactly the same for every peripheral on the chip. SPI, I2C, TIM all follow the same sequence. The register names differ, the clock bus differs, but the steps are identical.

Learn this pattern on UART because UART is debuggable with any cheap USB adapter. Then apply it to the next peripheral, and the one after that.
""",
    },
{
    "title": "Setting Up Syncthing on a Raspberry Pi",
    "slug": "syncthing-raspberry-pi",
    "excerpt": "Syncthing as a self-hosted Dropbox replacement. Installation, systemd service, firewall rules, and making it actually survive reboots.",
    "read_time": 5,
    "is_featured": False,
    "status": "published",
    "seo_title": "Syncthing on Raspberry Pi — Self-Hosted File Sync",
    "seo_description": "How to install and configure Syncthing on a Raspberry Pi as a self-hosted file sync server. systemd, firewall, and remote web UI setup.",
    "tags": ["Raspberry Pi", "Linux", "Self-Hosting"],
    "category": "Self-Hosting",
    "cover": "uploads/articles/syncthing-cover.jpg",
    "inline_assets": [],
    "diagrams": [],
    "attachments": [],
    "body":  """Syncthing is a peer-to-peer file synchronisation tool. No cloud, no account, no third party holding your files. You run it on your devices and they sync directly with each other. A Raspberry Pi makes a good always-on node — it is always reachable, consumes almost no power, and can act as the anchor that other devices sync through when they are not on the same network.

# Installation

Syncthing is in the Raspberry Pi OS repositories, but it is usually a version or two behind. Install from the official APT repository instead:

```bash
curl -s https://syncthing.net/release-key.txt | sudo apt-key add -
echo "deb https://apt.syncthing.net/ syncthing stable" | sudo tee /etc/apt/sources.list.d/syncthing.list
sudo apt update && sudo apt install syncthing
```

# Running as a systemd Service

Do not run Syncthing manually. Set it up as a user service so it starts on boot and restarts on failure.

```bash
# Enable and start as the pi user
systemctl --user enable syncthing
systemctl --user start syncthing

# Allow user services to run without an active login session
sudo loginctl enable-linger pi
```

`enable-linger` is the step most tutorials skip. Without it, the user service stops the moment you log out of the SSH session.

Check that it is running:

```bash
systemctl --user status syncthing
```

# Accessing the Web UI Remotely

By default Syncthing binds its web UI to `127.0.0.1:8384` — only accessible from localhost. To reach it from your laptop, either use an SSH tunnel or change the bind address.

SSH tunnel (safer — no firewall changes needed):

```bash
ssh -L 8384:localhost:8384 pi@raspberrypi.local
# Then open http://localhost:8384 in your browser
```

Or edit the config to bind to all interfaces — only do this if the Pi is on a trusted local network:

```xml
<!-- ~/.config/syncthing/config.xml -->
<gui enabled="true" tls="false">
    <address>0.0.0.0:8384</address>
    ...
</gui>
```

Restart Syncthing after editing the config: `systemctl --user restart syncthing`.

# Firewall Rules

Syncthing uses port 22000 for device-to-device sync traffic. If you have `ufw` enabled:

```bash
sudo ufw allow 22000/tcp
sudo ufw allow 22000/udp
sudo ufw allow 21027/udp  # local discovery
```

Without port 22000 open, devices on different networks cannot connect directly and fall back to relay servers, which are slower.

# Adding a Shared Folder

Once the web UI is open, adding a folder is straightforward: click Add Folder, set the path on the Pi (e.g. `/home/pi/sync`), and save. Then add your other devices by exchanging device IDs and share the folder with them.

The device ID is shown in Actions → Show ID. It is a long alphanumeric string that uniquely identifies each Syncthing instance. Share yours with the devices you want to sync with, and add theirs in return.

# Keeping the Data Drive Mounted

If your sync folder lives on an external drive, make sure it mounts before Syncthing starts. Add it to `/etc/fstab` with the `nofail` option so a missing drive does not prevent boot:
    """}
]
