import os
import socket
import subprocess
import time
import threading
import datetime

import requests
from flask import Flask, jsonify, request, abort, Response

lock = threading.Lock()
unavailable_until = 0

INIT = "INIT"
PAUSED = "PAUSED"
RUNNING = "RUNNING"
SHUTDOWN = "SHUTDOWN"
state = INIT

app = Flask(__name__)

log_data = f"{datetime.datetime.now()}: {INIT}\n"

def set_log(new_state):
    global log_data, state
    old_state = state
    log_data += f"{datetime.datetime.now()}: {old_state}->{new_state}\n"

def exec_command(command):
    try:
        result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr and not result.stdout:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"

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


@app.route('/api', methods=['GET'])
def index():
    global unavailable_until, state

    if state == PAUSED:
        return jsonify({"error": "paused"}), 503
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
        return resp, 200


@app.route('/state', methods=['GET', 'PUT'])
def service_state():
    global state

    if request.method == 'GET':
        return state, 200

    elif request.method == 'PUT':
        new_state = request.args.get("state")
        if not new_state:
            return jsonify({"error": "no state parameter"}), 400

        if new_state == PAUSED:
            if state != PAUSED:
                set_log(PAUSED)
                state = PAUSED
        elif new_state == RUNNING:
            if state != RUNNING:
                set_log(RUNNING)
                state = RUNNING
        else:
            return jsonify({"error": f"Invalid state: {new_state}"}), 400

        return jsonify({"state": state}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8199)
