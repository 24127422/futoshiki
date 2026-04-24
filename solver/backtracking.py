class BacktrackingSolver:
    def __init__(self, game):
        self.game = game
        self.expansions = 0

    def solve(self):
        self.expansions = 0
        is_solved = self._solve_recursive()
        return is_solved, self.expansions

    def _solve_recursive(self):
        for row in range(self.game.size):
            for col in range(self.game.size):
                if self.game.board[row][col] == 0:
                    for num in range(1, self.game.size + 1):
                        self.expansions += 1
                        if self.game.is_valid(row, col, num):
                            self.game.board[row][col] = num

                            if self._solve_recursive():
                                return True

                            self.game.board[row][col] = 0

                    return False

        return True