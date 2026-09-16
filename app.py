"""Advanced Calculator GUI Application - Black & White Brutalism Theme (No Emojis).

Features:
- Calculator (Basic & Scientific)
- Julian Day Converter
- Qibla Direction Finder with Graphical Compass Dial
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

        self.title("DESTA CALCULATOR & QIBLA FINDER")
        self.geometry("850x650")
        self.minsize(750, 580)
        self.configure(bg="#ffffff")

        # Custom Styling - Black & White Brutalism
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        bg_col = "#ffffff"
        fg_col = "#000000"
        card_bg = "#ffffff"

        self.style.configure(".", background=bg_col, foreground=fg_col, font=("Consolas", 10, "bold"))
        self.style.configure("TNotebook", background=bg_col, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=bg_col, foreground=fg_col, padding=[15, 8], font=("Consolas", 11, "bold"), borderwidth=2, relief="solid")
        self.style.map("TNotebook.Tab", background=[("selected", "#000000")], foreground=[("selected", "#ffffff")])

        self.style.configure("TFrame", background=bg_col)
        self.style.configure("Card.TFrame", background=card_bg, relief="solid", borderwidth=2)
        self.style.configure("TLabel", background=bg_col, foreground=fg_col, font=("Consolas", 10, "bold"))
        self.style.configure("Header.TLabel", background=bg_col, foreground=fg_col, font=("Consolas", 16, "bold"))
        self.style.configure("CardHeader.TLabel", background=card_bg, foreground=fg_col, font=("Consolas", 13, "bold"))
        self.style.configure("CardLabel.TLabel", background=card_bg, foreground=fg_col, font=("Consolas", 10, "bold"))

        self.style.configure("TButton", font=("Consolas", 10, "bold"), background="#ffffff", foreground="#000000", borderwidth=2, relief="solid")
        self.style.map("TButton", background=[("active", "#000000")], foreground=[("active", "#ffffff")])

        self.style.configure("Primary.TButton", background="#000000", foreground="#ffffff", font=("Consolas", 11, "bold"), borderwidth=2, relief="solid")
        self.style.map("Primary.TButton", background=[("active", "#333333")], foreground=[("active", "#ffffff")])

        # Header Title
        header_frame = tk.Frame(self, bg="#ffffff", bd=2, relief="solid", padx=15, pady=10)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_lbl = tk.Label(header_frame, text="DESTA CALCULATOR", bg="#ffffff", fg="#000000", font=("Consolas", 16, "bold"))
        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(header_frame, text="ARITHMETIC • JULIAN DAY • QIBLA FINDER", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold"))
        subtitle_lbl.pack(side="right")

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Build Tabs (NO EMOJIS)
        self.tab_calc = ttk.Frame(self.notebook)
        self.tab_julian = ttk.Frame(self.notebook)
        self.tab_qibla = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_calc, text=" CALCULATOR ")
        self.notebook.add(self.tab_julian, text=" JULIAN DAY ")
        self.notebook.add(self.tab_qibla, text=" QIBLA FINDER ")

        self._init_calculator_tab()
        self._init_julian_tab()
        self._init_qibla_tab()

    # --- TAB 1: Calculator ---
    def _init_calculator_tab(self):
        container = ttk.Frame(self.tab_calc, padding=15)
        container.pack(fill="both", expand=True)

        card = tk.Frame(container, bg="#ffffff", bd=2, relief="solid", padding=15)
        card.pack(fill="both", expand=True)

        # Display Screen
        self.calc_expr_var = tk.StringVar(value="")
        self.calc_result_var = tk.StringVar(value="0")

        expr_lbl = tk.Label(card, textvariable=self.calc_expr_var, bg="#ffffff", fg="#444444", font=("Consolas", 12, "bold"), anchor="e", padx=10)
        expr_lbl.pack(fill="x", pady=(0, 2))

        display_frame = tk.Frame(card, bg="#ffffff", bd=2, relief="solid")
        display_frame.pack(fill="x", pady=(0, 15))

        display_lbl = tk.Label(display_frame, textvariable=self.calc_result_var, bg="#ffffff", fg="#000000", font=("Consolas", 26, "bold"), anchor="e", padx=10, pady=8)
        display_lbl.pack(fill="x")

        # Button Grid
        btn_frame = tk.Frame(card, bg="#ffffff")
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
                bg_c = "#ffffff"
                fg_c = "#000000"
                if text == "=":
                    bg_c = "#000000"
                    fg_c = "#ffffff"
                elif text in ("C", "AC"):
                    bg_c = "#000000"
                    fg_c = "#ffffff"
                elif text in ("÷", "×", "-", "+", "^", "√", "π", "e", "±"):
                    bg_c = "#f0f0f0"
                    fg_c = "#000000"

                b = tk.Button(btn_frame, text=text, command=cmd, bg=bg_c, fg=fg_c, activebackground="#000000", activeforeground="#ffffff",
                              font=("Consolas", 12, "bold"), bd=2, relief="solid")
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
            except Exception:
                self.calc_result_var.set("ERROR")

    def _calc_evaluate(self):
        try:
            expr = self.calc_expr_var.get()
            if not expr:
                return
            allowed_names = {"math": math, "pi": math.pi, "e": math.e, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan}
            result = eval(expr, {"__builtins__": None}, allowed_names)

            if isinstance(result, float):
                result = round(result, 8)
                if result.is_integer():
                    result = int(result)

            self.calc_result_var.set(str(result))
        except Exception:
            self.calc_result_var.set("ERROR")

    # --- TAB 2: Julian Day ---
    def _init_julian_tab(self):
        container = ttk.Frame(self.tab_julian, padding=15)
        container.pack(fill="both", expand=True)

        card = tk.Frame(container, bg="#ffffff", bd=2, relief="solid", padx=15, pady=15)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="JULIAN DAY CALCULATOR", bg="#ffffff", fg="#000000", font=("Consolas", 13, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))

        # Inputs
        tk.Label(card, text="YEAR (YYYY):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.jd_year_ent = ttk.Entry(card, width=12, font=("Consolas", 11, "bold"))
        self.jd_year_ent.grid(row=1, column=1, sticky="w", pady=5, padx=5)

        tk.Label(card, text="MONTH (1-12):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=1, column=2, sticky="w", pady=5, padx=(15, 0))
        self.jd_month_ent = ttk.Entry(card, width=12, font=("Consolas", 11, "bold"))
        self.jd_month_ent.grid(row=1, column=3, sticky="w", pady=5, padx=5)

        tk.Label(card, text="DAY (1-31):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.jd_day_ent = ttk.Entry(card, width=12, font=("Consolas", 11, "bold"))
        self.jd_day_ent.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        tk.Label(card, text="TIME (HH:MM:SS):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=2, column=2, sticky="w", pady=5, padx=(15, 0))
        self.jd_time_ent = ttk.Entry(card, width=12, font=("Consolas", 11, "bold"))
        self.jd_time_ent.grid(row=2, column=3, sticky="w", pady=5, padx=5)

        tk.Label(card, text="UTC OFFSET (HRS):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        self.jd_utc_ent = ttk.Entry(card, width=12, font=("Consolas", 11, "bold"))
        self.jd_utc_ent.grid(row=3, column=1, sticky="w", pady=5, padx=5)

        # Buttons
        btn_frame = tk.Frame(card, bg="#ffffff")
        btn_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=15)

        calc_btn = ttk.Button(btn_frame, text="CALCULATE JULIAN DAY", style="Primary.TButton", command=self._compute_julian_day)
        calc_btn.pack(side="left", padx=(0, 10))

        now_btn = ttk.Button(btn_frame, text="SET CURRENT TIME", command=self._set_current_date_time)
        now_btn.pack(side="left")

        # Results Display Card
        res_card = tk.Frame(card, bg="#ffffff", bd=2, relief="solid", padx=15, pady=15)
        res_card.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=10)

        self.jd_val_lbl = tk.Label(res_card, text="JULIAN DAY (JD): --", bg="#ffffff", fg="#000000", font=("Consolas", 13, "bold"), anchor="w")
        self.jd_val_lbl.pack(fill="x", pady=2)

        self.mjd_val_lbl = tk.Label(res_card, text="MODIFIED JULIAN DAY (MJD): --", bg="#ffffff", fg="#000000", font=("Consolas", 11, "bold"), anchor="w")
        self.mjd_val_lbl.pack(fill="x", pady=2)

        self.jd_info_lbl = tk.Label(res_card, text="INPUT DATE: --", bg="#ffffff", fg="#333333", font=("Consolas", 10, "bold"), anchor="w")
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
        self.jd_utc_ent.insert(0, "7.0")

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

            self.jd_val_lbl.config(text=f"JULIAN DAY (JD):  {jd:.6f}")
            self.mjd_val_lbl.config(text=f"MODIFIED JULIAN DAY (MJD):  {mjd:.6f}")
            self.jd_info_lbl.config(text=f"GREGORIAN DATE: {yr}-{mo:02d}-{int(dy):02d} {hr:02d}:{mn:02d}:{sc:02d} (UTC{'+' if utc>=0 else ''}{utc})")

        except Exception as err:
            messagebox.showerror("INVALID INPUT", f"Error computing Julian Day: {err}")

    # --- TAB 3: Qibla Finder ---
    def _init_qibla_tab(self):
        container = ttk.Frame(self.tab_qibla, padding=15)
        container.pack(fill="both", expand=True)

        left_card = tk.Frame(container, bg="#ffffff", bd=2, relief="solid", padx=15, pady=15)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_card = tk.Frame(container, bg="#ffffff", bd=2, relief="solid", padx=15, pady=15)
        right_card.pack(side="right", fill="both", expand=True)

        # Left Controls
        tk.Label(left_card, text="QIBLA (KIBLAT) LOCATION", bg="#ffffff", fg="#000000", font=("Consolas", 13, "bold")).pack(anchor="w", pady=(0, 10))

        tk.Label(left_card, text="QUICK SELECT CITY:", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).pack(anchor="w", pady=2)

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
        city_cb = ttk.Combobox(left_card, textvariable=self.city_var, values=list(self.city_presets.keys()), state="readonly", font=("Consolas", 10, "bold"))
        city_cb.pack(fill="x", pady=(0, 15))
        city_cb.bind("<<ComboboxSelected>>", self._on_city_selected)

        # Manual Lat/Lon
        tk.Label(left_card, text="LATITUDE (°N / °S):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).pack(anchor="w", pady=2)
        self.lat_ent = ttk.Entry(left_card, font=("Consolas", 11, "bold"))
        self.lat_ent.pack(fill="x", pady=(0, 10))

        tk.Label(left_card, text="LONGITUDE (°E / °W):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).pack(anchor="w", pady=2)
        self.lon_ent = ttk.Entry(left_card, font=("Consolas", 11, "bold"))
        self.lon_ent.pack(fill="x", pady=(0, 15))

        calc_qibla_btn = ttk.Button(left_card, text="CALCULATE QIBLA DIRECTION", style="Primary.TButton", command=self._compute_qibla)
        calc_qibla_btn.pack(fill="x", pady=(0, 15))

        # Output Text Box
        self.qibla_res_box = tk.Frame(left_card, bg="#ffffff", bd=2, relief="solid", padx=12, pady=12)
        self.qibla_res_box.pack(fill="both", expand=True)

        self.q_bearing_lbl = tk.Label(self.qibla_res_box, text="BEARING: --°", bg="#ffffff", fg="#000000", font=("Consolas", 13, "bold"), anchor="w")
        self.q_bearing_lbl.pack(fill="x", pady=2)

        self.q_dir_lbl = tk.Label(self.qibla_res_box, text="DIRECTION: --", bg="#ffffff", fg="#000000", font=("Consolas", 11, "bold"), anchor="w")
        self.q_dir_lbl.pack(fill="x", pady=2)

        self.q_dist_lbl = tk.Label(self.qibla_res_box, text="DISTANCE TO MECCA: -- km", bg="#ffffff", fg="#333333", font=("Consolas", 10, "bold"), anchor="w")
        self.q_dist_lbl.pack(fill="x", pady=2)

        # Right Graphical Compass Canvas
        tk.Label(right_card, text="COMPASS DIAL", bg="#ffffff", fg="#000000", font=("Consolas", 13, "bold")).pack(anchor="w", pady=(0, 10))

        self.current_qibla_bearing = 0.0
        self.compass_canvas = tk.Canvas(right_card, bg="#ffffff", highlightthickness=2, highlightbackground="#000000")
        self.compass_canvas.pack(fill="both", expand=True)
        self.compass_canvas.bind("<Configure>", lambda e: self._draw_compass(self.current_qibla_bearing))

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

            self.current_qibla_bearing = bearing

            self.q_bearing_lbl.config(text=f"BEARING: {bearing}°")
            self.q_dir_lbl.config(text=f"DIRECTION: {direction} (FROM NORTH)")
            self.q_dist_lbl.config(text=f"DISTANCE TO MECCA: {dist:,.2f} km")

            self._draw_compass(bearing)

        except Exception as err:
            messagebox.showerror("INVALID INPUT", f"Error computing Qibla direction: {err}")

    def _draw_compass(self, bearing_deg: float):
        cv = self.compass_canvas
        cv.delete("all")

        w = cv.winfo_width() or 300
        h = cv.winfo_height() or 300
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 25

        if radius < 40:
            radius = 100

        # Draw Outer Ring (Solid Black)
        cv.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="#000000", width=3, fill="#ffffff")
        cv.create_oval(cx - radius + 6, cy - radius + 6, cx + radius - 6, cy + radius - 6, outline="#000000", width=1)

        # Cardinal Points
        cardinals = [("N", 0, "#000000"), ("E", 90, "#000000"), ("S", 180, "#000000"), ("W", 270, "#000000")]
        for label, deg, color in cardinals:
            rad = math.radians(deg - 90)
            lx = cx + (radius - 18) * math.cos(rad)
            ly = cy + (radius - 18) * math.sin(rad)
            cv.create_text(lx, ly, text=label, fill=color, font=("Consolas", 12, "bold"))

        # Tick marks
        for deg in range(0, 360, 15):
            rad = math.radians(deg - 90)
            x1 = cx + (radius - 6) * math.cos(rad)
            y1 = cy + (radius - 6) * math.sin(rad)
            x2 = cx + radius * math.cos(rad)
            y2 = cy + radius * math.sin(rad)
            cv.create_line(x1, y1, x2, y2, fill="#000000", width=1)

        # Draw North Needle (Solid black pointer)
        cv.create_line(cx, cy, cx, cy - (radius - 35), fill="#000000", width=3, arrow=tk.LAST, arrowshape=(10, 12, 5))

        # Draw Qibla Vector Needle (Thick black pointer)
        q_rad = math.radians(bearing_deg - 90)
        qx = cx + (radius - 30) * math.cos(q_rad)
        qy = cy + (radius - 30) * math.sin(q_rad)

        cv.create_line(cx, cy, qx, qy, fill="#000000", width=4, arrow=tk.LAST, arrowshape=(12, 15, 6))

        # Kaaba marker (Text MECCA box - NO EMOJIS)
        kx = cx + (radius - 12) * math.cos(q_rad)
        ky = cy + (radius - 12) * math.sin(q_rad)
        cv.create_rectangle(kx - 18, ky - 8, kx + 18, ky + 8, fill="#000000", outline="#000000", width=1)
        cv.create_text(kx, ky, text="MECCA", fill="#ffffff", font=("Consolas", 7, "bold"))

        # Center Dot
        cv.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#000000", outline="")

        # Text Overlay
        cv.create_text(cx, cy + radius + 12, text=f"QIBLA: {bearing_deg:.1f}°", fill="#000000", font=("Consolas", 11, "bold"))


if __name__ == "__main__":
    app = AdvancedCalculatorApp()
    app.mainloop()
