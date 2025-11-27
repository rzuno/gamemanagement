import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import os
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import platform

# Set Matplotlib backend to TkAgg
matplotlib.use("TkAgg")

# --- Font Configuration for Korean Support in Matplotlib ---
system_name = platform.system()
if system_name == "Windows":
    plt_font_family = "Malgun Gothic"
elif system_name == "Darwin":  # Mac
    plt_font_family = "AppleGothic"
else:
    plt_font_family = "NanumGothic"
matplotlib.rc("font", family=plt_font_family)
matplotlib.rc("axes", unicode_minus=False)

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Experience Manager (Vibe Edition)")
        self.root.geometry("1400x800")

        # Paths
        self.data_dir = "data"
        self.eval_path = os.path.join(self.data_dir, "game_evaluations.csv")
        self.wish_path = os.path.join(self.data_dir, "wish_list.csv")

        # Load Data
        self.evaluations_df = self.load_csv(self.eval_path)
        self.wishlist_df = self.load_csv(self.wish_path)

        # UI Layout
        self._init_ui()

    def load_csv(self, file_path):
        if os.path.exists(file_path):
            try:
                # Read CSV, ensuring numbers are treated as such where possible
                df = pd.read_csv(file_path)
                return df
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {file_path}: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    def save_csv(self, df, file_path):
        try:
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save {file_path}: {e}")

    # --- UI Construction ---
    def _init_ui(self):
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Left Menu (The "Center" Buttons when starting)
        self.menu_frame = ttk.Frame(self.main_container, width=250, padding=20)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Title in Menu
        ttk.Label(self.menu_frame, text="GAME\nMANAGER", font=("Arial", 20, "bold")).pack(pady=(0, 40))

        # Navigation Buttons
        btn_style = {"fill": tk.X, "pady": 10}
        ttk.Button(self.menu_frame, text="📂 List of Games", command=self.show_game_list).pack(**btn_style)
        ttk.Button(self.menu_frame, text="🎁 Wish List", command=self.show_wish_list).pack(**btn_style)
        ttk.Button(self.menu_frame, text="➕ Add Game", command=self.add_new_game_ui).pack(**btn_style)
        ttk.Separator(self.menu_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        ttk.Button(self.menu_frame, text="💾 Save All Changes", command=self.save_all_data).pack(**btn_style)

        # 2. Right Content Area
        self.content_frame = ttk.Frame(self.main_container, padding=20, relief="sunken")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Start with a welcome message
        self.clear_content()
        ttk.Label(self.content_frame, text="Select an option from the left menu.", font=("Arial", 14)).pack(pady=50)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def save_all_data(self):
        self.save_csv(self.evaluations_df, self.eval_path)
        self.save_csv(self.wishlist_df, self.wish_path)
        messagebox.showinfo("Saved", "All data saved to CSV.")

    # --- View: Game List ---
    def show_game_list(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="My Played Games", font=("Arial", 18, "bold")).pack(anchor="nw", pady=(0, 15))

        # Scrollable Frame
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.evaluations_df.empty:
            ttk.Label(scroll_frame, text="No games found in database.").pack()
            return

        # Headers
        header_frame = ttk.Frame(scroll_frame)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="Title", width=30, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Genre", width=20, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Total Score", width=10, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # Rows
        for index, row in self.evaluations_df.iterrows():
            row_frame = ttk.Frame(scroll_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            game_name = str(row.get('게임명', 'Unknown'))
            genre = str(row.get('장르', '-'))
            score = str(row.get('총점', '-'))

            ttk.Label(row_frame, text=game_name, width=30, anchor="w").pack(side=tk.LEFT, padx=5)
            ttk.Label(row_frame, text=genre, width=20, anchor="w").pack(side=tk.LEFT, padx=5)
            ttk.Label(row_frame, text=score, width=10, anchor="w").pack(side=tk.LEFT, padx=5)

            # View Stats Button
            btn = ttk.Button(row_frame, text="📊 View Stats", command=lambda idx=index: self.show_game_details(idx))
            btn.pack(side=tk.LEFT, padx=5)

    # --- View: Game Details (Stats + Logs) ---
    def show_game_details(self, df_index):
        self.clear_content()
        row = self.evaluations_df.iloc[df_index]
        game_name = str(row.get('게임명', 'Unknown'))

        # Header with Back button
        top_bar = ttk.Frame(self.content_frame)
        top_bar.pack(fill=tk.X, pady=10)
        ttk.Button(top_bar, text="< Back", command=self.show_game_list).pack(side=tk.LEFT)
        ttk.Label(top_bar, text=f"Details: {game_name}", font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=20)

        # Split Layout: Left (Chart) | Right (Logs)
        split_frame = ttk.Frame(self.content_frame)
        split_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(split_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_panel = ttk.Frame(split_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- 1. Statistics Chart (Left) ---
        ttk.Label(left_panel, text="Evaluation Scores", font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Extract scores
        eval_cols = ['만족도', '몰입감', '게임성', '그래픽', '사운드', '완성도']
        scores = []
        for col in eval_cols:
            val = row.get(col, 0)
            try:
                scores.append(float(val) if pd.notna(val) else 0)
            except:
                scores.append(0)

        # Draw Chart
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(eval_cols, scores, color='#5c85d6')
        ax.set_ylim(0, 5.5) # Assuming 5 is max, giving a bit of headroom
        ax.set_ylabel("Score (0-5)")
        ax.tick_params(axis='x', rotation=45)
        
        canvas = FigureCanvasTkAgg(fig, master=left_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- 2. Daily Logs (Right) ---
        ttk.Label(right_panel, text="Daily Logs / Remarks", font=("Arial", 12, "bold")).pack(anchor="w")
        
        log_text = tk.Text(right_panel, height=20, width=40)
        log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Load existing log
        log_content = self.read_daily_log(game_name)
        log_text.insert(tk.END, log_content)
        log_text.config(state=tk.DISABLED) # Read-only initially

        # Input for new log
        input_frame = ttk.Frame(right_panel)
        input_frame.pack(fill=tk.X, pady=5)
        entry = ttk.Entry(input_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def add_log():
            text = entry.get().strip()
            if text:
                self.append_daily_log(game_name, text)
                # Refresh UI
                timestamp = datetime.now().strftime("%Y-%m-%d")
                log_text.config(state=tk.NORMAL)
                log_text.insert(tk.END, f"\n[{timestamp}] {text}")
                log_text.config(state=tk.DISABLED)
                log_text.see(tk.END)
                entry.delete(0, tk.END)

        ttk.Button(input_frame, text="Add Log", command=add_log).pack(side=tk.RIGHT)

    # --- Daily Log Logic ---
    def get_log_filename(self, game_name):
        # Sanitize filename
        safe_name = "".join(x for x in str(game_name) if x.isalnum() or x in " -_").strip()
        return os.path.join(self.data_dir, f"{safe_name}_log.txt")

    def read_daily_log(self, game_name):
        fname = self.get_log_filename(game_name)
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def append_daily_log(self, game_name, text):
        fname = self.get_log_filename(game_name)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(fname, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")

    # --- View: Wish List ---
    def show_wish_list(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Wish List", font=("Arial", 18, "bold")).pack(anchor="nw", pady=(0, 15))

        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.wishlist_df.empty:
            ttk.Label(scroll_frame, text="Wishlist is empty.").pack()
            return

        # Headers
        header_frame = ttk.Frame(scroll_frame)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="Title", width=25, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Price Info", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Status", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Rows
        for index, row in self.wishlist_df.iterrows():
            row_frame = ttk.Frame(scroll_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            title = str(row.get('제목', 'Unknown'))
            price = str(row.get('가격현황', '-'))
            status = str(row.get('구매여부', '-'))

            ttk.Label(row_frame, text=title, width=25, anchor="w").pack(side=tk.LEFT)
            ttk.Label(row_frame, text=price, width=15, anchor="w").pack(side=tk.LEFT)
            ttk.Label(row_frame, text=status, width=15, anchor="w").pack(side=tk.LEFT)

            # Buy Button
            btn = ttk.Button(row_frame, text="💰 Bought It!", command=lambda idx=index: self.move_wish_to_library(idx))
            btn.pack(side=tk.LEFT, padx=5)

    def move_wish_to_library(self, wish_index):
        # 1. Get data from wishlist
        item = self.wishlist_df.iloc[wish_index]
        game_name = item.get('제목', 'Unknown')
        genre = item.get('장르', '')

        # 2. Add to Evaluations DF
        # We need to map Wishlist columns to Evaluation columns or set defaults
        new_row = {
            '게임명': game_name,
            '장르': genre,
            '시작': datetime.now().strftime("%Y%m%d"), # Today's date
            '분류': '대기중',
            '만족도': 0, '몰입감': 0, '게임성': 0, '그래픽': 0, '사운드': 0, '완성도': 0, '총점': 0
        }
        
        # Append using concat (pandas 2.0+ preference)
        self.evaluations_df = pd.concat([self.evaluations_df, pd.DataFrame([new_row])], ignore_index=True)

        # 3. Remove from Wishlist
        self.wishlist_df = self.wishlist_df.drop(wish_index).reset_index(drop=True)

        # 4. Save and Refresh
        self.save_all_data()
        messagebox.showinfo("Success", f"Moved '{game_name}' to Game Library!")
        self.show_wish_list()

    # --- Add New Game ---
    def add_new_game_ui(self):
        # Simple dialog implementation for now
        title = simpledialog.askstring("New Game", "Game Title:")
        if title:
            new_row = {
                '게임명': title,
                '분류': '대기중',
                '만족도': 0, '몰입감': 0, '게임성': 0, '그래픽': 0, '사운드': 0, '완성도': 0, '총점': 0
            }
            self.evaluations_df = pd.concat([self.evaluations_df, pd.DataFrame([new_row])], ignore_index=True)
            self.save_all_data()
            self.show_game_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()