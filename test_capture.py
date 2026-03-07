import subprocess
import time

try:
    p = subprocess.Popen(["uv", "run", "streamlit", "run", "test_simple.py", "--server.port=8513", "--server.headless=true"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    p.terminate()
    stdout, stderr = p.communicate()
    print("STDOUT:", stdout.decode("utf-8"))
    print("STDERR:", stderr.decode("utf-8"))
except Exception as e:
    print("Error:", e)
