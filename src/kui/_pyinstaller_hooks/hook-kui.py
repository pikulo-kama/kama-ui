import importlib.metadata
import os

from PyInstaller.utils.hooks import collect_entry_point, copy_metadata  # noqa
from PyInstaller.utils.hooks import collect_submodules, collect_data_files  # noqa


# 1. This finds all packages registered under your entry points
# and tells PyInstaller to bundle them as hidden imports.
plugin_data, hiddenimports = collect_entry_point("kama_ui.plugins")
datas = [plugin_data]


for dist in importlib.metadata.distributions():
    if any(ep.group == "kama_ui.plugins" for ep in dist.entry_points):
        datas += copy_metadata(dist.metadata['Name'])


datas += collect_data_files("kui.stylesheet")
hiddenimports += collect_submodules("kui.component")
hiddenimports += collect_submodules("kui.resolver")


for file_name in ["kamaconfig.yaml", "kamaconfig.yml"]:
    if os.path.exists(os.path.join(os.getcwd(), file_name)):
        config_data: tuple[str, str] = (file_name, ".")
        datas.append(config_data)
