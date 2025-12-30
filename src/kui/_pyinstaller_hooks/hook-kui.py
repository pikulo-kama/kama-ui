from PyInstaller.utils.hooks import collect_submodules, collect_data_files  # noqa
import os


datas = collect_data_files("kui.stylesheet")
hiddenimports = (
    collect_submodules("kui.component") +
    collect_submodules("kui.resolver")
)

for file_name in ["kamaconfig.yaml", "kamaconfig.yml"]:
    if os.path.exists(os.path.join(os.getcwd(), file_name)):
        datas.append((file_name, "."))
