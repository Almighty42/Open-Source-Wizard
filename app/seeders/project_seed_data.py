PROJECTS = [
    {
        "title": "Self-Hosted TRMNL Server",
        "slug": "self-hosted-trmnl-server",
        "excerpt": "Running a local TRMNL server behind Nginx on a Raspberry Pi, with custom plugins and a Let's Encrypt certificate.",
        "is_featured": True,
        "status": "published",
        "project_state": "ongoing",
        "platform": "Raspberry Pi",
        "repo_url": "https://github.com/luka/trmnl-server",
        "demo_url": None,
        "seo_title": "Self-Hosted TRMNL Server Setup",
        "seo_description": "How I set up a self-hosted TRMNL server on a Raspberry Pi with Nginx, Docker, and a custom plugin system.",
        "tags": ["Raspberry Pi", "Docker", "Nginx", "Python"],
        "category": "Self-Hosting",
        "cover": "static/uploads/projects/self-hosted-trmnl-server/images/trmnl-server-cover.jpg",
        "inline_assets": [
            "static/uploads/projects/self-hosted-trmnl-server/images/trmnl-ui-screenshot.webp",
        ],
        "attachments": [],
        "body": """\
TRMNL is an e-ink dashboard device with a plugin-based display system.
The official cloud backend is fine, but I wanted full control — custom plugins,
no rate limits, and local network access without a cloud dependency.

# Stack

- **Flask** for the plugin API
- **Docker Compose** for service isolation
- **Nginx** as reverse proxy with Let's Encrypt SSL
- **SQLite** for plugin state (simple enough for this use case)

![TRMNL UI](asset:static/uploads/projects/self-hosted-trmnl-server/images/trmnl-ui-screenshot.webp)

# Nginx Config

```nginx
server {
    listen 443 ssl;
    server_name trmnl.local;

    ssl_certificate     /etc/letsencrypt/live/trmnl.local/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trmnl.local/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

# Plugin System

Each plugin is a Python module that returns a dict of template variables.
The TRMNL device polls `/api/display` every 60 seconds and renders the response.

```python
@app.route("/api/display")
def display():
    plugin = load_plugin(request.args.get("plugin", "clock"))
    return jsonify(plugin.render())
```

# What's Left

- [ ] OTA plugin update mechanism
- [ ] Web UI for managing plugin order and schedule
- [ ] Battery level reporting from device back to server
""",
    },
    {
        "title": "Kindle Dashboard Mod",
        "slug": "kindle-dashboard-mod",
        "excerpt": "Jailbreaking a Kindle 4 and turning it into a low-power ambient dashboard using KUAL and a custom Python script.",
        "is_featured": True,
        "status": "published",
        "project_state": "finished",
        "platform": "Kindle",
        "repo_url": "https://github.com/luka/kindle-dashboard",
        "demo_url": None,
        "seo_title": "Kindle 4 Dashboard Mod",
        "seo_description": "How I jailbroke a Kindle 4 and turned it into a low-power ambient information display using KUAL and a custom Python script.",
        "tags": ["E-Ink", "Python", "Linux", "Debugging"],
        "category": "Reverse Engineering",
        "cover": "static/uploads/projects/kindle-dashboard-mod/images/kindle-dashboard-cover.jpg",
        "inline_assets": [
            "static/uploads/projects/kindle-dashboard-mod/images/dashboard.png",
        ],
        "attachments": [],
        "body": """\
An old Kindle 4 has a 6-inch e-ink display, a 1GHz ARM processor, 256MB RAM,
and draws about 170mW while rendering. It's basically a perfect ambient display.

![Dashboard](asset:static/uploads/projects/kindle-dashboard-mod/images/dashboard.png)

# Jailbreak

The Kindle 4 (2011) can be jailbroken using the `kindle-jailbreak` package.
Once jailbroken, KUAL (Kindle Unified Application Launcher) allows running
arbitrary scripts and binaries.

# Display Script

The dashboard script fetches data, generates a 600×800 PNG using Pillow,
and pushes it to the e-ink framebuffer via `eips`.

```python
import subprocess
from PIL import Image, ImageDraw, ImageFont

def render_dashboard(weather, time_str):
    img = Image.new("L", (600, 800), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/mnt/us/dashboard/fonts/Inter.ttf", 48)
    draw.text((40, 40), time_str, font=font, fill=0)
    draw.text((40, 120), weather, font=font, fill=0)
    img.save("/tmp/dashboard.png")
    subprocess.run(["eips", "-g", "/tmp/dashboard.png"])

render_dashboard("18°C, Cloudy", "14:32")
```

# Power

The Kindle stays in a light sleep between refreshes.
Full display refresh happens every 10 minutes; partial clock update every minute.
Average power draw: ~90mW — the original battery lasts weeks.

# Lessons

- `eips` only accepts 8-bit grayscale PNGs at exactly 600×800
- Font rendering needs explicit subpixel hints off for clean e-ink output
- The Kindle's Python is 2.7 — either use a cross-compiled Python 3 binary or stay on 2.7
""",
    },
    {
        "title": "ESP32 Sensor Node with Battery Telemetry",
        "slug": "esp32-sensor-node",
        "excerpt": "A wireless sensor node using an ESP32, BME280, and a LiPo battery with fuel gauge. Sends telemetry over MQTT with deep sleep between readings.",
        "is_featured": False,
        "status": "published",
        "project_state": "finished",
        "platform": "ESP32",
        "repo_url": "https://github.com/luka/esp32-sensor-node",
        "demo_url": "https://github.com/luka/esp32-sensor-node",
        "seo_title": "ESP32 Wireless Sensor Node",
        "seo_description": "Building a low-power ESP32 sensor node with BME280 and LiPo battery. Sends MQTT telemetry with deep sleep between readings.",
        "tags": ["ESP32", "C", "Power Management", "Debugging"],
        "category": "Embedded Systems",
        "cover": "",
        "attachments": [],
        "body": """\
A battery-powered sensor node that reads temperature, humidity, and pressure
from a BME280, sends the data over MQTT, then goes back to deep sleep.
Target runtime: 6 months on a single 2000mAh LiPo.

# Hardware

- ESP32-WROOM-32
- BME280 (I2C, 3.3V)
- MAX17048 fuel gauge (I2C)
- TP4056 charging module
- 2000mAh LiPo

# Deep Sleep Loop

```c
#define SLEEP_DURATION_US  (60 * 1000000ULL) // 60 seconds

void app_main(void) {
    init_i2c();
    bme280_data_t data = bme280_read();
    float soc = max17048_read_soc();

    mqtt_publish("/sensors/node1", 
        "{\"temp\": %.1f, \"hum\": %.1f, \"soc\": %.1f}",
        data.temperature, data.humidity, soc
    );

    mqtt_disconnect();
    wifi_stop();
    esp_deep_sleep(SLEEP_DURATION_US);
}
```

# Power Budget

| State | Current | Duration |
|---|---|---|
| Deep sleep | 10μA | 58s |
| WiFi connect + publish | ~180mA | ~2s |
| Average | ~8mA | — |

At 8mA average, a 2000mAh battery gives approximately **250 hours** — about 10 days.
Extending the sleep interval to 5 minutes drops average current to ~2mA and pushes
runtime to over 40 days.

# What's Next

- RTC-based scheduled wake instead of timer-only
- OTA firmware update support
- Second node for outdoor placement
""",
    },
]
