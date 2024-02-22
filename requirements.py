import os
import platform

pip_install = 'pip install -U pip'
packages = 'pip install -U discord requests aiohttp python-dotenv'

if platform.system == 'Windows':  # if OS is Windows
    os.system('python.exe -m' + pip_install)

elif platform.system=='Linux':  # if OS is Linux
    os.system('python3 -m' + pip_install)

os.system(packages)
