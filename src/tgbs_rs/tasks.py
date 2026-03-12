import ee


def check_ee_task_status(task_id):
    """
    Query an Earth Engine batch task by ID and return its current status.
    Prints state, progress, and error message (if any).
    """
    tasks = ee.batch.Task.list()

    for task in tasks:
        if task.id == task_id:
            status = task.status()
            print("Task ID:", task_id)
            print("State:", status.get("state"))
            print("Description:", status.get("description"))
            print("Progress:", status.get("progress", "N/A"))
            print("Error Message:", status.get("error_message", "None"))
            return status

    print("Task ID not found.")
    return None
