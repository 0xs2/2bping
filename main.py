# thanks hausemaster for putting this data in the info lol

from flask import Flask, request, jsonify, render_template
import requests
import threading
import schedule
import time
import json

# vars
f = "pings.json"
p = 9092
deb = False

# main
app = Flask(__name__)

def parse(i):
    return int(i.split(':')[1].replace(' ', ''))

def request():
    x = requests.get("https://api.mcsrvstat.us/2/2b2t.org")

    if x.status_code == 200:
        res = x.json()
        data = {
                "totalOnline": res['players']['online'],
                "totalIngame": parse(res['info']['clean'][0]),
                "totalQueue": parse(res['info']['clean'][1]),
                "totalPrio": parse(res['info']['clean'][2]),
                "pingedAt": round(time.time())
            }
        return data
    print("[2bping] got data")

def save(payload, status):
    with open(f, "r") as json_file:
        existing_data = json.load(json_file)

    existing_data.append(payload)
    with open(f, "w") as json_file:
        json.dump(existing_data, json_file)
    print("[2bping] Saved data")


def ping():
    r = request()
    if r:
        save(r, True)
        print("[2bping] got ping")


def background_task():
        while True:
            ping()
            time.sleep(60)

def start_background_task():
    bg_thread = threading.Thread(target=background_task)
    bg_thread.daemon = True
    bg_thread.start()


@app.route('/api/latest', methods=['GET'])
def latest():
    with open(f, 'r') as json_file:
        data = json.load(json_file)
    return jsonify({"sucesss": True, "result": data[-1]})

# latest
@app.route('/api/all', methods=['GET'])
def all():
    with open(f, 'r') as json_file:
        data = json.load(json_file)
    return jsonify({"sucesss": True, "result": data[-500:]})

@app.route('/', methods=['GET'])
def home():
    return render_template('graph.html')

if __name__ == '__main__':
    start_background_task()
    app.run(host='0.0.0.0', port=p, debug=deb)