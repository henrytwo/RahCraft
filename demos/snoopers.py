import platform
import datetime
import time
import getpass
import requests

current_version, current_build = '1.0', '1.0'

information = [
              current_version,
              current_build,
              platform.machine(),
              platform.version(),
              platform.platform(),
              platform.uname(),
              platform.system(),
              platform.processor(),
              getpass.getuser(),
              datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
              requests.get('http://ip.42.pl/raw').text]

for line in information:
    print(line)