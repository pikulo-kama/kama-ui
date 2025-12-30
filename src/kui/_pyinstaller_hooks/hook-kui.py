from PyInstaller.utils.hooks import collect_submodules, collect_data_files  # noqa
import os.path
import sys


datas = collect_data_files("kui.stylesheet")
hiddenimports = (
    collect_submodules("kui.component") +
    collect_submodules("kui.resolver")
)

base_path = os.path.dirname(os.path.abspath(__file__))
possible_files = [
    "kamaconfig.yaml",
    "kamaconfig.yml",
]

for file_name in possible_files:
    if os.path.exists(os.path.join(base_path, file_name)):
        datas.append((file_name, "."))

print(f">>> Kama-UI Hook: Found datas: {datas}", file=sys.stderr)
