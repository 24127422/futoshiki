class BruteForceSolver:
    def __init__(self, game, verbose=True):
        self.game = game
        self.size = game.size
        self.empty_cells = []
        self.expansions = 0
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def solve(self):
        self.empty_cells = []
        self.expansions = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.game.board[r][c] == 0:
                    self.empty_cells.append((r, c))

        self.log(f"--- STARTING BRUTE FORCE ---")
        self.log(f"Total empty cells to brute-force: {len(self.empty_cells)}")
        result = self._solve_recursive(0)
        self.log(f"--- FINISHED --- Success: {result} | Total Expansions: {self.expansions}")
        return result, self.expansions

    def _solve_recursive(self, index):
        if index == len(self.empty_cells):
            self.expansions += 1
            is_valid = self.game.is_entire_board_valid()
            self.log(f"[?] Reached a full board state. Checking validity... Result: {is_valid}")
            return is_valid

        row, col = self.empty_cells[index]
        self.log(f"\n[+] Assigning values to cell ({row}, {col}) without checking constraints")

        for num in range(1, self.size + 1):
            self.expansions += 1
            self.log(f"    -> Forcing ({row}, {col}) = {num}")
            self.game.board[row][col] = num

            if self._solve_recursive(index + 1):
                return True

            self.log(f"    <- Reverting ({row}, {col})")
            self.game.board[row][col] = 0

        return False