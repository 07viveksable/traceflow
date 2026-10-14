import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILE = BASE_DIR / "config" / "config.json"


def load_config():
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    return config