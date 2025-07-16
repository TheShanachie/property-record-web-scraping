import threading
import queue
import time
from flask import Flask, request, jsonify

class TaskServer:
    def __init__(self, max_tasks=3):
        self.max_tasks = max_tasks
        self.task_queue = queue.Queue()
        self.lock = threading.Semaphore(max_tasks)
        self.tasks = {}
        self.task_id = 0

    def worker(self):
        while True:
            task_id, wait_time = self.task_queue.get()
            if wait_time is None:
                break
            with self.lock:
                self.tasks[task_id]["status"] = "Processing"
                print(f"Task {task_id} waiting for {wait_time} seconds...")
                time.sleep(wait_time)  # Simulating task execution
                self.tasks[task_id]["status"] = "Completed"
                print(f"Task {task_id} completed.")
            self.task_queue.task_done()

    def add_task(self, wait_time):
        self.task_id += 1
        task_id = self.task_id
        self.tasks[task_id] = {"wait_time": wait_time, "status": "Queued"}
        self.task_queue.put((task_id, wait_time))
        return task_id

    def start(self):
        threads = []
        for _ in range(self.max_tasks):
            thread = threading.Thread(target=self.worker, daemon=True)
            thread.start()
            threads.append(thread)
        return threads

# Initialize and start the task server
server = TaskServer(max_tasks=3)
server.start()

# Flask API setup
app = Flask(__name__)

@app.route("/submit_task", methods=["POST"])
def submit_task():
    data = request.json
    wait_time = data.get("wait_time", 1)
    
    if not isinstance(wait_time, int) or wait_time < 0:
        return jsonify({"error": "Invalid wait_time. Must be a non-negative integer."}), 400

    task_id = server.add_task(wait_time)
    return jsonify({"task_id": task_id, "status": "Queued"})

@app.route("/task_status/<int:task_id>", methods=["GET"])
def task_status(task_id):
    task = server.tasks.get(task_id)
    if task:
        return jsonify({"task_id": task_id, "wait_time": task["wait_time"], "status": task["status"]})
    return jsonify({"error": "Task not found"}), 404

if __name__ == "__main__":
    app.run(port=5000)