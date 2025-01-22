from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

app = Flask(__name__)

TASKS_FILE = "tasks.json"


# Ensure tasks file exists
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "w") as f:
        json.dump([], f)


def load_tasks():
    """Load tasks from the tasks.json file."""
    with open(TASKS_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks):
    """Save the updated tasks to the tasks.json file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


@app.route("/whatsapp", methods=["POST","GET"])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    response = MessagingResponse()
    reply = ""

    tasks = load_tasks()

    # Add task functionality
    if incoming_msg.lower().startswith("add:"):
        task = incoming_msg[4:].strip()
        task_id = len(tasks) + 1
        tasks.append({
            "id": task_id,
            "task": task,
            "status": "Pending",
            "user": sender
        })
        save_tasks(tasks)
        reply = f"Task '{task}' has been added successfully!"

    # Mark task as complete functionality
    elif incoming_msg.lower().startswith("complete:"):
        task = incoming_msg[9:].strip()
        for t in tasks:
            if t["task"].lower() == task.lower() and t["status"] == "Pending":
                t["status"] = "Completed"
                save_tasks(tasks)
                reply = f"Task '{task}' marked as completed!"
                break
        else:
            reply = f"Task '{task}' not found or already completed."

    # Delete task functionality
    elif incoming_msg.lower().startswith("delete:"):
        task = incoming_msg[8:].strip()
        task_found = False
        for t in tasks:
            if t["task"].lower() == task.lower():
                tasks.remove(t)
                task_found = True
                break
        if task_found:
            save_tasks(tasks)
            reply = f"Task '{task}' has been deleted successfully!"
        else:
            reply = f"Task '{task}' not found."

    # List all tasks functionality
    elif incoming_msg.lower() == "list":
        if tasks:
            reply = "Here are your tasks:\n"
            for t in tasks:
                reply += f"- {t['task']} ({t['status']})\n"
        else:
            reply = "No tasks found."

    else:
        reply = "Invalid command. Use 'Add: <task>', 'Complete: <task>', 'Delete: <task>', or 'List' to see tasks."

    response.message(reply)
    return str(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
