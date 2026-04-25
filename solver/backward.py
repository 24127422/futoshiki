class BackwardCheckingSolver:
    def __init__(self, game, verbose=True):
        self.game = game
        self.size = game.size
        self.expansions = 0
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def solve(self):
        self.expansions = 0
        empty_cells = []
        for r in range(self.size):
            for c in range(self.size):
                if self.game.board[r][c] == 0:
                    empty_cells.append((r, c))

        self.log(f"--- STARTING BACKTRACKING ---")
        self.log(f"Empty cells to fill: {len(empty_cells)}")
        
        success = self._solve_bc(0, empty_cells)
        
        self.log(f"--- FINISHED ---")
        self.log(f"Success: {success} | Total Expansions: {self.expansions}")
        return success, self.expansions

    def _solve_bc(self, index, empty_cells):
        if index == len(empty_cells):
            self.log(">> Board is fully filled! Solution found.")
            return True

        row, col = empty_cells[index]
        self.log(f"\n[+] Inspecting cell ({row}, {col})")

        for num in range(1, self.size + 1):
            self.expansions += 1
            self.log(f"    -> Trying value {num} for cell ({row}, {col})...")
            
            if self.game.is_valid(row, col, num):
                self.log(f"       [Valid] Assigned ({row}, {col}) = {num}. Moving to next cell.")
                self.game.board[row][col] = num

                if self._solve_bc(index + 1, empty_cells):
                    return True

                self.log(f"       [Backtrack] Dead end reached. Unassigning {num} from ({row}, {col}).")
                self.game.board[row][col] = 0
            else:
                self.log(f"       [Invalid] Value {num} violates constraints at ({row}, {col}).")

        self.log(f"[-] All values from 1 to {self.size} failed for cell ({row}, {col}). Backtracking...")
        return False