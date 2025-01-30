import os
import socket
import subprocess
import time
import threading
import datetime
import logging
import docker


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

STATE_PATH = "/state/"
os.makedirs(os.path.dirname(f"{STATE_PATH}state.txt"), exist_ok=True)
if not os.path.exists(f"{STATE_PATH}state.txt"):
    with open(f"{STATE_PATH}state.txt", "w") as f:
        f.write("INIT")
        f.close()

if not os.path.exists(f"{STATE_PATH}log.txt"):
    with open(f"{STATE_PATH}log.txt", "w") as f:
        f.close()

else: # clear log on startup
    with open(f"{STATE_PATH}log.txt", "w") as f:
        f.write("")
        f.close()

def get_state():
    global state
    with open(f"{STATE_PATH}state.txt", "r") as state_file:
        state = state_file.readline()
        state_file.close()
        
def set_state(target_state):
    with open(f"{STATE_PATH}state.txt", "w") as state_file:
        global state
        state_file.write(target_state)
        state = target_state
        state_file.close()

def set_log(new_state):
    global state
    get_state()   
    old_state = state    
    set_state(new_state)
    with open(f"{STATE_PATH}log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()}: {old_state}->{new_state}\n")
        log_file.close()





def shutdown_system():
    client = docker.from_env()
    current_instance = socket.gethostname()

    self_id = None

    # stop other containers
    for container in client.containers.list():
        if "service1" in container.name and container.attrs['Config']['Hostname'] == current_instance:
            self_id = container.id
        else:
            container.stop()
            container.remove()

    # sate to init
    with open(f"{STATE_PATH}state.txt", "w", encoding="utf-8") as state_file:
        state_file.write("INIT")

    #  shut down self
    if self_id:
        time.sleep(1)
        self_container = client.containers.get(self_id)
        self_container.stop()

    


def stop_service():
    set_state(SHUTDOWN)
    def delayed_shutdown():
        time.sleep(5)
        shutdown_system()
    threading.Thread(target=delayed_shutdown).start()
    return jsonify({"message": "Shutting down services..."}), 200

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


@app.route('/request', methods=['GET'])
def index():
    global unavailable_until, state
    get_state()
    if state == INIT:
        return jsonify({"error": "not running"}), 503
    if state == SHUTDOWN:
        return jsonify({"error": "shutting down"}), 503
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
    get_state()

    if request.method == 'GET':
        return state, 200

    elif request.method == 'PUT':
        new_state = request.get_data(as_text=True)
        if not new_state:
            return jsonify({"error": "no state parameter"}), 400

        if new_state == SHUTDOWN:
            return stop_service()

        if new_state == PAUSED:
            if state != PAUSED:
                set_log(PAUSED)
        elif new_state == RUNNING:
            if state != RUNNING:
                set_log(RUNNING)
        elif new_state == INIT:
            set_log(INIT)
        else:
            return jsonify({"error": f"Invalid state: {new_state}"}), 400

        return state, 200
    
@app.route('/run-log', methods=['GET'])
def get_run_log():
    content = ""
    with open(f"{STATE_PATH}log.txt", "r") as log_file:
        content = log_file.read()
        log_file.close()
    return content, 200





if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8199)
