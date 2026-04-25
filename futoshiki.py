class Futoshiki:
    def __init__(self, filename=None):
        self.size = 0
        self.board = []
        self.clues = []  # Đánh dấu các ô gợi ý ban đầu
        self.history = []
        self.horizontal_cons = []  # 1: <, -1: >
        self.vertical_cons = []  # 1: ^, -1: v

        if filename:
            self.read_file(filename)

    def read_file(self, filename):
        try:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f.readlines()]
                # Lọc bỏ comment và dòng trống
                clean_lines = [line for line in lines if line and not line.startswith('#')]

            if not clean_lines:
                return

            # Đọc kích thước (ép kiểu về int)
            try:
                self.size = int(clean_lines[0])
            except ValueError:
                print("LỖI: Dòng đầu tiên của file input phải là một con số (VD: 4, 5). Hãy kiểm tra lại file input!")
                return

            idx = 1

            # Đọc Grid chính
            for _ in range(self.size):
                row = [int(x.strip()) for x in clean_lines[idx].split(',')]
                self.board.append(row)
                self.clues.append([val != 0 for val in row])
                idx += 1

            # Đọc Constraint ngang
            for _ in range(self.size):
                h_cons = [int(x.strip()) for x in clean_lines[idx].split(',')]
                self.horizontal_cons.append(h_cons)
                idx += 1

            # Đọc Constraint dọc
            for _ in range(self.size - 1):
                v_cons = [int(x.strip()) for x in clean_lines[idx].split(',')]
                self.vertical_cons.append(v_cons)
                idx += 1

            print(f"Load file success '{filename}' (Size: {self.size}x{self.size})")
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"Error occurred while reading file: {e}")

    def is_valid(self, row, col, num):
        """Kiểm tra xem số num điền vào ô (row, col) có hợp lệ không."""
        # 1. Kiểm tra hàng và cột
        for i in range(self.size):
            if self.board[row][i] == num or self.board[i][col] == num:
                return False

        # 2. Kiểm tra ràng buộc ngang
        if col > 0 and self.board[row][col - 1] != 0:
            left_val = self.board[row][col - 1]
            con = self.horizontal_cons[row][col - 1]
            if con == 1 and not (left_val < num): return False  # <
            if con == -1 and not (left_val > num): return False  # >

        if col < self.size - 1 and self.board[row][col + 1] != 0:
            right_val = self.board[row][col + 1]
            con = self.horizontal_cons[row][col]
            if con == 1 and not (num < right_val): return False  # <
            if con == -1 and not (num > right_val): return False  # >

        # 3. Kiểm tra ràng buộc dọc
        if row > 0 and self.board[row - 1][col] != 0:
            top_val = self.board[row - 1][col]
            con = self.vertical_cons[row - 1][col]
            if con == 1 and not (top_val < num): return False  # ^
            if con == -1 and not (top_val > num): return False  # v

        if row < self.size - 1 and self.board[row + 1][col] != 0:
            bottom_val = self.board[row + 1][col]
            con = self.vertical_cons[row][col]
            if con == 1 and not (num < bottom_val): return False  # ^
            if con == -1 and not (num > bottom_val): return False  # v

        return True

    def Val(self, i, j, v):
        return self.board[i][j] == v

    def LessH(self, i, j):
        return self.horizontal_cons[i][j] == 1 if j < self.size - 1 else False

    def GreaterH(self, i, j):
        return self.horizontal_cons[i][j] == -1 if j < self.size - 1 else False

    def LessV(self, i, j):
        return self.vertical_cons[i][j] == 1 if i < self.size - 1 else False

    def GreaterV(self, i, j):
        return self.vertical_cons[i][j] == -1 if i < self.size - 1 else False

    # --- CƠ CHẾ ĐIỀN SỐ & UNDO ---
    def set_value(self, r, c, v):
        if not self.clues[r][c]:
            self.board[r][c] = v

    def restart(self):
        self.history = []
        for r in range(self.size):
            for c in range(self.size):
                if not self.clues[r][c]:
                    self.board[r][c] = 0

    # --- KIỂM TRA LỖI (Nút Check) ---
    def get_errors(self):
        """Trả về danh sách các tọa độ (r, c) bị sai luật."""
        errors = set()
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r][c]
                if val == 0: continue

                # Kiểm tra hàng/cột trùng
                for k in range(self.size):
                    if k != c and self.board[r][k] == val: errors.add((r, c))
                    if k != r and self.board[k][c] == val: errors.add((r, c))

                # Kiểm tra ràng buộc ngang dùng FOL Predicates
                if self.LessH(r, c) and self.board[r][c + 1] != 0:
                    if not (val < self.board[r][c + 1]): errors.add((r, c)); errors.add((r, c + 1))
                if self.GreaterH(r, c) and self.board[r][c + 1] != 0:
                    if not (val > self.board[r][c + 1]): errors.add((r, c)); errors.add((r, c + 1))

                # Kiểm tra ràng buộc dọc
                if self.LessV(r, c) and self.board[r + 1][c] != 0:
                    if not (val < self.board[r + 1][c]): errors.add((r, c)); errors.add((r, r + 1))
                if self.GreaterV(r, c) and self.board[r + 1][c] != 0:
                    if not (val > self.board[r + 1][c]): errors.add((r, c)); errors.add((r + 1, c))
        return list(errors)

    def is_entire_board_valid(self):
        for r in range(self.size):
            for c in range(self.size):
                num = self.board[r][c]
                self.board[r][c] = 0
                if not self.is_valid(r, c, num):
                    self.board[r][c] = num
                    return False
                self.board[r][c] = num
        return True