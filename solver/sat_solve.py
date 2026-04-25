from solver.KB_CNF import FutoshikiKB
from pysat.solvers import Glucose3

class SATSolver:
    def __init__(self, game, verbose=True):
        self.game = game
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def solve(self):
        self.log("--- STARTING SAT SOLVER ---")
        self.log("Extracting givens and constraints from the board...")
        
        given = {}
        for r in range(self.game.size):
            for c in range(self.game.size):
                if self.game.board[r][c] != 0:
                    given[(r + 1, c + 1)] = self.game.board[r][c]

        less_h, greater_h = set(), set()
        for r in range(self.game.size):
            for c in range(len(self.game.horizontal_cons[r])):
                if self.game.horizontal_cons[r][c] == 1:
                    less_h.add((r + 1, c + 1))
                elif self.game.horizontal_cons[r][c] == -1:
                    greater_h.add((r + 1, c + 1))

        less_v, greater_v = set(), set()
        for r in range(len(self.game.vertical_cons)):
            for c in range(self.game.size):
                if self.game.vertical_cons[r][c] == 1:
                    less_v.add((r + 1, c + 1))
                elif self.game.vertical_cons[r][c] == -1:
                    greater_v.add((r + 1, c + 1))

        self.log(f"Building Knowledge Base (KB) for size {self.game.size}x{self.game.size}...")
        kb = FutoshikiKB(self.game.size, given, less_h, greater_h, less_v, greater_v)
        clauses = kb.build()
        enc = kb.enc

        self.log(f"Total CNF clauses generated: {len(clauses)}")
        self.log("Feeding clauses to Glucose3 SAT Solver...")

        with Glucose3() as solver:
            for clause in clauses:
                solver.add_clause(list(clause))
            
            if solver.solve():
                self.log(">> SAT Solver found a satisfying assignment (SAT)!")
                model = solver.get_model()
                for lit in model:
                    if lit > 0:
                        i, j, v = enc.decode(lit)
                        self.game.board[i-1][j-1] = v
                        # self.log(f"    Decoded: Cell ({i-1}, {j-1}) = {v}") # Bỏ comment nếu muốn in chi tiết gán từng ô

                stats = solver.accum_stats()
                expansions = stats.get('decisions', len(clauses))
                self.log(f"--- FINISHED --- Total decisions/expansions: {expansions}")
                return True, expansions
            
            self.log("[-] SAT Solver concluded the problem is UNSATISFIABLE (UNSAT).")
            return False, 0