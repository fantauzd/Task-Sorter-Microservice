import zmq
import json

# Create a ZeroMQ context and REQ socket
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:554")

# Prepare your request data
request_data = {
    "sort": "duedate",
    "tasks": [
        {"name": "Homework", "description": "Math and Science", "duedate": "12/01/2024", "priority": "2"},
        {"name": "Groceries", "description": "Buy fruits and vegetables", "duedate": "11/15/2024", "priority": "5"}
    ]
}

# Send request
socket.send_string(json.dumps(request_data))

# Receive and decode the response
response = json.loads(socket.recv_string())

# Print or process sorted tasks
sorted_tasks = response["tasks"]
for task in sorted_tasks:
    print(f"{task['name']} - Due: {task['duedate']} - Priority: {task['priority']}")