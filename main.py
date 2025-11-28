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


# ============================================================================
# Date Utilities - Convert between display format (YYYY/MM/DD) and storage format
# ============================================================================
class DateFormatter:
    """Handles conversion between display format (2023/09/12) and storage format (20230912)"""

    @staticmethod
    def to_display_format(date_str):
        """Convert storage format (20230912 or 20230912.0) to display format (2023/09/12)"""
        if not date_str or str(date_str).strip() == "":
            return ""

        # Remove .0 if present (from float conversion)
        date_str = str(date_str).replace(".0", "").strip()

        # If already in display format, return as is
        if "/" in date_str:
            return date_str

        # Convert from compact format (20230912) to display format (2023/09/12)
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[0:4]}/{date_str[4:6]}/{date_str[6:8]}"

        return date_str

    @staticmethod
    def to_storage_format(date_str):
        """Convert display format (2023/09/12) to storage format (2023/09/12)"""
        if not date_str or str(date_str).strip() == "":
            return ""

        date_str = str(date_str).strip()

        # Already in storage format (we now store as YYYY/MM/DD)
        if "/" in date_str:
            return date_str

        # Convert old format (20230912) to new format (2023/09/12)
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[0:4]}/{date_str[4:6]}/{date_str[6:8]}"

        return date_str

    @staticmethod
    def parse_from_fields(year, month, day):
        """Create date string from separate fields, using 00 for blank fields"""
        y = year.strip() if year.strip() else "0000"
        m = month.strip() if month.strip() else "00"
        d = day.strip() if day.strip() else "00"

        # Pad month and day to 2 digits
        if m != "00" and len(m) == 1:
            m = f"0{m}"
        if d != "00" and len(d) == 1:
            d = f"0{d}"

        return f"{y}/{m}/{d}"

    @staticmethod
    def split_to_fields(date_str):
        """Split date string into year, month, day components"""
        if not date_str or str(date_str).strip() == "":
            return "", "", ""

        date_str = DateFormatter.to_display_format(str(date_str))

        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                y, m, d = parts
                # Convert 00 to empty string for display
                if m == "00":
                    m = ""
                if d == "00":
                    d = ""
                return y, m, d

        return date_str, "", ""


# ============================================================================
# Custom Date Widget - Separate fields for Year/Month/Day
# ============================================================================
class DateWidget(ttk.Frame):
    """Custom widget with separate entry fields for Year, Month, and Day"""

    def __init__(self, parent, initial_value="", **kwargs):
        super().__init__(parent, **kwargs)

        # Split initial value
        year, month, day = DateFormatter.split_to_fields(initial_value)

        # Year field
        ttk.Label(self, text="Year:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 2))
        self.year_var = tk.StringVar(value=year)
        self.year_entry = ttk.Entry(self, textvariable=self.year_var, width=6, font=("Arial", 11))
        self.year_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Month field
        ttk.Label(self, text="Month:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 2))
        self.month_var = tk.StringVar(value=month)
        self.month_entry = ttk.Entry(self, textvariable=self.month_var, width=4, font=("Arial", 11))
        self.month_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Day field
        ttk.Label(self, text="Day:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 2))
        self.day_var = tk.StringVar(value=day)
        self.day_entry = ttk.Entry(self, textvariable=self.day_var, width=4, font=("Arial", 11))
        self.day_entry.pack(side=tk.LEFT)

    def get_date(self):
        """Get the date string in storage format (YYYY/MM/DD)"""
        return DateFormatter.parse_from_fields(
            self.year_var.get(),
            self.month_var.get(),
            self.day_var.get()
        )

    def set_date(self, date_str):
        """Set the date from a string"""
        year, month, day = DateFormatter.split_to_fields(date_str)
        self.year_var.set(year)
        self.month_var.set(month)
        self.day_var.set(day)


# ============================================================================
# Main Application
# ============================================================================
class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Experience Manager")

        # Center window and set size
        window_width = 1500
        window_height = 900
        self._center_window(window_width, window_height)

        # Paths
        self.data_dir = "data"
        self.eval_path = os.path.join(self.data_dir, "game_evaluations.csv")
        self.wish_path = os.path.join(self.data_dir, "wish_list.csv")

        # Load Data
        self.evaluations_df = self.load_csv(self.eval_path)
        self.wishlist_df = self.load_csv(self.wish_path)

        # Convert old date formats to new format
        self._migrate_date_formats()

        # State for Sorting
        self.sort_descending = True

        # Common Status Options
        self.status_options = [
            "메인1", "메인2", "대기중", "잠시멈춤",
            "엔딩완료", "업적완료", "중도폐기", "치트모드"
        ]

        # UI Layout
        self._init_ui()

    def _center_window(self, width, height):
        """Center the window on the screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _migrate_date_formats(self):
        """Convert old date formats (20230912.0) to new format (2023/09/12)"""
        for col in ['시작', '마무리']:
            if col in self.evaluations_df.columns:
                self.evaluations_df[col] = self.evaluations_df[col].apply(DateFormatter.to_display_format)

    def load_csv(self, file_path):
        """Load CSV file with error handling"""
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, dtype=str)
                df = df.fillna("")
                return df
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {file_path}: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    def save_csv(self, df, file_path):
        """Save CSV file with error handling"""
        try:
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save {file_path}: {e}")

    # ========================================================================
    # UI Construction
    # ========================================================================
    def _init_ui(self):
        """Initialize the main UI layout"""
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left Menu Panel
        self.menu_frame = ttk.Frame(self.main_container, width=280, padding=20)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(
            self.menu_frame,
            text="GAME\nMANAGER",
            font=("Arial", 22, "bold")
        ).pack(pady=(0, 40))

        # Menu buttons with larger fonts
        btn_style = {"fill": tk.X, "pady": 12}
        ttk.Button(
            self.menu_frame,
            text="📂 List of Games",
            command=self.show_game_list
        ).pack(**btn_style)

        ttk.Button(
            self.menu_frame,
            text="🎁 Wish List",
            command=self.show_wish_list
        ).pack(**btn_style)

        ttk.Button(
            self.menu_frame,
            text="➕ Add Game",
            command=self.add_new_game_ui
        ).pack(**btn_style)

        ttk.Button(
            self.menu_frame,
            text="📊 Statistics",
            command=self.show_statistics
        ).pack(**btn_style)

        ttk.Separator(self.menu_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        ttk.Button(
            self.menu_frame,
            text="💾 Save All Changes",
            command=self.save_all_data
        ).pack(**btn_style)

        # Right Content Area
        self.content_frame = ttk.Frame(self.main_container, padding=20, relief="sunken")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.clear_content()
        ttk.Label(
            self.content_frame,
            text="Select an option from the left menu.",
            font=("Arial", 16)
        ).pack(pady=50)

    def clear_content(self):
        """Clear all widgets from content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def save_all_data(self):
        """Save all data to CSV files"""
        self.save_csv(self.evaluations_df, self.eval_path)
        self.save_csv(self.wishlist_df, self.wish_path)
        messagebox.showinfo("Saved", "All data saved successfully!")

    # ========================================================================
    # View: Statistics (Placeholder)
    # ========================================================================
    def show_statistics(self):
        """Show statistics view (placeholder for future functionality)"""
        self.clear_content()

        ttk.Label(
            self.content_frame,
            text="📊 Statistics",
            font=("Arial", 20, "bold")
        ).pack(anchor="nw", pady=(0, 20))

        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Placeholder content
        ttk.Label(
            info_frame,
            text="Statistics feature coming soon!",
            font=("Arial", 16)
        ).pack(pady=50)

        ttk.Label(
            info_frame,
            text="This area will display:\n\n" \
                 "• Total games played\n" \
                 "• Average scores by genre\n" \
                 "• Gaming time analysis\n" \
                 "• Completion rates\n" \
                 "• Monthly gaming trends",
            font=("Arial", 13),
            justify=tk.LEFT
        ).pack(pady=20)

    # ========================================================================
    # View: Game List
    # ========================================================================
    def show_game_list(self):
        """Display the list of all games"""
        self.clear_content()

        # Top bar with title and sort button
        top_frame = ttk.Frame(self.content_frame)
        top_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            top_frame,
            text="My Played Games",
            font=("Arial", 20, "bold")
        ).pack(side=tk.LEFT)

        sort_btn_text = "⬇️ Sort: Newest First" if self.sort_descending else "⬆️ Sort: Oldest First"
        ttk.Button(
            top_frame,
            text=sort_btn_text,
            command=self.toggle_sort
        ).pack(side=tk.RIGHT)

        # Scrollable canvas for game list
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.evaluations_df.empty:
            ttk.Label(
                scroll_frame,
                text="No games found.",
                font=("Arial", 14)
            ).pack()
            return

        # Column definitions with larger fonts
        cols = [
            ("Title", "게임명", 32),
            ("Genre", "장르", 18),
            ("Status", "분류", 14),
            ("Start", "시작", 14),
            ("Finish", "마무리", 14),
            ("Score", "총점", 10),
        ]

        # Header row with larger font
        h_frame = ttk.Frame(scroll_frame)
        h_frame.pack(fill=tk.X, pady=8)

        for display_name, csv_key, width in cols:
            lbl = ttk.Label(
                h_frame,
                text=display_name,
                width=width,
                anchor="center",
                font=("Courier New", 12, "bold")
            )
            lbl.pack(side=tk.LEFT, padx=2)

        # Data rows with larger fonts
        for index, row in self.evaluations_df.iterrows():
            row_frame = ttk.Frame(scroll_frame)
            row_frame.pack(fill=tk.X, pady=3)

            for display_name, csv_key, width in cols:
                value = str(row.get(csv_key, ""))

                # Format dates
                if csv_key in ['시작', '마무리']:
                    value = DateFormatter.to_display_format(value)

                # Format score to 1 decimal
                if csv_key == '총점':
                    try:
                        value = f"{float(value):.1f}"
                    except (ValueError, TypeError):
                        value = "0.0"

                lbl = ttk.Label(
                    row_frame,
                    text=value,
                    width=width,
                    anchor="center",
                    font=("Courier New", 11)
                )
                lbl.pack(side=tk.LEFT, padx=2)

            # Details button
            ttk.Button(
                row_frame,
                text="📝 Details",
                command=lambda idx=index: self.show_game_details(idx)
            ).pack(side=tk.LEFT, padx=5)

    def toggle_sort(self):
        """Toggle sort order for game list"""
        self.sort_descending = not self.sort_descending
        self.evaluations_df = self.evaluations_df.sort_values(
            by='시작',
            ascending=not self.sort_descending,
            na_position='last'
        )
        self.evaluations_df = self.evaluations_df.reset_index(drop=True)
        self.show_game_list()

    # ========================================================================
    # View: Game Details
    # ========================================================================
    def show_game_details(self, df_index):
        """Show detailed view for a specific game"""
        self.clear_content()
        row = self.evaluations_df.iloc[df_index]
        game_name = str(row.get('게임명', 'Unknown'))

        # Top bar
        top_bar = ttk.Frame(self.content_frame)
        top_bar.pack(fill=tk.X, pady=10)

        ttk.Button(
            top_bar,
            text="< Back",
            command=self.show_game_list
        ).pack(side=tk.LEFT)

        ttk.Label(
            top_bar,
            text=f"{game_name}",
            font=("Arial", 18, "bold")
        ).pack(side=tk.LEFT, padx=20)

        # Status Dropdown
        status_frame = ttk.Frame(top_bar)
        status_frame.pack(side=tk.RIGHT)
        ttk.Label(status_frame, text="Status: ", font=("Arial", 11)).pack(side=tk.LEFT)

        current_status = str(row.get('분류', ''))
        status_var = tk.StringVar(value=current_status)
        status_cb = ttk.Combobox(
            status_frame,
            textvariable=status_var,
            values=self.status_options,
            width=12,
            state="readonly",
            font=("Arial", 11)
        )
        status_cb.pack(side=tk.LEFT)

        def on_status_change(_):
            self.evaluations_df.at[df_index, '분류'] = status_var.get()
            messagebox.showinfo("Updated", f"Status changed to {status_var.get()}")

        status_cb.bind("<<ComboboxSelected>>", on_status_change)

        # Game Info Section
        genre_value = str(row.get('장르', ''))
        start_value = DateFormatter.to_display_format(str(row.get('시작', '')))
        finish_value = DateFormatter.to_display_format(str(row.get('마무리', '')))

        info_frame = ttk.LabelFrame(self.content_frame, text="Game Info", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Display current info
        info_labels = ttk.Frame(info_frame)
        info_labels.pack(fill=tk.X, pady=(5, 10))

        ttk.Label(
            info_labels,
            text=f"장르: {genre_value}",
            width=40,
            anchor="w",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(
            info_labels,
            text=f"시작: {start_value}",
            width=25,
            anchor="w",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(
            info_labels,
            text=f"마무리: {finish_value}",
            width=25,
            anchor="w",
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        # Date edit section with custom date widgets
        edit_frame = ttk.Frame(info_frame)
        edit_frame.pack(fill=tk.X, pady=(0, 10))

        # Start date widget
        start_frame = ttk.LabelFrame(edit_frame, text="Start Date", padding=5)
        start_frame.pack(side=tk.LEFT, padx=(0, 20))
        start_widget = DateWidget(start_frame, initial_value=start_value)
        start_widget.pack()

        # Finish date widget
        finish_frame = ttk.LabelFrame(edit_frame, text="Finish Date", padding=5)
        finish_frame.pack(side=tk.LEFT, padx=(0, 20))
        finish_widget = DateWidget(finish_frame, initial_value=finish_value)
        finish_widget.pack()

        def save_dates():
            new_start = start_widget.get_date()
            new_finish = finish_widget.get_date()

            self.evaluations_df.at[df_index, '시작'] = new_start
            self.evaluations_df.at[df_index, '마무리'] = new_finish

            messagebox.showinfo("Saved", "Dates updated successfully!")
            self.show_game_details(df_index)

        ttk.Button(
            edit_frame,
            text="💾 Save Dates",
            command=save_dates
        ).pack(side=tk.LEFT)

        # Split view: Scores and Logs
        split_frame = ttk.Frame(self.content_frame)
        split_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(split_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_panel = ttk.Frame(split_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Evaluation Scores Chart ---
        stats_header = ttk.Frame(left_panel)
        stats_header.pack(fill=tk.X)

        ttk.Label(
            stats_header,
            text="Evaluation Scores",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT)

        ttk.Button(
            stats_header,
            text="✏️ Edit Scores",
            command=lambda: self.open_evaluation_editor(df_index)
        ).pack(side=tk.RIGHT)

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
        ax.bar_label(bars, fmt='%.1f')

        canvas = FigureCanvasTkAgg(fig, master=left_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- Daily Logs ---
        log_header = ttk.Frame(right_panel)
        log_header.pack(fill=tk.X)

        ttk.Label(
            log_header,
            text="Daily Logs",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT)

        self.log_editable = False
        self.edit_log_btn = ttk.Button(
            log_header,
            text="✏️ Edit / Delete Logs",
            command=lambda: self.toggle_log_edit(game_name)
        )
        self.edit_log_btn.pack(side=tk.RIGHT)

        self.log_text = tk.Text(right_panel, height=20, width=40, font=("Arial", 11))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

        log_content = self.read_daily_log(game_name)
        self.log_text.insert(tk.END, log_content)
        self.log_text.config(state=tk.DISABLED)

        self.quick_log_frame = ttk.Frame(right_panel)
        self.quick_log_frame.pack(fill=tk.X, pady=5)

        self.quick_entry = ttk.Entry(self.quick_log_frame, font=("Arial", 11))
        self.quick_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            self.quick_log_frame,
            text="Add Log",
            command=lambda: self.add_quick_log(game_name)
        ).pack(side=tk.RIGHT)

    def toggle_log_edit(self, game_name):
        """Toggle between view and edit mode for logs"""
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
            messagebox.showinfo("Saved", "Log file updated successfully!")

    def add_quick_log(self, game_name):
        """Add a quick log entry"""
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
        """Open popup window to edit evaluation scores"""
        row = self.evaluations_df.iloc[df_index]
        game_name = row.get('게임명', 'Unknown')

        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Scores: {game_name}")
        popup.geometry("400x500")

        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - 400) // 2
        y = (popup.winfo_screenheight() - 500) // 2
        popup.geometry(f"+{x}+{y}")

        eval_cols = ['만족도', '몰입감', '게임성', '그래픽', '사운드', '완성도']
        vars = {}

        for i, col in enumerate(eval_cols):
            ttk.Label(popup, text=col, font=("Arial", 12)).pack(pady=(10, 0))

            current_val = row.get(col, 0)
            try:
                current_val = float(current_val)
            except:
                current_val = 0.0

            v = tk.DoubleVar(value=current_val)
            vars[col] = v

            scale_frame = ttk.Frame(popup)
            scale_frame.pack(fill=tk.X, padx=20)

            val_label = ttk.Label(scale_frame, text=f"{current_val:.1f}", font=("Arial", 11))
            val_label.pack(side=tk.RIGHT)

            def update_label(val, label=val_label):
                label.config(text=f"{float(val):.1f}")

            scale = ttk.Scale(
                scale_frame,
                from_=0,
                to=5,
                variable=v,
                orient=tk.HORIZONTAL,
                command=update_label
            )
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def save_scores():
            total = 0
            for col in eval_cols:
                val = round(vars[col].get(), 1)
                self.evaluations_df.at[df_index, col] = val
                total += val

            avg_score = round(total / 6, 1)
            self.evaluations_df.at[df_index, '총점'] = avg_score

            messagebox.showinfo("Saved", f"Scores updated! New Total: {avg_score}")
            popup.destroy()
            self.show_game_details(df_index)

        ttk.Button(
            popup,
            text="Save Scores",
            command=save_scores
        ).pack(pady=20)

    def get_log_filename(self, game_name):
        """Generate safe filename for game log"""
        safe_name = "".join(x for x in str(game_name) if x.isalnum() or x in " -_").strip()
        return os.path.join(self.data_dir, f"{safe_name}_log.txt")

    def read_daily_log(self, game_name):
        """Read log file for a game"""
        fname = self.get_log_filename(game_name)
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def save_daily_log_file(self, game_name, content):
        """Save log file for a game"""
        fname = self.get_log_filename(game_name)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)

    # ========================================================================
    # View: Wish List
    # ========================================================================
    def show_wish_list(self):
        """Display the wish list"""
        self.clear_content()

        ttk.Label(
            self.content_frame,
            text="Wish List",
            font=("Arial", 20, "bold")
        ).pack(anchor="nw", pady=(0, 15))

        # Scrollable canvas
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.wishlist_df.empty:
            ttk.Label(
                scroll_frame,
                text="Wishlist is empty.",
                font=("Arial", 14)
            ).pack()
            return

        # Header row with larger fonts
        header_frame = ttk.Frame(scroll_frame)
        header_frame.pack(fill=tk.X, pady=8)

        ttk.Label(
            header_frame,
            text="Title",
            width=30,
            anchor="w",
            font=("Courier New", 12, "bold")
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            header_frame,
            text="Price",
            width=15,
            anchor="w",
            font=("Courier New", 12, "bold")
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            header_frame,
            text="Sale %",
            width=12,
            anchor="w",
            font=("Courier New", 12, "bold")
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            header_frame,
            text="Actions",
            width=20,
            anchor="center",
            font=("Courier New", 12, "bold")
        ).pack(side=tk.LEFT, padx=5)

        # Data rows with larger fonts
        for index, row in self.wishlist_df.iterrows():
            row_frame = ttk.Frame(scroll_frame)
            row_frame.pack(fill=tk.X, pady=3)

            title = str(row.get('제목', 'Unknown'))
            price = str(row.get('가격현황', '-'))
            discount = str(row.get('할인률', '-'))

            ttk.Label(
                row_frame,
                text=title,
                width=30,
                anchor="w",
                font=("Courier New", 11)
            ).pack(side=tk.LEFT, padx=5)

            ttk.Label(
                row_frame,
                text=price,
                width=15,
                anchor="w",
                font=("Courier New", 11)
            ).pack(side=tk.LEFT, padx=5)

            ttk.Label(
                row_frame,
                text=discount,
                width=12,
                anchor="w",
                font=("Courier New", 11)
            ).pack(side=tk.LEFT, padx=5)

            ttk.Button(
                row_frame,
                text="✏️ Edit",
                command=lambda idx=index: self.edit_wishlist_item(idx)
            ).pack(side=tk.LEFT, padx=2)

            ttk.Button(
                row_frame,
                text="💰 Bought",
                command=lambda idx=index: self.move_wish_to_library(idx)
            ).pack(side=tk.LEFT, padx=2)

    def edit_wishlist_item(self, index):
        """Edit a wishlist item"""
        current_title = self.wishlist_df.at[index, '제목']

        new_price = simpledialog.askstring(
            "Update Price",
            f"Enter price for {current_title}:",
            initialvalue=self.wishlist_df.at[index, '가격현황']
        )

        if new_price is not None:
            new_discount = simpledialog.askstring(
                "Update Discount",
                f"Enter discount %:",
                initialvalue=self.wishlist_df.at[index, '할인률']
            )

            if new_discount is not None:
                self.wishlist_df.at[index, '가격현황'] = new_price
                self.wishlist_df.at[index, '할인률'] = new_discount
                self.show_wish_list()

    def move_wish_to_library(self, wish_index):
        """Move a wishlist item to the game library"""
        item = self.wishlist_df.iloc[wish_index]
        game_name = item.get('제목', 'Unknown')
        genre = item.get('장르', '')

        # Create new row with formatted date
        today_date = datetime.now().strftime("%Y/%m/%d")

        new_row = {
            '게임명': game_name,
            '장르': genre,
            '시작': today_date,
            '마무리': '',
            '분류': '대기중',
            '만족도': 0.0,
            '몰입감': 0.0,
            '게임성': 0.0,
            '그래픽': 0.0,
            '사운드': 0.0,
            '완성도': 0.0,
            '총점': 0.0
        }

        self.evaluations_df = pd.concat(
            [self.evaluations_df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        self.wishlist_df = self.wishlist_df.drop(wish_index).reset_index(drop=True)

        messagebox.showinfo("Success", f"Moved '{game_name}' to Game Library!")
        self.show_wish_list()

    # ========================================================================
    # Add New Game
    # ========================================================================
    def add_new_game_ui(self):
        """Add a new game to the library"""
        title = simpledialog.askstring("New Game", "Game Title:")
        if title:
            today_date = datetime.now().strftime("%Y/%m/%d")

            new_row = {
                '게임명': title,
                '장르': '',
                '분류': '대기중',
                '시작': today_date,
                '마무리': '',
                '만족도': 0.0,
                '몰입감': 0.0,
                '게임성': 0.0,
                '그래픽': 0.0,
                '사운드': 0.0,
                '완성도': 0.0,
                '총점': 0.0
            }

            self.evaluations_df = pd.concat(
                [self.evaluations_df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            messagebox.showinfo("Success", f"Added '{title}' to your library!")
            self.show_game_list()


# ============================================================================
# Application Entry Point
# ============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
