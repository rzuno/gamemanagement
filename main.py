import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Management")
        self.root.geometry("1200x800")

        # Data
        self.evaluations_df = self.load_csv('data/game_evaluations.csv')
        self.wishlist_df = self.load_csv('data/wish_list.csv')

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for the list of games and buttons
        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right frame for game information
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Game list
        self.game_list_label = ttk.Label(left_frame, text="Played Games", font=("Arial", 14, "bold"))
        self.game_list_label.pack(pady=5)
        
        self.game_listbox = tk.Listbox(left_frame, width=50, height=30)
        self.game_listbox.pack(fill=tk.BOTH, expand=True)
        self.populate_game_list()

        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=10)

        add_button = ttk.Button(button_frame, text="Add New Game", command=self.add_new_game)
        add_button.grid(row=0, column=0, padx=5, pady=5)

        modify_button = ttk.Button(button_frame, text="Modify Game Evaluation", command=self.modify_game_evaluation)
        modify_button.grid(row=0, column=1, padx=5, pady=5)

        stats_button = ttk.Button(button_frame, text="Statistics", command=self.show_statistics)
        stats_button.grid(row=1, column=0, padx=5, pady=5)

        wishlist_button = ttk.Button(button_frame, text="Wish List", command=self.show_wish_list)
        wishlist_button.grid(row=1, column=1, padx=5, pady=5)

    def load_csv(self, file_path):
        if os.path.exists(file_path):
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {file_path}: {e}")
                return pd.DataFrame()
        else:
            messagebox.showwarning("Warning", f"{file_path} not found.")
            return pd.DataFrame()

    def populate_game_list(self):
        self.game_listbox.delete(0, tk.END)
        if not self.evaluations_df.empty:
            for game_name in self.evaluations_df['게임명']:
                self.game_listbox.insert(tk.END, game_name)

    def add_new_game(self):
        messagebox.showinfo("Info", "Add New Game button clicked.")

    def modify_game_evaluation(self):
        messagebox.showinfo("Info", "Modify Game Evaluation button clicked.")

    def show_statistics(self):
        messagebox.showinfo("Info", "Statistics button clicked.")

    def show_wish_list(self):
        messagebox.showinfo("Info", "Wish List button clicked.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()