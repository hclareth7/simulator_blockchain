import datetime
import json
import os
from time import sleep
import requests
from flask import render_template, redirect, request, Response, render_template
from datetime import datetime
import time
from simulator import app
import logging


logger = logging.getLogger('simulator')

logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

files = []


def submit_textarea(author, content):
    """
    Endpoint to create a new transaction via our application.
    """

    post_object = {
        'author': author,
        'content': content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,

                  headers={'Content-type': 'application/json'})


def create_file_from_list(output_file_name, target_list):
    file = open(f"{output_file_name}", "a")
    try:
        for line in target_list:
            file.write(f"{line}\n")
        file.close()
        logger.info(f"File {output_file_name} generated.")
    except (Exception) as error:
        logger.error(f"{error}")


def truncate_file():
    f = open('app.log', 'r+')
    f.truncate(0)  # need '0' when using r+


def run(amount_of_data, difficulty):
    # truncate_file()
    filename = 'data.json'
    datastore = ""
    results = []
    results.append(
        'timestamp_transactions,amount_of_data,difficulty,mine_time(sec)')

    with open(filename, 'r') as f:
        datastore = json.load(f)

    for key, value in datastore.items():
        new_value = json.dumps(value) * amount_of_data

        startTime_amount = datetime.now()
        submit_textarea(key, new_value)
        time_amount = datetime.now() - startTime_amount

        new_tx_address = f"{CONNECTED_NODE_ADDRESS}/mine?difficulty={difficulty}"
        startTime = datetime.now()

        requests.get(new_tx_address)

        time = datetime.now() - startTime
        result = f"{key}, {amount_of_data}, {difficulty}, {time_amount.total_seconds()}, {time.total_seconds()}"
        logger.info(f"simulator {result}")
        results.append(result)

    create_file_from_list(
        f'simulator/resources/output_{datetime.now()}_diff{difficulty}_amount{amount_of_data}.csv', results)


@app.route("/get_file")
def getPlotCSV():
    csv = ''
    file = request.args.get('filename')
    with open(f"simulator/resources/{file}") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename={file}"})


def get_file_list(path="simulator/resources"):
    global files
    files = os.listdir(path)


@app.route('/')
def index():
    get_file_list()
    return render_template('index.html',
                           title='(BETA) Simulator '
                                 'this is a simulator on BETA version',
                           files=files)


@app.route('/run_simulator', methods=['POST'])
def run_simulator():
    """
    Endpoint to create a new transaction via our application.
    """
    data = request.get_json()
    idata = int(data["idata"])
    difficulty = int(data["difficulty"])

    run(idata, difficulty)
    get_file_list()
    return "ok"


@app.route('/stream')
def stream():
    def generate():
        with open('app.log') as f:
            while True:
                yield f.read()
                sleep(1)

    return app.response_class(generate(), mimetype='text/plain')


truncate_file()
