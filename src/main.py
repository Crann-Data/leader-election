from flask import Flask, request, jsonify, render_template, Response
from uuid import uuid4
import time
import sys
import requests
from threading import Thread, Event
import json
import hashlib

app = Flask(__name__)

memory = {
    "id" : "",
    "leader": "unknown",
    "neighbours": {},
    "hashed_neighbours": {},
    "host": "127.0.0.1",
    "port": ""
    }


def add_neighbour(neighbour_id, json_data):
    """
    Add a neighour to current list if not present. Add a hash host and port map to the 
    neighbour ID.

    parameters:
        neigbour_id: key received from remote host
        json_data: value received from remote host

    return:
        None
    """
    if neighbour_id not in memory['neighbours']:
        memory['neighbours'][neighbour_id] = {"host": json_data['host'], "port": json_data['port']}
        memory['hashed_neighbours'][hashlib.md5(json.dumps(memory['neighbours'][neighbour_id]).encode('utf-8')).hexdigest()] = neighbour_id

@app.route('/', methods=['GET'])
def index():
    """
    Serve index.html

    return:
        rendered index.html
    """
    return render_template('index.html')


@app.route('/data', methods=['GET', 'POST'])
def data():
    """
    Handle data input and requests. Data is passed by calling POST
    with a json body of the total remote host memory.

    If the current leader is unknown, elect self and publish.

    args:
        request.json

    return:
        On GET return an event-stream of the local host memory
    """
    global memory
    def update():
        with app.app_context():
            while True:
                # Perform update
                time.sleep(0.1)
                yield f'data: {json.dumps(memory)}\n\n'

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
    """
    Post to a remote host current memory. If the remote host has a leader
    already set, set this remote leader as local leader.


    return:
        True: if request succeeded
        False: if request failed
    """
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
    """
    Hold a leader election by looking at the hosts one port
    above self, and one port below. First setting self as leader,
    correcting to the remote leader if one is returned.

    return: None
    """
    memory['leader'] = memory['id']
    
    search(str(int(sys.argv[1])+1))
    search(str(int(sys.argv[1])-1))
    print(f"election: {memory['leader']}")

class Updates(Thread):
    """
    Thread to periodically check with the remote neighbours if
    a change has occured
    """
   
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
            for neighbour_id in local_neighbours:
                if not search(memory['neighbours'][neighbour_id]['port'], memory['neighbours'][neighbour_id]['host']):
                    del memory['hashed_neighbours'][hashlib.md5(json.dumps(memory['neighbours'][neighbour_id]).encode ('utf-8')).hexdigest()]
                    del memory['neighbours'][neighbour_id]

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
    