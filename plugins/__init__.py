import importlib
import os
import re


def load_plugins():
    search_re = re.compile("^[^_].+\\.py$", re.IGNORECASE)
    plugins_dir = os.path.dirname(__file__)
    files = list(filter(search_re.search, os.listdir(plugins_dir)))
    plugins = ["." + os.path.splitext(f)[0] for f in files]
    importlib.import_module("plugins")
    modules = []
    for plugin in plugins:
        modules.append(importlib.import_module(plugin, package="plugins"))
    return modules
