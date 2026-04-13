import copy
import heapq

class AStarSolver:
    def __init__(self, game):
        self.game = game
        self.N = game.size

    def get_empty_cell(self, board): #tìm ô trống đầu tiên
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == 0:
                    return r, c
        return None

    def heuristic(self, board): # số ô trống còn lại
        empty_count = 0
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == 0:
                    empty_count += 1
        return empty_count

    def solve(self):
        # Trạng thái ban đầu
        initial_board = copy.deepcopy(self.game.board)

        pq = []
        tie_breaker = 0 
        
        h_initial = self.heuristic(initial_board)
        g_initial = 0
        f_initial = g_initial + h_initial
        
        heapq.heappush(pq, (f_initial, h_initial, tie_breaker, initial_board))

        while pq:
            # Lấy trạng thái có f(n) nhỏ nhất ra (Nếu f bằng nhau, lấy h nhỏ nhất)
            f, h, _, current_board = heapq.heappop(pq)
            
            empty_cell = self.get_empty_cell(current_board)
            
            # Trường hợp goal
            if not empty_cell:
                for r in range(self.N):
                    for c in range(self.N):
                        self.game.board[r][c] = current_board[r][c]
                return True
                
            r, c = empty_cell
            
            # Sinh Successors
            for num in range(1, self.N + 1):
                # Khác class nên cập nhật board chính để valid
                self.game.board = current_board 
                if self.game.is_valid(r, c, num):
                    # Nếu hợp lệ, tạo state mới
                    new_board = copy.deepcopy(current_board)
                    new_board[r][c] = num
                    
                    # Tính lại chi phí cho state mới
                    h_new = self.heuristic(new_board)
                    g_new = (self.N * self.N) - h_new # Số ô đã điền
                    f_new = g_new + h_new 
                    
                    tie_breaker += 1
                    # Đẩy state mới vào hàng đợi
                    heapq.heappush(pq, (f_new, h_new, tie_breaker, new_board))

        return False
