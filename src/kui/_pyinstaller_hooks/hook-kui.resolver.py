from PyInstaller.utils.hooks import collect_submodules  # noqa
hiddenimports = collect_submodules("kui.resolver")
