import tkinter as tk
import random
from search import EightPuzzle, astar_search

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver")
        self.root.geometry("500x500")

        self.bg_color = "#C9E6F0"
        self.tile_color = "#78B3CE"
        self.text_color = "black"

        self.root.config(bg=self.bg_color)

        self.start_state = (2, 6, 5, 0, 8, 7, 4, 3, 1)
        self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)

        self.create_grid()

        self.steps = []
        self.step_count = 0
        self.solution_process = None

        # Buttons frame
        self.buttons_frame = tk.Frame(self.root, bg=self.bg_color)
        self.buttons_frame.pack(pady=5)

        # Solve button
        self.solve_button = tk.Button(self.buttons_frame, text="Solve", command=self.solve_puzzle, font=('Arial', 16), bg=self.tile_color, fg=self.text_color)
        self.solve_button.grid(row=0, column=0, padx=10)

        # Reset button
        self.reset_button = tk.Button(self.buttons_frame, text="Reset", command=self.reset_puzzle, font=('Arial', 16), bg=self.tile_color, fg=self.text_color)
        self.reset_button.grid(row=0, column=1, padx=10)

        # Randomize button
        self.randomize_button = tk.Button(self.buttons_frame, text="Randomize", command=self.randomize_puzzle, font=('Arial', 16), bg=self.tile_color, fg=self.text_color)
        self.randomize_button.grid(row=0, column=2, padx=10)

        # Steps label
        self.steps_label = tk.Label(self.root, text="Steps: 0", font=('Arial', 16), bg=self.bg_color, fg=self.text_color)
        self.steps_label.pack(pady=10)

    def create_grid(self):
        # Create a frame to hold the puzzle tiles
        self.frame = tk.Frame(self.root, bg=self.bg_color)
        self.frame.pack(expand=True)

        self.tiles = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                value = self.start_state[i * 3 + j]
                self.tiles[i][j] = tk.Label(self.frame, text=str(value) if value != 0 else ' ',
                                            font=('Arial', 36), width=4, height=2, bg=self.tile_color, fg=self.text_color,
                                            borderwidth=2, relief="solid")
                self.tiles[i][j].grid(row=i, column=j, padx=5, pady=5, sticky="nsew")

        for i in range(3):
            self.frame.grid_columnconfigure(i, weight=1)
            self.frame.grid_rowconfigure(i, weight=1)

    def solve_puzzle(self):
        problem = EightPuzzle(self.start_state, self.goal_state)
        solution = astar_search(problem)

        if solution:
            self.steps = solution.path()
            self.step_count = 0
            self.steps_label.config(text=f"Steps: {len(self.steps) - 1}")
            self.show_next_step()

    def show_next_step(self):
        if self.step_count < len(self.steps):
            state = self.steps[self.step_count].state
            self.update_grid(state)
            self.step_count += 1
            self.root.after(500, self.show_next_step)

    def update_grid(self, state):
        for i in range(3):
            for j in range(3):
                value = state[i * 3 + j]
                self.tiles[i][j].config(text=str(value) if value != 0 else ' ')

    def reset_puzzle(self):
        self.update_grid(self.start_state)
        self.steps = []
        self.step_count = 0
        self.steps_label.config(text="Steps: 0")

    def randomize_puzzle(self):
        random_state = list(self.start_state)
        random.shuffle(random_state)
        while not self.is_solvable(random_state):
            random.shuffle(random_state)
        self.start_state = tuple(random_state)
        self.update_grid(self.start_state)
        self.steps_label.config(text="Steps: 0")

    def is_solvable(self, state):
        inversion_count = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                    inversion_count += 1
        return inversion_count % 2 == 0

root = tk.Tk()
app = PuzzleApp(root)
root.mainloop()
