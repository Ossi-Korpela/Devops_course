
from flask import Flask, jsonify

import subprocess
import requests
import time

import threading

lock = threading.Lock()
unavailable_until = 0


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
    global unavailable_until
    current_time = time.time()
    if current_time < unavailable_until:
        return jsonify({"error": "busy"}), 503
    
    with lock:
        info1 = sys_info()
        response2 = requests.get('http://service2:8200/')
        info2 = response2.json()
        
        resp = jsonify({
            "Service1": info1,
            "Service2": info2
        })

        
        unavailable_until = time.time() + 2      
        return resp



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8199)
