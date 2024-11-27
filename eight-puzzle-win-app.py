import tkinter as tk
import random
from tkinter import ttk
from search import EightPuzzle, astar_search
import math
import time


def manhattan_distance(state, goal_state):
    """
    Tính toán khoảng cách Manhattan giữa trạng thái hiện tại và trạng thái mục tiêu.
    Khoảng cách Manhattan là tổng của các khoảng cách hàng và cột giữa các ô hiện tại và vị trí đích của chúng.
    Công thức: |x1 - x2| + |y1 - y2|
    """
    distance = 0
    for i in range(9):  # Có 9 ô trong puzzle
        if state[i] != 0:  # Không tính ô trống
            current_pos = (i // 3, i % 3)  # Vị trí hiện tại trong ma trận, tính bằng cách chia lấy nguyên và lấy dư cho 3
            goal_pos = ((goal_state.index(state[i])) // 3, (goal_state.index(state[i])) % 3)  # Vị trí trong trạng thái mục tiêu, tính bằng cách tìm vị trí giá trị trong trạng thái mục tiêu, sau đó chia lấy nguyên và lấy dư cho 3
            distance += abs(current_pos[0] - goal_pos[0]) + abs(current_pos[1] - goal_pos[1])  # Tính Manhattan Distance
    return distance


class EightPuzzleWithManhattan(EightPuzzle):
    """
    Lớp kế thừa từ EightPuzzle, sử dụng hàm heuristic là khoảng cách Manhattan.
    """
    def h(self, node):
        return manhattan_distance(node.state, self.goal)


class EightPuzzleWithMisplacedTiles(EightPuzzle):
    """
    Lớp kế thừa từ EightPuzzle, sử dụng heuristic là số ô bị đặt sai vị trí.
    Công thức: Tổng số ô mà giá trị của chúng không khớp với giá trị ở vị trí mục tiêu, ngoại trừ ô trống.
    """
    def h(self, node):
        return sum(s != g and s != 0 for s, g in zip(node.state, self.goal))


class EightPuzzleWithEuclidean(EightPuzzle):
    """
    Lớp kế thừa từ EightPuzzle, sử dụng khoảng cách Euclidean làm hàm heuristic.
    Công thức: sqrt((x1 - x2)^2 + (y1 - y2)^2)
    """
    def h(self, node):
        distance = 0
        for i in range(9):
            if node.state[i] != 0:
                current_pos = (i // 3, i % 3)  # Vị trí hiện tại trong ma trận, tính bằng cách chia lấy nguyên và lấy dư cho 3
                goal_pos = (self.goal.index(node.state[i]) // 3, self.goal.index(node.state[i]) % 3)  # Vị trí trong trạng thái mục tiêu, tính bằng cách tìm vị trí giá trị trong trạng thái mục tiêu, sau đó chia lấy nguyên và lấy dư cho 3
                distance += math.sqrt((current_pos[0] - goal_pos[0])**2 + (current_pos[1] - goal_pos[1])**2)  # Tính khoảng cách Euclidean
        return distance


class EightPuzzleWithLinearConflict(EightPuzzleWithManhattan):
    """
    Lớp kế thừa từ EightPuzzleWithManhattan, thêm xung đột hàng/cột vào khoảng cách Manhattan.
    Công thức tổng quát: Manhattan Distance + 2 * (Số lượng xung đột hàng và cột)
    """
    def h(self, node):
        manhattan = super().h(node)
        linear_conflict = 0

        # Tính xung đột hàng
        for row in range(3):
            row_values = [node.state[row * 3 + col] for col in range(3)]
            for i in range(3):
                for j in range(i + 1, 3):
                    if (
                        row_values[i] != 0 and row_values[j] != 0 and
                        self.goal.index(row_values[i]) // 3 == row and
                        self.goal.index(row_values[j]) // 3 == row and
                        self.goal.index(row_values[i]) > self.goal.index(row_values[j])
                    ):
                        linear_conflict += 1  # Nếu hai ô cùng hàng và giá trị của chúng bị đảo ngược so với mục tiêu, tăng số lượng xung đột hàng

        # Tính xung đột cột
        for col in range(3):
            col_values = [node.state[row * 3 + col] for row in range(3)]
            for i in range(3):
                for j in range(i + 1, 3):
                    if (
                        col_values[i] != 0 and col_values[j] != 0 and
                        self.goal.index(col_values[i]) % 3 == col and
                        self.goal.index(col_values[j]) % 3 == col and
                        self.goal.index(col_values[i]) > self.goal.index(col_values[j])
                    ):
                        linear_conflict += 1  # Nếu hai ô cùng cột và giá trị của chúng bị đảo ngược so với mục tiêu, tăng số lượng xung đột cột

        return manhattan + 2 * linear_conflict  # Mỗi xung đột đóng góp thêm 2 đơn vị vào hàm heuristic


class PuzzleApp:
    def __init__(self, root):
        """
        Khởi tạo giao diện ứng dụng 8-Puzzle Solver.
        """
        self.root = root
        self.root.title("8-Puzzle Solver")
        self.root.geometry("500x600")

        # Đặt màu nền, màu ô, và màu chữ
        self.bg_color = "#C9E6F0"
        self.tile_color = "#78B3CE"
        self.text_color = "black"

        # Cấu hình màu nền cho cửa sổ chính
        self.root.config(bg=self.bg_color)

        # Khởi tạo trạng thái bắt đầu và trạng thái mục tiêu
        self.start_state = (2, 6, 5, 0, 8, 7, 4, 3, 1)
        self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)

        self.create_grid()  # Tạo giao diện lưới cho puzzle

        self.steps = []  # Lưu trữ các bước để giải puzzle
        self.step_count = 0  # Đếm số bước

        # Frame chứa các nút bấm
        self.buttons_frame = tk.Frame(self.root, bg=self.bg_color)
        self.buttons_frame.pack(pady=5)

        # Dropdown chọn phương pháp heuristic
        self.method_var = tk.StringVar(value="Manhattan Distance")
        self.method_label = tk.Label(self.buttons_frame, text="Select Method:", bg=self.bg_color, fg=self.text_color, font=("Arial", 12))
        self.method_label.grid(row=0, column=0, padx=5, pady=5)

        self.method_dropdown = ttk.Combobox(
            self.buttons_frame,
            textvariable=self.method_var,
            values=["Manhattan Distance", "Misplaced Tiles", "Euclidean Distance", "Linear Conflict"],
            state="readonly",
            font=("Arial", 12)
        )
        self.method_dropdown.grid(row=0, column=1, columnspan=2, padx=10, pady=5)

        # Nút Reset
        self.reset_button = tk.Button(
            self.buttons_frame,
            text="Reset",
            command=self.reset_puzzle,
            font=('Arial', 16),
            bg=self.tile_color,
            fg=self.text_color,
        )
        self.reset_button.grid(row=1, column=0, pady=10, padx=10)

        # Nút Randomize
        self.randomize_button = tk.Button(
            self.buttons_frame,
            text="Randomize",
            command=self.randomize_puzzle,
            font=('Arial', 16),
            bg=self.tile_color,
            fg=self.text_color,
        )
        self.randomize_button.grid(row=1, column=1, pady=10, padx=10)

        # Nút Solve
        self.solve_button = tk.Button(
            self.buttons_frame,
            text="Solve",
            command=self.solve_puzzle,
            font=('Arial', 16),
            bg=self.tile_color,
            fg=self.text_color,
        )
        self.solve_button.grid(row=1, column=2, padx=10)

        # Frame chứa thông tin số bước và thời gian
        self.info_frame = tk.Frame(self.root, bg=self.bg_color)
        self.info_frame.pack(pady=10)

        # Nhãn hiển thị số bước
        self.steps_label = tk.Label(
            self.info_frame, text="Steps: 0", font=('Arial', 16), bg=self.bg_color, fg=self.text_color
        )
        self.steps_label.grid(row=0, column=0, padx=10)

        # Nhãn hiển thị thời gian
        self.time_label = tk.Label(
            self.info_frame, text="Time: 0 ms", font=('Arial', 16), bg=self.bg_color, fg=self.text_color
        )
        self.time_label.grid(row=0, column=1, padx=10)

    def create_grid(self):
        """
        Tạo giao diện lưới chứa các ô của puzzle.
        Mỗi ô trong lưới được biểu diễn bằng một Label của Tkinter.
        Các ô được đặt trong một Frame để tạo bố cục lưới 3x3.
        
        - Sử dụng vòng lặp để tạo từng ô (Label), đặt giá trị bắt đầu từ trạng thái `start_state`.
        - Ô trống (giá trị 0) sẽ hiển thị như một ô trống không có số.
        - Đặt thuộc tính `grid` cho từng ô để sắp xếp chúng thành một lưới 3x3.
        """
        self.frame = tk.Frame(self.root, bg=self.bg_color)
        self.frame.pack(expand=True)

        self.tiles = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                value = self.start_state[i * 3 + j]  # Lấy giá trị của ô từ trạng thái bắt đầu
                self.tiles[i][j] = tk.Label(
                    self.frame,
                    text=str(value) if value != 0 else ' ',  # Nếu giá trị là 0, hiển thị ô trống
                    font=('Arial', 36),
                    width=4,
                    height=2,
                    bg=self.tile_color,
                    fg=self.text_color,
                    borderwidth=2,
                    relief="solid",
                )
                self.tiles[i][j].grid(row=i, column=j, padx=5, pady=5, sticky="nsew")  # Đặt ô vào đúng vị trí trong lưới

        for i in range(3):
            self.frame.grid_columnconfigure(i, weight=1)  # Định cấu hình để cột có kích thước tự động điều chỉnh
            self.frame.grid_rowconfigure(i, weight=1)  # Định cấu hình để hàng có kích thước tự động điều chỉnh

    def solve_puzzle(self):
        """
        Giải quyết puzzle bằng phương pháp heuristic được chọn và cập nhật giao diện với số bước và thời gian giải.
        """
        method = self.method_var.get()
        if method == "Manhattan Distance":
            problem = EightPuzzleWithManhattan(self.start_state, self.goal_state)
        elif method == "Misplaced Tiles":
            problem = EightPuzzleWithMisplacedTiles(self.start_state, self.goal_state)
        elif method == "Euclidean Distance":
            problem = EightPuzzleWithEuclidean(self.start_state, self.goal_state)
        elif method == "Linear Conflict":
            problem = EightPuzzleWithLinearConflict(self.start_state, self.goal_state)

        # Đo thời gian bắt đầu và kết thúc để tính thời gian giải quyết
        start_time = time.time()
        solution = astar_search(problem)
        end_time = time.time()

        elapsed_time = (end_time - start_time) * 1000  # Đổi sang milliseconds
        self.time_label.config(text=f"Time: {elapsed_time:.2f} ms")

        if solution:
            self.steps = solution.path()  # Lưu trữ các bước giải
            self.step_count = 0
            self.steps_label.config(text=f"Steps: {len(self.steps) - 1}")
            self.show_next_step()  # Hiển thị bước tiếp theo

    def show_next_step(self):
        """
        Hiển thị bước tiếp theo của giải pháp trên giao diện.
        """
        if self.step_count < len(self.steps):
            state = self.steps[self.step_count].state

            # Chỉ cập nhật giao diện khi trạng thái thay đổi
            if self.step_count == 0 or self.steps[self.step_count - 1].state != state:
                self.update_grid(state)

            self.step_count += 1
            self.root.after(500, self.show_next_step)  # Hiển thị bước tiếp theo sau 500ms

    def update_grid(self, state):
        """
        Cập nhật giao diện lưới để phản ánh trạng thái hiện tại của puzzle.
        """
        for i in range(3):
            for j in range(3):
                value = state[i * 3 + j]
                # Chỉ cập nhật ô nếu giá trị của nó thay đổi
                if self.tiles[i][j]['text'] != (str(value) if value != 0 else ' '):
                    self.tiles[i][j].config(text=str(value) if value != 0 else ' ')

    def reset_puzzle(self):
        """
        Đặt lại trạng thái của puzzle về trạng thái bắt đầu ban đầu.
        """
        self.update_grid(self.start_state)
        self.steps = []
        self.step_count = 0
        self.steps_label.config(text="Steps: 0")

    def randomize_puzzle(self):
        """
        Ngẫu nhiên hoá trạng thái của puzzle nhưng đảm bảo trạng thái này có thể giải được.
        """
        random_state = list(self.start_state)
        random.shuffle(random_state)
        while not self.is_solvable(random_state):
            random.shuffle(random_state)
        self.start_state = tuple(random_state)
        self.update_grid(self.start_state)
        self.steps_label.config(text="Steps: 0")

    def is_solvable(self, state):
        """
        Kiểm tra xem trạng thái của puzzle có thể giải được hay không bằng cách đếm số lần đảo ngược.
        Công thức: Đếm số cặp ô (i, j) sao cho i xuất hiện trước j và i > j. Nếu số lần đảo ngược là chẵn, puzzle có thể giải được.
        """
        inversion_count = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                    inversion_count += 1
        return inversion_count % 2 == 0


root = tk.Tk()
app = PuzzleApp(root)
root.mainloop()
