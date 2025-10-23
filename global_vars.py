import sys
import os.path
import PySide6
from pyqtconfig import ConfigManager

logo_base = "Emmas_owl_logo.png"
if getattr(sys, 'frozen', False):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    logo_path = os.path.join(bundle_dir, logo_base)
else:
    logo_path = logo_base


default_settings = {
    "default_proj": "default/default.json",
    "use_recent_proj": True,
    "most_recent_path": "default/default.json",
    "inout_polygon_path": "Scotese_2016a_Plate_Polygons.gpml"
}
default_metadata = {
    "default_proj": {
        "use_key_name": False,
        "display_name": "Default project"
    },
    "use_recent_proj": {
        "use_key_name": False,
        "display_name": "Use most recent project?"
    },
    "most_recent_path": {
        "prefer_hidden": True
    },
    "inout_polygon_path": {
        "use_key_name": False,
        "display_name": "Polygon file for assigning Plate IDs"
    }
}

configs = ConfigManager(default_settings, filename=".config_settings.json")
configs.set_many_metadata(default_metadata)


def update_config(updated_config_dict):
    global configs
    configs.set_many(updated_config_dict)
    configs.save()