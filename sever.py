"""
Server for Task-Sorter Microservice. Sorts Tasks based on name, due date, or priority.

receives message like: {'sort': 'duedate', 'tasks': [task1, task2, task3, etc]}
sends message like: {'sort': 'duedate', 'tasks': [task2, task1, task3, etc]} where the order of tasks has changed
as task2 has sooner duedate than task1).
"""

import zmq
import json

class Task:
    def __init__(self, name, description, duedate, priority):
        self.name = name
        self.description = description
        self.duedate = duedate
        self.priority = int(priority)  # Convert priority to integer so we don't sort lexicographically

    @staticmethod
    def from_dict(task_dict):
        return Task(task_dict['name'], task_dict['description'], task_dict['duedate'], task_dict['priority'])

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'duedate': self.duedate,
            'priority': str(self.priority)  # Convert back to string for consistency
        }

    def get_sort_value(self, sort_key):
        """
        Retrieve the value of specific attribute for a task
        :param sort_key: the attribute we want to retrieve
        :return: that attribute's value
        """
        return getattr(self, sort_key)

def sort_tasks(tasks, sort_key):
    """
    Uses built-in sorted function to a sort a list of objects by an object attribute.

    sorted() requires a list and a function get the attribute value to sort by.
    Lambda defines a function that receives a task and gets the attr value to sort by.

    :param tasks: list of objects to be sorted
    :param sort_key: str indicating attribute to sort by
    :return: list of task objects sorted by sort_key
    """
    return sorted(tasks, key=lambda task: task.get_sort_value(sort_key))

def main():
    # listen on port for a message
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:554")
    print("Server started and waiting for client requests...")

    while True:
        # find the attribute to sort by and the tasks, save them to variables, default to duedate and []
        message = socket.recv_json()
        print(f"Received message from client: {message}")
        sort_key = message.get('sort', 'duedate')
        print(f"Saved sort_key as {sort_key}")
        tasks_data = message.get('tasks', [])
        print(f"Saved tasks_data as {tasks_data}")

        # for each task, create a task object in a list
        tasks = [Task.from_dict(task_data) for task_data in tasks_data]
        print(f"created task objects from message!")
        sorted_tasks = sort_tasks(tasks, sort_key)
        print(f"Sorted task objects!")

        # format response back into task dictionary, place task dictionary
        # in super dictionary as the value for 'tasks' key
        sorted_tasks_data = [task.to_dict() for task in sorted_tasks]
        response = {
            'sort': sort_key,
            'tasks': sorted_tasks_data
        }
        socket.send_json(response)
        print(f"Sent response: {response}")

if __name__ == "__main__":
    main()