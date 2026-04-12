class BacktrackingSolver:
    def __init__(self, game):
        self.game = game

    def solve(self):
        for row in range(self.game.size):
            for col in range(self.game.size):
                if self.game.board[row][col] == 0:
                    for num in range(1, self.game.size + 1):
                        if self.game.is_valid(row, col, num):
                            self.game.board[row][col] = num

                            if self.solve():
                                return True

                            self.game.board[row][col] = 0

                    return False

        return True