class BruteForceSolver:
    def __init__(self, game):
        self.game = game
        self.size = game.size
        self.empty_cells = []

    def solve(self):
        self.empty_cells = []
        for r in range(self.size):
            for c in range(self.size):
                if self.game.board[r][c] == 0:
                    self.empty_cells.append((r, c))

        return self._solve_recursive(0)

    def _solve_recursive(self, index):
        if index == len(self.empty_cells):
            return self.game.is_entire_board_valid()

        row, col = self.empty_cells[index]

        for num in range(1, self.size + 1):
            self.game.board[row][col] = num

            if self._solve_recursive(index + 1):
                return True

            self.game.board[row][col] = 0

        return False