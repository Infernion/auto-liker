import codecs
import json
import logging
import os
from pathlib import Path


class SettingsManager:
    settings_dir = Path("./settings").absolute()

    def __init__(self, settings_dir):
        self.setting_dir = Path(settings_dir)

    @property
    def setting_path(self):
        return self.settings_dir / self.setting_file_name

    @property
    def setting_file_name(self):
        raise NotImplementedError

    def save_settings(self, settings):
        with open(self.setting_path, "w") as outfile:
            json.dump(settings, outfile, default=to_json)
            logging.debug(f"Settings for {self.setting_file_name} was saved.")

    def delete_setting(self):
        logging.debug(f"Deleting settings for {self.setting_file_name}.")
        os.remove(self.setting_path)

    def get_settings(self):
        if not self.setting_path.exists():
            return None

        with open(self.setting_path, "r") as file_data:
            logging.debug(f"Getting settings for {self.setting_file_name}.")
            cached_settings = json.load(file_data, object_hook=from_json)
            return cached_settings


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {
            "__class__": "bytes",
            "__value__": codecs.encode(python_object, "base64").decode(),
        }
    raise TypeError(repr(python_object) + " is not JSON serializable")


def from_json(json_object):
    if "__class__" in json_object and json_object["__class__"] == "bytes":
        return codecs.decode(json_object["__value__"].encode(), "base64")
    return json_object
