import heapq
from typing import List,Tuple
from algorithms.astar import AStarPlanner

class MultiGoalAStarPlanner(AStarPlanner):
    def plan(self,env,start,goals):
        remaining=set(goals); path=[start]; nodes_expanded=0; cur=start
        
        while remaining:
            open_set=[(self.heuristic(cur,g),cur) for g in remaining]; heapq.heapify(open_set)
            cf,lg={}, {cur:0.0}; exp=0; found=None
            while open_set:
                _,u=heapq.heappop(open_set); exp+=1
                if u in remaining: found=u; break
                for n in env.get_neighbors(u):
                    c=env.move_cost(u,n); tg=lg[u]+c
                    if tg<lg.get(n,float('inf')):
                        cf[n],lg[n]=u,tg
                        heapq.heappush(open_set,(tg+min(self.heuristic(n,g) for g in remaining),n))
            nodes_expanded+=exp
            if not found: break
            segment, p = [], found
            while p!=cur: segment.append(p); p=cf[p]
            path.extend(reversed(segment))
            if env.has_item(found): break
            remaining.remove(found); cur=found
        return path, nodes_expanded