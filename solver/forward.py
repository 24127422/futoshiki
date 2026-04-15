import copy

class ForwardCheckingSolver:
    def __init__(self, game):
        self.game = game
        self.size = game.size

    def solve(self):
        empty_cells = []
        for r in range(self.size):
            for c in range(self.size):
                if self.game.board[r][c] == 0:
                    empty_cells.append((r, c))

        
        domains = {cell: list(range(1, self.size + 1)) for cell in empty_cells}
        
        return self._solve_fc(0, empty_cells, domains)

    def _solve_fc(self, index, empty_cells, domains):
        if index == len(empty_cells):
            return True

        r, c = empty_cells[index]

        for val in domains[(r, c)]:
            
            if self.game.is_valid(r, c, val):
                self.game.board[r][c] = val

                
                new_domains = copy.deepcopy(domains)
                domain_wipeout = False

                for i in range(index + 1, len(empty_cells)):
                    nr, nc = empty_cells[i]

                    
                    if (nr == r or nc == c) and val in new_domains[(nr, nc)]:
                        new_domains[(nr, nc)].remove(val)

                    
                    
                    valid_values_left = []
                    for n_val in new_domains[(nr, nc)]:
                        if self.game.is_valid(nr, nc, n_val):
                            valid_values_left.append(n_val)
                    
                    new_domains[(nr, nc)] = valid_values_left

                    
                    if not new_domains[(nr, nc)]:
                        domain_wipeout = True
                        break

                
                if not domain_wipeout:
                    if self._solve_fc(index + 1, empty_cells, new_domains):
                        return True

                
                self.game.board[r][c] = 0

        return False