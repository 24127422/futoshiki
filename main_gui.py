import pygame
import sys
from futoshiki import Futoshiki


class FutoshikiGUI:
    # Color palette
    BG_COLOR = (245, 247, 252)

    WHITE = (255, 255, 255)
    BLACK = (40, 40, 40)

    PRIMARY = (99, 102, 241)
    PRIMARY_LIGHT = (210, 225, 255)

    SUCCESS = (34, 197, 94)
    SUCCESS_BG = (220, 252, 231)

    ERROR = (239, 68, 68)
    ERROR_BG = (254, 226, 226)

    BORDER = (210, 215, 225)
    HOVER = (235, 240, 255)

    def __init__(self, game_logic):
        self.game = game_logic
        if self.game.size == 0:
            print("Invalid board")
            sys.exit()

        self.N = game_logic.size
        self.errors = []

        # Layout metrics
        self.CELL_SIZE = 60
        self.CON_SIZE = 20
        self.MARGIN = 30

        self.BOARD_W = self.N * self.CELL_SIZE + (self.N - 1) * self.CON_SIZE

        # Dynamic Numpad Columns: 3 if N >= 5, else 2
        self.numpad_cols = 3 if self.N >= 5 else 2
        self.btn_size = 52
        self.numpad_gap = 10
        self.NUMPAD_W = self.btn_size * self.numpad_cols + self.numpad_gap * (self.numpad_cols - 1)

        self.btn_h = 36
        self.w_sol = 125
        self.solver_spacing = 15
        self.total_sol_w = 3 * self.w_sol + 2 * self.solver_spacing
        self.SOLVER_AREA_H = self.btn_h * 2 + self.solver_spacing

        self.WIDTH = self.MARGIN + self.BOARD_W + self.MARGIN + self.NUMPAD_W + self.MARGIN

        if self.WIDTH < self.total_sol_w + self.MARGIN * 2:
            self.WIDTH = self.total_sol_w + self.MARGIN * 2

        self.HEIGHT = self.MARGIN + self.BOARD_W + self.MARGIN + self.SOLVER_AREA_H + self.MARGIN

        pygame.init()
        pygame.display.set_caption(f"Futoshiki {self.N}x{self.N}")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.font = pygame.font.SysFont("Helvetica, Arial", 32, bold=True)
        self.con_font = pygame.font.SysFont("Helvetica, Arial", 24, bold=True)
        self.btn_font = pygame.font.SysFont("Helvetica, Arial", 14, bold=True)

        self.selected_cell = None

        self.init_numpad()

        start_y_sol1 = self.MARGIN + self.BOARD_W + self.MARGIN
        start_x_sol = (self.WIDTH - self.total_sol_w) // 2

        self.btn_bf_rect = pygame.Rect(start_x_sol, start_y_sol1, self.w_sol, self.btn_h)
        self.btn_bt_rect = pygame.Rect(start_x_sol + self.w_sol + self.solver_spacing, start_y_sol1, self.w_sol,
                                       self.btn_h)
        self.btn_fc_rect = pygame.Rect(start_x_sol + 2 * (self.w_sol + self.solver_spacing), start_y_sol1, self.w_sol,
                                       self.btn_h)

        start_y_sol2 = start_y_sol1 + self.btn_h + self.solver_spacing
        self.btn_bc_rect = pygame.Rect(start_x_sol, start_y_sol2, self.w_sol, self.btn_h)
        self.btn_astar_rect = pygame.Rect(start_x_sol + self.w_sol + self.solver_spacing, start_y_sol2, self.w_sol,
                                          self.btn_h)
        self.btn_sat_rect = pygame.Rect(start_x_sol + 2 * (self.w_sol + self.solver_spacing), start_y_sol2, self.w_sol,
                                        self.btn_h)

    def init_numpad(self):
        self.numpad_rects = {}
        start_x = self.MARGIN * 2 + self.BOARD_W
        start_y = self.MARGIN

        cols = self.numpad_cols

        for i in range(1, self.N + 1):
            row = (i - 1) // cols
            col = (i - 1) % cols
            x = start_x + col * (self.btn_size + self.numpad_gap)
            y = start_y + row * (self.btn_size + self.numpad_gap)
            self.numpad_rects[i] = pygame.Rect(x, y, self.btn_size, self.btn_size)

        row = self.N // cols + (1 if self.N % cols != 0 else 0)
        x = start_x
        y = start_y + row * (self.btn_size + self.numpad_gap)
        self.numpad_rects[0] = pygame.Rect(x, y, self.NUMPAD_W, self.btn_size)

        restart_y = y + self.btn_size + self.numpad_gap + 15
        self.btn_restart_rect = pygame.Rect(start_x, restart_y, self.NUMPAD_W, self.btn_h)

    def get_cell_pos(self, row, col):
        x = self.MARGIN + col * (self.CELL_SIZE + self.CON_SIZE)
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

    def draw_button(self, text, rect, is_primary=False):
        mouse_pos = pygame.mouse.get_pos()

        base_color = self.PRIMARY if rect.collidepoint(mouse_pos) else self.PRIMARY_LIGHT
        txt_color = self.WHITE if rect.collidepoint(mouse_pos) else self.BLACK

        pygame.draw.rect(self.screen, base_color, rect, border_radius=8)

        txt = self.btn_font.render(text, True, txt_color)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw_numpad(self):
        for num, rect in self.numpad_rects.items():
            text = str(num) if num > 0 else "X"
            self.draw_button(text, rect)

    def draw(self):
        self.screen.fill(self.BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

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
                            center=(x + self.CELL_SIZE + self.CON_SIZE // 2,
                                    y + self.CELL_SIZE // 2)))

                if r < self.N - 1:
                    con = self.game.vertical_cons[r][c]
                    if con != 0:
                        symbol = "^" if con == 1 else "v"
                        surf = self.con_font.render(symbol, True, self.BLACK)
                        self.screen.blit(surf, surf.get_rect(
                            center=(x + self.CELL_SIZE // 2,
                                    y + self.CELL_SIZE + self.CON_SIZE // 2)))

        self.draw_numpad()

        self.draw_button("Restart", self.btn_restart_rect, is_primary=True)

        self.draw_button("Brute Force", self.btn_bf_rect)
        self.draw_button("Backtrack", self.btn_bt_rect)
        self.draw_button("Forward Ch.", self.btn_fc_rect)

        self.draw_button("Backward Ch.", self.btn_bc_rect)
        self.draw_button("A*", self.btn_astar_rect)
        self.draw_button("CNF / SAT", self.btn_sat_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    handled = False

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
                        self.game.restart()
                        self.game.solve_brute_force()
                        self.selected_cell = None
                        self.errors = []

                    elif self.btn_bt_rect.collidepoint(pos):
                        self.game.restart()
                        self.game.solve_backtracking()
                        self.selected_cell = None
                        self.errors = []

                    elif self.btn_fc_rect.collidepoint(pos):
                        self.game.restart()
                        self.game.solve_forward_chaining()
                        self.selected_cell = None
                        self.errors = []

                    elif self.btn_bc_rect.collidepoint(pos):
                        self.game.restart()
                        self.game.solve_backward_chaining()
                        self.selected_cell = None
                        self.errors = []

                    elif self.btn_astar_rect.collidepoint(pos):
                        self.game.restart()
                        self.game.solve_astar()
                        self.selected_cell = None
                        self.errors = []

                    elif self.btn_sat_rect.collidepoint(pos):
                        self.game.restart()
                        self.game.solve_sat()
                        self.selected_cell = None
                        self.errors = []

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


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input-01.txt'
    game = Futoshiki(input_file)

    if game.size > 0:
        app = FutoshikiGUI(game)
        app.run()