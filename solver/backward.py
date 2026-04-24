class BackwardCheckingSolver:
    def __init__(self, game):
        self.game = game
        self.size = game.size
        self.expansions = 0

    def solve(self):
        self.expansions = 0
        empty_cells = []
        for r in range(self.size):
            for c in range(self.size):
                if self.game.board[r][c] == 0:
                    empty_cells.append((r, c))

        return self._solve_bc(0, empty_cells), self.expansions

    def _solve_bc(self, index, empty_cells):
        
        if index == len(empty_cells):
            return True

        row, col = empty_cells[index]

        for num in range(1, self.size + 1):
            self.expansions += 1
            
            if self.game.is_valid(row, col, num):
                self.game.board[row][col] = num

                
                if self._solve_bc(index + 1, empty_cells):
                    return True

                
                self.game.board[row][col] = 0

        return False