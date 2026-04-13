from __future__ import annotations
from itertools import combinations
from pathlib import Path
import sys

class FutoshikiEncoder:
    def __init__(self, N: int):
        self.N = N

    def var(self, i: int, j: int, v: int) -> int:
        N = self.N
        return (i - 1) * N * N + (j - 1) * N + (v - 1) + 1

    def total_vars(self) -> int:
        return self.N ** 3

    def decode(self, var_id: int) -> tuple[int, int, int]:
        N = self.N
        var_id -= 1
        v = var_id % N + 1
        var_id //= N
        j = var_id % N + 1
        i = var_id // N + 1
        return i, j, v



# KB Grounding
class FutoshikiKB:
    def __init__(
        self,
        N: int,
        given: dict[tuple[int, int], int] | None = None,
        less_h: set[tuple[int, int]] | None = None,
        greater_h: set[tuple[int, int]] | None = None,
        less_v: set[tuple[int, int]] | None = None,
        greater_v: set[tuple[int, int]] | None = None,
    ):
        self.N = N
        self.enc = FutoshikiEncoder(N)
        self.given = given or {}
        self.less_h = less_h or set()
        self.greater_h = greater_h or set()
        self.less_v = less_v or set()
        self.greater_v = greater_v or set()
        self.clauses: list[frozenset[int]] = []

    def build(self) -> list[frozenset[int]]:
        self.clauses = []
        self._ground_A1_at_least_one()
        self._ground_A2_at_most_one()
        self._ground_A3_row_uniqueness()
        self._ground_A4_col_uniqueness()
        self._ground_A5_horizontal_less()
        self._ground_A6_horizontal_greater()
        self._ground_A7_vertical_less()
        self._ground_A8_vertical_greater()
        self._ground_A9_given_clues()
        return self.clauses

    def _ground_A1_at_least_one(self):
        N, enc = self.N, self.enc
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                clause = frozenset(enc.var(i, j, v) for v in range(1, N + 1))
                self.clauses.append(clause)

    def _ground_A2_at_most_one(self):
        N, enc = self.N, self.enc
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                for v1, v2 in combinations(range(1, N + 1), 2):
                    clause = frozenset([-enc.var(i, j, v1), -enc.var(i, j, v2)])
                    self.clauses.append(clause)

    def _ground_A3_row_uniqueness(self):
        N, enc = self.N, self.enc
        for i in range(1, N + 1):
            for v in range(1, N + 1):
                for j1, j2 in combinations(range(1, N + 1), 2):
                    clause = frozenset([-enc.var(i, j1, v), -enc.var(i, j2, v)])
                    self.clauses.append(clause)

    def _ground_A4_col_uniqueness(self):
        N, enc = self.N, self.enc
        for j in range(1, N + 1):
            for v in range(1, N + 1):
                for i1, i2 in combinations(range(1, N + 1), 2):
                    clause = frozenset([-enc.var(i1, j, v), -enc.var(i2, j, v)])
                    self.clauses.append(clause)

    def _ground_A5_horizontal_less(self):
        N, enc = self.N, self.enc
        for (i, j) in self.less_h:
            if j + 1 > N: continue
            for v1 in range(1, N + 1):
                for v2 in range(1, N + 1):
                    if v1 >= v2:
                        clause = frozenset([-enc.var(i, j, v1), -enc.var(i, j + 1, v2)])
                        self.clauses.append(clause)

    def _ground_A6_horizontal_greater(self):
        N, enc = self.N, self.enc
        for (i, j) in self.greater_h:
            if j + 1 > N: continue
            for v1 in range(1, N + 1):
                for v2 in range(1, N + 1):
                    if v1 <= v2:
                        clause = frozenset([-enc.var(i, j, v1), -enc.var(i, j + 1, v2)])
                        self.clauses.append(clause)

    def _ground_A7_vertical_less(self):
        N, enc = self.N, self.enc
        for (i, j) in self.less_v:
            if i + 1 > N: continue
            for v1 in range(1, N + 1):
                for v2 in range(1, N + 1):
                    if v1 >= v2:
                        clause = frozenset([-enc.var(i, j, v1), -enc.var(i + 1, j, v2)])
                        self.clauses.append(clause)

    def _ground_A8_vertical_greater(self):
        N, enc = self.N, self.enc
        for (i, j) in self.greater_v:
            if i + 1 > N: continue
            for v1 in range(1, N + 1):
                for v2 in range(1, N + 1):
                    if v1 <= v2:
                        clause = frozenset([-enc.var(i, j, v1), -enc.var(i + 1, j, v2)])
                        self.clauses.append(clause)

    def _ground_A9_given_clues(self):
        enc = self.enc
        for (i, j), v in self.given.items():
            clause = frozenset([enc.var(i, j, v)])
            self.clauses.append(clause)



# Input parser
def parse_input(path: str) -> tuple[int, dict, set, set, set, set]:
    with open(path) as f:
        lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]

    idx = 0
    grid_lines = []
    for _ in range(len(lines)):
        row = [int(x) for x in lines[idx].split(',')]
        grid_lines.append(row)
        idx += 1
        if len(grid_lines) == len(grid_lines[0]): 
            break

    N = len(grid_lines)
    given = {}
    for i, row in enumerate(grid_lines, 1):
        for j, val in enumerate(row, 1):
            if val != 0:
                given[(i, j)] = val

    less_h, greater_h = set(), set()
    for i in range(1, N + 1):
        row = [int(x) for x in lines[idx].split(',')]
        idx += 1
        for j, c in enumerate(row, 1):
            if c == 1: less_h.add((i, j))
            elif c == -1: greater_h.add((i, j))

    less_v, greater_v = set(), set()
    for i in range(1, N):
        row = [int(x) for x in lines[idx].split(',')]
        idx += 1
        for j, c in enumerate(row, 1):
            if c == 1: less_v.add((i, j))
            elif c == -1: greater_v.add((i, j))

    return N, given, less_h, greater_h, less_v, greater_v

# CNF utilities
def clauses_to_dimacs(clauses: list[frozenset[int]], num_vars: int) -> str:
    lines = [f"p cnf {num_vars} {len(clauses)}"]
    for clause in clauses:
        lines.append(" ".join(map(str, sorted(clause, key=abs))) + " 0")
    return "\n".join(lines)


def print_cnf_summary(clauses: list[frozenset[int]], enc: FutoshikiEncoder):
    N = enc.N
    print(f"  Grid size     : {N}×{N}")
    print(f"  Variables     : {enc.total_vars()}  (Val(i,j,v) atoms)")
    print(f"  Total clauses : {len(clauses)}")


def ground_and_cnf(
    N: int, 
    given: dict | None = None, 
    less_h: set | None = None,
    greater_h: set | None = None, 
    less_v: set | None = None, 
    greater_v: set | None = None,
    ) -> tuple[list[frozenset[int]], FutoshikiEncoder]:
    
    kb = FutoshikiKB(N, given, less_h, greater_h, less_v, greater_v)
    return kb.build(), kb.enc


def ground_and_cnf_from_file(path: str) -> tuple[list[frozenset[int]], FutoshikiEncoder, int]:
    N, given, less_h, greater_h, less_v, greater_v = parse_input(path)
    clauses, enc = ground_and_cnf(N, given, less_h, greater_h, less_v, greater_v)
    return clauses, enc, N
