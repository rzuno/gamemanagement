import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os

CSV_FILE = 'game_management.csv'

class GameManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Game Manager')
        self.geometry('300x100')

        add_btn = ttk.Button(self, text='Add Game', command=self.open_add_window)
        add_btn.pack(pady=20)

        # Ensure CSV exists
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'icon_path'])

    def open_add_window(self):
        AddGameWindow(self)

class AddGameWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Add / Edit Game')
        self.geometry('400x200')

        # Placeholder for icon
        self.icon_label = ttk.Label(self, text='[No Icon]', relief='solid', width=15, anchor='center')
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Button to load image later (stub)
        load_img_btn = ttk.Button(self, text='Load Icon', command=self.load_icon)
        load_img_btn.grid(row=2, column=0, padx=10)

        # Name entry
        ttk.Label(self, text='Game Name:').grid(row=0, column=1, sticky='w', padx=10)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(self, textvariable=self.name_var, width=30)
        name_entry.grid(row=1, column=1, padx=10)

        # OK and Remove buttons
        ok_btn = ttk.Button(self, text='OK', command=self.save_game)
        ok_btn.grid(row=3, column=1, sticky='e', padx=10, pady=10)
        remove_btn = ttk.Button(self, text='Remove', command=self.remove_game)
        remove_btn.grid(row=3, column=0, sticky='w', padx=10, pady=10)

    def load_icon(self):
        # Placeholder stub for loading icon later
        messagebox.showinfo('Info', 'Load icon functionality coming soon.')

    def save_game(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning('Warning', 'Please enter a game name.')
            return

        # Append to CSV
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([name, ''])  # icon path empty for now
        messagebox.showinfo('Saved', f'Game "{name}" added.')
        self.destroy()

    def remove_game(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning('Warning', 'Please enter a game name to remove.')
            return

        # Read existing entries
        updated = []
        removed = False
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if row[0] != name:
                    updated.append(row)
                else:
                    removed = True

        if not removed:
            messagebox.showinfo('Info', f'Game "{name}" not found.')
            return

        # Write back
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(updated)

        messagebox.showinfo('Removed', f'Game "{name}" removed.')
        self.destroy()

if __name__ == '__main__':
    app = GameManagerApp()
    app.mainloop()
