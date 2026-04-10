import pygame
import sys
from futoshiki import Futoshiki

class FutoshikiGUI:
    # --- BẢNG MÀU ---
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BG_COLOR = (245, 245, 245)
    
    BLUE_CLUE = (0, 80, 200)      # Số đề bài cho
    RED_INPUT = (200, 50, 50)     # Số người dùng nhập
    
    YELLOW_SEL = (255, 255, 150)  # Ô đang chọn
    ERROR_HIGHLIGHT = (255, 180, 180) # Ô bị sai luật
    
    BTN_UNDO = (230, 126, 34)     # Cam
    BTN_RESTART = (149, 165, 166) # Xám
    BTN_CHECK = (52, 152, 219)    # Xanh dương
    BTN_SOLVE = (39, 174, 96)     # Xanh lá

    def __init__(self, game_logic):
        self.game = game_logic
        if self.game.size == 0:
            print("Lỗi: Dữ liệu bàn cờ không hợp lệ. Đóng chương trình.")
            sys.exit()
            
        self.N = game_logic.size
        self.errors = [] # Danh sách các ô vi phạm luật (r, c)
        
        # --- KÍCH THƯỚC HIỂN THỊ ---
        self.CELL_SIZE = 60
        self.MARGIN = 20
        self.CON_SIZE = 20
        
        # Tính toán chiều rộng và chiều cao động theo N
        self.WIDTH = self.N * self.CELL_SIZE + (self.N - 1) * self.CON_SIZE + 2 * self.MARGIN
        # Chiều cao tăng thêm 130px để chứa 2 hàng nút bấm
        self.HEIGHT = self.N * self.CELL_SIZE + (self.N - 1) * self.CON_SIZE + 2 * self.MARGIN + 130
        
        pygame.init()
        pygame.display.set_caption(f"Futoshiki - Size: {self.N}x{self.N}")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        # Fonts
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.con_font = pygame.font.SysFont("Courier", 24, bold=True)
        self.btn_font = pygame.font.SysFont("Arial", 18, bold=True)
        
        self.selected_cell = None
        
        # --- TỌA ĐỘ NÚT BẤM (Căn giữa theo WIDTH) ---
        center_x = self.WIDTH // 2
        btn_y1 = self.HEIGHT - 110 # Hàng trên
        btn_y2 = self.HEIGHT - 60  # Hàng dưới
        
        self.btn_undo_rect = pygame.Rect(center_x - 140, btn_y1, 80, 40)
        self.btn_restart_rect = pygame.Rect(center_x - 50, btn_y1, 100, 40)
        self.btn_check_rect = pygame.Rect(center_x + 60, btn_y1, 80, 40)
        
        self.btn_solve_rect = pygame.Rect(center_x - 140, btn_y2, 280, 40)

    def get_cell_pos(self, row, col):
        """Tính tọa độ góc trên trái của ô"""
        x = self.MARGIN + col * (self.CELL_SIZE + self.CON_SIZE)
        y = self.MARGIN + row * (self.CELL_SIZE + self.CON_SIZE)
        return x, y

    def get_cell_from_click(self, pos):
        """Xác định click chuột đang ở ô lưới nào"""
        x, y = pos
        for r in range(self.N):
            for c in range(self.N):
                cell_x, cell_y = self.get_cell_pos(r, c)
                cell_rect = pygame.Rect(cell_x, cell_y, self.CELL_SIZE, self.CELL_SIZE)
                if cell_rect.collidepoint(x, y):
                    return (r, c)
        return None

    def draw_button(self, text, rect, color):
        """Hàm vẽ nút bấm bo góc"""
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        txt_surf = self.btn_font.render(text, True, self.WHITE)
        self.screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))

    def draw(self):
        """Hàm vẽ toàn bộ giao diện"""
        self.screen.fill(self.BG_COLOR)
        
        # 1. Vẽ lưới bảng
        for r in range(self.N):
            for c in range(self.N):
                x, y = self.get_cell_pos(r, c)
                rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
                
                # Màu nền ô: Ưu tiên màu đỏ (Lỗi) -> Màu vàng (Đang chọn) -> Trắng (Mặc định)
                if (r, c) in self.errors:
                    pygame.draw.rect(self.screen, self.ERROR_HIGHLIGHT, rect)
                elif self.selected_cell == (r, c):
                    pygame.draw.rect(self.screen, self.YELLOW_SEL, rect)
                else:
                    pygame.draw.rect(self.screen, self.WHITE, rect)
                
                # Viền đen
                pygame.draw.rect(self.screen, self.BLACK, rect, 2)
                
                # Hiển thị số
                val = self.game.board[r][c]
                if val != 0:
                    color = self.BLUE_CLUE if self.game.clues[r][c] else self.RED_INPUT
                    text_surf = self.font.render(str(val), True, color)
                    self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

                # Vẽ Ràng buộc ngang (<, >)
                if c < self.N - 1:
                    con = self.game.horizontal_cons[r][c]
                    if con != 0:
                        txt = "<" if con == 1 else ">"
                        surf = self.con_font.render(txt, True, self.BLACK)
                        self.screen.blit(surf, surf.get_rect(center=(x + self.CELL_SIZE + self.CON_SIZE // 2, y + self.CELL_SIZE // 2)))

                # Vẽ Ràng buộc dọc (^, v)
                if r < self.N - 1:
                    con = self.game.vertical_cons[r][c]
                    if con != 0:
                        txt = "^" if con == 1 else "v"
                        surf = self.con_font.render(txt, True, self.BLACK)
                        self.screen.blit(surf, surf.get_rect(center=(x + self.CELL_SIZE // 2, y + self.CELL_SIZE + self.CON_SIZE // 2)))

        # 2. Vẽ các nút chức năng
        self.draw_button("Undo", self.btn_undo_rect, self.BTN_UNDO)
        self.draw_button("Restart", self.btn_restart_rect, self.BTN_RESTART)
        self.draw_button("Check", self.btn_check_rect, self.BTN_CHECK)
        self.draw_button("Auto Solve (Backtracking)", self.btn_solve_rect, self.BTN_SOLVE)
        
        pygame.display.flip()

    def run(self):
        """Vòng lặp sự kiện chính"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                # XỬ LÝ CLICK CHUỘT
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    
                    # 1. Click vào các nút chức năng
                    if self.btn_undo_rect.collidepoint(pos):
                        self.game.undo()
                        self.errors = [] # Xóa lỗi hiển thị
                        
                    elif self.btn_restart_rect.collidepoint(pos):
                        self.game.restart()
                        self.selected_cell = None
                        self.errors = []
                        
                    elif self.btn_check_rect.collidepoint(pos):
                        self.errors = self.game.get_errors()
                        if not self.errors:
                            print("Tuyệt vời! Hiện tại không có lỗi nào.")
                            
                    elif self.btn_solve_rect.collidepoint(pos):
                        print("Đang giải tự động...")
                        self.game.restart() # Xóa các số nhập tay để máy tự giải từ đầu
                        self.game.solve_backtracking()
                        self.selected_cell = None
                        self.errors = []
                        
                    # 2. Click vào các ô trên lưới
                    else:
                        clicked_cell = self.get_cell_from_click(pos)
                        if clicked_cell:
                            r, c = clicked_cell
                            # Chỉ cho phép chọn ô nếu nó không phải là gợi ý đề bài
                            if not self.game.clues[r][c]:
                                self.selected_cell = clicked_cell
                        else:
                            self.selected_cell = None

                # XỬ LÝ NHẬP BÀN PHÍM
                elif event.type == pygame.KEYDOWN and self.selected_cell:
                    r, c = self.selected_cell
                    
                    # Nhập số (1 -> N)
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        num = event.key - pygame.K_0
                        if num <= self.N:
                            self.game.set_value(r, c, num)
                            self.errors = [] # Xóa highlight lỗi cũ khi nhập số mới
                            
                    # Xóa số (Backspace / Delete) hoặc phím 0
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                        self.game.set_value(r, c, 0)
                        self.errors = []
                        
                    # Bỏ chọn ô (Escape)
                    elif event.key == pygame.K_ESCAPE:
                        self.selected_cell = None

            self.draw()
            
        pygame.quit()

# ==========================================
# KHỞI CHẠY APP
# ==========================================
if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input-01.txt'
    
    print(f"Đang tải cấu hình từ: {input_file}")
    game = Futoshiki(input_file)
    
    if game.size > 0:
        app = FutoshikiGUI(game)
        app.run()