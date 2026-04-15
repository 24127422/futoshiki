import pygame
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
class FutoshikiGUI:
    # Color palette
    BG_COLOR = (245, 247, 252)
    WHITE = (255, 255, 255)
    BLACK = (40, 40, 40)
    PRIMARY = (99, 102, 241)
    PRIMARY_LIGHT = (210, 225, 255)
    SUCCESS = (34, 197, 94)
    SUCCESS_LIGHT = (187, 247, 208)
    SUCCESS_BG = (220, 252, 231)
    ERROR = (239, 68, 68)
    ERROR_BG = (254, 226, 226)
    BORDER = (210, 215, 225)
    HOVER = (235, 240, 255)
    DISABLED_BG = (200, 200, 200)

    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        pygame.init()
        self.font = pygame.font.SysFont("Helvetica, Arial", 32, bold=True)
        self.con_font = pygame.font.SysFont("Helvetica, Arial", 24, bold=True)
        self.btn_font = pygame.font.SysFont("Helvetica, Arial", 14, bold=True)

        self.current_level = 1
        self.max_level = 10

        self.scan_levels()
        self.load_level()

    def scan_levels(self):
        self.level_info = {}
        for i in range(1, self.max_level + 1):
            filename = f"Inputs/input-{i:02d}.txt"
            size = "?"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                size = int(line)
                            except ValueError:
                                pass
                            break
            self.level_info[i] = size

    def load_level(self):
        filename = f"Inputs/input-{self.current_level:02d}.txt"

        if not os.path.exists(filename):
            print(f"Lỗi: Không tìm thấy file {filename}")
            sys.exit()

        self.game = Futoshiki(filename)
        if self.game.size == 0:
            print("Invalid board")
            sys.exit()

        self.N = self.game.size
        self.errors = []
        self.selected_cell = None

        # --- DYNAMIC SCALING START ---
        if self.N <= 5:
            self.CELL_SIZE = 60
            self.CON_SIZE = 20
            self.MARGIN = 30
            self.btn_size = 52
            # Re-scale fonts for normal size
            self.font = pygame.font.SysFont("Helvetica, Arial", 32, bold=True)
            self.con_font = pygame.font.SysFont("Helvetica, Arial", 24, bold=True)
        elif self.N <= 7:
            self.CELL_SIZE = 45
            self.CON_SIZE = 15
            self.MARGIN = 25
            self.btn_size = 44
            # Shrink fonts slightly
            self.font = pygame.font.SysFont("Helvetica, Arial", 26, bold=True)
            self.con_font = pygame.font.SysFont("Helvetica, Arial", 18, bold=True)
        else: 
            # For 8x8, 9x9 and above: significantly shrink to fit the screen
            self.CELL_SIZE = 35
            self.CON_SIZE = 12
            self.MARGIN = 15
            self.btn_size = 36
            self.font = pygame.font.SysFont("Helvetica, Arial", 20, bold=True)
            self.con_font = pygame.font.SysFont("Helvetica, Arial", 14, bold=True)
        # --- DYNAMIC SCALING END ---

        self.LEVEL_PANEL_W = 160

        self.BOARD_W = self.N * self.CELL_SIZE + (self.N - 1) * self.CON_SIZE
        self.BOARD_H = self.BOARD_W

        self.btn_h = 36
        self.w_sol = 125
        self.solver_spacing = 15
        self.total_sol_w = 3 * self.w_sol + 2 * self.solver_spacing
        self.SOLVER_AREA_H = self.btn_h * 2 + self.solver_spacing

        self.col2_w = max(self.BOARD_W, self.total_sol_w)

        self.numpad_cols = 3 if self.N >= 5 else 2
        # REMOVE the old self.btn_size = 52 from here since we set it above dynamically!
        self.numpad_gap = 10
        self.NUMPAD_W = self.btn_size * self.numpad_cols + self.numpad_gap * (self.numpad_cols - 1)

        self.col1_x = self.MARGIN
        self.col2_x = self.col1_x + self.LEVEL_PANEL_W + self.MARGIN
        self.col3_x = self.col2_x + self.col2_w + self.MARGIN

        self.board_start_x = self.col2_x + (self.col2_w - self.BOARD_W) // 2
        self.solver_start_x = self.col2_x + (self.col2_w - self.total_sol_w) // 2

        new_width = self.col3_x + self.NUMPAD_W + self.MARGIN

        level_panel_height = self.max_level * (self.btn_h + 10) - 10
        col2_height = self.BOARD_H + self.MARGIN + self.SOLVER_AREA_H

        numpad_rows = (self.N - 1) // self.numpad_cols + 1
        numpad_height = (numpad_rows + 1) * (
                self.btn_size + self.numpad_gap) - self.numpad_gap + self.MARGIN + self.btn_h

        content_height = max(level_panel_height, col2_height, numpad_height)
        new_height = self.MARGIN + content_height + self.MARGIN

        if not hasattr(self, 'WIDTH') or self.WIDTH != new_width or self.HEIGHT != new_height:
            self.WIDTH = new_width
            self.HEIGHT = new_height
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        pygame.display.set_caption(f"Futoshiki {self.N}x{self.N} - Level {self.current_level}")

        self.init_level_buttons()
        self.init_numpad()
        self.init_solver_buttons()

    def init_level_buttons(self):
        self.level_rects = {}
        start_y = self.MARGIN

        for i in range(1, self.max_level + 1):
            y = start_y + (i - 1) * (self.btn_h + 10)
            self.level_rects[i] = pygame.Rect(self.col1_x, y, self.LEVEL_PANEL_W, self.btn_h)

    def init_numpad(self):
        self.numpad_rects = {}
        start_y = self.MARGIN
        cols = self.numpad_cols

        for i in range(1, self.N + 1):
            row = (i - 1) // cols
            col = (i - 1) % cols
            x = self.col3_x + col * (self.btn_size + self.numpad_gap)
            y = start_y + row * (self.btn_size + self.numpad_gap)
            self.numpad_rects[i] = pygame.Rect(x, y, self.btn_size, self.btn_size)

        row = (self.N - 1) // cols + 1
        x = self.col3_x
        y = start_y + row * (self.btn_size + self.numpad_gap)
        self.numpad_rects[0] = pygame.Rect(x, y, self.NUMPAD_W, self.btn_size)

        restart_y = y + self.btn_size + self.MARGIN
        self.btn_restart_rect = pygame.Rect(x, restart_y, self.NUMPAD_W, self.btn_h)

    def init_solver_buttons(self):
        start_y_sol1 = self.MARGIN + self.BOARD_H + self.MARGIN

        self.btn_bf_rect = pygame.Rect(self.solver_start_x, start_y_sol1, self.w_sol, self.btn_h)
        self.btn_bt_rect = pygame.Rect(self.solver_start_x + self.w_sol + self.solver_spacing, start_y_sol1, self.w_sol,
                                       self.btn_h)
        self.btn_fc_rect = pygame.Rect(self.solver_start_x + 2 * (self.w_sol + self.solver_spacing), start_y_sol1,
                                       self.w_sol, self.btn_h)

        start_y_sol2 = start_y_sol1 + self.btn_h + self.solver_spacing
        self.btn_bc_rect = pygame.Rect(self.solver_start_x, start_y_sol2, self.w_sol, self.btn_h)
        self.btn_astar_rect = pygame.Rect(self.solver_start_x + self.w_sol + self.solver_spacing, start_y_sol2,
                                          self.w_sol, self.btn_h)
        self.btn_sat_rect = pygame.Rect(self.solver_start_x + 2 * (self.w_sol + self.solver_spacing), start_y_sol2,
                                        self.w_sol, self.btn_h)

    def get_cell_pos(self, row, col):
        x = self.board_start_x + col * (self.CELL_SIZE + self.CON_SIZE)
        y = self.MARGIN + row * (self.CELL_SIZE + self.CON_SIZE)
        return x, y

    def get_cell_from_click(self, pos):
        x, y = pos
        for r in range(self.N):
            for c in range(self.N):
                cell_x, cell_y = self.get_cell_pos(r, c)
                rect = pygame.Rect(cell_x, cell_y, self.CELL_SIZE, self.CELL_SIZE)
                if rect.collidepoint(x, y):
                    return (r, c)
        return None

    def draw_button(self, text, rect, is_primary=False, is_active_level=False, is_level=False):
        mouse_pos = pygame.mouse.get_pos()

        if is_active_level:
            pygame.draw.rect(self.screen, self.SUCCESS, rect, border_radius=8)
            txt_color = self.WHITE
        else:
            if is_level:
                base_color = self.SUCCESS_LIGHT if rect.collidepoint(mouse_pos) else self.PRIMARY_LIGHT
                txt_color = self.BLACK
            elif is_primary:
                base_color = (80, 85, 230) if rect.collidepoint(mouse_pos) else self.PRIMARY
                txt_color = self.WHITE
            else:
                base_color = self.PRIMARY if rect.collidepoint(mouse_pos) else self.PRIMARY_LIGHT
                txt_color = self.WHITE if rect.collidepoint(mouse_pos) else self.BLACK

            pygame.draw.rect(self.screen, base_color, rect, border_radius=8)

        txt = self.btn_font.render(text, True, txt_color)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw_numpad(self):
        for num, rect in self.numpad_rects.items():
            text = str(num) if num > 0 else "X"
            self.draw_button(text, rect)

    def draw_level_panel(self):
        panel_rect = pygame.Rect(self.col1_x - 10, self.MARGIN - 10, self.LEVEL_PANEL_W + 20,
                                 self.max_level * (self.btn_h + 10) + 10)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.BORDER, panel_rect, 2, border_radius=10)

        for lvl, rect in self.level_rects.items():
            size = self.level_info.get(lvl, "?")
            text = f"Level {lvl} ({size}x{size})"
            is_active = (lvl == self.current_level)
            self.draw_button(text, rect, is_active_level=is_active, is_level=True)

    def draw(self):
        self.screen.fill(self.BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        self.draw_level_panel()

        for r in range(self.N):
            for c in range(self.N):
                x, y = self.get_cell_pos(r, c)
                rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)

                val = self.game.board[r][c]
                is_clue = self.game.clues[r][c]

                bg_color = self.WHITE
                txt_color = self.BLACK

                if rect.collidepoint(mouse_pos) and not is_clue:
                    bg_color = self.HOVER

                if val != 0:
                    if (r, c) in self.errors:
                        bg_color = self.ERROR_BG
                        txt_color = self.ERROR
                    elif not is_clue:
                        bg_color = self.SUCCESS_BG
                        txt_color = self.SUCCESS

                if is_clue:
                    txt_color = self.PRIMARY
                if self.selected_cell == (r, c):
                    bg_color = self.PRIMARY_LIGHT

                pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(self.screen, self.BORDER, rect, 1, border_radius=8)

                if self.selected_cell == (r, c):
                    pygame.draw.rect(self.screen, self.PRIMARY, rect, 2, border_radius=8)

                if val != 0:
                    txt = self.font.render(str(val), True, txt_color)
                    self.screen.blit(txt, txt.get_rect(center=rect.center))

                if c < self.N - 1:
                    con = self.game.horizontal_cons[r][c]
                    if con != 0:
                        symbol = "<" if con == 1 else ">"
                        surf = self.con_font.render(symbol, True, self.BLACK)
                        self.screen.blit(surf, surf.get_rect(
                            center=(x + self.CELL_SIZE + self.CON_SIZE // 2, y + self.CELL_SIZE // 2)))

                if r < self.N - 1:
                    con = self.game.vertical_cons[r][c]
                    if con != 0:
                        symbol = "^" if con == 1 else "v"
                        surf = self.con_font.render(symbol, True, self.BLACK)
                        self.screen.blit(surf, surf.get_rect(
                            center=(x + self.CELL_SIZE // 2, y + self.CELL_SIZE + self.CON_SIZE // 2)))

        self.draw_numpad()
        self.draw_button("Restart", self.btn_restart_rect, is_primary=True)

        self.draw_button("Brute Force", self.btn_bf_rect)
        self.draw_button("Backtrack", self.btn_bt_rect)
        self.draw_button("Forward Ch.", self.btn_fc_rect)
        self.draw_button("Backward Ch.", self.btn_bc_rect)
        self.draw_button("A*", self.btn_astar_rect)
        self.draw_button("CNF", self.btn_sat_rect)

        pygame.display.flip()

    def save_output(self, solver_name, time_taken, memory_mb):
        os.makedirs("Outputs", exist_ok=True)
        filename = f"Outputs/output-{self.current_level:02d}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                for row in self.game.board:
                    f.write(",".join(map(str, row)) + "\n")
        except Exception as e:
            print(f"Lỗi khi ghi file: {e}")

        print("\n" + "=" * 40)
        print(f"LEVEL {self.current_level} - ALGORITHM: {solver_name}")
        print(f"  > Status: Solved & Saved to {filename}")
        print(f"  > Execution Time: {time_taken:.6f} seconds")
        print(f"  > RAM Consumption: {memory_mb:.4f} MB")
        print("=" * 40 + "\n")

    def execute_solver(self, solver_func, solver_name):
        self.game.restart()

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss

        start_time = time.perf_counter()

        solver_func()

        end_time = time.perf_counter()

        mem_after = process.memory_info().rss

        time_taken = end_time - start_time
        memory_used_mb = max(0, (mem_after - mem_before) / (1024 * 1024))

        self.selected_cell = None
        self.errors = self.game.get_errors()

        self.save_output(solver_name, time_taken, memory_used_mb)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    handled = False

                    for lvl, rect in self.level_rects.items():
                        if rect.collidepoint(pos):
                            if self.current_level != lvl:
                                self.current_level = lvl
                                self.load_level()
                            handled = True
                            break
                    if handled: continue

                    for num, rect in self.numpad_rects.items():
                        if rect.collidepoint(pos):
                            if self.selected_cell:
                                r, c = self.selected_cell
                                self.game.set_value(r, c, num)
                                self.errors = self.game.get_errors()
                            handled = True
                            break
                    if handled: continue

                    if self.btn_restart_rect.collidepoint(pos):
                        self.game.restart()
                        self.selected_cell = None
                        self.errors = []

                    elif self.btn_bf_rect.collidepoint(pos):
                        solver = BruteForceSolver(self.game)
                        self.execute_solver(solver.solve, "Brute Force")

                    elif self.btn_bt_rect.collidepoint(pos):
                        solver = BacktrackingSolver(self.game)
                        self.execute_solver(solver.solve, "Backtracking")

                    elif self.btn_fc_rect.collidepoint(pos):
                        solver = ForwardCheckingSolver(self.game)
                        self.execute_solver(solver.solve, "Forward Chaining")

                    elif self.btn_bc_rect.collidepoint(pos):
                        solver = BackwardCheckingSolver(self.game)
                        self.execute_solver(self.game.solve_backward_chaining, "Backward Chaining")

                    elif self.btn_astar_rect.collidepoint(pos):
                        solver = AStarSolver(self.game)
                        self.execute_solver(solver.solve, "A* Search")

                    elif self.btn_sat_rect.collidepoint(pos):
                        solver = SATSolver(self.game)
                        self.execute_solver(solver.solve, "CNF / SAT")
                    # -------------------------------------------------------------

                    else:
                        cell = self.get_cell_from_click(pos)
                        if cell and not self.game.clues[cell[0]][cell[1]]:
                            self.selected_cell = cell
                        elif not cell:
                            self.selected_cell = None

                elif event.type == pygame.KEYDOWN and self.selected_cell:
                    r, c = self.selected_cell

                    if pygame.K_1 <= event.key <= pygame.K_9:
                        num = event.key - pygame.K_0
                        if num <= self.N:
                            self.game.set_value(r, c, num)
                            self.errors = self.game.get_errors()

                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                        self.game.set_value(r, c, 0)
                        self.errors = self.game.get_errors()

                    elif event.key == pygame.K_ESCAPE:
                        self.selected_cell = None

            self.draw()

        pygame.quit()