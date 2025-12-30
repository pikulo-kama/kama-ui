import os.path

datas = []
possible_files = [
    "kamaconfig.yaml",
    "kamaconfig.yml",
]

for file_name in possible_files:
    if os.path.exists(os.path.join(os.getcwd(), file_name)):
        datas.append((file_name, "."))
