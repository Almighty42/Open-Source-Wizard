ARTICLES = [
    {
        "title": "AI in Embedded Development: Practical Uses Without the Hype",
        "slug": "ai-in-embedded-development",
        "excerpt": "LLMs won't replace embedded engineers — but they're already cutting debug time in half and generating driver boilerplate in seconds. Here's how I actually use AI tools in my firmware workflow.",
        "read_time": 8,
        "is_featured": True,
        "status": "published",
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
        ],
        "attachments": [
            "uploads/files/sensor_driver_port.c",
            "uploads/files/ai-embedded-workflow-checklist.pdf",
        ],
        "body": """\
There's a growing split in the embedded community. Half the engineers I talk to swear by AI coding tools.
The other half won't touch them — convinced that LLMs hallucinate register addresses and don't understand timing constraints.

Both sides have a point. This article isn't about hype. It's about where AI tools *actually* help in a firmware workflow,
and where they'll waste your time or silently break your code.

## The Honest Reality

AI models are trained predominantly on web, cloud, and application-layer code.
They've seen far less embedded C, and almost no vendor-specific HAL code for a niche MCU like the STM32G0 or RP2040.
That gap matters.

But "less useful than for web dev" isn't the same as "useless." There are specific parts of the embedded workflow
where AI provides genuine leverage — and a few where it's actively dangerous.

## Where AI Actually Helps

### 1. Boilerplate and Peripheral Initialization

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

### 2. Understanding Unfamiliar Code

When you open a 3-year-old driver written by someone who left the company,
asking an LLM to explain what a function does and what could go wrong is genuinely useful.

```c
// Pasted a 60-line I2C transaction handler into Claude.
// It immediately flagged a missing timeout guard on the ACK poll loop —
// which would have caused the MCU to hang on a disconnected sensor.
while (!(I2C1->SR1 & I2C_SR1_ADDR)); // no timeout — hangs forever if NACK
```

### 3. Writing Unit Tests

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

## Where AI Will Waste Your Time

> **Rule:** Any value that comes from a datasheet must be verified against the datasheet.
> AI output is a starting point, not a source of truth.

- Register addresses and bit masks — always verify
- RTOS stack sizes and interrupt priorities — you own this
- Anything safety-critical (IEC 61508, ISO 26262, MISRA C) — keep AI out

## A Real Workflow Example

Here's how I used AI when porting a sensor driver from Arduino to bare-metal ESP32:

1. Pasted the Arduino library into Claude, asked it to identify all hardware-dependent calls
2. Generated an abstraction layer with AI, mapping those calls to ESP-IDF equivalents
3. Used Copilot for the boilerplate ESP-IDF I2C master init
4. Debugged a timing issue by describing the symptoms — it suggested a missing stop condition before repeated start, which was correct

Total time: ~2 hours. My estimate without AI: 4–5 hours for an unfamiliar SDK.

## Edge AI: Running Models On-Device

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

## Goals

- Dual SSD storage (RAID 1 via `mdadm` or simple JBOD)
- Battery-backed (5–6 hours runtime)
- Gigabit ethernet + WiFi
- Runs Docker for services like Samba, Syncthing, and a lightweight dashboard
- Fits in a 3D-printed enclosure under 200mm × 120mm

## Parts

| Part | Notes |
|---|---|
| Raspberry Pi 4 (4GB) | Main compute |
| 2× Samsung 870 EVO 500GB | Connected via USB 3.0 hub |
| Waveshare UPS HAT | 18650 battery pack, I2C fuel gauge |
| 4-port USB 3.0 hub | Powered, plugged into Pi USB 3 port |
| 3D-printed enclosure | Designed in FreeCAD |

## Power Budget

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

## Software Stack

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

## What I'd Change

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
        "status": "draft",
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
]
