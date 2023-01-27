from flask import Flask, request, jsonify, render_template, Response
from uuid import uuid4
import time
import sys
import requests
from threading import Thread, Event

app = Flask(__name__)

memory = {
    "id" : "",
    "leader": "unknown",
    "neighbours": {},
    "host": "127.0.0.1",
    "port": ""
    }


def add_neighbour(neighbour_id, json_data):
    if neighbour_id not in memory['neighbours']:
        memory['neighbours'][neighbour_id] = {"host": json_data['host'], "port": json_data['port']}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/data', methods=['GET', 'POST'])
def data():
    global memory
    def update():
        with app.app_context():
            while True:
                # Perform update
                time.sleep(0.1)
                yield f'data: {memory}\n\n'

    if request.method == 'POST':
        json_data = request.json
        if memory['leader'] == 'unknown':
            memory['leader'] = json_data['leader']
        add_neighbour(json_data['id'], json_data)
        return jsonify(memory)
    else:
        if memory['leader'] == 'unknown':
            leader_elect()
        return Response(update(), mimetype='text/event-stream')

def search(port, host="127.0.0.1"):
    try:
        resp = requests.post('http://' + host + ':' + port + '/data', json=memory)
        if resp.json()['leader'] != 'unknown':
            json_data = resp.json()
            memory['leader'] = json_data['leader']
            add_neighbour(json_data['id'], json_data)
            for neighbour_id in json_data['neighbours']:
                if neighbour_id != memory['id']:
                    add_neighbour(neighbour_id, json_data['neighbours'][neighbour_id])
    except Exception as e:
        print(f"host {host}:{port}: Error {e}")
        return False
    return True

def leader_elect():
    memory['leader'] = memory['id']
    
    search(str(int(sys.argv[1])+1))
    search(str(int(sys.argv[1])-1))
    print(f"election: {memory['leader']}")

class Updates(Thread):
   
    StopEvent = 0
      
    def __init__(self,args):
        Thread.__init__(self)
        self.StopEvent = args
  
    # The run method is overridden to define 
    # the thread body 
    def run(self):
        global memory
        while True:
            time.sleep(0.5)
            local_neighbours = memory['neighbours'].copy()
            for host_id in local_neighbours:
                if not search(memory['neighbours'][host_id]['port'], memory['neighbours'][host_id]['host']):
                    del memory['neighbours'][host_id]

if __name__ == "__main__":
    Stop = Event()
    t = Updates(Stop)
    t.setDaemon(True)
    t.start()
    memory['id'] = str(uuid4())
    memory['port'] = sys.argv[1]

    try:
        app.run(port=int(sys.argv[1]), debug=True)
    except KeyboardInterrupt:
        print("exiting")
        Stop.set()
        exit(0)
    