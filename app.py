"""Desta desktop interface. Pure mathematics lives in engine.py."""
import math
import tkinter as tk
from tkinter import ttk, font as tkfont
from datetime import datetime, timezone
from calculator import Calculator
from engine import (
    CITIES, DAYS_ID, GREG_MONTHS, HIJRI_MONTHS, HIJRI_MONTHS_SHORT, PRAYERS,
    display_expression,
    calculate_julian_day, jd_to_gregorian, gregorian_to_hijri,
    hijri_to_jd, hijri_month_days, get_islamic_holiday, calculate_qibla,
    prayer_schedule, location_timezone, validate_date, validate_location,
)
from widgets import ScrollPage, button, label, THEME_PAPER, THEME_WHITE, THEME_BLACK, THEME_TEAL, THEME_YELLOW


class AdvancedCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Desta — Kalkulator & Kalender")
        self.geometry("960x780")
        self.minsize(620, 480)
        self.configure(bg=THEME_PAPER)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=(10, 8), font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", THEME_TEAL)])
        style.configure("TEntry", padding=7)
        style.configure("TCombobox", padding=7)
        heading = tk.Label(self, text="DESTA CALCULATOR", bg=THEME_TEAL, fg=THEME_BLACK, bd=3, relief="solid", font=("Arial", 20, "bold"), pady=8)
        heading.pack(fill="x", padx=12, pady=12)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.pages = []
        for title in ("Kalkulator", "Hari Julian", "Kiblat & Shalat", "Kalender"):
            page = ScrollPage(self.notebook)
            page.error = tk.StringVar()
            self.notebook.add(page, text=title)
            error = tk.Label(page.body, textvariable=page.error, fg="#800080", bg=THEME_WHITE, anchor="w", justify="left")
            error.pack(fill="x")
            error.bind("<Configure>", lambda event, widget=error: widget.configure(wraplength=max(100, event.width-8)))
            self.pages.append(page)
        self._init_calculator()
        self._init_julian()
        self._init_qibla()
        self._init_calendar()
        self.bind_all("<MouseWheel>", self._scroll)
        self.bind_all("<KeyPress>", self._keyboard, add="+")
        self.bind_all("<FocusIn>", self._reveal_focus, add="+")
        self.after(1000, self._prayer_tick)

    def _scroll(self, event):
        page = self.pages[self.notebook.index("current")]
        page.wheel(event)

    def _reveal_focus(self, event):
        page = self.pages[self.notebook.index("current")]
        widget = event.widget
        if not str(widget).startswith(str(page.body)):
            return
        self.update_idletasks()
        top = widget.winfo_rooty()-page.body.winfo_rooty()
        visible = page.canvas.canvasy(0)
        height = page.canvas.winfo_height()
        if top < visible or top + widget.winfo_height() > visible + height:
            page.canvas.yview_moveto(max(0, top-12)/max(1, page.body.winfo_height()))

    def _guard(self, page, fn):
        try:
            fn()
            page.error.set("")
            return True
        except (ValueError, OverflowError, TypeError) as error:
            page.error.set(str(error))
            return False

    def _text(self, parent, text="", variable=None):
        widget = label(parent, text, anchor="w", justify="left")
        if variable is not None:
            widget.configure(textvariable=variable)
        widget.pack(fill="x", pady=5)
        widget.bind("<Configure>", lambda e: widget.configure(wraplength=max(80,e.width-6)))
        return widget

    def _field(self, parent, title, value=""):
        self._text(parent, title)
        variable = tk.StringVar(value=str(value))
        entry = ttk.Entry(parent, textvariable=variable)
        entry.pack(fill="x", pady=(0, 8))
        return variable

    def _init_calculator(self):
        page = self.pages[0]
        body = page.body
        self.calc = Calculator()
        self.calc_expr_var = tk.StringVar(value="0")
        self.calc_result_var = tk.StringVar(value="0")
        self._text(body, "MASUKAN")
        entry = tk.Entry(body, textvariable=self.calc_expr_var, state="readonly", readonlybackground=THEME_WHITE, font=("Consolas", 15), justify="right", bd=3, relief="solid")
        entry.pack(fill="x")
        scrollbar = ttk.Scrollbar(body, orient="horizontal", command=entry.xview)
        scrollbar.pack(fill="x")
        entry.configure(xscrollcommand=scrollbar.set)
        self.calc_entry = entry
        self._text(body, "HASIL")
        self.result_font = tkfont.Font(family="Consolas", size=25, weight="bold")
        result = tk.Label(body, textvariable=self.calc_result_var, font=self.result_font, bg=THEME_WHITE, anchor="e", width=1)
        result.pack(fill="x", pady=(0, 12))
        def fit_result(_=None):
            available = max(10,result.winfo_width()-10)
            for size in range(25, 9, -1):
                self.result_font.configure(size=size)
                if self.result_font.measure(self.calc_result_var.get()) <= available: break
        result.bind("<Configure>", fit_result)
        self.calc_result_var.trace_add("write", lambda *_: fit_result())
        self.mode_button = button(body, "Mode sudut: DEG", self._toggle_angle, True)
        self.mode_button.pack(anchor="w", pady=(0, 12))
        panels = tk.Frame(body, bg=THEME_WHITE)
        panels.pack(fill="x")
        self.number_panel = tk.Frame(panels, bg=THEME_WHITE, bd=2, relief="solid", padx=8, pady=8)
        self.science_panel = tk.Frame(panels, bg=THEME_PAPER, bd=2, relief="solid", padx=8, pady=8)
        numeric = [("AC","clear"),("C","back"),("Ans","Ans"),("÷","/"),("7","7"),("8","8"),("9","9"),("×","*"),("4","4"),("5","5"),("6","6"),("−","-"),("1","1"),("2","2"),("3","3"),("+","+"),("±","fn:neg"),("0","0"),(".","."),("=","equals")]
        scientific = [("sin","fn:sin"),("cos","fn:cos"),("tan","fn:tan"),("asin","fn:asin"),("acos","fn:acos"),("atan","fn:atan"),("log","fn:log"),("ln","fn:ln"),("√x","fn:sqrt"),("x²","fn:square"),("xʸ","**"),("10ˣ","fn:powten"),("exp","fn:exp"),("1/x","fn:inv"),("n!","fn:factorial"),("abs","fn:abs"),("%","%"),("π","pi"),("e","e"),("(","("),(")",")")]
        for panel, title, keys, columns in [(self.number_panel,"ANGKA & OPERASI",numeric,4),(self.science_panel,"FUNGSI ILMIAH",scientific,3)]:
            self._text(panel,title)
            grid = tk.Frame(panel,bg=panel.cget("bg"));grid.pack(fill="both",expand=True)
            for i,(caption,action) in enumerate(keys):
                key = button(grid,caption,lambda a=action:self._calc_action(a),action=="equals")
                key.configure(width=1)
                if action in ("clear","back"): key.configure(bg=THEME_BLACK,fg=THEME_WHITE)
                key.grid(row=i//columns,column=i%columns,sticky="nsew",padx=3,pady=3)
                grid.columnconfigure(i%columns,weight=1,uniform="keys")
                grid.rowconfigure(i//columns,weight=1,minsize=50,uniform="keys")
        self.calc_layout = None
        def reflow(event):
            wide = event.width >= 760
            if wide == self.calc_layout:return
            self.calc_layout = wide
            self.number_panel.grid_forget();self.science_panel.grid_forget()
            panels.columnconfigure(0,weight=3 if wide else 1)
            panels.columnconfigure(1,weight=4 if wide else 0)
            if wide:
                self.science_panel.grid(row=0,column=0,sticky="nsew",padx=(0,10));self.number_panel.grid(row=0,column=1,sticky="nsew")
            else:
                self.number_panel.grid(row=0,column=0,sticky="nsew",pady=(0,10));self.science_panel.grid(row=1,column=0,sticky="nsew")
        panels.bind("<Configure>",reflow)
        self._text(body,"Keyboard: angka/operator, Enter untuk hasil, Backspace untuk hapus, Esc untuk kosongkan. Fungsi ilmiah bekerja pada operand terakhir; kelompokkan dengan kurung. % adalah sisa bagi.")

    def _calc_action(self, action):
        def perform():
            if action == "clear": self.calc.clear()
            elif action == "back": self.calc.backspace()
            elif action == "equals": self.calc.calculate()
            elif action.startswith("fn:"): self.calc.apply(action[3:])
            else: self.calc.append(action)
        self._guard(self.pages[0],perform)
        self.calc_expr_var.set(display_expression(self.calc.expression) or "0")
        self.calc_result_var.set(self.calc.result)
        self.calc_entry.xview_moveto(1)

    def _toggle_angle(self):
        modes=("DEG","RAD","GRAD")
        self.calc.mode=modes[(modes.index(self.calc.mode)+1)%3]
        self.calc.evaluated=False
        self.mode_button.configure(text="Mode sudut: "+self.calc.mode)

    def _keyboard(self,event):
        if self.notebook.index("current") != 0 or event.state & 0x000C:return
        if isinstance(event.widget,(ttk.Entry,ttk.Combobox)):return
        if isinstance(event.widget,tk.Button) and event.keysym in ("Return", "KP_Enter"):
            event.widget.invoke()
            return "break"
        action={"Return":"equals","KP_Enter":"equals","BackSpace":"back","Escape":"clear"}.get(event.keysym)
        if not action and event.char and event.char in "0123456789.+-*/%()=,^":action={"=":"equals",",":".","^":"**"}.get(event.char,event.char)
        if action:self._calc_action(action);return "break"

    def _init_julian(self):
        page=self.pages[1];body=page.body
        self.jd_vars={name:self._field(body,title) for name,title in [("year","Tahun"),("month","Bulan"),("day","Tanggal"),("time","Waktu lokal (JJ:MM:DD)"),("utc","UTC (jam)")]}
        button(body,"Hitung JD",lambda:self._guard(page,self._compute_jd),True).pack(fill="x",pady=5)
        button(body,"Waktu sekarang",self._set_current_datetime).pack(fill="x",pady=5)
        self.jd_result=tk.StringVar()
        self._text(body,variable=self.jd_result)
        self._text(body,"Tanggal menggunakan kalender Gregorian proleptik, termasuk sebelum 1582.")
        for variable in self.jd_vars.values():variable.trace_add("write",lambda *_:self.jd_result.set("Masukan berubah — tekan Hitung JD."))
        self._set_current_datetime()

    def _set_current_datetime(self):
        now=datetime.now().astimezone()
        for key,value in dict(year=now.year,month=now.month,day=now.day,time=now.strftime("%H:%M:%S"),utc=now.utcoffset().total_seconds()/3600).items():self.jd_vars[key].set(str(value))
        self._guard(self.pages[1],self._compute_jd)

    def _compute_jd(self):
        values={k:v.get() for k,v in self.jd_vars.items()}
        parts=values["time"].split(":")
        if len(parts)!=3:raise ValueError("Gunakan waktu JJ:MM:DD.")
        result=calculate_julian_day(int(values["year"]),int(values["month"]),int(values["day"]),*(int(x) for x in parts),float(values["utc"]))
        self.jd_result.set(f"JD: {result:.6f}\nMJD: {result-2400000.5:.6f}")

    def _init_qibla(self):
        page=self.pages[2];body=page.body
        self.zone=None;self.location=None;self.schedule=None
        self._text(body,"Kota")
        self.city_var=tk.StringVar(value=CITIES[0]["name"])
        city=ttk.Combobox(body,textvariable=self.city_var,values=["Koordinat manual"]+[c["name"] for c in CITIES],state="readonly")
        city.pack(fill="x",pady=5)
        city.bind("<<ComboboxSelected>>",lambda _:self._select_city())
        self.lat_var=self._field(body,"Lintang (°)")
        self.lon_var=self._field(body,"Bujur (°)")
        self.tz_var=self._field(body,"UTC (jam)")
        self.q_zone=tk.StringVar();self._text(body,variable=self.q_zone)
        button(body,"Hitung kiblat & shalat",lambda:self._guard(page,self._compute_qibla),True).pack(fill="x",pady=8)
        self.q_result=tk.StringVar();self._text(body,variable=self.q_result)
        self.current_qibla_bearing=0
        self.compass_canvas=tk.Canvas(body,bg=THEME_WHITE,height=280,highlightthickness=2,highlightbackground=THEME_BLACK)
        self.compass_canvas.pack(fill="x",pady=8)
        self.compass_canvas.bind("<Configure>",lambda _:self._draw_compass(self.current_qibla_bearing) if self.location else None)
        self._text(body,"Arah statis dari utara sejati. Desktop tidak memakai sensor GPS/kompas.")
        self.prayer_context=tk.StringVar();self._text(body,variable=self.prayer_context)
        self.prayer_countdown=tk.StringVar();self._text(body,variable=self.prayer_countdown)
        grid=tk.Frame(body,bg=THEME_WHITE);grid.pack(fill="x")
        self.prayer_values={}
        for i,(key,title) in enumerate(PRAYERS):
            frame=tk.Frame(grid,bg=THEME_PAPER,bd=2,relief="solid",padx=4,pady=6);frame.grid(row=i//3,column=i%3,sticky="nsew",padx=3,pady=3)
            grid.columnconfigure(i%3,weight=1,uniform="prayer")
            label(frame,title).pack()
            variable=tk.StringVar(value="—");self.prayer_values[key]=variable
            value=label(frame);value.configure(textvariable=variable);value.pack(fill="x")
            value.bind("<Configure>",lambda e,w=value:w.configure(wraplength=max(50,e.width-4)))
        self._text(body,"Estimasi Matahari: Subuh −20°, Isya −18°; +2 menit hanya pada Dzuhur/Maghrib. Bukan jadwal resmi. Waktu di lintang tinggi dapat tidak tersedia.")
        for variable in (self.lat_var,self.lon_var,self.tz_var):variable.trace_add("write",self._location_dirty)
        self.loading_location=False
        self._select_city()

    def _location_dirty(self,*_):
        if self.loading_location:return
        self.zone=None;self.location=None;self.schedule=None
        self.city_var.set("Koordinat manual")
        self.q_zone.set("UTC manual; sesuaikan dengan zona lokasi.")
        self.q_result.set("Lokasi berubah — tekan Hitung.")
        self.prayer_countdown.set("Jadwal menunggu perhitungan ulang.")
        self.prayer_context.set("")
        self.compass_canvas.delete("all")
        for variable in self.prayer_values.values():variable.set("—")

    def _select_city(self):
        city=next((c for c in CITIES if c["name"]==self.city_var.get()),None)
        if not city:self._location_dirty();return
        def select():
            tz=location_timezone(city["zone"])
            self.loading_location=True
            try:
                self.lat_var.set(str(city["lat"]));self.lon_var.set(str(city["lon"]));self.tz_var.set(str(datetime.now(tz).utcoffset().total_seconds()/3600))
            finally:self.loading_location=False
            self.zone=city["zone"]
            self._compute_qibla()
        self._guard(self.pages[2],select)

    def _compute_qibla(self):
        lat,lon,offset=float(self.lat_var.get()),float(self.lon_var.get()),float(self.tz_var.get())
        validate_location(lat,lon,offset)
        result=calculate_qibla(lat,lon)
        schedule=prayer_schedule(lat,lon,self.zone,offset)
        self.location=(lat,lon,self.zone,offset)
        self.schedule=schedule
        self.current_qibla_bearing=result["bearing_deg"]
        self.q_result.set(f"{self.city_var.get()}\nArah {result['bearing_deg']:.2f}° dari utara sejati\nJarak ke Ka’bah {result['distance_km']:,.1f} km")
        self.q_zone.set(f"Zona {self.zone}; UTC/DST mengikuti tanggal." if self.zone else "UTC manual.")
        self._draw_compass(self.current_qibla_bearing)
        self._render_prayers()

    def _render_prayers(self):
        for key,var in self.prayer_values.items():var.set(self.schedule["times"][key])
        self.prayer_context.set(f"{self.schedule['date']} · {self.city_var.get()} · UTC{self.schedule['offset']:+g}")

    def _prayer_tick(self):
        def update():
            if not self.location or not self.schedule:return
            now=datetime.now(timezone.utc)
            lat,lon,zone,offset=self.location
            if now.astimezone(location_timezone(zone,offset)).date()!=self.schedule["date"]:
                self.schedule=prayer_schedule(lat,lon,zone,offset,now)
                self._render_prayers()
            upcoming=next((e for e in self.schedule["events"] if e["timestamp"]>now.timestamp()),None)
            if not upcoming:self.prayer_countdown.set("Waktu berikutnya tidak tersedia.");return
            seconds=max(0,math.ceil(upcoming["timestamp"]-now.timestamp()))
            self.prayer_countdown.set(f"Menuju {upcoming['label']}: {seconds//3600:02d}:{seconds%3600//60:02d}:{seconds%60:02d}")
        try:
            update()
        except (ValueError, OverflowError, TypeError) as error:
            self.pages[2].error.set(str(error))
        self.after(1000,self._prayer_tick)

    def _init_calendar(self):
        page=self.pages[3];body=page.body;now=datetime.now()
        self.cal_year,self.cal_month,self.cal_day=now.year,now.month,now.day
        self._text(body,"Hijriah tabular (hisab aritmetika); tanggal resmi dapat berbeda.")
        nav=tk.Frame(body,bg=THEME_WHITE);nav.pack(fill="x")
        for i,(caption,action) in enumerate([("◀ Bulan lalu",lambda:self._move_month(-1)),("Hari ini",self._today),("Bulan depan ▶",lambda:self._move_month(1))]):
            button(nav,caption,action).grid(row=0,column=i,sticky="ew",padx=4);nav.columnconfigure(i,weight=1,uniform="nav")
        self.cal_year_var=self._field(body,"Tahun kalender (623–9998)",now.year)
        self._text(body,"Bulan kalender")
        self.cal_month_var=tk.StringVar(value=GREG_MONTHS[now.month-1]);month=ttk.Combobox(body,textvariable=self.cal_month_var,values=GREG_MONTHS,state="readonly");month.pack(fill="x")
        button(body,"Buka bulan",lambda:self._guard(page,self._jump_calendar)).pack(fill="x",pady=8)
        self.cal_title=tk.StringVar();self._text(body,variable=self.cal_title)
        self.cal_grid=tk.Frame(body,bg=THEME_WHITE);self.cal_grid.pack(fill="x")
        self.cal_selected=tk.StringVar();self._text(body,variable=self.cal_selected)
        self.greg_date=self._field(body,"Masehi → Hijriah (YYYY-MM-DD)",now.strftime("%Y-%m-%d"))
        button(body,"Konversi ke Hijriah",lambda:self._guard(page,self._convert_greg),True).pack(fill="x")
        self.greg_result=tk.StringVar();self._text(body,variable=self.greg_result)
        hy,hm,hd=gregorian_to_hijri(now.year,now.month,now.day)
        self.hijri_day=self._field(body,"Tanggal Hijriah",hd)
        self._text(body,"Bulan Hijriah")
        self.hijri_month=tk.StringVar(value=HIJRI_MONTHS[hm-1]);ttk.Combobox(body,textvariable=self.hijri_month,values=HIJRI_MONTHS,state="readonly").pack(fill="x")
        self.hijri_year=self._field(body,"Tahun Hijriah (1–9665)",hy)
        button(body,"Konversi ke Masehi",lambda:self._guard(page,self._convert_hijri),True).pack(fill="x")
        self.hijri_result=tk.StringVar();self._text(body,variable=self.hijri_result)
        self._text(body,"AWAL BULAN")
        self.table_kind=tk.StringVar(value="Hijriah")
        choice=ttk.Combobox(body,textvariable=self.table_kind,values=["Hijriah","Masehi"],state="readonly");choice.pack(fill="x");choice.bind("<<ComboboxSelected>>",lambda _:self._switch_table())
        self.table_year=self._field(body,"Tahun tabel",hy)
        actions=tk.Frame(body,bg=THEME_WHITE);actions.pack(fill="x")
        for i,(caption,action) in enumerate([("◀ Tahun",lambda:self._step_table(-1)),("Tampilkan",lambda:self._guard(page,self._render_table)),("Tahun ▶",lambda:self._step_table(1))]):
            button(actions,caption,action).grid(row=0,column=i,sticky="ew",padx=3);actions.columnconfigure(i,weight=1)
        self.table=ttk.Treeview(body,columns=("month","weekday","date","duration"),show="headings",height=12)
        for key,title,width in [("month","Bulan",130),("weekday","Hari",85),("date","Tanggal padanan",185),("duration","Durasi",85)]:self.table.heading(key,text=title);self.table.column(key,width=width,minwidth=70)
        self.table.pack(fill="x",pady=(8,0));scroll=ttk.Scrollbar(body,orient="horizontal",command=self.table.xview);scroll.pack(fill="x");self.table.configure(xscrollcommand=scroll.set)
        self.greg_date.trace_add("write",lambda *_:self.greg_result.set("Tanggal berubah — tekan Konversi."))
        for v in (self.hijri_day,self.hijri_month,self.hijri_year):v.trace_add("write",lambda *_:self.hijri_result.set("Tanggal berubah — tekan Konversi."))
        self._render_calendar();self._convert_greg();self._convert_hijri();self._render_table()

    def _calendar_year(self,value):
        year=int(value)
        if not 623<=year<=9998:raise ValueError("Tahun kalender harus 623–9998.")
        return year

    def _jump_calendar(self):
        year=self._calendar_year(self.cal_year_var.get());month=GREG_MONTHS.index(self.cal_month_var.get())+1
        self.cal_year,self.cal_month,self.cal_day=year,month,1
        self._render_calendar()

    def _move_month(self,delta):
        def move():
            total=self.cal_year*12+self.cal_month-1+delta
            year,month=divmod(total,12);self._calendar_year(year)
            self.cal_year,self.cal_month,self.cal_day=year,month+1,1
            self._render_calendar()
        self._guard(self.pages[3],move)

    def _today(self):
        now=datetime.now();self.cal_year,self.cal_month,self.cal_day=now.year,now.month,now.day;self._render_calendar()

    def _render_calendar(self):
        import calendar
        y,m=self.cal_year,self.cal_month
        days=calendar.monthrange(y,m)[1]
        dates=[gregorian_to_hijri(y,m,d) for d in range(1,days+1)]
        first,last=dates[0],dates[-1]
        self.cal_year_var.set(y);self.cal_month_var.set(GREG_MONTHS[m-1])
        self.cal_title.set(f"{GREG_MONTHS[m-1]} {y}\n{HIJRI_MONTHS[first[1]-1]} {first[0]} – {HIJRI_MONTHS[last[1]-1]} {last[0]} H")
        for child in self.cal_grid.winfo_children():child.destroy()
        for col,name in enumerate(DAYS_ID):
            label(self.cal_grid,name[:3]).grid(row=0,column=col,sticky="ew");self.cal_grid.columnconfigure(col,weight=1,uniform="day")
        dow=(validate_date(y,m,1).weekday()+1)%7
        self.cal_buttons={}
        for day,h in enumerate(dates,1):
            key=button(self.cal_grid,f"{day}\n{h[2]} {HIJRI_MONTHS_SHORT[h[1]-1]}",lambda d=day:self._select_day(d))
            key.configure(font=("Arial",9),padx=1,width=1)
            index=dow+day-1;key.grid(row=index//7+1,column=index%7,sticky="nsew",padx=1,pady=1)
            self.cal_buttons[day]=key
            key.bind("<Left>",lambda e,d=day:self._focus_day(max(1,d-1)))
            key.bind("<Right>",lambda e,d=day:self._focus_day(min(days,d+1)))
            key.bind("<Up>",lambda e,d=day:self._focus_day(max(1,d-7)))
            key.bind("<Down>",lambda e,d=day:self._focus_day(min(days,d+7)))
        self._select_day(min(self.cal_day,days))

    def _focus_day(self,day):
        self._select_day(day);self.cal_buttons[day].focus_set();return "break"

    def _select_day(self,day):
        self.cal_day=day;y,m=self.cal_year,self.cal_month;hy,hm,hd=gregorian_to_hijri(y,m,day);dow=(validate_date(y,m,day).weekday()+1)%7
        event=get_islamic_holiday(hm,hd,hy)
        self.cal_selected.set(f"{DAYS_ID[dow]}, {day} {GREG_MONTHS[m-1]} {y} M\n{hd} {HIJRI_MONTHS[hm-1]} {hy} H"+("\n"+event if event else ""))
        today=datetime.now()
        for d,key in self.cal_buttons.items():key.configure(bg=THEME_TEAL if d==day else THEME_YELLOW if (y,m,d)==(today.year,today.month,today.day) else THEME_WHITE)

    def _convert_greg(self):
        parts=self.greg_date.get().split("-")
        if len(parts)!=3:raise ValueError("Gunakan tanggal YYYY-MM-DD.")
        y,m,d=map(int,parts);self._calendar_year(y)
        hy,hm,hd=gregorian_to_hijri(y,m,d);self.greg_result.set(f"{hd} {HIJRI_MONTHS[hm-1]} {hy} H")

    def _convert_hijri(self):
        y,m,d=int(self.hijri_year.get()),HIJRI_MONTHS.index(self.hijri_month.get())+1,int(self.hijri_day.get())
        gy,gm,gd=jd_to_gregorian(hijri_to_jd(y,m,d));self.hijri_result.set(f"{gd} {GREG_MONTHS[gm-1]} {gy} M")

    def _switch_table(self):
        now=datetime.now();self.table_year.set(gregorian_to_hijri(now.year,now.month,now.day)[0] if self.table_kind.get()=="Hijriah" else now.year)
        self._guard(self.pages[3],self._render_table)

    def _step_table(self,delta):
        def step():
            year=int(self.table_year.get())+delta
            if self.table_kind.get()=="Hijriah":hijri_month_days(year,1)
            else:self._calendar_year(year)
            self.table_year.set(year);self._render_table()
        self._guard(self.pages[3],step)

    def _render_table(self):
        import calendar
        y=int(self.table_year.get());hijri=self.table_kind.get()=="Hijriah"
        if hijri:hijri_month_days(y,1)
        else:self._calendar_year(y)
        rows=[]
        for month in range(1,13):
            if hijri:
                gy,gm,gd=jd_to_gregorian(hijri_to_jd(y,month,1));title=HIJRI_MONTHS[month-1];value=f"{gd} {GREG_MONTHS[gm-1]} {gy} M";duration=hijri_month_days(y,month)
            else:
                gy,gm,gd=y,month,1;hy,hm,hd=gregorian_to_hijri(y,month,1);title=GREG_MONTHS[month-1];value=f"{hd} {HIJRI_MONTHS[hm-1]} {hy} H";duration=calendar.monthrange(y,month)[1]
            rows.append((title,DAYS_ID[(validate_date(gy,gm,gd).weekday()+1)%7],value,f"{duration} hari"))
        self.table.delete(*self.table.get_children())
        for row in rows:self.table.insert("","end",values=row)

    def _draw_compass(self, bearing_deg: float):
        cv = self.compass_canvas
        cv.delete("all")

        w = cv.winfo_width()
        h = cv.winfo_height()
        if w <= 1 or h <= 1:
            w, h = 260, 260
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 25

        if radius < 35:
            radius = max(25, min(w, h) / 2 - 8)

        # Draw Outer Ring (Solid Black)
        cv.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=THEME_BLACK, width=3, fill=THEME_WHITE)
        cv.create_oval(cx - radius + 6, cy - radius + 6, cx + radius - 6, cy + radius - 6, outline=THEME_BLACK, width=1)

        # Cardinal Points
        cardinals = [("U", 0, THEME_BLACK), ("T", 90, THEME_BLACK), ("S", 180, THEME_BLACK), ("B", 270, THEME_BLACK)]
        for label, deg, color in cardinals:
            rad = math.radians(deg - 90)
            lx = cx + (radius - 18) * math.cos(rad)
            ly = cy + (radius - 18) * math.sin(rad)
            cv.create_text(lx, ly, text=label, fill=color, font=("Arial", 11, "bold"))

        # Tick marks
        for deg in range(0, 360, 15):
            rad = math.radians(deg - 90)
            x1 = cx + (radius - 6) * math.cos(rad)
            y1 = cy + (radius - 6) * math.sin(rad)
            x2 = cx + radius * math.cos(rad)
            y2 = cy + radius * math.sin(rad)
            cv.create_line(x1, y1, x2, y2, fill=THEME_BLACK, width=1)

        # Draw North Needle (Solid black pointer)
        cv.create_line(cx, cy, cx, cy - (radius - 32), fill=THEME_BLACK, width=3, arrow=tk.LAST, arrowshape=(10, 12, 5))

        # Draw Qibla Vector Needle (Electric Yellow with black outline)
        q_rad = math.radians(bearing_deg - 90)
        qx = cx + (radius - 28) * math.cos(q_rad)
        qy = cy + (radius - 28) * math.sin(q_rad)

        cv.create_line(cx, cy, qx, qy, fill=THEME_YELLOW, width=5, arrow=tk.LAST, arrowshape=(12, 15, 6))

        # Kaaba marker (Isometric 3D Kaaba Graphic - Scaled proportionately)
        kx = cx + (radius - 14) * math.cos(q_rad)
        ky = cy + (radius - 14) * math.sin(q_rad)
        s = max(0.55, min(1.15, radius / 95.0))

        # Marble Foundation (Syadzarwan)
        cv.create_polygon(kx - 12 * s, ky + 1 * s, kx, ky + 7 * s, kx, ky + 9 * s, kx - 12 * s, ky + 3 * s, fill="#e5e5ea", outline=THEME_BLACK, width=1)
        cv.create_polygon(kx, ky + 7 * s, kx + 12 * s, ky + 1 * s, kx + 12 * s, ky + 3 * s, kx, ky + 9 * s, fill="#d1d1d6", outline=THEME_BLACK, width=1)
        # Left Face (Dark Black)
        cv.create_polygon(kx - 12 * s, ky - 9 * s, kx, ky - 3 * s, kx, ky + 7 * s, kx - 12 * s, ky + 1 * s, fill="#111111", outline=THEME_BLACK, width=1)
        # Right Face (Charcoal Black)
        cv.create_polygon(kx, ky - 3 * s, kx + 12 * s, ky - 9 * s, kx + 12 * s, ky + 1 * s, kx, ky + 7 * s, fill="#1c1c1e", outline=THEME_BLACK, width=1)
        # Roof
        cv.create_polygon(kx, ky - 16 * s, kx + 12 * s, ky - 9 * s, kx, ky - 3 * s, kx - 12 * s, ky - 9 * s, fill="#2c2c2e", outline=THEME_BLACK, width=1)
        # Golden Kiswah Band Left
        cv.create_polygon(kx - 12 * s, ky - 6.5 * s, kx, ky - 0.5 * s, kx, ky + 1.5 * s, kx - 12 * s, ky - 4.5 * s, fill=THEME_YELLOW, outline=THEME_BLACK, width=1)
        # Golden Kiswah Band Right
        cv.create_polygon(kx, ky - 0.5 * s, kx + 12 * s, ky - 6.5 * s, kx + 12 * s, ky - 4.5 * s, kx, ky + 1.5 * s, fill=THEME_YELLOW, outline=THEME_BLACK, width=1)
        # Golden Door (Bab al-Kaaba)
        cv.create_polygon(kx + 3 * s, ky - 1 * s, kx + 8 * s, ky - 3.5 * s, kx + 8 * s, ky + 2.5 * s, kx + 3 * s, ky + 5 * s, fill=THEME_YELLOW, outline=THEME_BLACK, width=1)

        # Center Dot
        cv.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=THEME_BLACK, outline="")

        # Text Overlay
        cv.create_text(cx, cy + radius + 12, text=f"KIBLAT: {bearing_deg:.1f}°", fill=THEME_BLACK, font=("Arial", 10, "bold"))



if __name__ == "__main__":
    AdvancedCalculatorApp().mainloop()
