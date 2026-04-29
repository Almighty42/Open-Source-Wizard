from app.models import Asset
from app.extensions import db
from app.seeders.base import BaseSeeder

CORE_ASSETS = [
    # --- Article covers ---
    {
        "path": "uploads/articles/ai-embedded-cover.jpg",
        "alt_text": "ESP32 development board next to a laptop showing C code",
        "caption": "AI-assisted firmware development at the workbench",
    },
    {
        "path": "uploads/articles/portable-nas-cover.jpg",
        "alt_text": "Raspberry Pi inside a compact 3D-printed enclosure",
        "caption": "The finished portable NAS build",
    },
    {
        "path": "uploads/articles/eink-debug-cover.jpg",
        "alt_text": "E-ink display showing partial refresh artifact",
        "caption": "Partial refresh ghosting on the 4.2 inch Waveshare panel",
    },

    # --- Project covers ---
    {
        "path": "uploads/projects/trmnl-server-cover.jpg",
        "alt_text": "TRMNL dashboard running on a self-hosted server",
        "caption": "Self-hosted TRMNL server behind Nginx",
    },
    {
        "path": "uploads/projects/kindle-dashboard-cover.jpg",
        "alt_text": "Jailbroken Kindle displaying a custom dashboard",
        "caption": "Jailbroken Kindle 4 running a live dashboard",
    },
    {
        "path": "uploads/projects/esp32-sensor-cover.jpg",
        "alt_text": "ESP32 sensor node on a breadboard with battery pack",
        "caption": "ESP32 sensor node with BME280 and LiPo battery",
    },

    # --- Inline article images ---
    {
        "path": "uploads/articles/ai-copilot-screenshot.png",
        "alt_text": "GitHub Copilot suggesting C code in Neovim",
        "caption": "Copilot autocompleting an I2C init function",
    },
    {
        "path": "uploads/articles/esp32-breadboard.jpg",
        "alt_text": "ESP32 wired to an I2C sensor breakout on a breadboard",
        "caption": "I2C sensor wiring during driver port testing",
    },
    {
        "path": "uploads/articles/nas-internals.jpg",
        "alt_text": "Internal wiring of the portable NAS enclosure",
        "caption": "Power routing and USB hub inside the enclosure",
    },

    # --- Diagrams ---
    {
        "path": "uploads/diagrams/i2c-sensor-block.svg",
        "alt_text": "Block diagram showing MCU to I2C sensor connection",
        "caption": "I2C bus topology for the sensor node",
    },
    {
        "path": "uploads/diagrams/cloud-vs-edge-ai.svg",
        "alt_text": "Diagram comparing cloud AI and edge AI architectures",
        "caption": "Cloud AI vs edge AI — where inference runs",
    },
    {
        "path": "uploads/diagrams/esp32-power-schematic.svg",
        "alt_text": "Schematic showing ESP32 power circuit with LDO regulator",
        "caption": "Power supply circuit for the ESP32 sensor node",
    },

    # --- Attachments ---
    {
        "path": "uploads/files/sensor_driver_port.c",
        "alt_text": None,
        "caption": "Ported I2C sensor driver for ESP-IDF",
    },
    {
        "path": "uploads/files/portable-nas-bom.pdf",
        "alt_text": None,
        "caption": "Full bill of materials for the portable NAS build",
    },
    {
        "path": "uploads/files/ai-embedded-workflow-checklist.pdf",
        "alt_text": None,
        "caption": "AI-assisted embedded development workflow checklist",
    },

    # --- Gallery ---
    {
        "path": "uploads/gallery/trmnl-ui-screenshot.png",
        "alt_text": "TRMNL web dashboard showing plugin grid",
        "caption": "TRMNL plugin grid after initial setup",
    },
    {
        "path": "uploads/gallery/kindle-dashboard-closeup.jpg",
        "alt_text": "Close-up of Kindle screen showing weather and calendar",
        "caption": "Weather and calendar widgets on the Kindle dashboard",
    },
    {
        "path": "uploads/gallery/esp32-sensor-enclosure.jpg",
        "alt_text": "3D-printed enclosure for the ESP32 sensor node",
        "caption": "Printed enclosure before final assembly",
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
