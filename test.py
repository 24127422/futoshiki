import sys
import os
import time
import psutil
from futoshiki import Futoshiki
from solver.backtracking import BacktrackingSolver
from solver.brute_force import BruteForceSolver
from solver.astar import AStarSolver
from solver.sat_solve import SATSolver
from solver.forward import ForwardCheckingSolver
from solver.backward import BackwardCheckingSolver


def get_solver(name, game):
    solvers = {
        "bf": BruteForceSolver,
        "bt": BacktrackingSolver,
        "astar": AStarSolver,
        "sat": SATSolver,
        "fc": ForwardCheckingSolver,
        "bc": BackwardCheckingSolver
    }
    solver_class = solvers.get(name.lower())
    if not solver_class:
        print(f"Lỗi: Không tìm thấy thuật toán '{name}'")
        print(f"Danh sách hỗ trợ: {list(solvers.keys())}")
        return None
    return solver_class(game)


def main():
    if len(sys.argv) < 3:
        return

    level = int(sys.argv[1])
    algo_name = sys.argv[2]
    filename = f"Inputs/input-{level:02d}.txt"

    if not os.path.exists(filename):
        print(f"Lỗi: Không tìm thấy file {filename}")
        return

    # Khởi tạo game
    game = Futoshiki(filename)
    solver = get_solver(algo_name, game)

    if not solver:
        return

    print(f"\nRUNNING | LEVEL {level} | {algo_name.upper()}")

    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss
    start_time = time.perf_counter()

    result = solver.solve()

    end_time = time.perf_counter()
    mem_after = process.memory_info().rss

    expansions = "N/A"
    if isinstance(result, tuple):
        is_solved, expansions = result
    else:
        is_solved = result

    if is_solved:
        print("Status: SUCCESS.")
        print("Result:")
        for row in game.board:
            print(" ".join(map(str, row)))
    else:
        print("Status: NO SOLUTION.")

    print("-" * 30)
    print(f"Time: {end_time - start_time:.6f} seconds")
    print(f"Memory: {(mem_after - mem_before) / (1024 * 1024):.4f} MB")
    print(f"Expansions: {expansions}")
    print("-" * 30)


if __name__ == "__main__":
    main()