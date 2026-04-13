import copy
import heapq

class AStarSolver:
    def __init__(self, game):
        self.game = game
        self.N = game.size

    def get_empty_cell(self, board):
        """Tìm ô trống đầu tiên trên bàn cờ."""
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == 0:
                    return r, c
        return None

    def heuristic(self, board):
        """
        Hàm Heuristic h(n): Đếm số ô trống còn lại trên bàn cờ.
        Trivially admissible theo yêu cầu của đề bài.
        """
        empty_count = 0
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == 0:
                    empty_count += 1
        return empty_count

    def solve(self):
        """Thuật toán tìm kiếm A*."""
        # Trạng thái ban đầu: copy toàn bộ board hiện tại
        initial_board = copy.deepcopy(self.game.board)
        
        # Hàng đợi ưu tiên (Priority Queue). 
        # Cấu trúc lưu: (f_score, h_score, tie_breaker, current_board)
        pq = []
        tie_breaker = 0 # Dùng để tránh lỗi so sánh 2 mảng khi f và h bằng nhau
        
        h_initial = self.heuristic(initial_board)
        g_initial = 0
        f_initial = g_initial + h_initial
        
        heapq.heappush(pq, (f_initial, h_initial, tie_breaker, initial_board))

        while pq:
            # Lấy trạng thái có f(n) nhỏ nhất ra (Nếu f bằng nhau, lấy h nhỏ nhất)
            f, h, _, current_board = heapq.heappop(pq)
            
            # Tìm ô trống để điền
            empty_cell = self.get_empty_cell(current_board)
            
            # Nếu không còn ô trống -> Đã tìm thấy Goal (lời giải)
            if not empty_cell:
                # Ghi nhận kết quả ngược lại vào game object để GUI hiển thị
                for r in range(self.N):
                    for c in range(self.N):
                        self.game.board[r][c] = current_board[r][c]
                return True
                
            r, c = empty_cell
            
            # Sinh ra các trạng thái con (Successors)
            for num in range(1, self.N + 1):
                # Mượn tạm board của game để dùng hàm is_valid
                self.game.board = current_board 
                if self.game.is_valid(r, c, num):
                    # Nếu hợp lệ, tạo state mới
                    new_board = copy.deepcopy(current_board)
                    new_board[r][c] = num
                    
                    # Tính toán lại chi phí cho state mới
                    h_new = self.heuristic(new_board)
                    g_new = (self.N * self.N) - h_new # Số ô đã điền
                    f_new = g_new + h_new 
                    
                    tie_breaker += 1
                    # Đẩy state mới vào hàng đợi
                    heapq.heappush(pq, (f_new, h_new, tie_breaker, new_board))

        return False