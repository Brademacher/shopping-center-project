import time

class MetricsLogger:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.compute_durations = []
        self.steps_taken = 0
        self.nodes_expanded = 0
        self.replans = 0
        self.success = False
        self.path_cost = 0

    def start_total_timer(self):
        self.start_time = time.time()

    def end_total_timer(self):
        self.end_time = time.time()

    def start_compute_timer(self):
        self.compute_start = time.time()

    def end_compute_timer(self):
        self.compute_durations.append(time.time() - self.compute_start)

    def log_replan(self):
        self.replans += 1

    def summarize(self):
        return {
            "total_time": round(self.end_time - self.start_time, 5) if self.end_time else 0,
            "compute_time": round(sum(self.compute_durations), 5),
            "steps_taken": self.steps_taken,
            "nodes_expanded": self.nodes_expanded,
            "replans": self.replans,
            "success": self.success,
            "path_cost": self.path_cost,
        }