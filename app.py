"""Advanced Calculator GUI Application - Neo-Brutalism Theme with Accent Yellow (No Emojis).

Features:
- Calculator (Basic & Scientific)
- Julian Day Converter
- Qibla Direction Finder with Graphical Compass Dial & Kaaba Icon
- Prayer Times (Waktu Shalat) Based on Location
- Dual Gregorian / Hijri Calendar with Navigation
- Date Converter (Gregorian to Hijri and Hijri to Gregorian)
- Start of Month Information (Awal Bulan Hijriah di Masehi & Awal Bulan Masehi di Hijriah)
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# --- Core Mathematical & Astronomical Functions ---

MECCA_LAT = 21.422487
MECCA_LON = 39.826206

HIJRI_MONTHS = [
    "Muharram", "Safar", "Rabi'ul-Awwal", "Rabi'ul-Akhir",
    "Jumadal-Ula", "Jumadal-Akhirah", "Rajab", "Sya'ban",
    "Ramadhan", "Syawwal", "Dzulqa'dah", "Dzulhijjah"
]

HIJRI_MONTHS_SHORT = [
    "Muh", "Saf", "Rab I", "Rab II",
    "Jum I", "Jum II", "Raj", "Sya",
    "Ram", "Syaw", "Dzulq", "Dzulh"
]

GREG_MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

DAYS_ID = ["Ahad", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]


def gregorian_to_jd(year: int, month: int, day: float) -> float:
    y = year
    m = month
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + (a // 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + day + b - 1524.5


def jd_to_gregorian(jd: float) -> tuple:
    jd0 = jd + 0.5
    z = math.floor(jd0)
    f = jd0 - z
    if z < 2299161:
        a = z
    else:
        alpha = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)
    day = b - d - math.floor(30.6001 * e) + f
    if e < 14:
        month = e - 1
    else:
        month = e - 13
    if month > 2:
        year = c - 4716
    else:
        year = c - 4715
    return int(year), int(month), int(round(day))


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

    directions = ["U", "UTL", "TL", "TTL", "T", "TGr", "TG", "STG",
                  "S", "SBD", "BD", "BBD", "B", "BBL", "BL", "UBL"]
    dir_idx = int((bearing_deg + 11.25) / 22.5) % 16

    return {
        "bearing_deg": round(bearing_deg, 4),
        "compass_direction": directions[dir_idx],
        "distance_km": round(distance_km, 2)
    }


def is_hijri_leap(year: int) -> bool:
    return (11 * year + 14) % 30 < 11


def hijri_month_days(year: int, month: int) -> int:
    if month % 2 == 1:
        return 30
    if month == 12 and is_hijri_leap(year):
        return 30
    return 29


def hijri_to_jd(year: int, month: int, day: int) -> float:
    y = year - 1
    days = y * 354 + math.floor((11 * y + 3) / 30)
    days += math.ceil(29.5 * (month - 1))
    days += day
    return days + 1948439.5 - 1


def jd_to_hijri(jd: float) -> tuple:
    jd0 = math.floor(jd) + 0.5
    d = jd0 - 1948439.5 + 1
    cycle = math.floor(d / 10631)
    d_cycle = d - 10631 * cycle
    y_cycle = math.floor((30 * d_cycle + 15) / 10631)
    year = 30 * cycle + y_cycle

    y = year - 1
    days_y = y * 354 + math.floor((11 * y + 3) / 30)
    d_rem = d - days_y

    if d_rem <= 0:
        year -= 1
        y = year - 1
        days_y = y * 354 + math.floor((11 * y + 3) / 30)
        d_rem = d - days_y
    else:
        max_days = 355 if is_hijri_leap(year) else 354
        if d_rem > max_days:
            year += 1
            y = year - 1
            days_y = y * 354 + math.floor((11 * y + 3) / 30)
            d_rem = d - days_y

    month = 1
    while month <= 12:
        m_len = hijri_month_days(year, month)
        if d_rem <= m_len:
            break
        d_rem -= m_len
        month += 1

    return int(year), int(month), int(round(d_rem))


def gregorian_to_hijri(year: int, month: int, day: int) -> tuple:
    jd = gregorian_to_jd(year, month, day)
    return jd_to_hijri(jd)


def get_islamic_holiday(h_month: int, h_day: int, h_year: int) -> str:
    if h_month == 1 and h_day == 1:
        return f"Tahun Baru Hijriah {h_year} H"
    if h_month == 1 and h_day == 9:
        return "Puasa Tasu'a"
    if h_month == 1 and h_day == 10:
        return "Puasa Asyura"
    if h_month == 3 and h_day == 12:
        return "Maulid Nabi Muhammad SAW"
    if h_month == 7 and h_day == 27:
        return "Isra Mi'raj"
    if h_month == 8 and h_day == 15:
        return "Malam Nisfu Sya'ban"
    if h_month == 9 and h_day == 1:
        return "Awal Puasa Ramadhan"
    if h_month == 9 and h_day == 17:
        return "Nuzulul Qur'an"
    if h_month == 10 and h_day == 1:
        return "Hari Raya Idul Fitri"
    if h_month == 10 and h_day == 2:
        return "Idul Fitri Hari Ke-2"
    if h_month == 12 and h_day == 8:
        return "Hari Tarwiyah"
    if h_month == 12 and h_day == 9:
        return "Hari Arafah"
    if h_month == 12 and h_day == 10:
        return "Hari Raya Idul Adha"
    if h_month == 12 and h_day in (11, 12, 13):
        return "Hari Tasyrik"
    if h_day in (13, 14, 15):
        return "Puasa Ayyamul Bidh"
    return ""


def calculate_prayer_times(lat: float, lon: float, tz: float, year: int, month: int, day: int, fajr_angle: float = 20.0, isha_angle: float = 18.0) -> dict:
    jd = gregorian_to_jd(year, month, day)
    d = jd - 2451545.0

    g = (357.529 + 0.98560028 * d) % 360
    q = (280.459 + 0.98564736 * d) % 360
    l = (q + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))) % 360
    e = 23.439 - 0.00000036 * d

    sin_dec = math.sin(math.radians(e)) * math.sin(math.radians(l))
    dec = math.asin(sin_dec)

    tan_e2 = math.tan(math.radians(e) / 2) ** 2
    sin_2l = math.sin(2 * math.radians(l))
    sin_g = math.sin(math.radians(g))
    eqt = 4 * math.degrees(
        tan_e2 * sin_2l - 2 * 0.0167086 * sin_g + 4 * 0.0167086 * tan_e2 * sin_g * math.cos(2 * math.radians(l))
        - 0.5 * (tan_e2 ** 2) * math.sin(4 * math.radians(l)) - 1.25 * (0.0167086 ** 2) * math.sin(2 * math.radians(g))
    )

    noon = 12.0 + tz - (lon / 15.0) - (eqt / 60.0)
    phi = math.radians(lat)

    def hour_angle(alt_deg: float) -> float:
        sin_alt = math.sin(math.radians(alt_deg))
        cos_ha = (sin_alt - math.sin(phi) * math.sin(dec)) / (math.cos(phi) * math.cos(dec))
        if cos_ha > 1:
            return 0.0
        if cos_ha < -1:
            return 180.0
        return math.degrees(math.acos(cos_ha))

    ha_sun = hour_angle(-0.8333)
    sunrise = noon - ha_sun / 15.0
    sunset = noon + ha_sun / 15.0

    ha_fajr = hour_angle(-fajr_angle)
    fajr = noon - ha_fajr / 15.0
    imsak = fajr - (10.0 / 60.0)

    alt_asr = math.degrees(math.atan(1.0 / (1.0 + math.tan(abs(phi - dec)))))
    ha_asr = hour_angle(alt_asr)
    asr = noon + ha_asr / 15.0

    maghrib = sunset + (2.0 / 60.0)  # +2 min ihtiyat
    ha_isha = hour_angle(-isha_angle)
    isha = noon + ha_isha / 15.0
    dhuhr = noon + (2.0 / 60.0)      # +2 min ihtiyat

    def fmt(h: float) -> str:
        h = (h % 24 + 24) % 24
        hours = int(h)
        mins = int(round((h - hours) * 60))
        if mins == 60:
            hours += 1
            mins = 0
        return f"{hours:02d}:{mins:02d}"

    return {
        "imsak": fmt(imsak),
        "fajr": fmt(fajr),
        "sunrise": fmt(sunrise),
        "dhuhr": fmt(dhuhr),
        "asr": fmt(asr),
        "maghrib": fmt(maghrib),
        "isha": fmt(isha)
    }


# --- GUI Application ---

class AdvancedCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("DESTA CALCULATOR - QIBLA, WAKTU SHALAT & KALENDER HIJRIAH")
        self.geometry("900x720")
        self.minsize(820, 640)
        self.configure(bg="#f8f8f5")

        # Custom Styling - Neo-Brutalism with Electric Yellow Accent
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        bg_col = "#f8f8f5"
        fg_col = "#000000"
        card_bg = "#ffffff"
        accent_yellow = "#ffde59"

        self.style.configure(".", background=bg_col, foreground=fg_col, font=("Consolas", 10, "bold"))
        self.style.configure("TNotebook", background=bg_col, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=card_bg, foreground=fg_col, padding=[14, 8], font=("Consolas", 10, "bold"), borderwidth=2, relief="solid")
        self.style.map("TNotebook.Tab", background=[("selected", accent_yellow)], foreground=[("selected", "#000000")])

        self.style.configure("TFrame", background=bg_col)
        self.style.configure("Card.TFrame", background=card_bg, relief="solid", borderwidth=2)
        self.style.configure("TLabel", background=bg_col, foreground=fg_col, font=("Consolas", 10, "bold"))
        self.style.configure("Header.TLabel", background=accent_yellow, foreground=fg_col, font=("Consolas", 16, "bold"))
        self.style.configure("CardHeader.TLabel", background=card_bg, foreground=fg_col, font=("Consolas", 12, "bold"))
        self.style.configure("CardLabel.TLabel", background=card_bg, foreground=fg_col, font=("Consolas", 10, "bold"))

        self.style.configure("TButton", font=("Consolas", 10, "bold"), background="#ffffff", foreground="#000000", borderwidth=2, relief="solid")
        self.style.map("TButton", background=[("active", "#000000")], foreground=[("active", "#ffffff")])

        self.style.configure("Primary.TButton", background=accent_yellow, foreground="#000000", font=("Consolas", 10, "bold"), borderwidth=2, relief="solid")
        self.style.map("Primary.TButton", background=[("active", "#000000")], foreground=[("active", "#ffffff")])

        # Header Title
        header_frame = tk.Frame(self, bg="#ffffff", bd=3, relief="solid", padx=15, pady=10)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_lbl = tk.Label(header_frame, text=" DESTA CALCULATOR ", bg=accent_yellow, fg="#000000", font=("Consolas", 15, "bold"), bd=2, relief="solid")
        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(header_frame, text="ARITHMETIC • JULIAN DAY • QIBLA & SHALAT • KALENDER HIJRIAH", bg="#ffffff", fg="#000000", font=("Consolas", 9, "bold"))
        subtitle_lbl.pack(side="right")

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Build Tabs (NO EMOJIS)
        self.tab_calc = ttk.Frame(self.notebook)
        self.tab_julian = ttk.Frame(self.notebook)
        self.tab_qibla = ttk.Frame(self.notebook)
        self.tab_calendar = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_calc, text=" CALCULATOR ")
        self.notebook.add(self.tab_julian, text=" JULIAN DAY ")
        self.notebook.add(self.tab_qibla, text=" QIBLA & SHALAT ")
        self.notebook.add(self.tab_calendar, text=" KALENDER & HIJRIAH ")

        self._init_calculator_tab()
        self._init_julian_tab()
        self._init_qibla_tab()
        self._init_calendar_tab()

    # --- TAB 1: Calculator ---
    def _init_calculator_tab(self):
        container = ttk.Frame(self.tab_calc, padding=15)
        container.pack(fill="both", expand=True)

        card = tk.Frame(container, bg="#ffffff", bd=2, relief="solid", padx=15, pady=15)
        card.pack(fill="both", expand=True)

        # Display Screen
        self.calc_expr_var = tk.StringVar(value="")
        self.calc_result_var = tk.StringVar(value="0")

        expr_lbl = tk.Label(card, textvariable=self.calc_expr_var, bg="#ffffff", fg="#555555", font=("Consolas", 12, "bold"), anchor="e", padx=10)
        expr_lbl.pack(fill="x", pady=(0, 2))

        display_frame = tk.Frame(card, bg="#ffffff", bd=3, relief="solid")
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
                    bg_c = "#ffde59"
                    fg_c = "#000000"
                elif text in ("C", "AC"):
                    bg_c = "#000000"
                    fg_c = "#ffffff"
                elif text in ("÷", "×", "-", "+", "^", "√", "π", "e", "±"):
                    bg_c = "#f4f4ee"
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

        card = tk.Frame(container, bg="#ffffff", bd=2, relief="solid", padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="CALENDAR DATE TO JULIAN DAY (JD)", bg="#ffffff", fg="#000000", font=("Consolas", 14, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))

        tk.Label(card, text="YEAR (YYYY):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        self.jd_yr_ent = ttk.Entry(card, font=("Consolas", 11, "bold"))
        self.jd_yr_ent.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=4)

        tk.Label(card, text="MONTH (1-12):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=1, column=2, sticky="w", pady=4)
        self.jd_mo_ent = ttk.Entry(card, font=("Consolas", 11, "bold"))
        self.jd_mo_ent.grid(row=1, column=3, sticky="ew", pady=4)

        tk.Label(card, text="DAY (1-31):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        self.jd_dy_ent = ttk.Entry(card, font=("Consolas", 11, "bold"))
        self.jd_dy_ent.grid(row=2, column=1, sticky="ew", padx=(0, 20), pady=4)

        tk.Label(card, text="TIME (HH:MM:SS):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=2, column=2, sticky="w", pady=4)
        self.jd_tm_ent = ttk.Entry(card, font=("Consolas", 11, "bold"))
        self.jd_tm_ent.grid(row=2, column=3, sticky="ew", pady=4)

        tk.Label(card, text="UTC OFFSET (HRS):", bg="#ffffff", fg="#000000", font=("Consolas", 10, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        self.jd_utc_ent = ttk.Entry(card, font=("Consolas", 11, "bold"))
        self.jd_utc_ent.grid(row=3, column=1, sticky="ew", padx=(0, 20), pady=4)

        card.columnconfigure(1, weight=1)
        card.columnconfigure(3, weight=1)

        btn_row = tk.Frame(card, bg="#ffffff")
        btn_row.grid(row=4, column=0, columnspan=4, sticky="ew", pady=15)

        calc_jd_btn = ttk.Button(btn_row, text="CALCULATE JULIAN DAY", style="Primary.TButton", command=self._compute_julian_day)
        calc_jd_btn.pack(side="left", padx=(0, 10))

        set_now_btn = ttk.Button(btn_row, text="SET CURRENT TIME", command=self._set_current_datetime)
        set_now_btn.pack(side="left")

        res_card = tk.Frame(card, bg="#ffffff", bd=2, relief="solid", padx=15, pady=15)
        res_card.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=10)

        self.jd_val_lbl = tk.Label(res_card, text="JULIAN DAY (JD): --", bg="#ffde59", fg="#000000", font=("Consolas", 13, "bold"), anchor="w", bd=2, relief="solid", padx=5)
        self.jd_val_lbl.pack(fill="x", pady=2)

        self.mjd_val_lbl = tk.Label(res_card, text="MODIFIED JULIAN DAY (MJD): --", bg="#ffffff", fg="#000000", font=("Consolas", 11, "bold"), anchor="w")
        self.mjd_val_lbl.pack(fill="x", pady=2)

        self.jd_info_lbl = tk.Label(res_card, text="GREGORIAN DATE: --", bg="#ffffff", fg="#333333", font=("Consolas", 10, "bold"), anchor="w")
        self.jd_info_lbl.pack(fill="x", pady=2)

        self._set_current_datetime()
        self._compute_julian_day()

    def _set_current_datetime(self):
        now = datetime.now()
        self.jd_yr_ent.delete(0, tk.END)
        self.jd_yr_ent.insert(0, str(now.year))
        self.jd_mo_ent.delete(0, tk.END)
        self.jd_mo_ent.insert(0, str(now.month))
        self.jd_dy_ent.delete(0, tk.END)
        self.jd_dy_ent.insert(0, str(now.day))
        self.jd_tm_ent.delete(0, tk.END)
        self.jd_tm_ent.insert(0, f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}")
        self.jd_utc_ent.delete(0, tk.END)
        self.jd_utc_ent.insert(0, "7.0")

    def _compute_julian_day(self):
        try:
            yr = int(self.jd_yr_ent.get())
            mo = int(self.jd_mo_ent.get())
            dy = float(self.jd_dy_ent.get())
            t_str = self.jd_tm_ent.get().strip()
            utc = float(self.jd_utc_ent.get())

            parts = [int(p) for p in t_str.split(":")]
            hr = parts[0] if len(parts) > 0 else 0
            mn = parts[1] if len(parts) > 1 else 0
            sc = parts[2] if len(parts) > 2 else 0

            jd = calculate_julian_day(yr, mo, dy, hr, mn, sc, utc)
            mjd = jd - 2400000.5

            self.jd_val_lbl.config(text=f"JULIAN DAY (JD):  {jd:.6f}")
            self.mjd_val_lbl.config(text=f"MODIFIED JULIAN DAY (MJD):  {mjd:.6f}")
            self.jd_info_lbl.config(text=f"GREGORIAN DATE: {yr}-{mo:02d}-{int(dy):02d} {hr:02d}:{mn:02d}:{sc:02d} (UTC{'+' if utc>=0 else ''}{utc})")

        except Exception as err:
            messagebox.showerror("INVALID INPUT", f"Error computing Julian Day: {err}")

    # --- TAB 3: Qibla & Prayer Times ---
    def _init_qibla_tab(self):
        container = ttk.Frame(self.tab_qibla, padding=12)
        container.pack(fill="both", expand=True)

        top_pane = tk.Frame(container, bg="#f8f8f5")
        top_pane.pack(fill="both", expand=True)

        left_card = tk.Frame(top_pane, bg="#ffffff", bd=2, relief="solid", padx=12, pady=12)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right_card = tk.Frame(top_pane, bg="#ffffff", bd=2, relief="solid", padx=12, pady=12)
        right_card.pack(side="right", fill="both", expand=True)

        # Left Controls
        tk.Label(left_card, text="QIBLA (KIBLAT) & WAKTU SHALAT", bg="#ffffff", fg="#000000", font=("Consolas", 12, "bold")).pack(anchor="w", pady=(0, 8))

        tk.Label(left_card, text="PILIH KOTA PRESET:", bg="#ffffff", fg="#000000", font=("Consolas", 9, "bold")).pack(anchor="w", pady=1)

        self.city_presets = {
            "Jakarta, Indonesia (WIB)": (-6.2088, 106.8456, 7.0),
            "Surabaya, Indonesia (WIB)": (-7.2575, 112.7521, 7.0),
            "Bandung, Indonesia (WIB)": (-6.9175, 107.6191, 7.0),
            "Medan, Indonesia (WIB)": (3.5952, 98.6722, 7.0),
            "Yogyakarta, Indonesia (WIB)": (-7.7956, 110.3695, 7.0),
            "Semarang, Indonesia (WIB)": (-6.9667, 110.4167, 7.0),
            "Makassar, Indonesia (WITA)": (-5.1477, 119.4327, 8.0),
            "Denpasar, Indonesia (WITA)": (-8.6705, 115.2126, 8.0),
            "Jayapura, Indonesia (WIT)": (-2.5489, 140.7181, 9.0),
            "Kuala Lumpur, Malaysia (MYT)": (3.1390, 101.6869, 8.0),
            "Makkah Al-Mukarramah (AST)": (21.4225, 39.8262, 3.0),
            "Madinah Al-Munawwarah (AST)": (24.4672, 39.6111, 3.0),
            "Riyadh, Saudi Arabia (AST)": (24.7136, 46.6753, 3.0),
            "London, United Kingdom (GMT)": (51.5074, -0.1278, 0.0),
            "New York, USA (EST)": (40.7128, -74.0060, -5.0),
            "Tokyo, Japan (JST)": (35.6762, 139.6503, 9.0),
            "Sydney, Australia (AEST)": (-33.8688, 151.2093, 10.0),
        }

        self.city_var = tk.StringVar(value="Jakarta, Indonesia (WIB)")
        city_cb = ttk.Combobox(left_card, textvariable=self.city_var, values=list(self.city_presets.keys()), state="readonly", font=("Consolas", 9, "bold"))
        city_cb.pack(fill="x", pady=(0, 8))
        city_cb.bind("<<ComboboxSelected>>", self._on_city_selected)

        # Coordinate inputs
        coords_frame = tk.Frame(left_card, bg="#ffffff")
        coords_frame.pack(fill="x", pady=(0, 8))

        tk.Label(coords_frame, text="LAT (°N/S):", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.lat_ent = ttk.Entry(coords_frame, font=("Consolas", 9, "bold"), width=12)
        self.lat_ent.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        tk.Label(coords_frame, text="LON (°E/W):", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=1, sticky="w")
        self.lon_ent = ttk.Entry(coords_frame, font=("Consolas", 9, "bold"), width=12)
        self.lon_ent.grid(row=1, column=1, sticky="ew", padx=(0, 5))

        tk.Label(coords_frame, text="UTC (JAM):", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=2, sticky="w")
        self.tz_ent = ttk.Entry(coords_frame, font=("Consolas", 9, "bold"), width=8)
        self.tz_ent.grid(row=1, column=2, sticky="ew")

        coords_frame.columnconfigure(0, weight=1)
        coords_frame.columnconfigure(1, weight=1)
        coords_frame.columnconfigure(2, weight=1)

        calc_qibla_btn = ttk.Button(left_card, text="HITUNG QIBLA & JADWAL SHALAT", style="Primary.TButton", command=self._compute_qibla)
        calc_qibla_btn.pack(fill="x", pady=(0, 8))

        # Output Text Box
        self.qibla_res_box = tk.Frame(left_card, bg="#ffffff", bd=2, relief="solid", padx=10, pady=8)
        self.qibla_res_box.pack(fill="x", pady=(0, 8))

        self.q_bearing_lbl = tk.Label(self.qibla_res_box, text="BEARING: --°", bg="#ffde59", fg="#000000", font=("Consolas", 11, "bold"), anchor="w", bd=1, relief="solid", padx=4)
        self.q_bearing_lbl.pack(fill="x", pady=1)

        self.q_dir_lbl = tk.Label(self.qibla_res_box, text="ARAH: --", bg="#ffffff", fg="#000000", font=("Consolas", 9, "bold"), anchor="w")
        self.q_dir_lbl.pack(fill="x", pady=1)

        self.q_dist_lbl = tk.Label(self.qibla_res_box, text="JARAK KE KA'BAH: -- km", bg="#ffffff", fg="#333333", font=("Consolas", 9, "bold"), anchor="w")
        self.q_dist_lbl.pack(fill="x", pady=1)

        # Right Graphical Compass Canvas
        tk.Label(right_card, text="KOMPAS VEKTOR KIBLAT", bg="#ffffff", fg="#000000", font=("Consolas", 11, "bold")).pack(anchor="w", pady=(0, 5))

        self.current_qibla_bearing = 0.0
        self.compass_canvas = tk.Canvas(right_card, bg="#ffffff", highlightthickness=2, highlightbackground="#000000", width=260, height=260)
        self.compass_canvas.pack(fill="both", expand=True)
        self.compass_canvas.bind("<Configure>", lambda e: self._draw_compass(self.current_qibla_bearing))

        # Bottom Frame: Prayer Times Grid
        bottom_card = tk.Frame(container, bg="#ffffff", bd=2, relief="solid", padx=12, pady=10)
        bottom_card.pack(fill="x", pady=(8, 0))

        pr_header = tk.Frame(bottom_card, bg="#ffffff")
        pr_header.pack(fill="x", pady=(0, 6))

        tk.Label(pr_header, text="JADWAL WAKTU SHALAT HARI INI", bg="#ffffff", fg="#000000", font=("Consolas", 11, "bold")).pack(side="left")
        self.pr_date_lbl = tk.Label(pr_header, text="STANDAR KEMENAG RI", bg="#ffde59", fg="#000000", font=("Consolas", 9, "bold"), bd=1, relief="solid", padx=5)
        self.pr_date_lbl.pack(side="right")

        # 7 prayer cards in grid
        self.prayer_grid_frame = tk.Frame(bottom_card, bg="#ffffff")
        self.prayer_grid_frame.pack(fill="x")

        self.prayer_widgets = {}
        prayers_list = [("IMSAK", "imsak"), ("SUBUH", "fajr"), ("TERBIT", "sunrise"),
                        ("DZUHUR", "dhuhr"), ("ASHAR", "asr"), ("MAGHRIB", "maghrib"), ("ISYA", "isha")]

        for idx, (p_title, p_key) in enumerate(prayers_list):
            p_box = tk.Frame(self.prayer_grid_frame, bg="#ffffff", bd=2, relief="solid", padx=5, pady=6)
            p_box.grid(row=0, column=idx, sticky="nsew", padx=3)
            self.prayer_grid_frame.columnconfigure(idx, weight=1)

            t_lbl = tk.Label(p_box, text=p_title, bg="#ffffff", fg="#000000", font=("Consolas", 8, "bold"))
            t_lbl.pack()

            val_lbl = tk.Label(p_box, text="--:--", bg="#ffffff", fg="#000000", font=("Consolas", 13, "bold"))
            val_lbl.pack(pady=2)

            self.prayer_widgets[p_key] = (p_box, val_lbl, t_lbl)

        self._on_city_selected(None)

    def _on_city_selected(self, event):
        city = self.city_var.get()
        if city in self.city_presets:
            lat, lon, tz = self.city_presets[city]
            self.lat_ent.delete(0, tk.END)
            self.lat_ent.insert(0, str(lat))
            self.lon_ent.delete(0, tk.END)
            self.lon_ent.insert(0, str(lon))
            self.tz_ent.delete(0, tk.END)
            self.tz_ent.insert(0, str(tz))
            self._compute_qibla()

    def _compute_qibla(self):
        try:
            lat = float(self.lat_ent.get())
            lon = float(self.lon_ent.get())
            tz = float(self.tz_ent.get())

            res = calculate_qibla(lat, lon)
            bearing = res["bearing_deg"]
            direction = res["compass_direction"]
            dist = res["distance_km"]

            self.current_qibla_bearing = bearing

            self.q_bearing_lbl.config(text=f"BEARING: {bearing:.2f}°")
            self.q_dir_lbl.config(text=f"ARAH: {direction} ({bearing:.1f}° DARI UTARA SEJATI)")
            self.q_dist_lbl.config(text=f"JARAK KE KA'BAH: {dist:,.2f} km")

            self._draw_compass(bearing)

            # Prayer Times
            now = datetime.now()
            p_res = calculate_prayer_times(lat, lon, tz, now.year, now.month, now.day)
            h_now = gregorian_to_hijri(now.year, now.month, now.day)
            self.pr_date_lbl.config(text=f"{now.day} {GREG_MONTHS[now.month-1]} {now.year} M / {h_now[2]} {HIJRI_MONTHS[h_now[1]-1]} {h_now[0]} H")

            for key, (box, val_lbl, title_lbl) in self.prayer_widgets.items():
                val_lbl.config(text=p_res.get(key, "--:--"))

        except Exception as err:
            messagebox.showerror("INVALID INPUT", f"Error computing Qibla and Prayer Times: {err}")

    def _draw_compass(self, bearing_deg: float):
        cv = self.compass_canvas
        cv.delete("all")

        w = cv.winfo_width() or 260
        h = cv.winfo_height() or 260
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 25

        if radius < 40:
            radius = 90

        # Draw Outer Ring (Solid Black)
        cv.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="#000000", width=3, fill="#ffffff")
        cv.create_oval(cx - radius + 6, cy - radius + 6, cx + radius - 6, cy + radius - 6, outline="#000000", width=1)

        # Cardinal Points
        cardinals = [("U", 0, "#000000"), ("T", 90, "#000000"), ("S", 180, "#000000"), ("B", 270, "#000000")]
        for label, deg, color in cardinals:
            rad = math.radians(deg - 90)
            lx = cx + (radius - 18) * math.cos(rad)
            ly = cy + (radius - 18) * math.sin(rad)
            cv.create_text(lx, ly, text=label, fill=color, font=("Consolas", 11, "bold"))

        # Tick marks
        for deg in range(0, 360, 15):
            rad = math.radians(deg - 90)
            x1 = cx + (radius - 6) * math.cos(rad)
            y1 = cy + (radius - 6) * math.sin(rad)
            x2 = cx + radius * math.cos(rad)
            y2 = cy + radius * math.sin(rad)
            cv.create_line(x1, y1, x2, y2, fill="#000000", width=1)

        # Draw North Needle (Solid black pointer)
        cv.create_line(cx, cy, cx, cy - (radius - 32), fill="#000000", width=3, arrow=tk.LAST, arrowshape=(10, 12, 5))

        # Draw Qibla Vector Needle (Electric Yellow with black outline)
        q_rad = math.radians(bearing_deg - 90)
        qx = cx + (radius - 28) * math.cos(q_rad)
        qy = cy + (radius - 28) * math.sin(q_rad)

        cv.create_line(cx, cy, qx, qy, fill="#ffde59", width=5, arrow=tk.LAST, arrowshape=(12, 15, 6))

        # Kaaba marker (Isometric 3D Kaaba Graphic - NO MECCA TEXT)
        kx = cx + (radius - 14) * math.cos(q_rad)
        ky = cy + (radius - 14) * math.sin(q_rad)
        s = 0.85

        # Marble Foundation (Syadzarwan)
        cv.create_polygon(kx - 12 * s, ky + 1 * s, kx, ky + 7 * s, kx, ky + 9 * s, kx - 12 * s, ky + 3 * s, fill="#e5e5ea", outline="#000000", width=1)
        cv.create_polygon(kx, ky + 7 * s, kx + 12 * s, ky + 1 * s, kx + 12 * s, ky + 3 * s, kx, ky + 9 * s, fill="#d1d1d6", outline="#000000", width=1)
        # Left Face (Dark Black)
        cv.create_polygon(kx - 12 * s, ky - 9 * s, kx, ky - 3 * s, kx, ky + 7 * s, kx - 12 * s, ky + 1 * s, fill="#111111", outline="#000000", width=1)
        # Right Face (Charcoal Black)
        cv.create_polygon(kx, ky - 3 * s, kx + 12 * s, ky - 9 * s, kx + 12 * s, ky + 1 * s, kx, ky + 7 * s, fill="#1c1c1e", outline="#000000", width=1)
        # Roof
        cv.create_polygon(kx, ky - 16 * s, kx + 12 * s, ky - 9 * s, kx, ky - 3 * s, kx - 12 * s, ky - 9 * s, fill="#2c2c2e", outline="#000000", width=1)
        # Golden Kiswah Band Left
        cv.create_polygon(kx - 12 * s, ky - 6.5 * s, kx, ky - 0.5 * s, kx, ky + 1.5 * s, kx - 12 * s, ky - 4.5 * s, fill="#ffde59", outline="#000000", width=1)
        # Golden Kiswah Band Right
        cv.create_polygon(kx, ky - 0.5 * s, kx + 12 * s, ky - 6.5 * s, kx + 12 * s, ky - 4.5 * s, kx, ky + 1.5 * s, fill="#ffde59", outline="#000000", width=1)
        # Golden Door (Bab al-Kaaba)
        cv.create_polygon(kx + 3 * s, ky - 1 * s, kx + 8 * s, ky - 3.5 * s, kx + 8 * s, ky + 2.5 * s, kx + 3 * s, ky + 5 * s, fill="#ffde59", outline="#000000", width=1)

        # Center Dot
        cv.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#000000", outline="")

        # Text Overlay
        cv.create_text(cx, cy + radius + 12, text=f"KIBLAT: {bearing_deg:.1f}°", fill="#000000", font=("Consolas", 10, "bold"))

    # --- TAB 4: Kalender & Hijriah ---
    def _init_calendar_tab(self):
        container = ttk.Frame(self.tab_calendar, padding=10)
        container.pack(fill="both", expand=True)

        # Canvas with scrollbar for full scrollable view
        canvas = tk.Canvas(container, bg="#f8f8f5", highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#f8f8f5")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_content, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        canvas.configure(yscrollcommand=v_scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        # 1. Calendar Header & Grid Card
        cal_card = tk.Frame(scroll_content, bg="#ffffff", bd=2, relief="solid", padx=12, pady=12)
        cal_card.pack(fill="x", pady=(0, 12))

        # Nav bar
        cal_nav_frame = tk.Frame(cal_card, bg="#ffffff")
        cal_nav_frame.pack(fill="x", pady=(0, 8))

        prev_btn = tk.Button(cal_nav_frame, text="◀ BULAN LALU", bg="#ffffff", fg="#000000", font=("Consolas", 9, "bold"), bd=2, relief="solid", command=self._cal_prev_month)
        prev_btn.pack(side="left", padx=(0, 4))

        today_btn = tk.Button(cal_nav_frame, text="HARI INI", bg="#ffde59", fg="#000000", font=("Consolas", 9, "bold"), bd=2, relief="solid", command=self._cal_go_today)
        today_btn.pack(side="left", padx=(0, 4))

        next_btn = tk.Button(cal_nav_frame, text="BULAN DEPAN ▶", bg="#ffffff", fg="#000000", font=("Consolas", 9, "bold"), bd=2, relief="solid", command=self._cal_next_month)
        next_btn.pack(side="left")

        # Center Title
        title_frame = tk.Frame(cal_nav_frame, bg="#ffffff")
        title_frame.pack(side="left", expand=True)

        self.cal_title_greg = tk.Label(title_frame, text="SEPTEMBER 2026", bg="#ffffff", fg="#000000", font=("Consolas", 13, "bold"))
        self.cal_title_greg.pack()

        self.cal_title_hijri = tk.Label(title_frame, text="RABI'UL-AWWAL 1448 H", bg="#ffffff", fg="#444444", font=("Consolas", 9, "bold"))
        self.cal_title_hijri.pack()

        # Jump controls
        jump_frame = tk.Frame(cal_nav_frame, bg="#ffffff")
        jump_frame.pack(side="right")

        self.cal_m_var = tk.StringVar(value="September")
        m_cb = ttk.Combobox(jump_frame, textvariable=self.cal_m_var, values=GREG_MONTHS, state="readonly", width=10, font=("Consolas", 9, "bold"))
        m_cb.pack(side="left", padx=2)
        m_cb.bind("<<ComboboxSelected>>", lambda e: self._cal_jump())

        self.cal_y_var = tk.StringVar(value="2026")
        y_spin = ttk.Spinbox(jump_frame, from_=1920, to=2100, textvariable=self.cal_y_var, width=6, font=("Consolas", 9, "bold"), command=self._cal_jump)
        y_spin.pack(side="left", padx=2)

        # Days of week header
        days_header_frame = tk.Frame(cal_card, bg="#000000")
        days_header_frame.pack(fill="x", pady=(0, 2))

        for idx, d_name in enumerate(["AHAD", "SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]):
            bg_col_d = "#e63946" if idx == 0 else ("#2a9d8f" if idx == 5 else "#000000")
            lbl = tk.Label(days_header_frame, text=d_name, bg=bg_col_d, fg="#ffffff", font=("Consolas", 8, "bold"), pady=4)
            lbl.grid(row=0, column=idx, sticky="nsew", padx=1)
            days_header_frame.columnconfigure(idx, weight=1)

        # Calendar days grid
        self.cal_grid_frame = tk.Frame(cal_card, bg="#dddddd")
        self.cal_grid_frame.pack(fill="x")
        for i in range(7):
            self.cal_grid_frame.columnconfigure(i, weight=1)

        # Selected day detail card
        self.cal_sel_frame = tk.Frame(cal_card, bg="#fbfbf8", bd=2, relief="solid", padx=10, pady=6)
        self.cal_sel_frame.pack(fill="x", pady=(8, 0))

        self.cal_sel_lbl = tk.Label(self.cal_sel_frame, text="TANGGAL: --", bg="#fbfbf8", fg="#000000", font=("Consolas", 10, "bold"), anchor="w")
        self.cal_sel_lbl.pack(fill="x")

        # 2. Date Converters (Gregorian <-> Hijri)
        conv_wrapper = tk.Frame(scroll_content, bg="#f8f8f5")
        conv_wrapper.pack(fill="x", pady=(0, 12))

        conv_left = tk.Frame(conv_wrapper, bg="#ffffff", bd=2, relief="solid", padx=12, pady=10)
        conv_left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        conv_right = tk.Frame(conv_wrapper, bg="#ffffff", bd=2, relief="solid", padx=12, pady=10)
        conv_right.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # Left: Gregorian to Hijri
        tk.Label(conv_left, text="KONVERSI MASEHI ➔ HIJRIAH", bg="#ffde59", fg="#000000", font=("Consolas", 10, "bold"), bd=1, relief="solid", padx=4, pady=2).pack(fill="x", pady=(0, 8))

        g_in_frame = tk.Frame(conv_left, bg="#ffffff")
        g_in_frame.pack(fill="x", pady=(0, 6))

        tk.Label(g_in_frame, text="TGL (1-31):", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.cg_d = ttk.Entry(g_in_frame, font=("Consolas", 9, "bold"), width=6)
        self.cg_d.grid(row=1, column=0, padx=(0, 4))

        tk.Label(g_in_frame, text="BULAN:", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=1, sticky="w")
        self.cg_m = ttk.Combobox(g_in_frame, values=GREG_MONTHS, state="readonly", width=10, font=("Consolas", 9, "bold"))
        self.cg_m.grid(row=1, column=1, padx=(0, 4))

        tk.Label(g_in_frame, text="TAHUN (M):", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=2, sticky="w")
        self.cg_y = ttk.Entry(g_in_frame, font=("Consolas", 9, "bold"), width=8)
        self.cg_y.grid(row=1, column=2)

        ttk.Button(conv_left, text="KONVERSI KE HIJRIAH", style="Primary.TButton", command=self._convert_greg_to_hijri).pack(fill="x", pady=6)

        self.cg_res_box = tk.Frame(conv_left, bg="#ffffff", bd=1, relief="solid", padx=8, pady=6)
        self.cg_res_box.pack(fill="x")
        self.cg_res_lbl = tk.Label(self.cg_res_box, text="HASIL HIJRIAH: --", bg="#ffffff", font=("Consolas", 9, "bold"), anchor="w")
        self.cg_res_lbl.pack(fill="x")
        self.cg_holiday_lbl = tk.Label(self.cg_res_box, text="", bg="#ffffff", fg="#e63946", font=("Consolas", 8, "bold"), anchor="w")
        self.cg_holiday_lbl.pack(fill="x")

        # Right: Hijri to Gregorian
        tk.Label(conv_right, text="KONVERSI HIJRIAH ➔ MASEHI", bg="#ffde59", fg="#000000", font=("Consolas", 10, "bold"), bd=1, relief="solid", padx=4, pady=2).pack(fill="x", pady=(0, 8))

        h_in_frame = tk.Frame(conv_right, bg="#ffffff")
        h_in_frame.pack(fill="x", pady=(0, 6))

        tk.Label(h_in_frame, text="TGL (1-30):", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.ch_d = ttk.Entry(h_in_frame, font=("Consolas", 9, "bold"), width=6)
        self.ch_d.grid(row=1, column=0, padx=(0, 4))

        tk.Label(h_in_frame, text="BULAN HIJRIAH:", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=1, sticky="w")
        self.ch_m = ttk.Combobox(h_in_frame, values=HIJRI_MONTHS, state="readonly", width=14, font=("Consolas", 9, "bold"))
        self.ch_m.grid(row=1, column=1, padx=(0, 4))

        tk.Label(h_in_frame, text="TAHUN (H):", bg="#ffffff", font=("Consolas", 8, "bold")).grid(row=0, column=2, sticky="w")
        self.ch_y = ttk.Entry(h_in_frame, font=("Consolas", 9, "bold"), width=8)
        self.ch_y.grid(row=1, column=2)

        ttk.Button(conv_right, text="KONVERSI KE MASEHI", style="Primary.TButton", command=self._convert_hijri_to_greg).pack(fill="x", pady=6)

        self.ch_res_box = tk.Frame(conv_right, bg="#ffffff", bd=1, relief="solid", padx=8, pady=6)
        self.ch_res_box.pack(fill="x")
        self.ch_res_lbl = tk.Label(self.ch_res_box, text="HASIL MASEHI: --", bg="#ffffff", font=("Consolas", 9, "bold"), anchor="w")
        self.ch_res_lbl.pack(fill="x")
        self.ch_holiday_lbl = tk.Label(self.ch_res_box, text="", bg="#ffffff", fg="#e63946", font=("Consolas", 8, "bold"), anchor="w")
        self.ch_holiday_lbl.pack(fill="x")

        # 3. Tables for Start of Months (Awal Bulan Hijriah & Masehi)
        tables_wrapper = tk.Frame(scroll_content, bg="#f8f8f5")
        tables_wrapper.pack(fill="x", pady=(0, 10))

        tbl_left = tk.Frame(tables_wrapper, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
        tbl_left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tbl_right = tk.Frame(tables_wrapper, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
        tbl_right.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # Awal Bulan Hijriah di Masehi
        tk.Label(tbl_left, text="AWAL BULAN HIJRIAH DI MASEHI", bg="#ffde59", fg="#000000", font=("Consolas", 9, "bold"), bd=1, relief="solid", padx=4, pady=2).pack(fill="x", pady=(0, 4))

        hy_bar = tk.Frame(tbl_left, bg="#ffffff")
        hy_bar.pack(fill="x", pady=2)
        tk.Button(hy_bar, text="◀", font=("Consolas", 8, "bold"), command=lambda: self._step_hy(-1)).pack(side="left")
        self.tbl_hy_var = tk.StringVar(value="1448")
        ttk.Entry(hy_bar, textvariable=self.tbl_hy_var, width=8, font=("Consolas", 9, "bold")).pack(side="left", padx=4)
        tk.Label(hy_bar, text="H", bg="#ffffff", font=("Consolas", 9, "bold")).pack(side="left")
        tk.Button(hy_bar, text="▶", font=("Consolas", 8, "bold"), command=lambda: self._step_hy(1)).pack(side="left", padx=2)
        ttk.Button(hy_bar, text="RENDER", command=self._render_hijri_starts).pack(side="right")

        self.tree_hijri = ttk.Treeview(tbl_left, columns=("Bulan", "Hari", "Masehi", "Durasi"), show="headings", height=12)
        self.tree_hijri.heading("Bulan", text="BULAN H")
        self.tree_hijri.heading("Hari", text="HARI")
        self.tree_hijri.heading("Masehi", text="TGL MASEHI")
        self.tree_hijri.heading("Durasi", text="DURASI")
        self.tree_hijri.column("Bulan", width=80, anchor="w")
        self.tree_hijri.column("Hari", width=50, anchor="center")
        self.tree_hijri.column("Masehi", width=95, anchor="w")
        self.tree_hijri.column("Durasi", width=50, anchor="center")
        self.tree_hijri.pack(fill="both", expand=True, pady=4)

        # Awal Bulan Masehi di Hijriah
        tk.Label(tbl_right, text="AWAL BULAN MASEHI DI HIJRIAH", bg="#ffde59", fg="#000000", font=("Consolas", 9, "bold"), bd=1, relief="solid", padx=4, pady=2).pack(fill="x", pady=(0, 4))

        gy_bar = tk.Frame(tbl_right, bg="#ffffff")
        gy_bar.pack(fill="x", pady=2)
        tk.Button(gy_bar, text="◀", font=("Consolas", 8, "bold"), command=lambda: self._step_gy(-1)).pack(side="left")
        self.tbl_gy_var = tk.StringVar(value="2026")
        ttk.Entry(gy_bar, textvariable=self.tbl_gy_var, width=8, font=("Consolas", 9, "bold")).pack(side="left", padx=4)
        tk.Label(gy_bar, text="M", bg="#ffffff", font=("Consolas", 9, "bold")).pack(side="left")
        tk.Button(gy_bar, text="▶", font=("Consolas", 8, "bold"), command=lambda: self._step_gy(1)).pack(side="left", padx=2)
        ttk.Button(gy_bar, text="RENDER", command=self._render_greg_starts).pack(side="right")

        self.tree_greg = ttk.Treeview(tbl_right, columns=("Bulan", "Hari", "Hijriah", "Durasi"), show="headings", height=12)
        self.tree_greg.heading("Bulan", text="BULAN M")
        self.tree_greg.heading("Hari", text="HARI")
        self.tree_greg.heading("Hijriah", text="TGL HIJRIAH")
        self.tree_greg.heading("Durasi", text="DURASI")
        self.tree_greg.column("Bulan", width=80, anchor="w")
        self.tree_greg.column("Hari", width=50, anchor="center")
        self.tree_greg.column("Hijriah", width=95, anchor="w")
        self.tree_greg.column("Durasi", width=50, anchor="center")
        self.tree_greg.pack(fill="both", expand=True, pady=4)

        # Initialize Calendar State
        now = datetime.now()
        self.cal_cur_y = now.year
        self.cal_cur_m = now.month - 1

        self._render_calendar()

        # Initialize Converter inputs
        self.cg_d.insert(0, str(now.day))
        self.cg_m.set(GREG_MONTHS[now.month - 1])
        self.cg_y.insert(0, str(now.year))
        self._convert_greg_to_hijri()

        h_now = gregorian_to_hijri(now.year, now.month, now.day)
        self.ch_d.insert(0, str(h_now[2]))
        self.ch_m.set(HIJRI_MONTHS[h_now[1] - 1])
        self.ch_y.insert(0, str(h_now[0]))
        self._convert_hijri_to_greg()

        # Render Start Tables
        self.tbl_hy_var.set(str(h_now[0]))
        self.tbl_gy_var.set(str(now.year))
        self._render_hijri_starts()
        self._render_greg_starts()

    def _cal_prev_month(self):
        self.cal_cur_m -= 1
        if self.cal_cur_m < 0:
            self.cal_cur_m = 11
            self.cal_cur_y -= 1
        self._render_calendar()

    def _cal_next_month(self):
        self.cal_cur_m += 1
        if self.cal_cur_m > 11:
            self.cal_cur_m = 0
            self.cal_cur_y += 1
        self._render_calendar()

    def _cal_go_today(self):
        now = datetime.now()
        self.cal_cur_y = now.year
        self.cal_cur_m = now.month - 1
        self._render_calendar()

    def _cal_jump(self):
        try:
            m_idx = GREG_MONTHS.index(self.cal_m_var.get())
            y = int(self.cal_y_var.get())
            self.cal_cur_m = m_idx
            self.cal_cur_y = y
            self._render_calendar()
        except Exception:
            pass

    def _render_calendar(self):
        for widget in self.cal_grid_frame.winfo_children():
            widget.destroy()

        y = self.cal_cur_y
        m = self.cal_cur_m

        self.cal_title_greg.config(text=f"{GREG_MONTHS[m].upper()} {y}")
        self.cal_m_var.set(GREG_MONTHS[m])
        self.cal_y_var.set(str(y))

        first_h = jd_to_hijri(gregorian_to_jd(y, m + 1, 1))
        # Days in month
        if m in (0, 2, 4, 6, 7, 9, 11):
            dim = 31
        elif m in (3, 5, 8, 10):
            dim = 30
        else:
            dim = 29 if ((y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)) else 28

        last_h = jd_to_hijri(gregorian_to_jd(y, m + 1, dim))

        if first_h[1] == last_h[1]:
            self.cal_title_hijri.config(text=f"{HIJRI_MONTHS[first_h[1]-1]} {first_h[0]} H")
        else:
            self.cal_title_hijri.config(text=f"{HIJRI_MONTHS[first_h[1]-1]} - {HIJRI_MONTHS[last_h[1]-1]} {first_h[0]} H")

        # First day dow
        first_dow = datetime(y, m + 1, 1).weekday()
        # In Python weekday: Monday=0, Sunday=6. We want Sunday=0, Monday=1
        first_dow = (first_dow + 1) % 7

        now = datetime.now()
        is_current_month = (now.year == y and now.month == (m + 1))

        # Blank padding
        for c in range(first_dow):
            f = tk.Frame(self.cal_grid_frame, bg="#f5f5f0", bd=1, relief="solid", height=45)
            f.grid(row=0, column=c, sticky="nsew", padx=1, pady=1)

        row = 0
        col = first_dow

        for d in range(1, dim + 1):
            h_date = gregorian_to_hijri(y, m + 1, d)
            is_today = is_current_month and (d == now.day)

            bg_c = "#ffde59" if is_today else "#ffffff"
            bd_c = 2 if is_today else 1

            cell = tk.Frame(self.cal_grid_frame, bg=bg_c, bd=bd_c, relief="solid", height=46)
            cell.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

            top_f = tk.Frame(cell, bg=bg_c)
            top_f.pack(fill="x", padx=2, pady=1)

            g_lbl = tk.Label(top_f, text=str(d), bg=bg_c, fg="#000000", font=("Consolas", 10, "bold"))
            g_lbl.pack(side="left")

            h_lbl = tk.Label(top_f, text=f"{h_date[2]} {HIJRI_MONTHS_SHORT[h_date[1]-1]}", bg="#000000", fg="#ffffff", font=("Consolas", 6, "bold"), padx=2)
            h_lbl.pack(side="right")

            holiday = get_islamic_holiday(h_date[1], h_date[2], h_date[0])
            if holiday:
                ev_lbl = tk.Label(cell, text=holiday, bg=bg_c, fg="#000000", font=("Consolas", 6, "bold"), anchor="w")
                ev_lbl.pack(fill="x", padx=2)

            cell.bind("<Button-1>", lambda e, day=d, hd=h_date, hol=holiday: self._on_cal_day_click(day, hd, hol))
            g_lbl.bind("<Button-1>", lambda e, day=d, hd=h_date, hol=holiday: self._on_cal_day_click(day, hd, hol))
            h_lbl.bind("<Button-1>", lambda e, day=d, hd=h_date, hol=holiday: self._on_cal_day_click(day, hd, hol))

            col += 1
            if col == 7:
                col = 0
                row += 1

        if is_current_month:
            h_today = gregorian_to_hijri(y, m + 1, now.day)
            hol_today = get_islamic_holiday(h_today[1], h_today[2], h_today[0])
            self._on_cal_day_click(now.day, h_today, hol_today)

    def _on_cal_day_click(self, day, h_date, holiday):
        dow_idx = datetime(self.cal_cur_y, self.cal_cur_m + 1, day).weekday()
        dow_idx = (dow_idx + 1) % 7
        dow_name = DAYS_ID[dow_idx]

        txt = f"TERPILIH: {dow_name}, {day} {GREG_MONTHS[self.cal_cur_m]} {self.cal_cur_y} M  =  {h_date[2]} {HIJRI_MONTHS[h_date[1]-1]} {h_date[0]} H"
        if holiday:
            txt += f"  [{holiday}]"
        self.cal_sel_lbl.config(text=txt)

    def _convert_greg_to_hijri(self):
        try:
            d = int(self.cg_d.get())
            m = GREG_MONTHS.index(self.cg_m.get()) + 1
            y = int(self.cg_y.get())

            h = gregorian_to_hijri(y, m, d)
            dow_idx = (datetime(y, m, d).weekday() + 1) % 7
            hol = get_islamic_holiday(h[1], h[2], h[0])

            self.cg_res_lbl.config(text=f"HASIL: {DAYS_ID[dow_idx]}, {h[2]} {HIJRI_MONTHS[h[1]-1]} {h[0]} H")
            self.cg_holiday_lbl.config(text=f"PERINGATAN: {hol}" if hol else "")
        except Exception as err:
            messagebox.showerror("ERROR", f"Gagal mengonversi Masehi: {err}")

    def _convert_hijri_to_greg(self):
        try:
            d = int(self.ch_d.get())
            m = HIJRI_MONTHS.index(self.ch_m.get()) + 1
            y = int(self.ch_y.get())

            jd = hijri_to_jd(y, m, d)
            gy, gm, gd = jd_to_gregorian(jd)
            dow_idx = (datetime(gy, gm, gd).weekday() + 1) % 7
            hol = get_islamic_holiday(m, d, y)

            self.ch_res_lbl.config(text=f"HASIL: {DAYS_ID[dow_idx]}, {gd} {GREG_MONTHS[gm-1]} {gy} M")
            self.ch_holiday_lbl.config(text=f"PERINGATAN: {hol}" if hol else "")
        except Exception as err:
            messagebox.showerror("ERROR", f"Gagal mengonversi Hijriah: {err}")

    def _step_hy(self, delta):
        try:
            val = int(self.tbl_hy_var.get()) + delta
            self.tbl_hy_var.set(str(val))
            self._render_hijri_starts()
        except Exception:
            pass

    def _step_gy(self, delta):
        try:
            val = int(self.tbl_gy_var.get()) + delta
            self.tbl_gy_var.set(str(val))
            self._render_greg_starts()
        except Exception:
            pass

    def _render_hijri_starts(self):
        for item in self.tree_hijri.get_children():
            self.tree_hijri.delete(item)

        try:
            hy = int(self.tbl_hy_var.get())
            for m in range(1, 13):
                jd = hijri_to_jd(hy, m, 1)
                gy, gm, gd = jd_to_gregorian(jd)
                dow_idx = (datetime(gy, gm, gd).weekday() + 1) % 7
                dur = hijri_month_days(hy, m)
                self.tree_hijri.insert("", "end", values=(f"1 {HIJRI_MONTHS[m-1]}", DAYS_ID[dow_idx], f"{gd} {GREG_MONTHS[gm-1]} {gy}", f"{dur} Hari"))
        except Exception:
            pass

    def _render_greg_starts(self):
        for item in self.tree_greg.get_children():
            self.tree_greg.delete(item)

        try:
            gy = int(self.tbl_gy_var.get())
            for m in range(1, 13):
                jd = gregorian_to_jd(gy, m, 1)
                hy, hm, hd = jd_to_hijri(jd)
                dow_idx = (datetime(gy, m, 1).weekday() + 1) % 7
                if m in (1, 3, 5, 7, 8, 10, 12):
                    dur = 31
                elif m in (4, 6, 9, 11):
                    dur = 30
                else:
                    dur = 29 if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)) else 28
                self.tree_greg.insert("", "end", values=(f"1 {GREG_MONTHS[m-1]}", DAYS_ID[dow_idx], f"{hd} {HIJRI_MONTHS[hm-1]} {hy} H", f"{dur} Hari"))
        except Exception:
            pass


if __name__ == "__main__":
    app = AdvancedCalculatorApp()
    app.mainloop()
