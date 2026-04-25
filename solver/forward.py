import copy

class ForwardCheckingSolver:
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

        domains = {cell: list(range(1, self.size + 1)) for cell in empty_cells}
        
        self.log(f"--- STARTING FORWARD CHECKING ---")
        self.log(f"Empty cells to fill: {len(empty_cells)}")
        
        success = self._solve_fc(0, empty_cells, domains)
        
        self.log(f"--- FINISHED ---")
        self.log(f"Success: {success} | Total Expansions: {self.expansions}")
        return success, self.expansions

    def _solve_fc(self, index, empty_cells, domains):
        if index == len(empty_cells):
            self.log(">> Board is fully filled! Solution found.")
            return True

        r, c = empty_cells[index]
        self.log(f"\n[+] Inspecting cell ({r}, {c})")
        self.log(f"    Available domain for ({r}, {c}): {domains[(r, c)]}")

        for val in domains[(r, c)]:
            self.expansions += 1
            self.log(f"    -> Trying value {val} for cell ({r}, {c})...")

            if self.game.is_valid(r, c, val):
                self.game.board[r][c] = val
                self.log(f"       [Valid] Assigned ({r}, {c}) = {val}. Running Forward Checking...")
                
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
                        self.log(f"       [WARNING] Domain wipeout at cell ({nr}, {nc})! No valid values left. Backtracking...")
                        domain_wipeout = True
                        break

                if not domain_wipeout:
                    self.log(f"       [Safe] Forward Checking passed. Moving to next cell.")
                    if self._solve_fc(index + 1, empty_cells, new_domains):
                        return True

                self.log(f"       [Backtrack] Reverting assignment {val} at cell ({r}, {c}).")
                self.game.board[r][c] = 0
            else:
                self.log(f"       [Invalid] Value {val} violates constraints at ({r}, {c}).")

        self.log(f"[-] All values failed for cell ({r}, {c}). Backtracking to previous cell.")
        return False