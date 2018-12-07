import json
import os
import sys

from cerberus import Validator


class DaemonConfig:

    def __init__(self):
        self.default_config = {"plaintext_only": False,
                               "random_hit_chance": False,
                               "random_instances": False,
                               "save_logs": False}
        self.custom_config = self.default_config

    def setup(self):
        """Read and setup custom daemon configuration if provided."""
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.split(cur_dir)[0]
        cfg_path = os.path.join(parent_dir, "config", "daemon.json")
        try:
            with open(cfg_path) as f:
                try:
                    custom_config = json.load(f)
                except json.JSONDecodeError:
                    sys.exit("Error: Daemon configuration file is "
                             "not a valid JSON document!")
            self.custom_config = custom_config
        except FileNotFoundError:
            pass

    def valid(self):
        """Return a bool indicating the validity of custom daemon configuration."""
        schemas = [{"plaintext_only": {"type": "boolean",
                                     "allowed": [False]},
                  "random_hit_chance": {"type": "boolean"},
                  "random_instances": {"type": "boolean",
                                       "forbidden": [True]},
                  "save_logs": {"type": "boolean"}},

                  {"plaintext_only": {"type": "boolean",
                                     "allowed": [True]},
                  "random_hit_chance": {"type": "boolean"},
                  "random_instances": {"type": "boolean"},
                  "save_logs": {"type": "boolean"}}]

        schema = {"c": {"oneof_schema": schemas, "type": "dict"}}
        v = Validator(schema)

        config = {"c": self.custom_config}
        res = v.validate(config)
        return res
