import heapq
from typing import Tuple, List

class AStarPlanner:
    def heuristic(self,a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])+abs(a[2]-b[2])

    def plan(self,env,start,goal):
        open_set=[]; heapq.heappush(open_set,(self.heuristic(start,goal),start))
        came_from, g_score={}, {start:0.0}; nodes_expanded=0

        while open_set:
            _,cur=heapq.heappop(open_set); nodes_expanded+=1
            if cur==goal:
                path=[]
                while cur in came_from: path.append(cur); cur=came_from[cur]
                path.append(start); return list(reversed(path)),nodes_expanded
            for n in env.get_neighbors(cur):
                c = env.move_cost(cur,n)
                tg = g_score[cur]+c
                if tg<g_score.get(n,float('inf')):
                    came_from[n],g_score[n]=cur,tg
                    heapq.heappush(open_set,(tg+self.heuristic(n,goal),n))
                    
        return [],nodes_expanded