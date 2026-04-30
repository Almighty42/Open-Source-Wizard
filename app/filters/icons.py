from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ICON_DIR = BASE_DIR / "static" / "assets" / "icons"

def _load_svg(filename: str) -> str:
    with open(ICON_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()

INFO_ICON = _load_svg("blockquote_info.svg")
COPY_ICON = _load_svg("copy_code.svg")

LANGUAGE_LABELS = {
    "python": "Python", "c": "C", "cpp": "C++",
    "bash": "Bash", "sh": "Bash", "yaml": "YAML",
    "json": "JSON", "html": "HTML", "css": "CSS",
    "javascript": "JavaScript", "js": "JavaScript", "nginx": "Nginx",
}

LANGUAGE_ICONS = {
    key: _load_svg(f"languages/{filename}")
    for key, filename in {
        "python": "python.svg", "c": "c.svg", "cpp": "cpp.svg",
        "css": "css.svg", "html": "html.svg", "javascript": "js.svg",
        "js": "js.svg", "json": "json.svg", "nginx": "nginx.svg",
        "yaml": "yaml.svg", "bash": "bash.svg", "sh": "bash.svg",
    }.items()
}
