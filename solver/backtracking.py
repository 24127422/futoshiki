class BacktrackingSolver:
    def __init__(self, game, verbose=True):
        self.game = game
        self.expansions = 0
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def solve(self):
        self.expansions = 0
        self.log(f"--- STARTING STANDARD BACKTRACKING ---")
        is_solved = self._solve_recursive()
        self.log(f"--- FINISHED --- Success: {is_solved} | Total Expansions: {self.expansions}")
        return is_solved, self.expansions

    def _solve_recursive(self):
        for row in range(self.game.size):
            for col in range(self.game.size):
                if self.game.board[row][col] == 0:
                    self.log(f"\n[+] Inspecting cell ({row}, {col})")
                    for num in range(1, self.game.size + 1):
                        self.expansions += 1
                        self.log(f"    -> Trying value {num} for cell ({row}, {col})...")
                        if self.game.is_valid(row, col, num):
                            self.log(f"       [Valid] Assigned ({row}, {col}) = {num}. Proceeding deeper...")
                            self.game.board[row][col] = num

                            if self._solve_recursive():
                                return True

                            self.log(f"       [Backtrack] Unassigning {num} from ({row}, {col}).")
                            self.game.board[row][col] = 0
                        else:
                            self.log(f"       [Invalid] Value {num} violates constraints.")

                    self.log(f"[-] All values failed for cell ({row}, {col}). Backtracking...")
                    return False

        self.log(">> Board is fully filled! Solution found.")
        return True