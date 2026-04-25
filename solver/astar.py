import copy
import heapq

class AStarSolver:
    def __init__(self, game, verbose=True):
        self.game = game
        self.N = game.size
        self.expansions = 0
        self.verbose = verbose  

    def log(self, message):
        if self.verbose:
            print(message)

    def get_empty_cell(self, board): 
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == 0:
                    return r, c
        return None

    def heuristic(self, board): 
        empty_count = 0
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == 0:
                    empty_count += 1
        return empty_count

    def solve(self):
        self.expansions = 0
        initial_board = copy.deepcopy(self.game.board)
        pq = []
        tie_breaker = 0 
        
        h_initial = self.heuristic(initial_board)
        g_initial = 0
        f_initial = g_initial + h_initial
        
        self.log(f"--- STARTING A* SEARCH ---")
        self.log(f"Initial State: Heuristic (empty cells) = {h_initial}")

        heapq.heappush(pq, (f_initial, h_initial, tie_breaker, initial_board))

        while pq:
            self.expansions += 1
            f, h, _, current_board = heapq.heappop(pq)
            
            self.log(f"\n[+] Expanding node: f={f}, g={f-h}, h={h}")
            
            empty_cell = self.get_empty_cell(current_board)
            
            
            if not empty_cell:
                self.log(">> No empty cells left! Goal state reached.")
                for r in range(self.N):
                    for c in range(self.N):
                        self.game.board[r][c] = current_board[r][c]
                return True, self.expansions
                
            r, c = empty_cell
            self.log(f"    Selected empty cell: ({r}, {c})")
            
            for num in range(1, self.N + 1):
                
                self.game.board = current_board 
                if self.game.is_valid(r, c, num):
                    
                    new_board = copy.deepcopy(current_board)
                    new_board[r][c] = num
                    
                    h_new = self.heuristic(new_board)
                    g_new = (self.N * self.N) - h_new 
                    f_new = g_new + h_new 
                    tie_breaker += 1
                    self.log(f"    -> [Valid] Assigned {num} to ({r}, {c}). New state: f={f_new}, h={h_new}. Pushing to queue.")
                    
                    heapq.heappush(pq, (f_new, h_new, tie_breaker, new_board))
                else:
                    self.log(f"    -> [Invalid] Value {num} violates constraints at ({r}, {c}).")

        self.log("[-] Queue empty. No solution found.")
        return False, self.expansions