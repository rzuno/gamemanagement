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
        self.root.title("Game Experience Manager (Manual v3 - Fixed Sort & Decimals)")
        self.root.geometry("1400x850")

        # Paths
        self.data_dir = "data"
        self.eval_path = os.path.join(self.data_dir, "game_evaluations.csv")
        self.wish_path = os.path.join(self.data_dir, "wish_list.csv")

        # Load Data
        self.evaluations_df = self.load_csv(self.eval_path)
        self.wishlist_df = self.load_csv(self.wish_path)

        # State for Sorting
        self.sort_descending = True

        # Common Status Options
        self.status_options = [
            "메인1", "메인2", "대기중", "잠시멈춤", 
            "엔딩완료", "업적완료", "중도폐기", "치트모드"
        ]

        # UI Layout
        self._init_ui()

    def load_csv(self, file_path):
        if os.path.exists(file_path):
            try:
                # Read CSV as strings initially to preserve formatting
                df = pd.read_csv(file_path, dtype=str)
                df = df.fillna("")
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
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Left Menu
        self.menu_frame = ttk.Frame(self.main_container, width=250, padding=20)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(self.menu_frame, text="GAME\nMANAGER", font=("Arial", 20, "bold")).pack(pady=(0, 40))

        btn_style = {"fill": tk.X, "pady": 10}
        ttk.Button(self.menu_frame, text="📂 List of Games", command=self.show_game_list).pack(**btn_style)
        ttk.Button(self.menu_frame, text="🎁 Wish List", command=self.show_wish_list).pack(**btn_style)
        ttk.Button(self.menu_frame, text="➕ Add Game", command=self.add_new_game_ui).pack(**btn_style)
        ttk.Separator(self.menu_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        ttk.Button(self.menu_frame, text="💾 Save All Changes", command=self.save_all_data).pack(**btn_style)

        # 2. Right Content Area
        self.content_frame = ttk.Frame(self.main_container, padding=20, relief="sunken")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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
        
        top_frame = ttk.Frame(self.content_frame)
        top_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(top_frame, text="My Played Games", font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        sort_btn_text = "⬇️ Sort: Newest First" if self.sort_descending else "⬆️ Sort: Oldest First"
        ttk.Button(top_frame, text=sort_btn_text, command=self.toggle_sort).pack(side=tk.RIGHT)

        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.evaluations_df.empty:
            ttk.Label(scroll_frame, text="No games found.").pack()
            return

        h_frame = ttk.Frame(scroll_frame)
        h_frame.pack(fill=tk.X, pady=5)
        cols = [
            ("Title", "게임명", 25, "w"),
            ("Genre", "장르", 15, "w"),
            ("Status", "분류", 10, "center"),
            ("Start", "시작", 12, "center"),
            ("Finish", "마무리", 12, "center"),
            ("Score", "총점", 6, "center"),
        ]
        for name, _, w, anchor in cols:
            ttk.Label(h_frame, text=name, width=w, anchor=anchor, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=2)

        # Use index from iterrows() which will match position due to reset_index in sort
        for index, row in self.evaluations_df.iterrows():
            row_frame = ttk.Frame(scroll_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            def get_s(col):
                return str(row.get(col, ""))
            
            # Format Score to 1 decimal place if it's a number
            raw_score = row.get('총점', '0')
            try:
                display_score = f"{float(raw_score):.1f}"
            except:
                display_score = raw_score

            for _, col_key, w, anchor in cols:
                value = display_score if col_key == '총점' else get_s(col_key)
                ttk.Label(row_frame, text=value, width=w, anchor=anchor).pack(side=tk.LEFT, padx=2)
            
            # Pass the current loop index (which is reliable after reset_index)
            ttk.Button(row_frame, text="📝 Details", command=lambda idx=index: self.show_game_details(idx)).pack(side=tk.LEFT, padx=5)

    def toggle_sort(self):
        self.sort_descending = not self.sort_descending
        # 1. Sort
        self.evaluations_df = self.evaluations_df.sort_values(by='시작', ascending=not self.sort_descending, na_position='last')
        # 2. BUG FIX: Reset Index so row 0 is actually the first item in the dataframe!
        self.evaluations_df = self.evaluations_df.reset_index(drop=True)
        self.show_game_list()

    # --- View: Game Details ---
    def show_game_details(self, df_index):
        self.clear_content()
        # Because we reset_index, iloc[df_index] is guaranteed to be correct
        row = self.evaluations_df.iloc[df_index]
        game_name = str(row.get('게임명', 'Unknown'))
        
        top_bar = ttk.Frame(self.content_frame)
        top_bar.pack(fill=tk.X, pady=10)
        ttk.Button(top_bar, text="< Back", command=self.show_game_list).pack(side=tk.LEFT)
        ttk.Label(top_bar, text=f"{game_name}", font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=20)

        # Status Dropdown
        status_frame = ttk.Frame(top_bar)
        status_frame.pack(side=tk.RIGHT)
        ttk.Label(status_frame, text="Status: ").pack(side=tk.LEFT)
        
        current_status = str(row.get('분류', ''))
        status_var = tk.StringVar(value=current_status)
        status_cb = ttk.Combobox(status_frame, textvariable=status_var, values=self.status_options, width=12, state="readonly")
        status_cb.pack(side=tk.LEFT)
        
        def on_status_change(_):
            self.evaluations_df.at[df_index, '분류'] = status_var.get()
            messagebox.showinfo("Updated", f"Status changed to {status_var.get()}")

        status_cb.bind("<<ComboboxSelected>>", on_status_change)

        genre_value = str(row.get('장르', ''))
        start_value = str(row.get('시작', ''))
        finish_value = str(row.get('마무리', ''))

        info_frame = ttk.LabelFrame(self.content_frame, text="Game Info")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_labels = ttk.Frame(info_frame)
        info_labels.pack(fill=tk.X, padx=10, pady=(5, 10))
        ttk.Label(info_labels, text=f"장르: {genre_value}", width=40, anchor="w").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(info_labels, text=f"시작: {start_value}", width=20, anchor="w").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(info_labels, text=f"마무리: {finish_value}", width=20, anchor="w").pack(side=tk.LEFT)

        edit_frame = ttk.Frame(info_frame)
        edit_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(edit_frame, text="시작").pack(side=tk.LEFT)
        start_var = tk.StringVar(value=start_value)
        start_entry = ttk.Entry(edit_frame, textvariable=start_var, width=15)
        start_entry.pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(edit_frame, text="마무리").pack(side=tk.LEFT)
        finish_var = tk.StringVar(value=finish_value)
        finish_entry = ttk.Entry(edit_frame, textvariable=finish_var, width=15)
        finish_entry.pack(side=tk.LEFT, padx=(5, 20))

        def save_dates():
            self.evaluations_df.at[df_index, '시작'] = start_var.get().strip()
            self.evaluations_df.at[df_index, '마무리'] = finish_var.get().strip()
            messagebox.showinfo("Saved", "Dates updated.")
            self.show_game_details(df_index)

        ttk.Button(edit_frame, text="💾 Save Dates", command=save_dates).pack(side=tk.LEFT)

        split_frame = ttk.Frame(self.content_frame)
        split_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(split_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_panel = ttk.Frame(split_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Statistics ---
        stats_header = ttk.Frame(left_panel)
        stats_header.pack(fill=tk.X)
        ttk.Label(stats_header, text="Evaluation Scores", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(stats_header, text="✏️ Edit Scores", command=lambda: self.open_evaluation_editor(df_index)).pack(side=tk.RIGHT)

        eval_cols = ['만족도', '몰입감', '게임성', '그래픽', '사운드', '완성도']
        scores = []
        for col in eval_cols:
            val = row.get(col, 0)
            try:
                scores.append(float(val) if val and str(val).strip() != "" else 0.0)
            except:
                scores.append(0.0)

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(eval_cols, scores, color='#5c85d6')
        ax.set_ylim(0, 5.5)
        ax.bar_label(bars, fmt='%.1f') # Format chart labels to 1 decimal
        
        canvas = FigureCanvasTkAgg(fig, master=left_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- Logs ---
        log_header = ttk.Frame(right_panel)
        log_header.pack(fill=tk.X)
        ttk.Label(log_header, text="Daily Logs", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        self.log_editable = False
        self.edit_log_btn = ttk.Button(log_header, text="✏️ Edit / Delete Logs", command=lambda: self.toggle_log_edit(game_name))
        self.edit_log_btn.pack(side=tk.RIGHT)

        self.log_text = tk.Text(right_panel, height=20, width=40)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_content = self.read_daily_log(game_name)
        self.log_text.insert(tk.END, log_content)
        self.log_text.config(state=tk.DISABLED)

        self.quick_log_frame = ttk.Frame(right_panel)
        self.quick_log_frame.pack(fill=tk.X, pady=5)
        self.quick_entry = ttk.Entry(self.quick_log_frame)
        self.quick_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(self.quick_log_frame, text="Add Log", command=lambda: self.add_quick_log(game_name)).pack(side=tk.RIGHT)

    def toggle_log_edit(self, game_name):
        if not self.log_editable:
            self.log_editable = True
            self.log_text.config(state=tk.NORMAL, bg="#fffbe6")
            self.edit_log_btn.config(text="💾 Save Changes")
            self.quick_log_frame.pack_forget()
        else:
            new_content = self.log_text.get("1.0", tk.END)
            self.save_daily_log_file(game_name, new_content)
            self.log_editable = False
            self.log_text.config(state=tk.DISABLED, bg="white")
            self.edit_log_btn.config(text="✏️ Edit / Delete Logs")
            self.quick_log_frame.pack(fill=tk.X, pady=5)
            messagebox.showinfo("Saved", "Log file updated.")

    def add_quick_log(self, game_name):
        text = self.quick_entry.get().strip()
        if text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = f"[{timestamp}] {text}\n"
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, entry)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            fname = self.get_log_filename(game_name)
            with open(fname, "a", encoding="utf-8") as f:
                f.write(entry)
            self.quick_entry.delete(0, tk.END)

    def open_evaluation_editor(self, df_index):
        row = self.evaluations_df.iloc[df_index]
        game_name = row.get('게임명', 'Unknown')
        
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Scores: {game_name}")
        popup.geometry("350x450")

        eval_cols = ['만족도', '몰입감', '게임성', '그래픽', '사운드', '완성도']
        vars = {}

        for i, col in enumerate(eval_cols):
            ttk.Label(popup, text=col).pack(pady=(10, 0))
            current_val = row.get(col, 0)
            try:
                current_val = float(current_val)
            except:
                current_val = 0.0
            
            v = tk.DoubleVar(value=current_val)
            vars[col] = v
            
            scale_frame = ttk.Frame(popup)
            scale_frame.pack(fill=tk.X, padx=20)
            
            # ISSUE #3 RESOLUTION:
            # Label that updates dynamically to show "3.4", "3.5" etc.
            val_label = ttk.Label(scale_frame, text=f"{current_val:.1f}")
            val_label.pack(side=tk.RIGHT)
            
            # Update label on drag
            def update_label(val, label=val_label):
                label.config(text=f"{float(val):.1f}")

            scale = ttk.Scale(scale_frame, from_=0, to=5, variable=v, orient=tk.HORIZONTAL, command=update_label)
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def save_scores():
            total = 0
            for col in eval_cols:
                # Force 1 decimal precision on save
                val = round(vars[col].get(), 1)
                self.evaluations_df.at[df_index, col] = val
                total += val
            
            # Calc Average and format to 1 decimal
            avg_score = round(total / 6, 1)
            self.evaluations_df.at[df_index, '총점'] = avg_score
            
            messagebox.showinfo("Saved", f"Scores updated! New Total: {avg_score}")
            popup.destroy()
            self.show_game_details(df_index)

        ttk.Button(popup, text="Save Scores", command=save_scores).pack(pady=20)

    def get_log_filename(self, game_name):
        safe_name = "".join(x for x in str(game_name) if x.isalnum() or x in " -_").strip()
        return os.path.join(self.data_dir, f"{safe_name}_log.txt")

    def read_daily_log(self, game_name):
        fname = self.get_log_filename(game_name)
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def save_daily_log_file(self, game_name, content):
        fname = self.get_log_filename(game_name)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)

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

        for index, row in self.wishlist_df.iterrows():
            row_frame = ttk.Frame(scroll_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            title = str(row.get('제목', 'Unknown'))
            price = str(row.get('가격현황', '-'))
            discount = str(row.get('할인률', '-'))

            ttk.Label(row_frame, text=title, width=25, anchor="w").pack(side=tk.LEFT)
            ttk.Label(row_frame, text=price, width=12, anchor="w").pack(side=tk.LEFT)
            ttk.Label(row_frame, text=discount, width=10, anchor="w").pack(side=tk.LEFT)
            
            ttk.Button(row_frame, text="✏️ Edit", command=lambda idx=index: self.edit_wishlist_item(idx)).pack(side=tk.LEFT, padx=2)
            ttk.Button(row_frame, text="💰 Bought", command=lambda idx=index: self.move_wish_to_library(idx)).pack(side=tk.LEFT, padx=2)

    def edit_wishlist_item(self, index):
        current_title = self.wishlist_df.at[index, '제목']
        new_price = simpledialog.askstring("Update Price", f"Enter price for {current_title}:", initialvalue=self.wishlist_df.at[index, '가격현황'])
        if new_price is not None:
            new_discount = simpledialog.askstring("Update Discount", f"Enter discount %:", initialvalue=self.wishlist_df.at[index, '할인률'])
            if new_discount is not None:
                self.wishlist_df.at[index, '가격현황'] = new_price
                self.wishlist_df.at[index, '할인률'] = new_discount
                self.show_wish_list()

    def move_wish_to_library(self, wish_index):
        item = self.wishlist_df.iloc[wish_index]
        game_name = item.get('제목', 'Unknown')
        genre = item.get('장르', '')

        new_row = {
            '게임명': game_name,
            '장르': genre,
            '시작': datetime.now().strftime("%Y%m%d"),
            '분류': '대기중',
            '만족도': 0.0, '몰입감': 0.0, '게임성': 0.0, '그래픽': 0.0, '사운드': 0.0, '완성도': 0.0, '총점': 0.0
        }
        
        self.evaluations_df = pd.concat([self.evaluations_df, pd.DataFrame([new_row])], ignore_index=True)
        self.wishlist_df = self.wishlist_df.drop(wish_index).reset_index(drop=True)
        messagebox.showinfo("Success", f"Moved '{game_name}' to Game Library!")
        self.show_wish_list()

    def add_new_game_ui(self):
        title = simpledialog.askstring("New Game", "Game Title:")
        if title:
            new_row = {
                '게임명': title,
                '분류': '대기중',
                '만족도': 0.0, '몰입감': 0.0, '게임성': 0.0, '그래픽': 0.0, '사운드': 0.0, '완성도': 0.0, '총점': 0.0,
                '시작': datetime.now().strftime("%Y%m%d"), '마무리': ''
            }
            self.evaluations_df = pd.concat([self.evaluations_df, pd.DataFrame([new_row])], ignore_index=True)
            self.show_game_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
