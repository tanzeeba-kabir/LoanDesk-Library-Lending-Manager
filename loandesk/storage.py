"""Helpers for reading and writing JSON files."""

import json


def load_json(filepath):
    """Read a JSON file and return its contents."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(filepath, data):
    """Write data to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
