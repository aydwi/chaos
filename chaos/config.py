import json
import os
import sys

from cerberus import Validator

class DaemonConfig:

    def __init__(self):
        self.default_config = {'save_logs': False,
                               'randomize': False,
                               'X11_special_paste': False,
                               'plaintext_only': False}
        self.custom_config = self.default_config

    def set_config(self):
        """Read and set custom daemon configuration if provided."""
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.split(cur_dir)[0]
        cfg_path = os.path.join(parent_dir, 'config', 'daemon.json')
        try:
            with open(cfg_path) as f:
                try:
                    custom_config = json.load(f)
                except json.JSONDecodeError:
                    sys.exit("Error: Daemon configuration file is not a valid JSON document!")
            self.custom_config = custom_config
        except FileNotFoundError:
            pass

    def valid_config(self):
        """Return a bool indicating the validity of custom daemon configuration."""
        schema = {'save_logs': {'type': 'boolean'},
                  'randomize': {'type': 'boolean'},
                  'X11_special_paste': {'type': 'boolean'},
                  'plaintext_only': {'type': 'boolean'}}
        v = Validator()
        res = v.validate(self.custom_config, schema)
        return res
