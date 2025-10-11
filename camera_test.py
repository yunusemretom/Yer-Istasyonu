import subprocess
import re
import platform

def list_cameras():
    system = platform.system().lower()

    if "windows" in system:
        cmd = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
    elif "linux" in system:
        cmd = ['ffmpeg', '-f', 'v4l2', '-list_devices', 'true', '-i', '']
    elif "darwin" in system:  # macOS
        cmd = ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '']
    else:
        raise Exception("Bilinmeyen işletim sistemi")

    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    devices = re.findall(r'\[.*?\] "(.*?)"', result.stderr)
    return devices

print(list_cameras())
