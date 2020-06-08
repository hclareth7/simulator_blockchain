import json
import requests
from datetime import datetime

# prompt the user for a file to import
filter = "JSON file (*.json)|*.json|All Files (*.*)|*.*||"
filename = 'data.json'
datastore = ""
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
# Read JSON data into the datastore variable
amount_of_data = 5
difficulty = 5


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
        print(f"File {output_file_name} generated.")
    except (Exception) as error:
        print("Error: ", error)

# Use the new datastore datastructure


results = []
if filename:
    with open(filename, 'r') as f:
        datastore = json.load(f)

for key, value in datastore.items():
    #print(f'adding {key}')
    for i in range(1, amount_of_data):
        new_value = json.dumps(value) * i
        submit_textarea(key, new_value)
        print(len(new_value))
        new_tx_address = f"{CONNECTED_NODE_ADDRESS}/mine?difficulty={difficulty}"
        startTime = datetime.now()
        requests.get(new_tx_address)
        time = datetime.now() - startTime
        result = f"{key}, {time.total_seconds()}"
        print(result)
        results.append(result)

create_file_from_list(f'output_{datetime.now()}_diff{difficulty}_amount{amount_of_data}.csv', results)


new_tx_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)


response = requests.get(new_tx_address)
if response.status_code == 200:
    content = []
    chain = json.loads(response.content)
    # print(chain)
