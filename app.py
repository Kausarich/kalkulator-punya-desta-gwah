"""Advanced Calculator GUI Application using Tkinter.

Features:
- Calculator (Basic & Scientific)
- Julian Day Converter
- Qibla Direction Finder with Visual Graphical Compass Dial
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# --- Core Mathematical Functions ---

MECCA_LAT = 21.422487
MECCA_LON = 39.826206


def calculate_julian_day(year: int, month: int, day: float, hour: int = 12, minute: int = 0, second: int = 0, utc_offset: float = 0.0) -> float:
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")
    if day < 1 or day > 31:
        raise ValueError("Day must be between 1 and 31.")

    time_in_utc_hours = hour + (minute / 60.0) + (second / 3600.0) - utc_offset
    fractional_day = day + (time_in_utc_hours / 24.0)

    y = year
    m = month
    if m <= 2:
        y -= 1
        m += 12

    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)

    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + fractional_day + b - 1524.5


def calculate_qibla(latitude: float, longitude: float) -> dict:
    if not (-90.0 <= latitude <= 90.0):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not (-180.0 <= longitude <= 180.0):
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    phi_u = math.radians(latitude)
    lambda_u = math.radians(longitude)
    phi_m = math.radians(MECCA_LAT)
    lambda_m = math.radians(MECCA_LON)

    delta_lambda = lambda_m - lambda_u

    y = math.sin(delta_lambda)
    x = math.cos(phi_u) * math.tan(phi_m) - math.sin(phi_u) * math.cos(delta_lambda)

    bearing_deg = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

    dphi = phi_m - phi_u
    haversine_a = math.sin(dphi / 2)**2 + math.cos(phi_u) * math.cos(phi_m) * math.sin(delta_lambda / 2)**2
    distance_km = 6371.0 * 2 * math.atan2(math.sqrt(haversine_a), math.sqrt(1 - haversine_a))

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    dir_idx = int((bearing_deg + 11.25) / 22.5) % 16

    return {
        "bearing_deg": round(bearing_deg, 4),
        "compass_direction": directions[dir_idx],
        "distance_km": round(distance_km, 2)
    }


# --- GUI Application ---

class AdvancedCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Desta Calculator & Qibla Finder")
        self.geometry("850x650")
        self.minsize(750, 580)
        self.configure(bg="#1e1e2e")

        # Custom Styling
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Configure Colors
        bg_dark = "#1e1e2e"
        card_bg = "#2a2a3c"
        accent_blue = "#89b4fa"
        fg_white = "#cdd6f4"
        
        self.style.configure(".", background=bg_dark, foreground=fg_white, font=("Segoe UI", 10))
        self.style.configure("TNotebook", background=bg_dark, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=card_bg, foreground=fg_white, padding=[15, 8], font=("Segoe UI", 11, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", accent_blue)], foreground=[("selected", "#11111b")])
        
        self.style.configure("TFrame", background=bg_dark)
        self.style.configure("Card.TFrame", background=card_bg, relief="flat")
        self.style.configure("TLabel", background=bg_dark, foreground=fg_white, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=bg_dark, foreground=accent_blue, font=("Segoe UI", 16, "bold"))
        self.style.configure("CardHeader.TLabel", background=card_bg, foreground=accent_blue, font=("Segoe UI", 13, "bold"))
        self.style.configure("CardLabel.TLabel", background=card_bg, foreground=fg_white, font=("Segoe UI", 10))
        self.style.configure("Result.TLabel", background=card_bg, foreground="#a6e3a1", font=("Segoe UI", 12, "bold"))

        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), background=card_bg, foreground=fg_white, borderwidth=1)
        self.style.map("TButton", background=[("active", accent_blue)], foreground=[("active", "#11111b")])

        self.style.configure("Primary.TButton", background=accent_blue, foreground="#11111b", font=("Segoe UI", 11, "bold"))
        self.style.map("Primary.TButton", background=[("active", "#b4befe")])

        # Header Title
        header_frame = ttk.Frame(self, padding=(20, 15, 20, 10))
        header_frame.pack(fill="x")
        title_lbl = ttk.Label(header_frame, text="Desta Riadi's Calculator", style="Header.TLabel")
        title_lbl.pack(side="left")
        subtitle_lbl = ttk.Label(header_frame, text=" Count Arithmetic • Julian Day • Qibla Finder", font=("Segoe UI", 10, "italic"), foreground="#a6adc8")
        subtitle_lbl.pack(side="right")

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Build Tabs
        self.tab_calc = ttk.Frame(self.notebook)
        self.tab_julian = ttk.Frame(self.notebook)
        self.tab_qibla = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_calc, text=" 🧮 Calculator ")
        self.notebook.add(self.tab_julian, text=" 📅 Julian Day ")
        self.notebook.add(self.tab_qibla, text=" 🧭 Qibla Finder ")

        self._init_calculator_tab()
        self._init_julian_tab()
        self._init_qibla_tab()

    # --- TAB 1: Calculator ---
    def _init_calculator_tab(self):
        container = ttk.Frame(self.tab_calc, padding=20)
        container.pack(fill="both", expand=True)

        card = ttk.Frame(container, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)

        # Display Screen
        self.calc_expr_var = tk.StringVar(value="")
        self.calc_result_var = tk.StringVar(value="0")

        expr_lbl = tk.Label(card, textvariable=self.calc_expr_var, bg="#1e1e2e", fg="#a6adc8", font=("Segoe UI", 12), anchor="e", padx=10)
        expr_lbl.pack(fill="x", pady=(0, 2))

        display_lbl = tk.Label(card, textvariable=self.calc_result_var, bg="#1e1e2e", fg="#89b4fa", font=("Consolas", 26, "bold"), anchor="e", padx=10)
        display_lbl.pack(fill="x", pady=(0, 15))

        # Button Grid
        btn_frame = tk.Frame(card, bg="#2a2a3c")
        btn_frame.pack(fill="both", expand=True)

        buttons = [
            [("C", self._calc_clear_entry), ("AC", self._calc_clear_all), ("(", lambda: self._calc_append("(")), (")", lambda: self._calc_append(")")), ("÷", lambda: self._calc_append("/"))],
            [("7", lambda: self._calc_append("7")), ("8", lambda: self._calc_append("8")), ("9", lambda: self._calc_append("9")), ("^", lambda: self._calc_append("**")), ("×", lambda: self._calc_append("*"))],
            [("4", lambda: self._calc_append("4")), ("5", lambda: self._calc_append("5")), ("6", lambda: self._calc_append("6")), ("√", self._calc_sqrt), ("-", lambda: self._calc_append("-"))],
            [("1", lambda: self._calc_append("1")), ("2", lambda: self._calc_append("2")), ("3", lambda: self._calc_append("3")), ("π", lambda: self._calc_append(str(math.pi))), ("+", lambda: self._calc_append("+"))],
            [("0", lambda: self._calc_append("0")), (".", lambda: self._calc_append(".")), ("±", self._calc_negate), ("e", lambda: self._calc_append(str(math.e))), ("=", self._calc_evaluate)],
        ]

        for r, row in enumerate(buttons):
            btn_frame.rowconfigure(r, weight=1)
            for c, (text, cmd) in enumerate(row):
                btn_frame.columnconfigure(c, weight=1)
                bg_col = "#313244"
                fg_col = "#cdd6f4"
                if text == "=":
                    bg_col = "#89b4fa"
                    fg_col = "#11111b"
                elif text in ("C", "AC"):
                    bg_col = "#f38ba8"
                    fg_col = "#11111b"
                elif text in ("÷", "×", "-", "+", "^", "√", "π", "e", "±"):
                    bg_col = "#45475a"
                    fg_col = "#a6e3a1"

                b = tk.Button(btn_frame, text=text, command=cmd, bg=bg_col, fg=fg_col, activebackground="#89b4fa", activeforeground="#11111b",
                              font=("Segoe UI", 12, "bold"), bd=0, relief="flat")
                b.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)

    def _calc_append(self, char):
        curr = self.calc_expr_var.get()
        self.calc_expr_var.set(curr + char)

    def _calc_clear_all(self):
        self.calc_expr_var.set("")
        self.calc_result_var.set("0")

    def _calc_clear_entry(self):
        curr = self.calc_expr_var.get()
        self.calc_expr_var.set(curr[:-1])

    def _calc_negate(self):
        curr = self.calc_expr_var.get()
        if curr.startswith("-"):
            self.calc_expr_var.set(curr[1:])
        else:
            self.calc_expr_var.set("-" + curr)

    def _calc_sqrt(self):
        try:
            val = float(self.calc_result_var.get())
            if val < 0:
                raise ValueError("Invalid domain")
            res = math.sqrt(val)
            self.calc_result_var.set(str(res))
            self.calc_expr_var.set(f"√({val})")
        except Exception:
            try:
                expr = self.calc_expr_var.get()
                val = eval(expr, {"__builtins__": None, "math": math})
                res = math.sqrt(val)
                self.calc_result_var.set(str(res))
                self.calc_expr_var.set(f"√({expr})")
            except Exception as e:
                self.calc_result_var.set("Error")

    def _calc_evaluate(self):
        try:
            expr = self.calc_expr_var.get()
            if not expr:
                return
            # Safe evaluation with math module namespace
            allowed_names = {"math": math, "pi": math.pi, "e": math.e, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan}
            result = eval(expr, {"__builtins__": None}, allowed_names)
            
            if isinstance(result, float):
                result = round(result, 8)
                if result.is_integer():
                    result = int(result)

            self.calc_result_var.set(str(result))
        except Exception as err:
            self.calc_result_var.set("Error")

    # --- TAB 2: Julian Day ---
    def _init_julian_tab(self):
        container = ttk.Frame(self.tab_julian, padding=20)
        container.pack(fill="both", expand=True)

        card = ttk.Frame(container, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="📅 Julian Day Calculator", style="CardHeader.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))

        # Inputs
        ttk.Label(card, text="Year (YYYY):", style="CardLabel.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.jd_year_ent = ttk.Entry(card, width=12, font=("Segoe UI", 11))
        self.jd_year_ent.grid(row=1, column=1, sticky="w", pady=5, padx=5)

        ttk.Label(card, text="Month (1-12):", style="CardLabel.TLabel").grid(row=1, column=2, sticky="w", pady=5, padx=(15, 0))
        self.jd_month_ent = ttk.Entry(card, width=12, font=("Segoe UI", 11))
        self.jd_month_ent.grid(row=1, column=3, sticky="w", pady=5, padx=5)

        ttk.Label(card, text="Day (1-31):", style="CardLabel.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        self.jd_day_ent = ttk.Entry(card, width=12, font=("Segoe UI", 11))
        self.jd_day_ent.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        ttk.Label(card, text="Time (HH:MM:SS):", style="CardLabel.TLabel").grid(row=2, column=2, sticky="w", pady=5, padx=(15, 0))
        self.jd_time_ent = ttk.Entry(card, width=12, font=("Segoe UI", 11))
        self.jd_time_ent.grid(row=2, column=3, sticky="w", pady=5, padx=5)

        ttk.Label(card, text="UTC Offset (Hours):", style="CardLabel.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        self.jd_utc_ent = ttk.Entry(card, width=12, font=("Segoe UI", 11))
        self.jd_utc_ent.grid(row=3, column=1, sticky="w", pady=5, padx=5)

        # Buttons
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=15)

        calc_btn = ttk.Button(btn_frame, text="Calculate Julian Day", style="Primary.TButton", command=self._compute_julian_day)
        calc_btn.pack(side="left", padx=(0, 10))

        now_btn = ttk.Button(btn_frame, text="Set Current Date/Time", command=self._set_current_date_time)
        now_btn.pack(side="left")

        # Results Display Card
        res_card = tk.Frame(card, bg="#1e1e2e", bd=1, relief="solid", padx=15, pady=15)
        res_card.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=10)

        self.jd_val_lbl = tk.Label(res_card, text="Julian Day (JD): --", bg="#1e1e2e", fg="#a6e3a1", font=("Segoe UI", 13, "bold"), anchor="w")
        self.jd_val_lbl.pack(fill="x", pady=2)

        self.mjd_val_lbl = tk.Label(res_card, text="Modified Julian Day (MJD): --", bg="#1e1e2e", fg="#89b4fa", font=("Segoe UI", 12), anchor="w")
        self.mjd_val_lbl.pack(fill="x", pady=2)

        self.jd_info_lbl = tk.Label(res_card, text="Input Date: --", bg="#1e1e2e", fg="#a6adc8", font=("Segoe UI", 10), anchor="w")
        self.jd_info_lbl.pack(fill="x", pady=2)

        self._set_current_date_time()
        self._compute_julian_day()

    def _set_current_date_time(self):
        now = datetime.now()
        self.jd_year_ent.delete(0, tk.END)
        self.jd_year_ent.insert(0, str(now.year))

        self.jd_month_ent.delete(0, tk.END)
        self.jd_month_ent.insert(0, str(now.month))

        self.jd_day_ent.delete(0, tk.END)
        self.jd_day_ent.insert(0, str(now.day))

        self.jd_time_ent.delete(0, tk.END)
        self.jd_time_ent.insert(0, now.strftime("%H:%M:%S"))

        self.jd_utc_ent.delete(0, tk.END)
        self.jd_utc_ent.insert(0, "7.0")  # Default WIB (+7)

    def _compute_julian_day(self):
        try:
            yr = int(self.jd_year_ent.get())
            mo = int(self.jd_month_ent.get())
            dy = float(self.jd_day_ent.get())
            t_str = self.jd_time_ent.get().strip()
            
            hr, mn, sc = 12, 0, 0
            if t_str:
                t_parts = [int(p) for p in t_str.split(":")]
                hr = t_parts[0]
                mn = t_parts[1] if len(t_parts) > 1 else 0
                sc = t_parts[2] if len(t_parts) > 2 else 0

            utc = float(self.jd_utc_ent.get() or "0")

            jd = calculate_julian_day(yr, mo, dy, hr, mn, sc, utc)
            mjd = jd - 2400000.5

            self.jd_val_lbl.config(text=f"Julian Day (JD):  {jd:.6f}")
            self.mjd_val_lbl.config(text=f"Modified Julian Day (MJD):  {mjd:.6f}")
            self.jd_info_lbl.config(text=f"Gregorian Date: {yr}-{mo:02d}-{int(dy):02d} {hr:02d}:{mn:02d}:{sc:02d} (UTC{'+' if utc>=0 else ''}{utc})")

        except Exception as err:
            messagebox.showerror("Invalid Input", f"Error computing Julian Day: {err}")

    # --- TAB 3: Qibla Finder ---
    def _init_qibla_tab(self):
        container = ttk.Frame(self.tab_qibla, padding=20)
        container.pack(fill="both", expand=True)

        left_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        right_card.pack(side="right", fill="both", expand=True)

        # Left Controls
        ttk.Label(left_card, text="🧭 Qibla (Kiblat) Location", style="CardHeader.TLabel").pack(anchor="w", pady=(0, 10))

        # City Presets
        ttk.Label(left_card, text="Quick Select City:", style="CardLabel.TLabel").pack(anchor="w", pady=2)
        
        self.city_presets = {
            "Jakarta, Indonesia": (-6.2088, 106.8456),
            "Surabaya, Indonesia": (-7.2575, 112.7521),
            "Bandung, Indonesia": (-6.9175, 107.6191),
            "Medan, Indonesia": (3.5952, 98.6722),
            "Makassar, Indonesia": (-5.1477, 119.4327),
            "Kuala Lumpur, Malaysia": (3.1390, 101.6869),
            "Riyadh, Saudi Arabia": (24.7136, 46.6753),
            "London, United Kingdom": (51.5074, -0.1278),
            "New York, USA": (40.7128, -74.0060),
            "Tokyo, Japan": (35.6762, 139.6503),
            "Sydney, Australia": (-33.8688, 151.2093),
        }

        self.city_var = tk.StringVar(value="Jakarta, Indonesia")
        city_cb = ttk.Combobox(left_card, textvariable=self.city_var, values=list(self.city_presets.keys()), state="readonly", font=("Segoe UI", 10))
        city_cb.pack(fill="x", pady=(0, 15))
        city_cb.bind("<<ComboboxSelected>>", self._on_city_selected)

        # Manual Lat/Lon
        ttk.Label(left_card, text="Latitude (°N / °S):", style="CardLabel.TLabel").pack(anchor="w", pady=2)
        self.lat_ent = ttk.Entry(left_card, font=("Segoe UI", 11))
        self.lat_ent.pack(fill="x", pady=(0, 10))

        ttk.Label(left_card, text="Longitude (°E / °W):", style="CardLabel.TLabel").pack(anchor="w", pady=2)
        self.lon_ent = ttk.Entry(left_card, font=("Segoe UI", 11))
        self.lon_ent.pack(fill="x", pady=(0, 15))

        calc_qibla_btn = ttk.Button(left_card, text="Calculate Qibla Bearing", style="Primary.TButton", command=self._compute_qibla)
        calc_qibla_btn.pack(fill="x", pady=(0, 15))

        # Output Text Box
        self.qibla_res_box = tk.Frame(left_card, bg="#1e1e2e", bd=1, relief="solid", padx=12, pady=12)
        self.qibla_res_box.pack(fill="both", expand=True)

        self.q_bearing_lbl = tk.Label(self.qibla_res_box, text="Bearing: --°", bg="#1e1e2e", fg="#a6e3a1", font=("Segoe UI", 13, "bold"), anchor="w")
        self.q_bearing_lbl.pack(fill="x", pady=2)

        self.q_dir_lbl = tk.Label(self.qibla_res_box, text="Direction: --", bg="#1e1e2e", fg="#89b4fa", font=("Segoe UI", 11), anchor="w")
        self.q_dir_lbl.pack(fill="x", pady=2)

        self.q_dist_lbl = tk.Label(self.qibla_res_box, text="Distance to Kaaba: -- km", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10), anchor="w")
        self.q_dist_lbl.pack(fill="x", pady=2)

        # Right Graphical Compass Canvas
        ttk.Label(right_card, text="🧭 Interactive Compass Dial", style="CardHeader.TLabel").pack(anchor="w", pady=(0, 10))

        self.compass_canvas = tk.Canvas(right_card, bg="#1e1e2e", highlightthickness=0)
        self.compass_canvas.pack(fill="both", expand=True)

        self._on_city_selected(None)

    def _on_city_selected(self, event):
        city = self.city_var.get()
        if city in self.city_presets:
            lat, lon = self.city_presets[city]
            self.lat_ent.delete(0, tk.END)
            self.lat_ent.insert(0, str(lat))
            self.lon_ent.delete(0, tk.END)
            self.lon_ent.insert(0, str(lon))
            self._compute_qibla()

    def _compute_qibla(self):
        try:
            lat = float(self.lat_ent.get())
            lon = float(self.lon_ent.get())

            res = calculate_qibla(lat, lon)
            bearing = res["bearing_deg"]
            direction = res["compass_direction"]
            dist = res["distance_km"]

            self.q_bearing_lbl.config(text=f"Bearing: {bearing}°")
            self.q_dir_lbl.config(text=f"Direction: {direction} (from North)")
            self.q_dist_lbl.config(text=f"Distance to Kaaba: {dist:,.2f} km")

            self._draw_compass(bearing)

        except Exception as err:
            messagebox.showerror("Invalid Input", f"Error computing Qibla direction: {err}")

    def _draw_compass(self, bearing_deg: float):
        cv = self.compass_canvas
        cv.delete("all")

        w = cv.winfo_width() or 300
        h = cv.winfo_height() or 300
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 25

        if radius < 40:
            radius = 100

        # Draw Outer Ring
        cv.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="#89b4fa", width=3, fill="#11111b")
        cv.create_oval(cx - radius + 8, cy - radius + 8, cx + radius - 8, cy + radius - 8, outline="#45475a", width=1)

        # Cardinal Points
        cardinals = [("N", 0, "#f38ba8"), ("E", 90, "#cdd6f4"), ("S", 180, "#cdd6f4"), ("W", 270, "#cdd6f4")]
        for label, deg, color in cardinals:
            rad = math.radians(deg - 90)
            lx = cx + (radius - 18) * math.cos(rad)
            ly = cy + (radius - 18) * math.sin(rad)
            cv.create_text(lx, ly, text=label, fill=color, font=("Segoe UI", 11, "bold"))

        # Tick marks
        for deg in range(0, 360, 15):
            rad = math.radians(deg - 90)
            x1 = cx + (radius - 6) * math.cos(rad)
            y1 = cy + (radius - 6) * math.sin(rad)
            x2 = cx + radius * math.cos(rad)
            y2 = cy + radius * math.sin(rad)
            cv.create_line(x1, y1, x2, y2, fill="#585b70", width=1)

        # Draw North Needle (Red arrow pointing up)
        cv.create_line(cx, cy, cx, cy - (radius - 35), fill="#f38ba8", width=3, arrow=tk.LAST, arrowshape=(10, 12, 5))

        # Draw Qibla Vector Needle (Emerald Green / Gold)
        q_rad = math.radians(bearing_deg - 90)
        qx = cx + (radius - 30) * math.cos(q_rad)
        qy = cy + (radius - 30) * math.sin(q_rad)

        cv.create_line(cx, cy, qx, qy, fill="#a6e3a1", width=4, arrow=tk.LAST, arrowshape=(12, 15, 6))

        # Kaaba icon marker near the tip
        kx = cx + (radius - 12) * math.cos(q_rad)
        ky = cy + (radius - 12) * math.sin(q_rad)
        cv.create_rectangle(kx - 6, ky - 6, kx + 6, ky + 6, fill="#f9e2af", outline="#11111b", width=1)
        cv.create_text(kx, ky, text="🕋", font=("Segoe UI Emoji", 10))

        # Center Dot
        cv.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#89b4fa", outline="")

        # Text Overlay
        cv.create_text(cx, cy + radius + 12, text=f"Qibla: {bearing_deg:.1f}°", fill="#a6e3a1", font=("Segoe UI", 11, "bold"))


if __name__ == "__main__":
    app = AdvancedCalculatorApp()
    app.mainloop()
