
from flask import Flask, jsonify

import subprocess
import requests


app = Flask(__name__)


def sys_info():
    ip = subprocess.getoutput("hostname -I").strip()
    processes = subprocess.getoutput("ps -ax")
    disk = subprocess.getoutput("df -h /")
    uptime = subprocess.getoutput("uptime -p")
    return {
        "IP address": ip,
        "Processes": processes,
        "Disk space": disk,
        "Uptime": uptime
    }

@app.route('/', methods=['GET'])
def index():
    info1 = sys_info()
    response2 = requests.get('http://service2:8200/')
    info2 = response2.json()
    return jsonify({
        "Service1": info1,
        "Service2": info2
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8199)
