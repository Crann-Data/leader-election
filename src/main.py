from flask import Flask, request, jsonify
from uuid import uuid4
import sys
import requests

app = Flask(__name__)

memory = {
    "id" : uuid4(),
    "leader": "unknown"
    }

@app.route('/data', methods=['GET', 'POST'])
def data():
    global memory
    if request.method == 'POST':
        if memory['leader'] == 'unknown':
            memory['leader'] = request.json['leader']
        return jsonify(memory)
    else:
        if memory['leader'] == 'unknown':
            leader_elect()
        return jsonify(memory)


def leader_elect():
    memory['leader'] = memory['id']
    try:
        resp = requests.post('http://127.0.0.1:' + str(int(sys.argv[1])+1) + '/data', json={'leader': str(memory['id'])})
        if resp.json()['leader'] != 'unknown':
            memory['leader'] = resp.json()['leader']
    except Exception as e:
        print(f"host {str(int(sys.argv[1])+1)} not found: Error {e}")
    try:
        resp = requests.post('http://127.0.0.1:' + str(int(sys.argv[1])-1) + '/data', json={'leader': str(memory['id'])})
        if resp.json()['leader'] != 'unknown':
            memory['leader'] = resp.json()['leader']
    except Exception as e:
        print(f"host {str(int(sys.argv[1])-1)} not found: Error {e}")
    print(f"election: {memory['leader']}")

if __name__ == "__main__":
    app.run(port=int(sys.argv[1]), debug=True)