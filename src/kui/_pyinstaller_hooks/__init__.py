import os


def get_hook_dirs():
    dirr = os.path.dirname(__file__)

    with open("C:\\Users\\djara\\AppData\\Roaming\\SaveGem\\test.txt", "w") as file:
        file.write(dirr)

    return [dirr]
