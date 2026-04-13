from solver.KB_CNF import FutoshikiKB
from pysat.solvers import Glucose3

class SATSolver:
    def __init__(self, game):
        self.game = game

    def solve(self):
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

        kb = FutoshikiKB(self.game.size, given, less_h, greater_h, less_v, greater_v)
        clauses = kb.build()
        enc = kb.enc

        with Glucose3() as solver:
            for clause in clauses:
                solver.add_clause(list(clause))
            
            if solver.solve():
                model = solver.get_model()
                for lit in model:
                    if lit > 0:
                        i, j, v = enc.decode(lit)
                        self.game.board[i-1][j-1] = v
                return True
            return False