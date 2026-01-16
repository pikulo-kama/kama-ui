import importlib.metadata
import os

from PyInstaller.utils.hooks import collect_entry_point, copy_metadata  # noqa
from PyInstaller.utils.hooks import collect_submodules, collect_data_files  # noqa


datas, hiddenimports = collect_entry_point("kama_ui.plugins")

# Import modules and metadata of KamaUI plugins
# since they're being discovered and invoked
# dynamically.
for dist in importlib.metadata.distributions():
    if not any(ep.group == "kama_ui.plugins" for ep in dist.entry_points):
        continue

    # Use the actual package name (the folder name),
    # not just the metadata Name
    library_name = dist.metadata["Name"]
    packages = dist.read_text("top_level.txt").strip().splitlines()

    datas += copy_metadata(library_name)

    for package_name in packages:
        hiddenimports.append(package_name)
        hiddenimports += collect_submodules(package_name)
        datas += collect_data_files(package_name)

# Collect resolvers, components, controllers and stylesheet
# since they're not being imported anywhere.
datas += collect_data_files("kui.stylesheet")
hiddenimports += collect_submodules("kui.component")
hiddenimports += collect_submodules("kui.controller")
hiddenimports += collect_submodules("kui.resolver")

for file_name in ["kamaconfig.yaml", "kamaconfig.yml"]:
    if os.path.exists(os.path.join(os.getcwd(), file_name)):
        datas.append((file_name, "."))
