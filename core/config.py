import json
import os.path

config_path = os.path.join(os.path.dirname(__file__), "../config.json")

with open(config_path, "r") as config_json_file:
    config = json.load(config_json_file)
