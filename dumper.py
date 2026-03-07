import urllib.request
import re

html = urllib.request.urlopen("http://127.0.0.1:8503").read().decode("utf-8")
print(html)
