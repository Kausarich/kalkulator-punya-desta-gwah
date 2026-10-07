"""Shared desktop theme and scroll containers."""
import tkinter as tk
from tkinter import ttk

THEME_PAPER = "#F5F5DC"
THEME_WHITE = "#FFFFFF"
THEME_BLACK = "#000000"
THEME_TEAL = "#00C2C8"
THEME_MAGENTA = "#F000FF"
THEME_YELLOW = "#FFD700"


def label(parent, text="", **options):
    return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=THEME_BLACK, font=("Arial", 10), **options)


def button(parent, text, command, primary=False):
    return tk.Button(parent, text=text, command=command, bg=THEME_TEAL if primary else THEME_WHITE,
                     fg=THEME_BLACK, activebackground=THEME_BLACK, activeforeground=THEME_WHITE,
                     font=("Arial", 10, "bold"), bd=3, relief="solid", padx=8, pady=7,
                     highlightcolor=THEME_YELLOW, cursor="hand2")


class ScrollPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, bg=THEME_PAPER, highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.canvas, bg=THEME_WHITE, padx=14, pady=14)
        self.window = self.canvas.create_window(0, 0, window=self.body, anchor="nw")
        self.body.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.window, width=event.width))

    def wheel(self, event):
        self.canvas.yview_scroll(-int(event.delta / 120), "units")
