"""
Client for ZeroMQ request to task-sorter Microservice
Sends request to server via request socket and receives a reply message

sends message like: {'sort': 'duedate', 'tasks': [task1, task2, task3, etc]}
receives message like: {'sort': 'duedate', 'tasks': [task2, task1, task3, etc]} where the order of tasks has changed
as task2 has sooner duedate than task1).
"""

import zmq
import json
import unittest

class Task:
    def __init__(self, name, description, duedate, priority):
        self.name = name
        self.description = description
        self.duedate = duedate
        self.priority = priority

    def __str__(self):
        return f"Task Name: {self.name}, Due Date: {self.duedate}, Priority {self.priority}"

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'duedate': self.duedate,
            'priority': self.priority
        }

# Create request socket and connect to reply socket on local machine
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:554")

# Create demo tasks for testing
task1 = Task("Complete Homework Assignment", "Finish all assignments due before December 4th", "11/24/2024", "2")
task2 = Task("Purchase Tire Chains", "Purchase 2 Snow Tire Chains", "11/21/2024", "8")
task3 = Task("Purchase Cardboard Boxes", "Visit the Post Office for boxes", "11/13/2024", "10")
task4 = Task("Pack Up Apartment", "Place belongings into cardboard boxes", "11/26/2024", "1")

class TestingMicroservice(unittest.TestCase):
    # Must use setUp and tearDown as they run for each test, this avoids errors with concurrently messaging server
    def setUp(self):
        # create request socket and connect to reply socket on local machine
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:554")

    def tearDown(self):
        # clean up by closing the socket and terminating the context
        self.socket.close()
        self.context.term()

    def send_and_receive(self, sort_key, tasks):
        # format parameters into dictionary before sending message to server
        # access the tasks in the returned dictionary to compare results to test
        message = {
            'sort': sort_key,
            'tasks': [task.to_dict() for task in tasks]
        }
        self.socket.send_string(json.dumps(message))
        response = json.loads(self.socket.recv_string())
        return response['tasks']

    def test_name(self):
        sorted_tasks = self.send_and_receive('name', [task2, task1, task3, task4])
        self.assertEqual([task['name'] for task in sorted_tasks], ["Complete Homework Assignment", "Pack Up Apartment", "Purchase Cardboard Boxes", "Purchase Tire Chains"])

    def test_duedate(self):
        sorted_tasks = self.send_and_receive('duedate', [task2, task1, task3, task4])
        self.assertEqual([task['duedate'] for task in sorted_tasks], ["11/13/2024", "11/21/2024", "11/24/2024", "11/26/2024"])

    def test_priority(self):
        sorted_tasks = self.send_and_receive('priority', [task2, task1, task3, task4])
        self.assertEqual([task['priority'] for task in sorted_tasks], ["1", "2", "8", "10"])

if __name__ == '__main__':
    unittest.main()
