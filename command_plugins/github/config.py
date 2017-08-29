from hubcommander.auth_plugins.enabled_plugins import AUTH_PLUGINS
import json
import os
from pathlib import Path

# Define the organizations that this Bot will examine.
ORGS = json.loads(Path(os.environ["HUBCOMMANDER_ORGS"]).read_text())
# github API Version
GITHUB_VERSION = "application/vnd.github.v3+json"
# GITHUB API PATH:
GITHUB_URL = "https://api.github.com/"

modules = {}
def load_auth_plugin(module_name, class_name):
    if modules.get(module_name, None):
        return modules[module_name]
    modules[module_name] = getattr(importlib.import_module(module_name), class_name)()

USER_COMMAND_DICT = json.loads(Path(os.environ["HUBCOMMANDER_USER_COMMANDS"]).read_text())
if USER_COMMAND_DICT:
    for k, v in USER_COMMAND_DICT.items():
        if v.get("auth"):
           USER_COMMAND_DICT[k]["auth"]["plugin"] = AUTH_PLUGINS[v["auth"]["plugin"]]
           v["auth"].setdefault("kwargs", {})

# if set to True, any commands not mentioned in the USER_COMMAND_DICT will be
# enabled by default
IMPLICIT_COMMAND_ENABLE = os.environ.get("IMPLICIT_COMMAND_ENABLE", True) == True
