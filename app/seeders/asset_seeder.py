from app.models import Asset
from app.extensions import db
from app.seeders.base import BaseSeeder

CORE_ASSETS = [
    # --- Article covers ---
    {
        "path": "static/uploads/articles/ai-in-embedded-development/images/ai-embedded-cover.jpg",
        "alt_text": "ESP32 development board next to a laptop showing C code",
        "caption": "AI-assisted firmware development at the workbench",
    },
    {
        "path": "static/uploads/articles/portable-raspberry-pi-nas/images/nas-internals.jpg",
        "alt_text": "Raspberry Pi NAS internals with SSDs and wiring",
        "caption": "Internal layout of the portable Raspberry Pi NAS build",
    },
    {
        "path": "static/uploads/articles/eink-refresh-bug/images/eink-debug-cover.jpg",
        "alt_text": "E-ink display showing partial refresh artifact",
        "caption": "Partial refresh ghosting on the 4.2 inch Waveshare panel",
    },
    {
        "path": "static/uploads/articles/ai-in-embedded-development-article/images/cover.png",
        "alt_text": "Neovim window with AI-suggested embedded C code",
        "caption": "Using AI tools inside a terminal-focused firmware workflow",
    },
    {
        "path": "static/uploads/articles/uart-driver-stm32/images/uart-stm32-cover.webp",
        "alt_text": "STM32 development board connected via USB-UART adapter",
        "caption": "Bare-metal UART driver running on an STM32F4 board",
    },

    # --- Project covers  ---
    {
        "path": "static/uploads/projects/self-hosted-trmnl-server/images/trmnl-server-cover.jpg",
        "alt_text": "TRMNL dashboard running on a self-hosted server",
        "caption": "Self-hosted TRMNL server behind Nginx",
    },
    {
        "path": "static/uploads/projects/kindle-dashboard-mod/images/kindle-dashboard-cover.jpg",
        "alt_text": "Jailbroken Kindle displaying a custom dashboard",
        "caption": "Jailbroken Kindle 4 running a live dashboard",
    },

    # --- Inline article images ---
    {
        "path": "static/uploads/articles/ai-in-embedded-development/images/ai-copilot-screenshot.png",
        "alt_text": "GitHub Copilot suggesting C code in Neovim",
        "caption": "Copilot autocompleting an I2C init function",
    },
    {
        "path": "static/uploads/articles/ai-in-embedded-development/images/esp32-breadboard.jpg",
        "alt_text": "ESP32 wired to an I2C sensor breakout on a breadboard",
        "caption": "I2C sensor wiring during driver port testing",
    },
    {
        "path": "static/uploads/articles/portable-raspberry-pi-nas/images/nas-internals.jpg",
        "alt_text": "Internal wiring of the portable NAS enclosure",
        "caption": "Power routing and USB hub inside the enclosure",
    },

    # --- Inline project images ---

    {
        "path": "static/uploads/projects/self-hosted-trmnl-server/images/trmnl-ui-screenshot.webp",
        "alt_text": "Placeholder",
        "caption": "Placeholder",
    },

    {
        "path": "static/uploads/projects/kindle-dashboard-mod/images/dashboard.png",
        "alt_text": "Placeholder",
        "caption": "Placeholder",
    },

    # --- Diagrams ---
    {
        "path": "static/uploads/articles/ai-in-embedded-development/diagrams/i2c-sensor-block.png",
        "alt_text": "Block diagram showing MCU to I2C sensor connection",
        "caption": "I2C bus topology for the sensor node",
    },

    # --- Attachments ---
    {
        "path": "static/uploads/articles/ai-in-embedded-development/files/sensor_driver_port.c",
        "alt_text": None,
        "caption": "Ported I2C sensor driver for ESP-IDF",
    },

    # --- Videos ---
    {
        "path": "static/uploads/articles/ai-in-embedded-development/videos/esp32-demo.mp4",
        "alt_text": None,
        "caption": "ESP32 sensor node demo",
    },
]

class AssetSeeder(BaseSeeder):
    def run(self):
        created = 0
        skipped = 0
        for data in CORE_ASSETS:
            exists = db.session.query(Asset).filter_by(path=data["path"]).first()
            if exists:
                skipped += 1
                continue
            asset = Asset(
                    path=data["path"],
                    alt_text=data["alt_text"],
                    caption=data["caption"],
            )
            db.session.add(asset)
            created += 1
        db.session.commit()
        print(f"[AssetSeeder] {created} created, {skipped} skipped.")
