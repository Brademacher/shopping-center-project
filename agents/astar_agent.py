from algorithms.astar import AStarPlanner

class AStarAgent:
    def __init__(self):
        self.planner = AStarPlanner()

    def run(self, env):
        start = (0, 0, 0)                  # entrance

        path, total_exp, false_visits = [], 0, 0
        for store in env.stores:           # try every candidate
            seg, seg_exp = self.planner.plan(env, start, store)
            path += seg[1:]                # drop duplicate start
            total_exp += seg_exp
            start = store

            if env.has_item(store):        # <<< correct test
                break                      #   item found
            false_visits += 1

        return path, total_exp, false_visits
